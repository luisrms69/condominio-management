# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_to_date, now_datetime, nowdate


class TestCommitteeMeeting(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for committee meeting tests"""
		# Create test user
		if not frappe.db.exists("User", "test_committee_meeting@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "test_committee_meeting@example.com",
					"first_name": "Test",
					"last_name": "Committee",
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)

		# Create test property registry
		if not frappe.db.exists("Property Registry", "TEST-PROP-MTG-001"):
			property_doc = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"property_code": "TEST-PROP-MTG-001",
					"property_type": "Apartamento",
					"is_active": 1,
				}
			)
			property_doc.insert(ignore_permissions=True)

		# Create test committee member
		if not frappe.db.exists("Committee Member", {"user": "test_committee_meeting@example.com"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_committee_meeting@example.com",
					"property_registry": "TEST-PROP-MTG-001",
					"role_in_committee": "Presidente",
					"start_date": nowdate(),
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"user": "test_committee_meeting@example.com"}, "name"
			)

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SALA-REUNIONES"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Sala de Reuniones Test",
					"space_code": "TEST-SALA-REUNIONES",
					"space_type": "Sala de Reuniones",
					"capacity": 20,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

	def test_committee_meeting_creation(self):
		"""Test basic committee meeting creation"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión de Prueba",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		meeting.insert()

		# Verify the document was created
		self.assertTrue(meeting.name)
		self.assertEqual(meeting.meeting_title, "Reunión de Prueba")
		self.assertEqual(meeting.status, "Planificada")
		self.assertEqual(meeting.pending_items_count, 0)
		self.assertEqual(meeting.completion_rate, 0)

		# Clean up
		meeting.delete()

	def test_meeting_date_validation(self):
		"""Test that meetings cannot be scheduled in the past"""
		past_date = add_to_date(now_datetime(), days=-1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión en el Pasado",
				"meeting_date": past_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			meeting.insert()

	def test_physical_space_validation(self):
		"""Test that physical space is required for non-virtual meetings"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión sin Espacio",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				# No physical_space specified
			}
		)

		with self.assertRaises(frappe.ValidationError):
			meeting.insert()

	def test_virtual_meeting_link_validation(self):
		"""Test that virtual meeting link is required for virtual meetings"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión Virtual sin Enlace",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Virtual",
				# No virtual_meeting_link specified
			}
		)

		with self.assertRaises(frappe.ValidationError):
			meeting.insert()

	def test_load_committee_members_as_attendees(self):
		"""Test loading committee members as attendees"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión con Miembros",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		meeting.insert()

		# Load committee members as attendees
		meeting.load_committee_members_as_attendees()

		# Verify attendees were loaded
		self.assertTrue(len(meeting.attendees) > 0)
		self.assertEqual(meeting.attendees[0].committee_member, self.test_committee_member)
		self.assertEqual(meeting.attendees[0].attendance_status, "Presente")

		# Clean up
		meeting.delete()

	def test_completion_rate_calculation(self):
		"""Test completion rate calculation based on agenda items"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión con Agenda",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		# Add agenda items
		meeting.append(
			"agenda_items",
			{
				"topic_title": "Tema 1",
				"topic_category": "Financiero",
				"decisions_taken": "Decisión tomada para tema 1",
			},
		)

		meeting.append(
			"agenda_items",
			{
				"topic_title": "Tema 2",
				"topic_category": "Operativo",
				# No decisions_taken
			},
		)

		meeting.insert()

		# Verify completion rate is 50% (1 out of 2 items completed)
		self.assertEqual(meeting.completion_rate, 50)
		self.assertEqual(meeting.pending_items_count, 1)

		# Clean up
		meeting.delete()

	def test_attendance_summary(self):
		"""Test attendance summary calculation"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión con Asistencia",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Híbrida",
				"physical_space": "TEST-SALA-REUNIONES",
				"virtual_meeting_link": "https://meet.example.com/test",
			}
		)

		# Add attendees with different statuses
		meeting.append(
			"attendees", {"committee_member": self.test_committee_member, "attendance_status": "Presente"}
		)

		meeting.append(
			"attendees", {"committee_member": self.test_committee_member, "attendance_status": "Virtual"}
		)

		meeting.append(
			"attendees", {"committee_member": self.test_committee_member, "attendance_status": "Ausente"}
		)

		meeting.insert()

		# Get attendance summary
		summary = meeting.get_attendance_summary()

		self.assertEqual(summary["total_attendees"], 3)
		self.assertEqual(summary["present_count"], 1)
		self.assertEqual(summary["virtual_count"], 1)
		self.assertEqual(summary["absent_count"], 1)
		self.assertEqual(summary["attendance_rate"], 66.66666666666667)

		# Clean up
		meeting.delete()

	def test_agenda_summary(self):
		"""Test agenda summary calculation"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión con Resumen de Agenda",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		# Add agenda items
		meeting.append(
			"agenda_items",
			{
				"topic_title": "Tema Completado",
				"topic_category": "Financiero",
				"decisions_taken": "Decisión tomada",
				"time_spent": "00:30:00",
			},
		)

		meeting.append(
			"agenda_items",
			{"topic_title": "Tema Pendiente", "topic_category": "Operativo", "time_spent": "00:15:00"},
		)

		meeting.insert()

		# Get agenda summary
		summary = meeting.get_agenda_summary()

		self.assertEqual(summary["total_items"], 2)
		self.assertEqual(summary["completed_items"], 1)
		self.assertEqual(summary["pending_items"], 1)
		self.assertEqual(summary["completion_rate"], 50)
		self.assertEqual(summary["total_time_minutes"], 45)

		# Clean up
		meeting.delete()

	def test_upcoming_meetings(self):
		"""Test getting upcoming meetings"""
		future_date = add_to_date(now_datetime(), days=1)

		meeting = frappe.get_doc(
			{
				"doctype": "Committee Meeting",
				"meeting_title": "Reunión Próxima",
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"meeting_format": "Presencial",
				"physical_space": "TEST-SALA-REUNIONES",
			}
		)

		meeting.insert()

		# Get upcoming meetings
		upcoming = frappe.get_doc("Committee Meeting", meeting.name).get_upcoming_meetings()

		# Should include our test meeting
		meeting_names = [m["name"] for m in upcoming]
		self.assertIn(meeting.name, meeting_names)

		# Clean up
		meeting.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up any remaining test meetings
		frappe.db.delete("Committee Meeting", {"meeting_title": ["like", "%Prueba%"]})
		frappe.db.delete("Committee Meeting", {"meeting_title": ["like", "%Test%"]})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
