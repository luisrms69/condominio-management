# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, nowdate


class TestMeetingSchedule(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-SCHEDULE-%"')
		frappe.db.sql(
			'DELETE FROM `tabMeeting Schedule` WHERE schedule_name LIKE "%Test%" OR schedule_name LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-SCHEDULE-%"')
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SPACE-MEETING"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Schedule Company"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-SCHEDULE-%"')
		frappe.db.sql(
			'DELETE FROM `tabMeeting Schedule` WHERE schedule_name LIKE "%Test%" OR schedule_name LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-SCHEDULE-%"')
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SPACE-MEETING"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Schedule Company"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for meeting schedule tests"""
		# Create test company
		if not frappe.db.exists("Company", "Test Schedule Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Schedule Company', 'Test Schedule Company', 'TSC', 'USD')"
			)
			frappe.db.commit()

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SPACE-MEETING"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Sala de Reuniones Test",
					"space_code": "TEST-SPACE-MEETING",
					"space_type": "Sala de Reuniones",
					"capacity": 20,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

		# Create test properties
		cls.test_properties = []
		for i in range(2):
			prop_code = f"TEST-PROP-SCHEDULE-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Schedule Property {i+1}",
						"naming_series": "PROP-.YYYY.-",
						"company": "Test Schedule Company",
						# "property_usage_type": "Residencial",
						# "acquisition_type": "Compra",
						# "property_status_type": "Activo",
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
					"role_in_committee": "Presidente" if i == 0 else "Secretario",
					"start_date": nowdate(),
					"end_date": add_days(nowdate(), 365),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			cls.test_members.append(member.name)

	def test_meeting_schedule_creation(self):
		"""Test basic meeting schedule creation"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma de Prueba 2025",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
				"status": "Activo",
			}
		)

		schedule.insert()

		# Verify the document was created
		self.assertTrue(schedule.name)
		self.assertEqual(schedule.schedule_name, "Cronograma de Prueba 2025")
		self.assertEqual(schedule.schedule_year, 2025)
		self.assertEqual(schedule.status, "Activo")

		# Clean up
		schedule.delete()

	def test_add_scheduled_meeting(self):
		"""Test adding scheduled meetings"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma con Reuniones",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
			}
		)

		schedule.insert()

		# Add scheduled meetings
		schedule.add_scheduled_meeting(
			"Reunión Mensual Enero", "2025-01-15", "10:00", "Reunión mensual ordinaria", "Ordinaria"
		)
		schedule.add_scheduled_meeting(
			"Reunión Mensual Febrero", "2025-02-15", "10:00", "Reunión mensual ordinaria", "Ordinaria"
		)

		# Verify meetings were added
		self.assertEqual(len(schedule.scheduled_meetings), 2)
		self.assertEqual(schedule.scheduled_meetings[0].meeting_title, "Reunión Mensual Enero")
		self.assertEqual(schedule.scheduled_meetings[1].scheduled_date, "2025-02-15")

		# Clean up
		schedule.delete()

	def test_generate_annual_schedule(self):
		"""Test generating annual meeting schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Anual 2025",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
				"frequency": "Mensual",
				"default_meeting_day": 15,
				"default_meeting_time": "10:00",
			}
		)

		schedule.insert()

		# Generate annual schedule
		schedule.generate_annual_schedule()

		# Verify schedule was generated (should have 12 monthly meetings)
		self.assertEqual(len(schedule.scheduled_meetings), 12)

		# Check first and last meetings
		first_meeting = schedule.scheduled_meetings[0]
		last_meeting = schedule.scheduled_meetings[-1]

		self.assertEqual(first_meeting.scheduled_date, "2025-01-15")
		self.assertEqual(last_meeting.scheduled_date, "2025-12-15")
		self.assertEqual(first_meeting.scheduled_time, "10:00")

		# Clean up
		schedule.delete()

	def test_create_committee_meetings(self):
		"""Test creating actual committee meetings from schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma para Crear Reuniones",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
			}
		)

		# Add a scheduled meeting manually
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión Test",
				"scheduled_date": add_days(nowdate(), 7),
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"description": "Reunión de prueba",
				"status": "Programada",
			},
		)

		schedule.insert()

		# Create committee meetings
		created_meetings = schedule.create_committee_meetings()

		# Verify meetings were created
		self.assertGreater(len(created_meetings), 0)

		# Verify meeting was created in Committee Meeting doctype
		meeting_exists = frappe.db.exists(
			"Committee Meeting", {"meeting_title": "Reunión Test", "meeting_date": add_days(nowdate(), 7)}
		)
		self.assertTrue(meeting_exists)

		# Clean up
		schedule.delete()
		if meeting_exists:
			frappe.delete_doc("Committee Meeting", meeting_exists)

	def test_schedule_synchronization(self):
		"""Test synchronizing schedule with existing meetings"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Sincronización",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
			}
		)

		# Add scheduled meetings
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión Sync Test",
				"scheduled_date": add_days(nowdate(), 10),
				"scheduled_time": "14:00",
				"meeting_type": "Ordinaria",
				"status": "Programada",
			},
		)

		schedule.insert()

		# Synchronize schedule
		sync_results = schedule.synchronize_with_meetings()

		# Verify synchronization results
		self.assertIsNotNone(sync_results)
		self.assertIn("synchronized", sync_results)

		# Clean up
		schedule.delete()

	def test_schedule_conflicts_detection(self):
		"""Test detecting conflicts in schedule"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Conflictos",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
			}
		)

		# Add conflicting meetings (same date/time/space)
		conflict_date = add_days(nowdate(), 5)
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión A",
				"scheduled_date": conflict_date,
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"status": "Programada",
			},
		)
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión B",
				"scheduled_date": conflict_date,
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"status": "Programada",
			},
		)

		schedule.insert()

		# Check for conflicts
		conflicts = schedule.check_scheduling_conflicts()

		# Verify conflicts were detected
		self.assertGreater(len(conflicts), 0)

		# Clean up
		schedule.delete()

	def test_schedule_notifications(self):
		"""Test schedule notification system"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Notificaciones",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
				"enable_notifications": 1,
				"notification_days_before": 3,
			}
		)

		# Add upcoming meeting
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión Próxima",
				"scheduled_date": add_days(nowdate(), 2),  # Within notification window
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"status": "Programada",
			},
		)

		schedule.insert()

		# Send notifications
		notifications = schedule.send_upcoming_meeting_notifications()

		# Verify notifications were prepared
		self.assertIsNotNone(notifications)

		# Clean up
		schedule.delete()

	def test_recurring_schedule_pattern(self):
		"""Test recurring schedule patterns"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Recurrente",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
				"frequency": "Quincenal",
				"default_meeting_day": 1,  # First day of month
				"default_meeting_time": "09:00",
			}
		)

		schedule.insert()

		# Generate recurring pattern
		schedule.generate_recurring_pattern()

		# Verify pattern was generated (should have 24 bi-weekly meetings)
		self.assertGreater(len(schedule.scheduled_meetings), 20)

		# Clean up
		schedule.delete()

	def test_schedule_template_application(self):
		"""Test applying schedule templates"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma desde Template",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
			}
		)

		schedule.insert()

		# Apply standard template
		schedule.apply_schedule_template("Standard Committee Schedule")

		# Verify template was applied
		self.assertGreater(len(schedule.scheduled_meetings), 0)

		# Clean up
		schedule.delete()

	def test_schedule_status_tracking(self):
		"""Test tracking schedule status"""
		schedule = frappe.get_doc(
			{
				"doctype": "Meeting Schedule",
				"schedule_name": "Cronograma Estados",
				"schedule_year": 2025,
				"schedule_type": "Anual",
				"organizer": self.__class__.test_members[0],
				"default_physical_space": "TEST-SPACE-MEETING",
				"status": "Activo",
			}
		)

		# Add meetings with different statuses
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión Completada",
				"scheduled_date": add_days(nowdate(), -5),
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"status": "Completada",
			},
		)
		schedule.append(
			"scheduled_meetings",
			{
				"meeting_title": "Reunión Cancelada",
				"scheduled_date": add_days(nowdate(), -2),
				"scheduled_time": "10:00",
				"meeting_type": "Ordinaria",
				"status": "Cancelada",
			},
		)

		schedule.insert()

		# Update schedule status
		schedule.update_schedule_status()

		# Verify status tracking
		self.assertEqual(schedule.total_meetings, 2)
		self.assertEqual(schedule.completed_meetings, 1)
		self.assertEqual(schedule.cancelled_meetings, 1)

		# Clean up
		schedule.delete()

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
