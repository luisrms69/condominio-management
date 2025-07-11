# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, nowdate


class TestCommunityEvent(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for community event tests"""
		# Create test committee member
		if not frappe.db.exists("Committee Member", {"member_name": "Test Event Organizer"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"member_name": "Test Event Organizer",
					"role": "Vocal",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"member_name": "Test Event Organizer"}, "name"
			)

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SALON-EVENTOS"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Salón de Eventos Test",
					"space_code": "TEST-SALON-EVENTOS",
					"space_type": "Salón de Eventos",
					"capacity": 100,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

	def test_community_event_creation(self):
		"""Test basic community event creation"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento de Prueba",
				"event_description": "Descripción del evento de prueba",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"event_location": "TEST-SALON-EVENTOS",
				"approved_budget": 5000,
				"registration_limit": 50,
				"event_status": "Planificado",
			}
		)

		event.insert()

		# Verify the document was created
		self.assertTrue(event.name)
		self.assertEqual(event.event_name, "Evento de Prueba")
		self.assertEqual(event.event_status, "Planificado")
		self.assertEqual(event.total_expenses, 0)
		self.assertEqual(event.registered_attendees_count, 0)

		# Clean up
		event.delete()

	def test_event_date_validation(self):
		"""Test that event start date must be before or equal to end date"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Fecha Inválida",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 25),  # Before start date
				"approved_budget": 1000,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			event.insert()

	def test_budget_validation(self):
		"""Test that budget cannot be negative"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Presupuesto Negativo",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"approved_budget": -1000,  # Negative budget
			}
		)

		with self.assertRaises(frappe.ValidationError):
			event.insert()

	def test_expenses_exceed_budget_validation(self):
		"""Test that expenses cannot exceed approved budget"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Presupuesto Excedido",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"approved_budget": 1000,
			}
		)

		# Add expenses that exceed budget
		event.append(
			"event_expenses",
			{"expense_description": "Decoración", "expense_category": "Materiales", "amount": 800},
		)

		event.append(
			"event_expenses",
			{
				"expense_description": "Catering",
				"expense_category": "Alimentación",
				"amount": 500,  # Total: 1300, exceeds budget of 1000
			},
		)

		with self.assertRaises(frappe.ValidationError):
			event.insert()

	def test_add_event_organizer(self):
		"""Test adding event organizers"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Organizadores",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"approved_budget": 2000,
			}
		)

		# Add event organizer
		event.append(
			"event_organizers",
			{
				"committee_member": self.test_committee_member,
				"organizer_role": "Coordinador General",
				"responsibilities": "Coordinación general del evento",
			},
		)

		event.insert()

		# Verify organizer was added
		self.assertEqual(len(event.event_organizers), 1)
		self.assertEqual(event.event_organizers[0].committee_member, self.test_committee_member)
		self.assertEqual(event.event_organizers[0].organizer_role, "Coordinador General")

		# Clean up
		event.delete()

	def test_add_event_expense(self):
		"""Test adding event expenses"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Gastos",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"approved_budget": 3000,
			}
		)

		event.insert()

		# Add expense
		event.add_expense("Decoración floral", "Materiales", 500, "Flores y arreglos para decoración")

		# Verify expense was added
		self.assertEqual(len(event.event_expenses), 1)
		self.assertEqual(event.event_expenses[0].expense_description, "Decoración floral")
		self.assertEqual(event.event_expenses[0].amount, 500)
		self.assertEqual(event.total_expenses, 500)

		# Clean up
		event.delete()

	def test_budget_utilization_calculation(self):
		"""Test budget utilization calculation"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Utilización Presupuesto",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"approved_budget": 2000,
			}
		)

		# Add expenses
		event.append(
			"event_expenses",
			{"expense_description": "Alquiler equipo sonido", "expense_category": "Equipos", "amount": 800},
		)

		event.append(
			"event_expenses",
			{"expense_description": "Refrigerios", "expense_category": "Alimentación", "amount": 400},
		)

		event.insert()

		# Calculate budget utilization
		event.calculate_budget_utilization()

		# Verify calculations (1200 spent out of 2000 = 60%)
		self.assertEqual(event.total_expenses, 1200)
		self.assertEqual(event.budget_utilization_percentage, 60)
		self.assertEqual(event.remaining_budget, 800)

		# Clean up
		event.delete()

	def test_register_attendee(self):
		"""Test registering event attendees"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Registro",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"registration_limit": 10,
				"event_status": "Abierto para Registro",
			}
		)

		event.insert()

		# Register attendee
		event.register_attendee("Juan Pérez", "juan@example.com", "555-1234")

		# Verify attendee was registered
		self.assertEqual(len(event.event_registrations), 1)
		self.assertEqual(event.event_registrations[0].attendee_name, "Juan Pérez")
		self.assertEqual(event.registered_attendees_count, 1)

		# Clean up
		event.delete()

	def test_registration_limit_validation(self):
		"""Test that registration doesn't exceed limit"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Límite Registro",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"registration_limit": 1,
				"event_status": "Abierto para Registro",
			}
		)

		# Add registration manually to reach limit
		event.append(
			"event_registrations",
			{
				"attendee_name": "Primer Asistente",
				"attendee_email": "primero@example.com",
				"registration_status": "Confirmado",
			},
		)

		event.insert()

		# Try to register another attendee (should fail)
		with self.assertRaises(frappe.ValidationError):
			event.register_attendee("Segundo Asistente", "segundo@example.com", "555-5678")

		# Clean up
		event.delete()

	def test_capacity_validation(self):
		"""Test validation against physical space capacity"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Validación Capacidad",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
				"event_location": "TEST-SALON-EVENTOS",  # Capacity: 100
				"registration_limit": 150,  # Exceeds space capacity
			}
		)

		# Should show warning but not fail
		event.insert()

		# Clean up
		event.delete()

	def test_add_event_activity(self):
		"""Test adding event activities"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento con Actividades",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 30),
				"event_end_date": add_days(nowdate(), 30),
			}
		)

		# Add event activity
		event.append(
			"event_activities",
			{
				"activity_name": "Bienvenida y registro",
				"activity_type": "Preparación",
				"activity_start_time": "09:00:00",
				"activity_end_time": "10:00:00",
				"is_mandatory": 1,
			},
		)

		event.insert()

		# Verify activity was added
		self.assertEqual(len(event.event_activities), 1)
		self.assertEqual(event.event_activities[0].activity_name, "Bienvenida y registro")
		self.assertTrue(event.event_activities[0].is_mandatory)

		# Clean up
		event.delete()

	def test_get_upcoming_events(self):
		"""Test getting upcoming events"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento Próximo",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), 15),
				"event_end_date": add_days(nowdate(), 15),
				"event_status": "Planificado",
			}
		)

		event.insert()

		# Get upcoming events
		upcoming = event.get_upcoming_events()

		# Should include our test event
		event_names = [e["name"] for e in upcoming]
		self.assertIn(event.name, event_names)

		# Clean up
		event.delete()

	def test_complete_event(self):
		"""Test completing an event"""
		event = frappe.get_doc(
			{
				"doctype": "Community Event",
				"event_name": "Evento para Completar",
				"event_type": "Social",
				"event_start_date": add_days(nowdate(), -1),  # Past date
				"event_end_date": add_days(nowdate(), -1),
				"event_status": "En Curso",
			}
		)

		event.insert()

		# Complete event
		event.complete_event("Evento completado exitosamente. Gran participación.")

		# Verify event was completed
		self.assertEqual(event.event_status, "Completado")
		self.assertIsNotNone(event.completion_date)
		self.assertEqual(event.completion_notes, "Evento completado exitosamente. Gran participación.")

		# Clean up
		event.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test events
		frappe.db.delete("Community Event", {"event_name": ["like", "%Prueba%"]})
		frappe.db.delete("Community Event", {"event_name": ["like", "%Test%"]})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
