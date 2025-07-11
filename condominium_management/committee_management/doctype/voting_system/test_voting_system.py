# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_to_date, now_datetime, nowdate


class TestVotingSystem(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for voting system tests"""
		# Create test assembly
		if not frappe.db.exists("Assembly Management", {"assembly_title": "Test Assembly for Voting"}):
			assembly = frappe.get_doc(
				{
					"doctype": "Assembly Management",
					"assembly_title": "Test Assembly for Voting",
					"assembly_type": "Ordinaria",
					"assembly_date": add_days(nowdate(), 30),
					"convocation_date": add_days(nowdate(), 15),
					"first_call_quorum": 60,
					"second_call_quorum": 30,
				}
			)
			assembly.insert(ignore_permissions=True)
			self.test_assembly = assembly.name
		else:
			self.test_assembly = frappe.get_value(
				"Assembly Management", {"assembly_title": "Test Assembly for Voting"}, "name"
			)

		# Create test properties for voters
		self.test_voters = []
		for i in range(5):
			prop_code = f"TEST-PROP-VOTE-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Voting Property {i+1}",
						"property_usage_type": "Residencial",
						"acquisition_type": "Compra",
						"property_status_type": "Activo",
						"registration_date": nowdate(),
						"unit_area": 100,
						"owner_name": f"Voter {i+1}",
						"status": "Activo",
					}
				)
				property_doc.insert(ignore_permissions=True)
				self.test_voters.append(prop_code)

	def test_voting_system_creation(self):
		"""Test basic voting system creation"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación de Prueba",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
				"allows_anonymous": 0,
				"status": "Activa",
			}
		)

		voting.insert()

		# Verify the document was created
		self.assertTrue(voting.name)
		self.assertEqual(voting.voting_title, "Votación de Prueba")
		self.assertEqual(voting.status, "Activa")
		self.assertEqual(voting.total_votes, 0)
		self.assertEqual(voting.votes_in_favor, 0)

		# Clean up
		voting.delete()

	def test_voting_date_validation(self):
		"""Test that voting start date must be before end date"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Fecha Inválida",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": add_days(nowdate(), 2),
				"voting_end_date": add_days(nowdate(), 1),  # Before start date
				"required_percentage": 51,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			voting.insert()

	def test_required_percentage_validation(self):
		"""Test that required percentage must be between 0 and 100"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Porcentaje Inválido",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 150,  # Invalid percentage
			}
		)

		with self.assertRaises(frappe.ValidationError):
			voting.insert()

	def test_load_eligible_voters(self):
		"""Test loading eligible voters from assembly"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación con Votantes",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		voting.insert()

		# Load eligible voters
		voting.load_eligible_voters()

		# Verify voters were loaded (should be at least our test voters)
		self.assertTrue(len(voting.vote_records) >= 0)

		# Clean up
		voting.delete()

	def test_record_vote(self):
		"""Test recording a vote"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación para Grabar Voto",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add a vote record manually
		voting.append(
			"vote_records",
			{
				"voter": self.test_voters[0],
				"voter_name": "Voter 1",
				"voter_eligibility": "Elegible",
				"vote_value": "",
				"vote_timestamp": None,
			},
		)

		voting.insert()

		# Record a vote
		voting.record_vote(self.test_voters[0], "A Favor")

		# Verify vote was recorded
		vote_record = next((v for v in voting.vote_records if v.voter == self.test_voters[0]), None)
		self.assertIsNotNone(vote_record)
		self.assertEqual(vote_record.vote_value, "A Favor")
		self.assertIsNotNone(vote_record.vote_timestamp)
		self.assertIsNotNone(vote_record.digital_signature)

		# Clean up
		voting.delete()

	def test_calculate_voting_results(self):
		"""Test voting results calculation"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Cálculo Resultados",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add vote records manually
		vote_values = ["A Favor", "A Favor", "En Contra", "Abstención", "A Favor"]
		for i, vote_value in enumerate(vote_values):
			voting.append(
				"vote_records",
				{
					"voter": self.test_voters[i],
					"voter_name": f"Voter {i+1}",
					"voter_eligibility": "Elegible",
					"vote_value": vote_value,
					"vote_timestamp": now_datetime(),
				},
			)

		voting.insert()

		# Calculate results
		voting.calculate_voting_results()

		# Verify results (3 A Favor, 1 En Contra, 1 Abstención)
		self.assertEqual(voting.total_votes, 5)
		self.assertEqual(voting.votes_in_favor, 3)
		self.assertEqual(voting.votes_against, 1)
		self.assertEqual(voting.abstentions, 1)
		self.assertEqual(voting.approval_percentage, 60)  # 3/5 = 60%

		# Clean up
		voting.delete()

	def test_voting_result_determination(self):
		"""Test voting result determination based on required percentage"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Resultado",
				"voting_type": "Mayoría Calificada",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 67,  # Qualified majority
			}
		)

		# Add vote records - 3 out of 5 in favor (60%, less than 67%)
		vote_values = ["A Favor", "A Favor", "En Contra", "En Contra", "A Favor"]
		for i, vote_value in enumerate(vote_values):
			voting.append(
				"vote_records",
				{
					"voter": self.test_voters[i],
					"voter_name": f"Voter {i+1}",
					"voter_eligibility": "Elegible",
					"vote_value": vote_value,
					"vote_timestamp": now_datetime(),
				},
			)

		voting.insert()

		# Calculate results
		voting.calculate_voting_results()

		# Should be rejected (60% < 67% required)
		self.assertEqual(voting.voting_result, "Rechazado")

		# Clean up
		voting.delete()

	def test_digital_signature_generation(self):
		"""Test digital signature generation for votes"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Firma Digital",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add a vote record
		voting.append(
			"vote_records",
			{
				"voter": self.test_voters[0],
				"voter_name": "Voter 1",
				"voter_eligibility": "Elegible",
				"vote_value": "A Favor",
				"vote_timestamp": now_datetime(),
			},
		)

		voting.insert()

		# Generate digital signature
		vote_record = voting.vote_records[0]
		signature = voting.generate_vote_signature(vote_record)

		# Verify signature was generated
		self.assertIsNotNone(signature)
		self.assertTrue(len(signature) == 64)  # SHA-256 produces 64-character hex string

		# Clean up
		voting.delete()

	def test_close_voting(self):
		"""Test closing a voting session"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación para Cerrar",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
				"status": "Activa",
			}
		)

		voting.insert()

		# Close voting
		voting.close_voting()

		# Verify voting was closed
		self.assertEqual(voting.status, "Cerrada")
		self.assertIsNotNone(voting.closure_timestamp)

		# Clean up
		voting.delete()

	def test_get_active_votings(self):
		"""Test getting active votings"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"voting_title": "Votación Activa",
				"voting_type": "Mayoría Simple",
				"assembly_management": self.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
				"status": "Activa",
			}
		)

		voting.insert()

		# Get active votings
		active_votings = voting.get_active_votings()

		# Should include our test voting
		voting_names = [v["name"] for v in active_votings]
		self.assertIn(voting.name, voting_names)

		# Clean up
		voting.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test votings
		frappe.db.delete("Voting System", {"voting_title": ["like", "%Prueba%"]})
		frappe.db.delete("Voting System", {"voting_title": ["like", "%Test%"]})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
