# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestContactInformation(FrappeTestCase):
	"""Test cases for Contact Information DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")
		self.test_data = {
			"contact_type": "Administrador",
			"contact_name": "Juan Pérez Test",
			"email": "juan.perez.test@example.com",
			"phone": "+52 55 1234 5678",
		}

	def test_contact_information_creation(self):
		"""Test basic creation of Contact Information."""
		# Create a new Contact Information
		contact = frappe.get_doc({"doctype": "Contact Information", **self.test_data})
		contact.insert()

		# Verify the document was created successfully
		self.assertTrue(contact.name)
		self.assertEqual(contact.contact_name, "Juan Pérez Test")
		self.assertEqual(contact.email, "juan.perez.test@example.com")

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_email_validation(self):
		"""Test email format validation."""
		# Test valid email
		contact = frappe.get_doc(
			{
				"doctype": "Contact Information",
				"contact_type": "Administrador",
				"contact_name": "Test Email",
				"email": "valid@example.com",
			}
		)
		contact.insert()
		self.assertEqual(contact.email, "valid@example.com")

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_phone_validation(self):
		"""Test phone number validation."""
		# Test valid phone formats
		valid_phones = ["+52 55 1234 5678", "55 1234 5678", "(55) 1234-5678"]

		for phone in valid_phones:
			contact = frappe.get_doc(
				{
					"doctype": "Contact Information",
					"contact_type": "Administrador",
					"contact_name": f"Test Phone {phone}",
					"phone": phone,
				}
			)
			contact.insert()
			self.assertEqual(contact.phone, phone)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Contact Information")

		# Check DocType label
		self.assertEqual(meta.get("label"), "Información de Contacto")

		# Check key field labels
		name_field = meta.get_field("contact_name")
		if name_field:
			self.assertIn("Nombre", name_field.label)

		email_field = meta.get_field("email")
		if email_field:
			self.assertIn("Email", email_field.label)

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase automatically handles transaction rollback
