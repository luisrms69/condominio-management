# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyCopropiedad(FrappeTestCase):
	def test_copropiedad_validation(self):
		"""Test validaciones básicas de copropiedad"""
		# Test porcentaje negativo
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "12345678",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": -10.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad.validate()

		# Test porcentaje mayor a 100%
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "María González",
				"owner_id": "87654321",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 110.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad2.validate()

	def test_owner_info_validation(self):
		"""Test validación de información del propietario"""
		# Nombre vacío
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "",
				"owner_id": "12345678",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 50.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad.validate()

		# ID vacío
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 50.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad2.validate()

	def test_owner_id_format_validation(self):
		"""Test validación de formato de identificación"""
		# ID muy corto para persona natural
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "123",  # Muy corto
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 50.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad.validate()

		# ID válido para persona natural
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "12345678",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 50.0,
			}
		)

		# No debe arrojar error
		copropiedad2.validate()

	def test_display_methods(self):
		"""Test métodos de display"""
		# Persona Natural
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "12345678",
				"owner_type": "Persona Natural",
				"copropiedad_percentage": 60.0,
			}
		)

		display_name = copropiedad.get_owner_display_name()
		self.assertEqual(display_name, "Juan Pérez (C.C. 12345678)")

		ownership_display = copropiedad.get_ownership_display()
		self.assertEqual(ownership_display, "Juan Pérez (C.C. 12345678) - 60.0%")

		# Persona Jurídica
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Empresa ABC S.A.S.",
				"owner_id": "900123456",
				"owner_type": "Persona Jurídica",
				"copropiedad_percentage": 40.0,
			}
		)

		display_name2 = copropiedad2.get_owner_display_name()
		self.assertEqual(display_name2, "Empresa ABC S.A.S. (NIT 900123456)")

		ownership_display2 = copropiedad2.get_ownership_display()
		self.assertEqual(ownership_display2, "Empresa ABC S.A.S. (NIT 900123456) - 40.0%")
