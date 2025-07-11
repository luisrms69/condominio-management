# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCommunityEvent(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-EVENT-%"')
		frappe.db.sql(
			'DELETE FROM `tabCommunity Event` WHERE event_name LIKE "%Test%" OR event_name LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-EVENT-%"')
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SPACE-EVENT"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Event Company"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-EVENT-%"')
		frappe.db.sql(
			'DELETE FROM `tabCommunity Event` WHERE event_name LIKE "%Test%" OR event_name LIKE "%Prueba%"'
		)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-EVENT-%"')
		frappe.db.sql('DELETE FROM `tabPhysical Space` WHERE space_code = "TEST-SPACE-EVENT"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Event Company"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for community event tests"""
		# Create test company
		if not frappe.db.exists("Company", "Test Event Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Event Company', 'Test Event Company', 'TEC', 'USD')"
			)
			frappe.db.commit()

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SPACE-EVENT"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Espacio Eventos Test",
					"space_code": "TEST-SPACE-EVENT",
					"space_type": "Salón de Eventos",
					"capacity": 100,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

		# Create test properties
		cls.test_properties = []
		for i in range(3):
			prop_code = f"TEST-PROP-EVENT-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Event Property {i+1}",
						"naming_series": "PROP-.YYYY.-",
						"company": "Test Event Company",
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
					"role_in_committee": "Miembro" if i > 0 else "Presidente",
					"start_date": nowdate(),
					"end_date": add_days(nowdate(), 365),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			cls.test_members.append(member.name)

	def test_community_event_creation(self):
		"""Test basic community event creation"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento de Prueba",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 7),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"status": "Planificado",
				"description": "Evento de prueba para testing",
			}
		)

		event.insert()

		# Verify the document was created
		self.assertTrue(event.name)
		self.assertEqual(event.event_name, "Evento de Prueba")
		self.assertEqual(event.status, "Planificado")
		self.assertEqual(event.total_budget, 0)

		# Clean up
		event.delete()

	def test_event_date_validation(self):
		"""Test that event date cannot be in the past"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Fecha Pasada",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), -5),  # Past date
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"description": "Event with past date",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			event.insert()

	def test_add_event_organizer(self):
		"""Test adding event organizers"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Organizadores",
				"event_type": "Administrativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"description": "Event with organizers",
			}
		)

		event.insert()

		# Add organizers
		event.add_organizer(self.__class__.test_members[1], "Coordinador")
		event.add_organizer(self.__class__.test_members[2], "Asistente")

		# Verify organizers were added
		self.assertEqual(len(event.organizers), 2)
		self.assertEqual(event.organizers[0].committee_member, self.__class__.test_members[1])
		self.assertEqual(event.organizers[0].role, "Coordinador")

		# Clean up
		event.delete()

	def test_add_event_expense(self):
		"""Test adding event expenses"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Gastos",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"description": "Event with expenses",
			}
		)

		event.insert()

		# Add expenses
		event.add_expense("Decoración", 500.00, "Decoraciones para el evento")
		event.add_expense("Catering", 1000.00, "Servicio de alimentación")

		# Verify expenses were added
		self.assertEqual(len(event.expenses), 2)
		self.assertEqual(event.expenses[0].description, "Decoración")
		self.assertEqual(event.expenses[0].amount, 500.00)
		self.assertEqual(event.expenses[1].amount, 1000.00)

		# Clean up
		event.delete()

	def test_calculate_total_budget(self):
		"""Test total budget calculation"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Cálculo Presupuesto",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"description": "Event for budget calculation",
			}
		)

		# Add expenses manually
		event.append("expenses", {"description": "Decoración", "amount": 300.00, "category": "Decoración"})
		event.append("expenses", {"description": "Sonido", "amount": 200.00, "category": "Equipo"})
		event.append("expenses", {"description": "Catering", "amount": 800.00, "category": "Alimentación"})

		event.insert()

		# Calculate budget
		event.calculate_total_budget()

		# Verify total budget (300 + 200 + 800 = 1300)
		self.assertEqual(event.total_budget, 1300.00)

		# Clean up
		event.delete()

	def test_event_registration(self):
		"""Test event registration functionality"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Registros",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"max_attendees": 50,
				"registration_required": 1,
				"description": "Event with registration",
			}
		)

		event.insert()

		# Register attendees
		event.register_attendee(self.__class__.test_properties[0], "Confirmado")
		event.register_attendee(self.__class__.test_properties[1], "Pendiente")

		# Verify registrations
		self.assertEqual(len(event.registrations), 2)
		self.assertEqual(event.registrations[0].property_registry, self.__class__.test_properties[0])
		self.assertEqual(event.registrations[0].status, "Confirmado")

		# Clean up
		event.delete()

	def test_event_activities(self):
		"""Test adding event activities"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Actividades",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"description": "Event with activities",
			}
		)

		event.insert()

		# Add activities
		event.add_activity("Bienvenida", "09:00", "09:30", "Recepción de invitados")
		event.add_activity("Presentación", "09:30", "10:00", "Presentación del evento")

		# Verify activities
		self.assertEqual(len(event.activities), 2)
		self.assertEqual(event.activities[0].activity_name, "Bienvenida")
		self.assertEqual(event.activities[0].start_time, "09:00")
		self.assertEqual(event.activities[1].end_time, "10:00")

		# Clean up
		event.delete()

	def test_event_capacity_validation(self):
		"""Test event capacity validation"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Capacidad",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"max_attendees": 2,  # Limited capacity
				"registration_required": 1,
				"description": "Event with capacity limit",
			}
		)

		event.insert()

		# Register up to capacity
		event.register_attendee(self.__class__.test_properties[0], "Confirmado")
		event.register_attendee(self.__class__.test_properties[1], "Confirmado")

		# Try to register beyond capacity
		with self.assertRaises(frappe.ValidationError):
			event.register_attendee(self.__class__.test_properties[2], "Confirmado")

		# Clean up
		event.delete()

	def test_event_status_progression(self):
		"""Test event status progression"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Estados",
				"event_type": "Recreativo",
				"event_date": add_days(nowdate(), 10),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"status": "Planificado",
				"description": "Event status progression",
			}
		)

		event.insert()

		# Test status progression
		event.start_event()
		self.assertEqual(event.status, "En Progreso")

		event.complete_event()
		self.assertEqual(event.status, "Completado")

		# Clean up
		event.delete()

	def test_recurring_event(self):
		"""Test recurring event functionality"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Recurrente",
				"event_type": "Administrativo",
				"event_date": add_days(nowdate(), 7),
				"physical_space": "TEST-SPACE-EVENT",
				"organizer": self.__class__.test_members[0],
				"is_recurring": 1,
				"recurrence_pattern": "Mensual",
				"description": "Recurring event",
			}
		)

		event.insert()

		# Create next occurrence
		next_event = event.create_next_occurrence()

		# Verify next occurrence
		self.assertIsNotNone(next_event)
		self.assertEqual(next_event.event_name, "Evento Recurrente")
		self.assertEqual(next_event.is_recurring, 1)

		# Clean up
		event.delete()
		if next_event:
			next_event.delete()

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
