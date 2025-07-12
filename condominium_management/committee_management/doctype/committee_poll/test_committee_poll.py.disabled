# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCommitteePoll(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-POLL-%"')
		frappe.db.sql(
			'DELETE FROM `tabCommittee Poll` WHERE poll_title LIKE "%Test%" OR poll_title LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-POLL-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Poll Company"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-POLL-%"')
		frappe.db.sql(
			'DELETE FROM `tabCommittee Poll` WHERE poll_title LIKE "%Test%" OR poll_title LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-POLL-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Poll Company"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for committee poll tests"""
		# Create test company
		if not frappe.db.exists("Company", "Test Poll Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Poll Company', 'Test Poll Company', 'TPC', 'USD')"
			)
			frappe.db.commit()

		# Create test properties
		cls.test_properties = []
		for i in range(3):
			prop_code = f"TEST-PROP-POLL-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Poll Property {i+1}",
						"naming_series": "PROP-.YYYY.-",
						"company": "Test Poll Company",
						"property_usage_type": "Residencial",
						"acquisition_type": "Compra",
						"property_status_type": "Activo",
						"registration_date": nowdate(),
					}
				)
				property_doc.insert(ignore_permissions=True)
				cls.test_properties.append(prop_code)

		# Create test committee members
		cls.test_members = []
		for i, prop_code in enumerate(cls.test_properties):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"property_registry": prop_code,
					"role_in_committee": "Miembro" if i > 0 else "Presidente",
					"start_date": nowdate(),
					"end_date": add_days(nowdate(), 365),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			cls.test_members.append(member.name)

	def test_committee_poll_creation(self):
		"""Test basic committee poll creation"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta de Prueba",
				"poll_type": "Opinión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"status": "Activa",
				"description": "Encuesta de prueba para testing",
			}
		)

		poll.insert()

		# Verify the document was created
		self.assertTrue(poll.name)
		self.assertEqual(poll.poll_title, "Encuesta de Prueba")
		self.assertEqual(poll.status, "Activa")
		self.assertEqual(poll.total_responses, 0)

		# Clean up
		poll.delete()

	def test_poll_date_validation(self):
		"""Test that poll start date must be before end date"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Fecha Inválida",
				"poll_type": "Opinión",
				"start_date": add_days(nowdate(), 7),
				"end_date": add_days(nowdate(), 2),  # Before start date
				"is_anonymous": 0,
				"description": "Test poll with invalid dates",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			poll.insert()

	def test_add_poll_option(self):
		"""Test adding poll options"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta con Opciones",
				"poll_type": "Decisión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"description": "Test poll with options",
			}
		)

		poll.insert()

		# Add poll options
		poll.add_poll_option("Opción A", "Primera opción de prueba")
		poll.add_poll_option("Opción B", "Segunda opción de prueba")

		# Verify options were added
		self.assertEqual(len(poll.poll_options), 2)
		self.assertEqual(poll.poll_options[0].option_text, "Opción A")
		self.assertEqual(poll.poll_options[1].option_text, "Opción B")

		# Clean up
		poll.delete()

	def test_record_response(self):
		"""Test recording a poll response"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta para Respuesta",
				"poll_type": "Decisión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"description": "Test poll for responses",
			}
		)

		# Add poll options
		poll.append("poll_options", {"option_text": "Sí", "description": "Respuesta positiva"})
		poll.append("poll_options", {"option_text": "No", "description": "Respuesta negativa"})

		poll.insert()

		# Record response
		poll.record_response(self.__class__.test_members[0], "Sí")

		# Verify response was recorded
		self.assertEqual(poll.total_responses, 1)
		response = next(
			(r for r in poll.responses if r.committee_member == self.__class__.test_members[0]), None
		)
		self.assertIsNotNone(response)
		self.assertEqual(response.selected_option, "Sí")

		# Clean up
		poll.delete()

	def test_calculate_poll_results(self):
		"""Test poll results calculation"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Cálculo Resultados",
				"poll_type": "Decisión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"description": "Test poll for results calculation",
			}
		)

		# Add poll options
		poll.append("poll_options", {"option_text": "Sí", "description": "Respuesta positiva"})
		poll.append("poll_options", {"option_text": "No", "description": "Respuesta negativa"})

		# Add responses manually
		responses = ["Sí", "Sí", "No"]
		for i, response in enumerate(responses):
			poll.append(
				"responses",
				{
					"committee_member": self.__class__.test_members[i % len(self.__class__.test_members)],
					"selected_option": response,
					"response_timestamp": frappe.utils.now_datetime(),
				},
			)

		poll.insert()

		# Calculate results
		poll.calculate_poll_results()

		# Verify results (2 Sí, 1 No)
		self.assertEqual(poll.total_responses, 3)
		yes_option = next((o for o in poll.poll_options if o.option_text == "Sí"), None)
		no_option = next((o for o in poll.poll_options if o.option_text == "No"), None)

		self.assertEqual(yes_option.vote_count, 2)
		self.assertEqual(no_option.vote_count, 1)
		self.assertEqual(yes_option.percentage, 66.67)
		self.assertEqual(no_option.percentage, 33.33)

		# Clean up
		poll.delete()

	def test_close_poll(self):
		"""Test closing a poll"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta para Cerrar",
				"poll_type": "Opinión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"status": "Activa",
				"description": "Test poll for closing",
			}
		)

		poll.insert()

		# Close poll
		poll.close_poll()

		# Verify poll was closed
		self.assertEqual(poll.status, "Cerrada")
		self.assertIsNotNone(poll.closure_timestamp)

		# Clean up
		poll.delete()

	def test_get_active_polls(self):
		"""Test getting active polls"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Activa",
				"poll_type": "Opinión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 0,
				"status": "Activa",
				"description": "Test active poll",
			}
		)

		poll.insert()

		# Get active polls
		active_polls = poll.get_active_polls()

		# Should include our test poll
		poll_names = [p["name"] for p in active_polls]
		self.assertIn(poll.name, poll_names)

		# Clean up
		poll.delete()

	def test_anonymous_poll(self):
		"""Test anonymous poll functionality"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Anónima",
				"poll_type": "Opinión",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), 7),
				"is_anonymous": 1,
				"description": "Test anonymous poll",
			}
		)

		poll.insert()

		# Verify anonymous flag is set
		self.assertEqual(poll.is_anonymous, 1)

		# Clean up
		poll.delete()

	def test_poll_expiry_validation(self):
		"""Test that expired polls cannot accept responses"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Expirada",
				"poll_type": "Opinión",
				"start_date": add_days(nowdate(), -10),
				"end_date": add_days(nowdate(), -2),  # Expired
				"is_anonymous": 0,
				"description": "Test expired poll",
			}
		)

		poll.insert()

		# Try to record response on expired poll
		with self.assertRaises(frappe.ValidationError):
			poll.record_response(self.__class__.test_members[0], "Test response")

		# Clean up
		poll.delete()

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
