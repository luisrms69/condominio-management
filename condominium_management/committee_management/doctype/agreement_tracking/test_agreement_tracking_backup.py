# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate


class TestAgreementTracking(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for agreement tracking tests"""
		# Create test user
		if not frappe.db.exists("User", "test_agreement@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "test_agreement@example.com",
					"first_name": "Test",
					"last_name": "Agreement",
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)

		# Create test company first (required for property registry)
		if not frappe.db.exists("Company", "Test Committee Company"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Committee Company",
					"abbr": "TCC",
					"default_currency": "USD",
				}
			)
			company.insert(ignore_permissions=True)

		# Create required master data
		self.create_test_masters()

		# Create test property registry (required for committee member)
		if not frappe.db.exists("Property Registry", "PROP-TEST-001"):
			property_registry = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"naming_series": "PROP-.YYYY.-",
					"property_name": "Apartamento de Prueba",
					"property_code": "PROP-TEST-001",
					"company": "Test Committee Company",
					"property_usage_type": "Residencial",
					"acquisition_type": "Compra",
					"property_status_type": "Activo",
					"registration_date": nowdate(),
					"total_area_sqm": 85.5,
				}
			)
			property_registry.insert(ignore_permissions=True)

		# Create test committee member
		if not frappe.db.exists("Committee Member", {"user": "test_agreement@example.com"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_agreement@example.com",
					"property_registry": "PROP-TEST-001",
					"full_name": "Test Agreement Member",
					"role_in_committee": "Secretario",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"user": "test_agreement@example.com"}, "name"
			)

	def create_test_masters(self):
		"""Create required master data for tests"""
		# Create Property Usage Type
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc(
				{
					"doctype": "Property Usage Type",
					"usage_type_name": "Residencial",
					"description": "Uso residencial para vivienda",
				}
			)
			usage_type.insert(ignore_permissions=True)

		# Create Acquisition Type
		if not frappe.db.exists("Acquisition Type", "Compra"):
			acquisition_type = frappe.get_doc(
				{
					"doctype": "Acquisition Type",
					"acquisition_type_name": "Compra",
					"description": "Adquisición por compra",
				}
			)
			acquisition_type.insert(ignore_permissions=True)

		# Create Property Status Type
		if not frappe.db.exists("Property Status Type", "Activo"):
			status_type = frappe.get_doc(
				{
					"doctype": "Property Status Type",
					"status_type_name": "Activo",
					"description": "Propiedad activa",
				}
			)
			status_type.insert(ignore_permissions=True)

	def test_agreement_tracking_creation(self):
		"""Test basic agreement tracking creation"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo de Prueba",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
				"priority": "Alta",
				"status": "Pendiente",
				"description": "Descripción del acuerdo de prueba",
			}
		)

		agreement.insert()

		# Verify the document was created
		self.assertTrue(agreement.name)
		self.assertEqual(agreement.agreement_title, "Acuerdo de Prueba")
		self.assertEqual(agreement.status, "Pendiente")
		self.assertEqual(agreement.completion_percentage, 0)

		# Clean up
		agreement.delete()

	def test_date_validation(self):
		"""Test that agreement date must be before due date"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Fecha Inválida",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": add_days(nowdate(), 30),
				"due_date": nowdate(),  # Before agreement date
				"responsible_person": self.test_committee_member,
				"priority": "Media",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			agreement.insert()

	def test_completion_percentage_validation(self):
		"""Test that completion percentage must be between 0 and 100"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Porcentaje Inválido",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
				"completion_percentage": 150,  # Invalid percentage
			}
		)

		with self.assertRaises(frappe.ValidationError):
			agreement.insert()

	def test_auto_status_update_completed(self):
		"""Test that status is automatically updated when completion is 100%"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Completado",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
				"completion_percentage": 100,
				"status": "En Progreso",
			}
		)

		agreement.insert()

		# Status should be automatically updated to Completado
		self.assertEqual(agreement.status, "Completado")

		# Clean up
		agreement.delete()

	def test_auto_status_update_overdue(self):
		"""Test that status is automatically updated when due date passes"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Vencido",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": add_days(nowdate(), -10),
				"due_date": add_days(nowdate(), -1),  # Past due date
				"responsible_person": self.test_committee_member,
				"status": "En Progreso",
			}
		)

		agreement.insert()

		# Status should be automatically updated to Vencido
		self.assertEqual(agreement.status, "Vencido")

		# Clean up
		agreement.delete()

	def test_add_progress_update(self):
		"""Test adding progress updates"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo con Progreso",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
			}
		)

		agreement.insert()

		# Add progress update
		agreement.add_progress_update("Primera actualización de progreso", 25)

		# Verify progress update was added
		self.assertEqual(len(agreement.progress_updates), 1)
		self.assertEqual(
			agreement.progress_updates[0].update_description, "Primera actualización de progreso"
		)
		self.assertEqual(agreement.progress_updates[0].percentage_complete, 25)
		self.assertEqual(agreement.completion_percentage, 25)

		# Clean up
		agreement.delete()

	def test_calculate_days_remaining(self):
		"""Test calculating days remaining until due date"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Días Restantes",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 15),
				"responsible_person": self.test_committee_member,
			}
		)

		agreement.insert()

		# Calculate days remaining
		days_remaining = agreement.calculate_days_remaining()

		# Should be 15 days
		self.assertEqual(days_remaining, 15)

		# Test overdue agreement
		agreement.due_date = add_days(nowdate(), -5)
		days_remaining = agreement.calculate_days_remaining()
		self.assertEqual(days_remaining, -5)

		# Clean up
		agreement.delete()

	def test_get_overdue_agreements(self):
		"""Test getting overdue agreements"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Vencido para Consulta",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": add_days(nowdate(), -20),
				"due_date": add_days(nowdate(), -5),
				"responsible_person": self.test_committee_member,
				"status": "En Progreso",
			}
		)

		agreement.insert()

		# Get overdue agreements
		overdue = agreement.get_overdue_agreements()

		# Should include our test agreement
		agreement_names = [a["name"] for a in overdue]
		self.assertIn(agreement.name, agreement_names)

		# Clean up
		agreement.delete()

	def test_get_pending_agreements_by_member(self):
		"""Test getting pending agreements by committee member"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo Pendiente por Miembro",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
				"status": "Pendiente",
			}
		)

		agreement.insert()

		# Get pending agreements for this member
		pending = agreement.get_pending_agreements_by_member(self.test_committee_member)

		# Should include our test agreement
		agreement_names = [a["name"] for a in pending]
		self.assertIn(agreement.name, agreement_names)

		# Clean up
		agreement.delete()

	def test_mark_as_completed(self):
		"""Test marking agreement as completed"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo para Completar",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": add_days(nowdate(), 30),
				"responsible_person": self.test_committee_member,
				"status": "En Progreso",
			}
		)

		agreement.insert()

		# Mark as completed
		agreement.mark_as_completed("Acuerdo completado exitosamente")

		# Verify it was marked as completed
		self.assertEqual(agreement.status, "Completado")
		self.assertEqual(agreement.completion_percentage, 100)
		self.assertIsNotNone(agreement.completion_date)
		self.assertEqual(agreement.completion_notes, "Acuerdo completado exitosamente")

		# Clean up
		agreement.delete()

	def test_extend_due_date(self):
		"""Test extending due date"""
		original_due_date = add_days(nowdate(), 30)
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"agreement_title": "Acuerdo para Extender",
				"agreement_type": "Resolución de Asamblea",
				"agreement_date": nowdate(),
				"due_date": original_due_date,
				"responsible_person": self.test_committee_member,
			}
		)

		agreement.insert()

		# Extend due date by 15 days
		new_due_date = add_days(original_due_date, 15)
		agreement.extend_due_date(new_due_date, "Extensión necesaria por motivos técnicos")

		# Verify due date was extended
		self.assertEqual(getdate(agreement.due_date), getdate(new_due_date))
		self.assertTrue(len(agreement.progress_updates) > 0)

		# Clean up
		agreement.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test agreements
		frappe.db.delete("Agreement Tracking", {"agreement_title": ["like", "%Prueba%"]})
		frappe.db.delete("Agreement Tracking", {"agreement_title": ["like", "%Test%"]})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
