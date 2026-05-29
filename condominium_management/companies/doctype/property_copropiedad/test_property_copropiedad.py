# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyCopropiedad(FrappeTestCase):
	def test_copropiedad_validation(self):
		"""Test validaciones básicas de copropiedad"""
		# Porcentaje negativo
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_type": "Persona Física",
				"copropiedad_percentage": -10.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad.validate()

		# Porcentaje mayor a 100%
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "María González",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 110.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad2.validate()

	def test_owner_info_validation(self):
		"""Test validación de información del propietario"""
		# Nombre vacío debe fallar
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 50.0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			copropiedad.validate()

		# owner_id vacío es válido — no debe bloquear
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 50.0,
			}
		)

		copropiedad2.validate()

	def test_owner_id_format_validation(self):
		"""ID inválido emite advertencia pero no bloquea"""
		# Formato incorrecto para RFC/CURP — no debe bloquear
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "123",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 50.0,
			}
		)

		copropiedad.validate()

		# RFC válido Persona Física — no debe arrojar error
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "PERJ850101AB3",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 50.0,
			}
		)

		copropiedad2.validate()

		# RFC válido Persona Moral — no debe arrojar error
		copropiedad3 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Empresa ABC S.A. de C.V.",
				"owner_id": "ABC850101AB3",
				"owner_type": "Persona Moral",
				"copropiedad_percentage": 100.0,
			}
		)

		copropiedad3.validate()

	def test_display_methods(self):
		"""Test métodos de display"""
		# Persona Física con ID
		copropiedad = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Juan Pérez",
				"owner_id": "PERJ850101AB3",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 60.0,
			}
		)

		self.assertEqual(copropiedad.get_owner_display_name(), "Juan Pérez (PERJ850101AB3)")
		self.assertEqual(copropiedad.get_ownership_display(), "Juan Pérez (PERJ850101AB3) - 60.0%")

		# Persona Moral con ID
		copropiedad2 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Empresa ABC S.A. de C.V.",
				"owner_id": "ABC850101AB3",
				"owner_type": "Persona Moral",
				"copropiedad_percentage": 40.0,
			}
		)

		self.assertEqual(copropiedad2.get_owner_display_name(), "Empresa ABC S.A. de C.V. (ABC850101AB3)")
		self.assertEqual(
			copropiedad2.get_ownership_display(), "Empresa ABC S.A. de C.V. (ABC850101AB3) - 40.0%"
		)

		# Sin owner_id — solo nombre
		copropiedad3 = frappe.get_doc(
			{
				"doctype": "Property Copropiedad",
				"owner_name": "Propietario Sin ID",
				"owner_type": "Persona Física",
				"copropiedad_percentage": 100.0,
			}
		)

		self.assertEqual(copropiedad3.get_owner_display_name(), "Propietario Sin ID")
		self.assertEqual(copropiedad3.get_ownership_display(), "Propietario Sin ID - 100.0%")
