# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.utils import add_days, getdate


class TestPropertyAccountDirect(unittest.TestCase):
	"""Tests directos para Property Account"""

	def setUp(self):
		"""Setup básico para cada test"""
		frappe.set_user("Administrator")

	def test_property_account_doctype_exists(self):
		"""Verificar que el DocType Property Account existe"""
		self.assertTrue(frappe.db.exists("DocType", "Property Account"))

	def test_property_account_fields_exist(self):
		"""Verificar que los campos principales existen"""
		meta = frappe.get_meta("Property Account")

		required_fields = ["property_registry", "customer", "billing_frequency", "current_balance"]
		for field in required_fields:
			field_obj = meta.get_field(field)
			self.assertIsNotNone(field_obj, f"Campo '{field}' debe existir")

	def test_property_account_select_options(self):
		"""Verificar opciones de campos Select"""
		meta = frappe.get_meta("Property Account")

		# Verificar opciones de billing_frequency
		billing_frequency_field = meta.get_field("billing_frequency")
		self.assertIn("Mensual", billing_frequency_field.options)
		self.assertIn("Bimestral", billing_frequency_field.options)
		self.assertIn("Trimestral", billing_frequency_field.options)

		# Verificar opciones de account_status
		account_status_field = meta.get_field("account_status")
		self.assertIn("Activa", account_status_field.options)
		self.assertIn("Suspendida", account_status_field.options)
		self.assertIn("Morosa", account_status_field.options)

	def test_property_account_currency_fields(self):
		"""Verificar campos monetarios"""
		meta = frappe.get_meta("Property Account")

		currency_fields = [
			"current_balance",
			"credit_balance",
			"pending_amount",
			"last_payment_amount",
			"monthly_fee_amount",
			"ytd_paid_amount",
			"total_invoiced_ytd",
		]

		for field_name in currency_fields:
			field = meta.get_field(field_name)
			self.assertEqual(field.fieldtype, "Currency", f"Campo {field_name} debe ser Currency")
			self.assertEqual(field.precision, "2", f"Campo {field_name} debe tener precisión 2")

	def test_property_account_permissions(self):
		"""Verificar permisos definidos"""
		meta = frappe.get_meta("Property Account")
		permissions = meta.permissions

		# System Manager debe tener todos los permisos
		system_manager_perms = next((p for p in permissions if p.role == "System Manager"), None)
		self.assertIsNotNone(system_manager_perms)
		self.assertEqual(system_manager_perms.create, 1)
		self.assertEqual(system_manager_perms.read, 1)
		self.assertEqual(system_manager_perms.write, 1)
		self.assertEqual(system_manager_perms.delete, 1)

		# Administrador Financiero debe poder crear/editar
		admin_perms = next((p for p in permissions if p.role == "Administrador Financiero"), None)
		self.assertIsNotNone(admin_perms, "Rol 'Administrador Financiero' debe existir en permisos")
		self.assertEqual(admin_perms.create, 1)
		self.assertEqual(admin_perms.read, 1)
		self.assertEqual(admin_perms.write, 1)

	def test_create_basic_property_account(self):
		"""Test creación básica de Property Account"""
		# Limpiar datos previos
		if frappe.db.exists("Property Account", "TEST Cuenta Básica"):
			frappe.delete_doc("Property Account", "TEST Cuenta Básica")

		# Crear documento básico
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "TEST Cuenta Básica",
				"property_registry": "TEST_PROP_001",
				"customer": "TEST_CUSTOMER_001",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			}
		)

		# Verificar campos básicos
		self.assertEqual(doc.doctype, "Property Account")
		self.assertEqual(doc.account_name, "TEST Cuenta Básica")
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.current_balance, 0.0)

		# Limpiar
		if frappe.db.exists("Property Account", "TEST Cuenta Básica"):
			frappe.delete_doc("Property Account", "TEST Cuenta Básica")


if __name__ == "__main__":
	unittest.main()
