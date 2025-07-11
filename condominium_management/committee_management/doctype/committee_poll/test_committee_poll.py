# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, now_datetime, nowdate


class TestCommitteePoll(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for committee poll tests"""
		# Create test user
		if not frappe.db.exists("User", "test_poll@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "test_poll@example.com",
					"first_name": "Test",
					"last_name": "Poll",
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)

		# Create test committee member
		if not frappe.db.exists("Committee Member", {"user": "test_poll@example.com"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_poll@example.com",
					"member_name": "Test Poll Member",
					"role": "Presidente",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"user": "test_poll@example.com"}, "name"
			)

	def test_committee_poll_creation(self):
		"""Test basic committee poll creation"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta de Prueba",
				"poll_description": "Descripción de la encuesta de prueba",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"poll_status": "Activa",
				"allows_anonymous": 0,
			}
		)

		poll.insert()

		# Verify the document was created
		self.assertTrue(poll.name)
		self.assertEqual(poll.poll_title, "Encuesta de Prueba")
		self.assertEqual(poll.poll_status, "Activa")
		self.assertEqual(poll.total_responses, 0)

		# Clean up
		poll.delete()

	def test_poll_date_validation(self):
		"""Test that poll start date must be before end date"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Fecha Inválida",
				"poll_start_date": add_days(nowdate(), 7),
				"poll_end_date": nowdate(),  # Before start date
				"created_by": self.test_committee_member,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			poll.insert()

	def test_poll_options_required(self):
		"""Test that poll must have at least one option"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Sin Opciones",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				# No poll_options provided
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
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
			}
		)

		# Add poll options
		poll.append(
			"poll_options", {"option_text": "Opción A", "option_description": "Descripción de la opción A"}
		)

		poll.append(
			"poll_options", {"option_text": "Opción B", "option_description": "Descripción de la opción B"}
		)

		poll.insert()

		# Verify options were added
		self.assertEqual(len(poll.poll_options), 2)
		self.assertEqual(poll.poll_options[0].option_text, "Opción A")
		self.assertEqual(poll.poll_options[1].option_text, "Opción B")

		# Clean up
		poll.delete()

	def test_record_response(self):
		"""Test recording poll responses"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta para Respuestas",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"poll_status": "Activa",
			}
		)

		# Add poll options
		poll.append("poll_options", {"option_text": "Sí", "response_count": 0})

		poll.append("poll_options", {"option_text": "No", "response_count": 0})

		poll.insert()

		# Record responses
		poll.record_response(self.test_committee_member, "Sí")

		# Verify response was recorded
		self.assertEqual(poll.total_responses, 1)
		yes_option = next((opt for opt in poll.poll_options if opt.option_text == "Sí"), None)
		self.assertIsNotNone(yes_option)
		self.assertEqual(yes_option.response_count, 1)

		# Clean up
		poll.delete()

	def test_calculate_poll_results(self):
		"""Test calculating poll results"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Cálculo Resultados",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
			}
		)

		# Add poll options with responses
		poll.append("poll_options", {"option_text": "Opción A", "response_count": 3})

		poll.append("poll_options", {"option_text": "Opción B", "response_count": 2})

		poll.append("poll_options", {"option_text": "Opción C", "response_count": 1})

		poll.insert()

		# Calculate results
		poll.calculate_poll_results()

		# Verify results
		self.assertEqual(poll.total_responses, 6)
		self.assertEqual(poll.poll_options[0].response_percentage, 50)  # 3/6 = 50%
		self.assertEqual(poll.poll_options[1].response_percentage, 33.33)  # 2/6 = 33.33%
		self.assertEqual(poll.poll_options[2].response_percentage, 16.67)  # 1/6 = 16.67%

		# Winner should be Option A
		self.assertEqual(poll.winning_option, "Opción A")

		# Clean up
		poll.delete()

	def test_close_poll(self):
		"""Test closing a poll"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta para Cerrar",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"poll_status": "Activa",
			}
		)

		# Add a poll option
		poll.append("poll_options", {"option_text": "Opción Única", "response_count": 1})

		poll.insert()

		# Close poll
		poll.close_poll()

		# Verify poll was closed
		self.assertEqual(poll.poll_status, "Cerrada")
		self.assertIsNotNone(poll.closure_date)

		# Clean up
		poll.delete()

	def test_auto_close_expired_poll(self):
		"""Test that poll is automatically closed when end date passes"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Expirada",
				"poll_start_date": add_days(nowdate(), -7),
				"poll_end_date": add_days(nowdate(), -1),  # Past end date
				"created_by": self.test_committee_member,
				"poll_status": "Activa",
			}
		)

		# Add a poll option
		poll.append("poll_options", {"option_text": "Opción Test", "response_count": 0})

		poll.insert()

		# Status should be automatically updated to Cerrada
		self.assertEqual(poll.poll_status, "Cerrada")

		# Clean up
		poll.delete()

	def test_get_active_polls(self):
		"""Test getting active polls"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Activa",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"poll_status": "Activa",
			}
		)

		# Add a poll option
		poll.append("poll_options", {"option_text": "Opción Test", "response_count": 0})

		poll.insert()

		# Get active polls
		active_polls = poll.get_active_polls()

		# Should include our test poll
		poll_names = [p["name"] for p in active_polls]
		self.assertIn(poll.name, poll_names)

		# Clean up
		poll.delete()

	def test_get_poll_summary(self):
		"""Test getting poll summary"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Resumen",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"poll_status": "Cerrada",
			}
		)

		# Add poll options with responses
		poll.append("poll_options", {"option_text": "Sí", "response_count": 4, "response_percentage": 80})

		poll.append("poll_options", {"option_text": "No", "response_count": 1, "response_percentage": 20})

		poll.total_responses = 5
		poll.winning_option = "Sí"

		poll.insert()

		# Get poll summary
		summary = poll.get_poll_summary()

		# Verify summary
		self.assertEqual(summary["total_responses"], 5)
		self.assertEqual(summary["winning_option"], "Sí")
		self.assertEqual(summary["participation_rate"], 100)  # Assuming 5 eligible participants
		self.assertEqual(len(summary["option_results"]), 2)

		# Clean up
		poll.delete()

	def test_anonymous_poll(self):
		"""Test anonymous poll functionality"""
		poll = frappe.get_doc(
			{
				"doctype": "Committee Poll",
				"poll_title": "Encuesta Anónima",
				"poll_start_date": nowdate(),
				"poll_end_date": add_days(nowdate(), 7),
				"created_by": self.test_committee_member,
				"allows_anonymous": 1,
			}
		)

		# Add poll option
		poll.append("poll_options", {"option_text": "Opción Anónima", "response_count": 0})

		poll.insert()

		# Record anonymous response
		poll.record_anonymous_response("Opción Anónima")

		# Verify response was recorded without voter identification
		self.assertEqual(poll.total_responses, 1)
		option = poll.poll_options[0]
		self.assertEqual(option.response_count, 1)

		# Clean up
		poll.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test polls
		frappe.db.delete("Committee Poll", {"poll_title": ["like", "%Prueba%"]})
		frappe.db.delete("Committee Poll", {"poll_title": ["like", "%Test%"]})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
