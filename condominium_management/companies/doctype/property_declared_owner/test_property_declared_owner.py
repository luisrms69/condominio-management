# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


class TestPropertyDeclaredOwner(IntegrationTestCase):
	def test_owner_percentage_validation(self):
		"""Test validaciones de porcentaje de titularidad"""
		# Porcentaje negativo
		owner = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Juan Pérez",
				"owner_type": "Persona Física",
				"ownership_percentage": -10.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			owner.validate()

		# Porcentaje mayor a 100%
		owner2 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "María González",
				"owner_type": "Persona Física",
				"ownership_percentage": 110.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			owner2.validate()

	def test_owner_info_validation(self):
		"""Test validación de información del propietario"""
		# Nombre vacío debe fallar
		owner = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "",
				"owner_type": "Persona Física",
				"ownership_percentage": 50.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			owner.validate()

		# owner_id vacío es válido — no debe bloquear
		owner2 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Juan Pérez",
				"owner_id": "",
				"owner_type": "Persona Física",
				"ownership_percentage": 50.0,
			}
		)

		owner2.validate()

	def test_owner_id_format_validation(self):
		"""ID inválido emite advertencia pero no bloquea"""
		# Formato incorrecto para RFC/CURP — no debe bloquear
		owner = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Juan Pérez",
				"owner_id": "123",
				"owner_type": "Persona Física",
				"ownership_percentage": 50.0,
			}
		)

		owner.validate()

		# RFC válido Persona Física — no debe arrojar error
		owner2 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Juan Pérez",
				"owner_id": "PERJ850101AB3",
				"owner_type": "Persona Física",
				"ownership_percentage": 50.0,
			}
		)

		owner2.validate()

		# RFC válido Persona Moral — no debe arrojar error
		owner3 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Empresa ABC S.A. de C.V.",
				"owner_id": "ABC850101AB3",
				"owner_type": "Persona Moral",
				"ownership_percentage": 100.0,
			}
		)

		owner3.validate()

	def test_display_methods(self):
		"""Test métodos de display"""
		# Persona Física con ID
		owner = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Juan Pérez",
				"owner_id": "PERJ850101AB3",
				"owner_type": "Persona Física",
				"ownership_percentage": 60.0,
			}
		)

		self.assertEqual(owner.get_owner_display_name(), "Juan Pérez (PERJ850101AB3)")
		self.assertEqual(owner.get_ownership_display(), "Juan Pérez (PERJ850101AB3) - 60.0%")

		# Persona Moral con ID
		owner2 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Empresa ABC S.A. de C.V.",
				"owner_id": "ABC850101AB3",
				"owner_type": "Persona Moral",
				"ownership_percentage": 40.0,
			}
		)

		self.assertEqual(owner2.get_owner_display_name(), "Empresa ABC S.A. de C.V. (ABC850101AB3)")
		self.assertEqual(owner2.get_ownership_display(), "Empresa ABC S.A. de C.V. (ABC850101AB3) - 40.0%")

		# Sin owner_id — solo nombre
		owner3 = frappe.get_doc(
			{
				"doctype": "Property Declared Owner",
				"owner_name": "Propietario Sin ID",
				"owner_type": "Persona Física",
				"ownership_percentage": 100.0,
			}
		)

		self.assertEqual(owner3.get_owner_display_name(), "Propietario Sin ID")
		self.assertEqual(owner3.get_ownership_display(), "Propietario Sin ID - 100.0%")
