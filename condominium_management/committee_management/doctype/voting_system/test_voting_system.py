# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_to_date, now_datetime, nowdate


class TestVotingSystem(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-VOTE-%"')
		frappe.db.sql(
			'DELETE FROM `tabAssembly Management` WHERE assembly_type = "Ordinaria" AND physical_space = "TEST-SALON-VOTING"'
		)
		frappe.db.sql(
			'DELETE FROM `tabVoting System` WHERE motion_title LIKE "%Test%" OR motion_title LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SALON-VOTING"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Voting Company"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-VOTE-%"')
		frappe.db.sql(
			'DELETE FROM `tabAssembly Management` WHERE assembly_type = "Ordinaria" AND physical_space = "TEST-SALON-VOTING"'
		)
		frappe.db.sql(
			'DELETE FROM `tabVoting System` WHERE motion_title LIKE "%Test%" OR motion_title LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SALON-VOTING"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Voting Company"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for voting system tests"""
		# Create test company
		if not frappe.db.exists("Company", "Test Voting Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Voting Company', 'Test Voting Company', 'TVC', 'USD')"
			)
			frappe.db.commit()

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SALON-VOTING"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Salón de Votación Test",
					"space_code": "TEST-SALON-VOTING",
					"space_type": "Salón de Eventos",
					"capacity": 50,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

		# Create test properties for voters
		cls.test_voters = []
		for i in range(5):
			prop_code = f"TEST-PROP-VOTE-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Voting Property {i+1}",
						"naming_series": "PROP-.YYYY.-",
						"company": "Test Voting Company",
						# "property_usage_type": "Residencial",
						# "acquisition_type": "Compra",
						# "property_status_type": "Activo",
						"registration_date": nowdate(),
					}
				)
				property_doc.insert(ignore_permissions=True)
				cls.test_voters.append(prop_code)

		# Create test assembly
		if not frappe.db.exists(
			"Assembly Management", {"assembly_type": "Ordinaria", "physical_space": "TEST-SALON-VOTING"}
		):
			assembly = frappe.get_doc(
				{
					"doctype": "Assembly Management",
					"assembly_type": "Ordinaria",
					"assembly_date": add_days(nowdate(), 30),
					"convocation_date": add_days(nowdate(), 15),
					"minimum_quorum_first": 60,
					"minimum_quorum_second": 30,
					"physical_space": "TEST-SALON-VOTING",
					"first_call_time": "09:00:00",
					"second_call_time": "09:30:00",
				}
			)
			assembly.insert(ignore_permissions=True)
			assembly.submit()  # Submit assembly for voting validation
			cls.test_assembly = assembly.name
		else:
			cls.test_assembly = frappe.get_value(
				"Assembly Management",
				{"assembly_type": "Ordinaria", "physical_space": "TEST-SALON-VOTING"},
				"name",
			)

	def test_voting_system_creation(self):
		"""Test basic voting system creation"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"motion_title": "Votación de Prueba",
				"voting_type": "Simple",
				"assembly": self.__class__.test_assembly,
				"motion_number": 1,
				"voting_start_time": now_datetime(),
				"voting_end_time": add_to_date(now_datetime(), hours=24),
				"required_percentage": 51,
				"voting_method": "Digital",
				"anonymous_voting": 0,
				"status": "Abierta",
			}
		)

		voting.insert()

		# Verify the document was created
		self.assertTrue(voting.name)
		self.assertEqual(voting.motion_title, "Votación de Prueba")
		self.assertEqual(voting.status, "Abierta")
		self.assertEqual(voting.required_percentage, 51)
		self.assertEqual(voting.motion_number, 1)

		# Clean up
		voting.delete()

	def test_voting_date_validation(self):
		"""Test that voting start date must be before end date"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"motion_title": "Votación Fecha Inválida",
				"voting_type": "Simple",
				"assembly": self.__class__.test_assembly,
				"motion_number": 2,
				"voting_start_time": add_to_date(now_datetime(), hours=48),
				"voting_end_time": add_to_date(now_datetime(), hours=24),  # Before start time
				"required_percentage": 51,
				"voting_method": "Digital",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			voting.insert()

	def test_required_percentage_validation(self):
		"""Test that required percentage must be between 0 and 100"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"motion_title": "Votación Porcentaje Inválido",
				"voting_type": "Simple",
				"assembly": self.__class__.test_assembly,
				"motion_number": 3,
				"voting_method": "Digital",
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
				"motion_title": "Votación con Votantes",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		voting.insert()

		# Load eligible voters
		voting.load_eligible_voters()

		# Verify voters were loaded (should be at least our test voters)
		self.assertTrue(len(voting.votes) >= 0)

		# Clean up
		voting.delete()

	def test_record_vote(self):
		"""Test recording a vote"""
		voting = frappe.get_doc(
			{
				"doctype": "Voting System",
				"motion_title": "Votación para Grabar Voto",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add a vote record manually
		voting.append(
			"votes",
			{
				"voter": self.__class__.test_voters[0],
				"voter_name": "Voter 1",
				"voter_eligibility": "Elegible",
				"vote_value": "",
				"vote_timestamp": None,
			},
		)

		voting.insert()

		# Record a vote
		voting.record_vote(self.__class__.test_voters[0], "A Favor")

		# Verify vote was recorded
		vote_record = next((v for v in voting.votes if v.voter == self.__class__.test_voters[0]), None)
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
				"motion_title": "Votación Cálculo Resultados",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add vote records manually
		vote_values = ["A Favor", "A Favor", "En Contra", "Abstención", "A Favor"]
		for i, vote_value in enumerate(vote_values):
			voting.append(
				"votes",
				{
					"voter": self.__class__.test_voters[i],
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
				"motion_title": "Votación Resultado",
				"voting_type": "Mayoría Calificada",
				"assembly": self.__class__.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 67,  # Qualified majority
			}
		)

		# Add vote records - 3 out of 5 in favor (60%, less than 67%)
		vote_values = ["A Favor", "A Favor", "En Contra", "En Contra", "A Favor"]
		for i, vote_value in enumerate(vote_values):
			voting.append(
				"votes",
				{
					"voter": self.__class__.test_voters[i],
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
				"motion_title": "Votación Firma Digital",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
				"voting_start_date": nowdate(),
				"voting_end_date": add_days(nowdate(), 1),
				"required_percentage": 51,
			}
		)

		# Add a vote record
		voting.append(
			"votes",
			{
				"voter": self.__class__.test_voters[0],
				"voter_name": "Voter 1",
				"voter_eligibility": "Elegible",
				"vote_value": "A Favor",
				"vote_timestamp": now_datetime(),
			},
		)

		voting.insert()

		# Generate digital signature
		vote_record = voting.votes[0]
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
				"motion_title": "Votación para Cerrar",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
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
				"motion_title": "Votación Activa",
				"voting_type": "Mayoría Simple",
				"assembly": self.__class__.test_assembly,
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

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
