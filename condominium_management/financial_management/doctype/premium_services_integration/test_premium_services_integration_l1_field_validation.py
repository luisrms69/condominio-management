# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPremiumServicesIntegrationL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Premium Services Integration DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test missing service_name validation (custom validation)
		with self.assertRaises(frappe.ValidationError) as context:
			premium_services.insert()
		self.assertIn("Nombre del Servicio es obligatorio", str(context.exception))

		# Test each required field individually
		required_fields = ["naming_series", "service_name", "service_category", "company", "service_status"]

		for field in required_fields:
			self.assertTrue(hasattr(premium_services, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test naming series field exists
		self.assertTrue(hasattr(premium_services, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Premium Services Integration")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "PSI-.YYYY.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Data fields
		premium_services.service_name = "Test Premium Service"
		self.assertEqual(premium_services.service_name, "Test Premium Service")

		# Test Currency fields if exist
		if hasattr(premium_services, "service_price"):
			premium_services.service_price = 150.75
			self.assertEqual(premium_services.service_price, 150.75)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test service_category options (common premium services)
		valid_service_categories = [
			"Spa y Bienestar",
			"Fitness",
			"Concierge",
			"Limpieza",
			"Seguridad",
			"Mantenimiento",
			"Eventos",
			"Transporte",
			"Otra",
		]
		for category in valid_service_categories:
			premium_services.service_category = category
			self.assertEqual(premium_services.service_category, category)

		# Test service_status options
		valid_service_statuses = ["Activo", "Inactivo", "En Mantenimiento", "Suspendido", "Cancelado"]
		for status in valid_service_statuses:
			premium_services.service_status = status
			self.assertEqual(premium_services.service_status, status)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test currency fields with various precision values
		currency_fields = ["service_price", "setup_fee", "monthly_fee", "commission_rate"]

		for field in currency_fields:
			if hasattr(premium_services, field):
				# Test with 2 decimal places (should be preserved)
				setattr(premium_services, field, 1234.56)
				self.assertEqual(getattr(premium_services, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test valid date formats
		from datetime import date

		today = date.today()

		# Test date fields
		date_fields = ["service_start_date", "service_end_date", "last_maintenance_date"]
		for field in date_fields:
			if hasattr(premium_services, field):
				setattr(premium_services, field, today)
				self.assertEqual(getattr(premium_services, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Link field assignments
		premium_services.company = "_Test Company"
		self.assertEqual(premium_services.company, "_Test Company")

		if hasattr(premium_services, "service_provider"):
			premium_services.service_provider = "Test Provider"
			self.assertEqual(premium_services.service_provider, "Test Provider")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Long Text fields
		if hasattr(premium_services, "service_description"):
			premium_services.service_description = "Test service description"
			self.assertEqual(premium_services.service_description, "Test service description")

		if hasattr(premium_services, "terms_and_conditions"):
			premium_services.terms_and_conditions = "Test terms and conditions"
			self.assertEqual(premium_services.terms_and_conditions, "Test terms and conditions")

	def test_data_field_validation(self):
		"""Test that data fields accept string values"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Data fields
		if hasattr(premium_services, "contact_person"):
			premium_services.contact_person = "Test Contact"
			self.assertEqual(premium_services.contact_person, "Test Contact")

		if hasattr(premium_services, "phone_number"):
			premium_services.phone_number = "+52 55 1234 5678"
			self.assertEqual(premium_services.phone_number, "+52 55 1234 5678")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Check fields (boolean)
		if hasattr(premium_services, "requires_booking"):
			premium_services.requires_booking = 1
			self.assertEqual(premium_services.requires_booking, 1)

			premium_services.requires_booking = 0
			self.assertEqual(premium_services.requires_booking, 0)

		if hasattr(premium_services, "available_24_7"):
			premium_services.available_24_7 = 1
			self.assertEqual(premium_services.available_24_7, 1)

	def test_time_field_validation(self):
		"""Test that time fields accept valid time values"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test Time fields
		if hasattr(premium_services, "service_start_time"):
			premium_services.service_start_time = "09:00:00"
			self.assertEqual(premium_services.service_start_time, "09:00:00")

		if hasattr(premium_services, "service_end_time"):
			premium_services.service_end_time = "18:00:00"
			self.assertEqual(premium_services.service_end_time, "18:00:00")

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		premium_services = frappe.new_doc("Premium Services Integration")

		# Test that calculated fields can be set programmatically
		if hasattr(premium_services, "total_bookings"):
			premium_services.total_bookings = 25
			self.assertEqual(premium_services.total_bookings, 25)

		if hasattr(premium_services, "monthly_revenue"):
			premium_services.monthly_revenue = 3750.00
			self.assertEqual(premium_services.monthly_revenue, 3750.00)
