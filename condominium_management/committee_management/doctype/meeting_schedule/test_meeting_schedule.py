# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from datetime import datetime

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate


class TestMeetingSchedule(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for meeting schedule tests"""
		# Create test committee member
		if not frappe.db.exists("Committee Member", {"member_name": "Test Schedule Member"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"member_name": "Test Schedule Member",
					"role": "Presidente",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"member_name": "Test Schedule Member"}, "name"
			)

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SALA-SCHEDULE"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Sala Schedule Test",
					"space_code": "TEST-SALA-SCHEDULE",
					"space_type": "Sala de Reuniones",
					"capacity": 20,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

	def test_meeting_schedule_creation(self):
		"""Test basic meeting schedule creation"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
				"auto_create_meetings": 1,
			}
		)

		# Add a scheduled meeting
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": datetime(2025, 6, 15).date(),
				"meeting_type": "Ordinaria",
				"tentative_time": "18:00:00",
				"tentative_location": "TEST-SALA-SCHEDULE",
				"is_mandatory": 1,
			},
		)

		schedule.insert()

		# Verify the document was created
		self.assertTrue(schedule.name)
		self.assertEqual(schedule.schedule_year, 2025)
		self.assertEqual(schedule.schedule_period, "Anual")
		self.assertEqual(schedule.meetings_created_count, 0)
		self.assertEqual(len(schedule.scheduled_meetings), 1)

		# Clean up
		schedule.delete()

	def test_schedule_year_validation(self):
		"""Test that schedule year cannot be too far in the past"""
		current_year = datetime.now().year

		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": current_year - 5,  # Too far in the past
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add a scheduled meeting
		schedule.append(
			"scheduled_meetings",
			{"meeting_date": datetime(current_year - 5, 6, 15).date(), "meeting_type": "Ordinaria"},
		)

		with self.assertRaises(frappe.ValidationError):
			schedule.insert()

	def test_scheduled_meetings_required(self):
		"""Test that at least one scheduled meeting is required"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
				# No scheduled_meetings
			}
		)

		with self.assertRaises(frappe.ValidationError):
			schedule.insert()

	def test_meeting_date_year_validation(self):
		"""Test that meeting dates must be in the schedule year"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add meeting with wrong year
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": datetime(2024, 6, 15).date(),  # Wrong year
				"meeting_type": "Ordinaria",
			},
		)

		with self.assertRaises(frappe.ValidationError):
			schedule.insert()

	def test_duplicate_meeting_dates_validation(self):
		"""Test that duplicate meeting dates are not allowed"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add duplicate meeting dates
		duplicate_date = datetime(2025, 6, 15).date()
		schedule.append("scheduled_meetings", {"meeting_date": duplicate_date, "meeting_type": "Ordinaria"})

		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": duplicate_date,  # Duplicate
				"meeting_type": "Extraordinaria",
			},
		)

		with self.assertRaises(frappe.ValidationError):
			schedule.insert()

	def test_generate_annual_schedule(self):
		"""Test generating standard annual schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		schedule.insert()

		# Generate annual schedule
		schedule.generate_standard_schedule()

		# Verify 12 monthly meetings were created
		self.assertEqual(len(schedule.scheduled_meetings), 12)

		# Verify meeting types
		meeting_types = [m.meeting_type for m in schedule.scheduled_meetings]
		self.assertIn("Planeación", meeting_types)
		self.assertIn("Evaluación", meeting_types)
		self.assertIn("Revisión Financiera", meeting_types)

		# Clean up
		schedule.delete()

	def test_generate_semestral_schedule(self):
		"""Test generating standard semestral schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Semestral",
				"created_by": self.test_committee_member,
			}
		)

		schedule.insert()

		# Generate semestral schedule
		schedule.generate_standard_schedule()

		# Verify 6 meetings were created
		self.assertEqual(len(schedule.scheduled_meetings), 6)

		# Clean up
		schedule.delete()

	def test_generate_trimestral_schedule(self):
		"""Test generating standard trimestral schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Trimestral",
				"created_by": self.test_committee_member,
			}
		)

		schedule.insert()

		# Generate trimestral schedule
		schedule.generate_standard_schedule()

		# Verify 3 meetings were created
		self.assertEqual(len(schedule.scheduled_meetings), 3)

		# Clean up
		schedule.delete()

	def test_create_committee_meeting(self):
		"""Test creating committee meeting from scheduled meeting"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add a scheduled meeting for tomorrow
		tomorrow = add_days(nowdate(), 1)
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": tomorrow,
				"meeting_type": "Ordinaria",
				"tentative_location": "TEST-SALA-SCHEDULE",
				"suggested_topics": "Tema 1\nTema 2\nTema 3",
			},
		)

		schedule.insert()

		# Create committee meeting
		scheduled_meeting = schedule.scheduled_meetings[0]
		meeting_doc = schedule.create_committee_meeting(scheduled_meeting)

		# Verify meeting was created
		self.assertIsNotNone(meeting_doc)
		self.assertEqual(meeting_doc.physical_space, "TEST-SALA-SCHEDULE")
		self.assertEqual(len(meeting_doc.agenda_items), 3)  # 3 suggested topics

		# Clean up
		if meeting_doc:
			meeting_doc.delete()
		schedule.delete()

	def test_create_upcoming_meetings(self):
		"""Test creating upcoming meetings automatically"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
				"auto_create_meetings": 1,
			}
		)

		# Add upcoming meeting
		future_date = add_days(nowdate(), 5)
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": future_date,
				"meeting_type": "Ordinaria",
				"tentative_location": "TEST-SALA-SCHEDULE",
			},
		)

		# Add past meeting (should not be created)
		past_date = add_days(nowdate(), -5)
		schedule.append("scheduled_meetings", {"meeting_date": past_date, "meeting_type": "Ordinaria"})

		schedule.insert()
		schedule.submit()  # This should trigger meeting creation

		# Verify only future meeting was created
		self.assertEqual(schedule.meetings_created_count, 1)
		self.assertTrue(schedule.scheduled_meetings[0].meeting_created)
		self.assertFalse(schedule.scheduled_meetings[1].meeting_created)

		# Clean up
		for meeting in schedule.scheduled_meetings:
			if meeting.linked_meeting:
				frappe.delete_doc("Committee Meeting", meeting.linked_meeting, ignore_permissions=True)
		schedule.delete()

	def test_sync_scheduled_meetings(self):
		"""Test syncing scheduled meetings"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add upcoming meeting
		future_date = add_days(nowdate(), 10)
		schedule.append("scheduled_meetings", {"meeting_date": future_date, "meeting_type": "Ordinaria"})

		schedule.insert()
		schedule.submit()

		# Sync meetings
		result = schedule.sync_scheduled_meetings()

		# Verify sync results
		self.assertIn("meetings_created", result)
		self.assertIn("meetings_pending", result)

		# Clean up
		for meeting in schedule.scheduled_meetings:
			if meeting.linked_meeting:
				frappe.delete_doc("Committee Meeting", meeting.linked_meeting, ignore_permissions=True)
		schedule.delete()

	def test_get_schedule_summary(self):
		"""Test getting schedule summary statistics"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add mixed meetings
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": add_days(nowdate(), 5),
				"meeting_type": "Ordinaria",
				"is_mandatory": 1,
				"meeting_created": 0,
			},
		)

		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": add_days(nowdate(), -5),
				"meeting_type": "Extraordinaria",
				"is_mandatory": 0,
				"meeting_created": 1,
			},
		)

		schedule.insert()

		# Get summary
		summary = schedule.get_schedule_summary()

		# Verify summary
		self.assertEqual(summary["total_meetings"], 2)
		self.assertEqual(summary["mandatory_meetings"], 1)
		self.assertEqual(summary["created_meetings"], 1)
		self.assertEqual(summary["pending_meetings"], 1)
		self.assertEqual(summary["upcoming_meetings"], 1)
		self.assertEqual(summary["past_meetings"], 1)

		# Clean up
		schedule.delete()

	def test_get_next_scheduled_meeting(self):
		"""Test getting next scheduled meeting"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": 2025,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add meetings in different order
		schedule.append(
			"scheduled_meetings", {"meeting_date": add_days(nowdate(), 10), "meeting_type": "Ordinaria"}
		)

		schedule.append(
			"scheduled_meetings",
			{
				"meeting_date": add_days(nowdate(), 5),  # This should be next
				"meeting_type": "Extraordinaria",
			},
		)

		schedule.insert()

		# Get next meeting
		next_meeting = schedule.get_next_scheduled_meeting()

		# Verify it's the closest future meeting
		self.assertIsNotNone(next_meeting)
		self.assertEqual(getdate(next_meeting.meeting_date), getdate(add_days(nowdate(), 5)))

		# Clean up
		schedule.delete()

	def test_get_active_schedules(self):
		"""Test getting active schedules"""
		current_year = datetime.now().year

		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_year": current_year,
				"schedule_period": "Anual",
				"created_by": self.test_committee_member,
			}
		)

		# Add a meeting
		schedule.append(
			"scheduled_meetings",
			{"meeting_date": datetime(current_year, 6, 15).date(), "meeting_type": "Ordinaria"},
		)

		schedule.insert()
		schedule.submit()

		# Get active schedules
		active_schedules = schedule.get_active_schedules()

		# Should include our test schedule
		schedule_names = [s["name"] for s in active_schedules]
		self.assertIn(schedule.name, schedule_names)

		# Clean up
		schedule.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test schedules
		frappe.db.delete("Meeting Schedule", {"created_by": self.test_committee_member})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
