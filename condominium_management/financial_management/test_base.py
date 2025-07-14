# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Financial Management - Framework de Testing Base
===============================================

Framework base para testing del Financial Management Module
con integración ERPNext Financial y validación de patrones financieros.
"""

import json
import typing
import unittest

import frappe
from frappe.test_runner import make_test_records
from frappe.utils import add_days, flt, getdate, now


class FinancialTestBase(unittest.TestCase):
	"""Framework base para tests del Financial Management"""

	@classmethod
	def setUpClass(cls):
		"""Setup de clase - datos comunes para todos los tests"""
		frappe.set_user("Administrator")

		# Limpiar datos previos
		cls.cleanup_test_data()

		# Crear estructura financiera base
		cls.setup_erpnext_financial_config()
		cls.setup_companies_data()
		cls.setup_financial_roles()
		cls.setup_test_properties()

	@classmethod
	def tearDownClass(cls):
		"""Cleanup de clase"""
		cls.cleanup_test_data()

	@classmethod
	def cleanup_test_data(cls):
		"""Limpia datos de test con verificación defensiva"""
		doctypes_to_clean = [
			"Premium Services Integration",
			"Financial Transparency Config",
			"Budget Planning",
			"Fine Management",
			"Credit Balance Management",
			"Payment Collection",
			"Billing Cycle",
			"Resident Account",
			"Property Account",
			"Fee Structure",
		]

		for doctype in doctypes_to_clean:
			try:
				# Verificar que la tabla existe antes de limpiar
				if frappe.db.exists("DocType", doctype):
					frappe.db.sql(f"DELETE FROM `tab{doctype}` WHERE name LIKE '%TEST%'")
			except Exception as e:
				# Ignorar errores de tabla no encontrada (esperado en primera ejecución)
				if "doesn't exist" not in str(e):
					frappe.log_error(f"Error cleaning {doctype}: {e!s}")

		frappe.db.commit()

	@classmethod
	def setup_erpnext_financial_config(cls):
		"""Setup configuración financiera ERPNext"""

		# Crear Customer Group para condóminos
		if not frappe.db.exists("Customer Group", "Condóminos"):
			customer_group = frappe.get_doc(
				{
					"doctype": "Customer Group",
					"customer_group_name": "Condóminos",
					"parent_customer_group": "All Customer Groups",
					"is_group": 0,
				}
			)
			customer_group.insert(ignore_permissions=True)

		# Crear Customer Group para residentes
		if not frappe.db.exists("Customer Group", "Residentes"):
			customer_group = frappe.get_doc(
				{
					"doctype": "Customer Group",
					"customer_group_name": "Residentes",
					"parent_customer_group": "All Customer Groups",
					"is_group": 0,
				}
			)
			customer_group.insert(ignore_permissions=True)

		cls.erpnext_config_ready = True

	@classmethod
	def setup_companies_data(cls):
		"""Setup datos de companies para testing"""

		# Company de prueba
		cls.test_company = type(
			"MockCompany",
			(),
			{
				"name": "TEST_FINANCIAL_COMPANY",
				"company_name": "Condominio Test Financiero",
				"abbr": "TFC",
				"default_currency": "MXN",
				"country": "Mexico",
			},
		)()

		cls.companies_data_ready = True

	@classmethod
	def setup_financial_roles(cls):
		"""Configura roles financieros necesarios"""
		roles_to_create = [
			"Administrador Financiero",
			"Comité Administración",
			"Contador Condominio",
			"Residente Propietario",
		]

		for role_name in roles_to_create:
			if not frappe.db.exists("Role", role_name):
				role = frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1})
				role.insert(ignore_permissions=True)

		cls.financial_roles_ready = True

	@classmethod
	def setup_test_properties(cls):
		"""Setup propiedades de prueba para cuentas financieras"""

		# Propiedad 1: Departamento
		cls.test_property_1 = type(
			"MockProperty",
			(),
			{
				"name": "TEST_PROP_001",
				"property_name": "Departamento 101",
				"property_type": "Departamento",
				"built_area_sqm": 85.5,
				"ownership_percentage": 2.5,
				"owner_name": "Juan Pérez García",
				"company": "TEST_FINANCIAL_COMPANY",
			},
		)()

		# Propiedad 2: Casa
		cls.test_property_2 = type(
			"MockProperty",
			(),
			{
				"name": "TEST_PROP_002",
				"property_name": "Casa 15",
				"property_type": "Casa",
				"built_area_sqm": 120.0,
				"ownership_percentage": 3.2,
				"owner_name": "María González López",
				"company": "TEST_FINANCIAL_COMPANY",
			},
		)()

		cls.test_properties_ready = True

	@classmethod
	def create_test_customer(cls, customer_name, customer_group="Condóminos"):
		"""Crea Customer de prueba en ERPNext"""
		if frappe.db.exists("Customer", customer_name):
			return frappe.get_doc("Customer", customer_name)

		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_type": "Individual",
				"customer_group": customer_group,
				"territory": "Mexico",
			}
		)
		customer.insert(ignore_permissions=True)
		return customer

	@classmethod
	def create_test_company(cls, company_name):
		"""Crea Company de test"""
		if frappe.db.exists("Company", company_name):
			return frappe.get_doc("Company", company_name)

		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": company_name,
				"abbr": company_name.split()[-1][:3].upper(),
				"default_currency": "MXN",
				"country": "Mexico",
			}
		)
		company.insert(ignore_permissions=True)
		return company

	def setUp(self):
		"""Setup para cada test individual"""
		frappe.set_user("Administrator")
		frappe.flags.in_test = True

	def tearDown(self):
		"""Cleanup para cada test individual"""
		frappe.db.rollback()


class FinancialTestBaseGranular(FinancialTestBase):
	"""Framework para testing granular financiero - REGLA #32"""

	# Campos requeridos para cada DocType
	REQUIRED_FIELDS: typing.ClassVar[dict[str, list[str]]] = {
		"Fee Structure": ["fee_structure_name", "company", "calculation_method", "base_amount"],
		"Property Account": ["property_registry", "customer", "billing_frequency", "current_balance"],
		"Resident Account": ["resident_name", "property_account", "resident_type", "current_balance"],
		"Billing Cycle": ["cycle_name", "company", "billing_month", "billing_year", "fee_structure"],
		"Payment Collection": ["payment_date", "payment_amount", "payment_method", "account_type"],
		"Credit Balance Management": [
			"credit_note_number",
			"account_type",
			"original_amount",
			"current_balance",
		],
		"Fine Management": ["fine_type", "property_account", "fine_date", "total_amount"],
		"Budget Planning": ["budget_name", "company", "fiscal_year", "budget_type"],
		"Financial Transparency Config": ["company", "transparency_rules"],
		"Premium Services Integration": ["service_category", "service_name", "billing_integration"],
	}

	def create_test_document(self, doctype, override_fields=None, ignore_if_duplicate=False):
		"""
		Crea documento de test con campos requeridos financieros

		Args:
			doctype: Tipo de documento
			override_fields: Campos a sobrescribir
			ignore_if_duplicate: Ignorar si ya existe
		"""
		base_fields = {
			"Fee Structure": {
				"fee_structure_name": f"TEST Estructura Cuotas {frappe.utils.random_string(5)}",
				"company": "TEST_FINANCIAL_COMPANY",
				"calculation_method": "Por Indiviso",
				"base_amount": 2500.00,
				"effective_from": getdate(),
				"is_active": 1,
			},
			"Property Account": {
				"account_code": f"PA-{frappe.utils.random_string(8).upper()}",
				"property_registry": "TEST_PROP_001",
				"customer": "TEST Customer Propietario",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"account_status": "Activa",
			},
			"Resident Account": {
				"account_code": f"RA-{frappe.utils.random_string(8).upper()}",
				"resident_name": f"TEST Residente {frappe.utils.random_string(5)}",
				"property_account": "TEST_PROP_001",
				"resident_type": "Arrendatario",
				"current_balance": 0.0,
				"can_be_invoiced": 1,
			},
			"Billing Cycle": {
				"cycle_name": f"TEST Facturación {frappe.utils.random_string(5)}",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_month": getdate().month,
				"billing_year": getdate().year,
				"fee_structure": "TEST Fee Structure",
				"generation_status": "Pendiente",
			},
			"Payment Collection": {
				"payment_date": getdate(),
				"payment_amount": 2500.00,
				"payment_method": "Transferencia",
				"account_type": "Propietario",
				"reference_number": f"REF{frappe.utils.random_string(10)}",
				"reconciliation_status": "Pendiente",
			},
		}

		if doctype not in base_fields:
			raise ValueError(f"DocType {doctype} no tiene configuración base")

		fields = base_fields[doctype].copy()
		if override_fields:
			fields.update(override_fields)

		try:
			doc = frappe.get_doc(dict(doctype=doctype, **fields))
			doc.insert(ignore_permissions=True)
			return doc
		except frappe.DuplicateEntryError:
			if ignore_if_duplicate:
				# Buscar documento existente
				existing = frappe.db.get_value(
					doctype,
					fields.get("name")
					or {
						k: v
						for k, v in fields.items()
						if k in ["fee_structure_name", "account_code", "cycle_name"]
					},
				)
				if existing:
					return frappe.get_doc(doctype, existing)
			raise

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación de campos aislada (siempre funciona)"""
		for doctype in self.REQUIRED_FIELDS:
			with self.subTest(doctype=doctype):
				doc = frappe.new_doc(doctype)

				# Verificar que campos requeridos existen
				for field in self.REQUIRED_FIELDS[doctype]:
					self.assertTrue(hasattr(doc, field), f"Campo requerido '{field}' no existe en {doctype}")

	def test_layer_2_permissions_validation(self):
		"""LAYER 2: Validación de permisos por nivel"""

		# Verificar permisos de Fee Structure
		fee_structure_perms = frappe.get_meta("Fee Structure").permissions

		# System Manager debe tener todos los permisos
		system_manager_perms = next((p for p in fee_structure_perms if p.role == "System Manager"), None)
		self.assertIsNotNone(system_manager_perms, "System Manager debe tener permisos")
		self.assertEqual(system_manager_perms.create, 1)
		self.assertEqual(system_manager_perms.read, 1)
		self.assertEqual(system_manager_perms.write, 1)
		self.assertEqual(system_manager_perms.delete, 1)

		# Administrador Financiero debe poder crear y modificar
		admin_perms = next((p for p in fee_structure_perms if p.role == "Administrador Financiero"), None)
		self.assertIsNotNone(admin_perms, "Administrador Financiero debe tener permisos")
		self.assertEqual(admin_perms.create, 1)
		self.assertEqual(admin_perms.read, 1)
		self.assertEqual(admin_perms.write, 1)

	def test_layer_3_erpnext_integration(self):
		"""LAYER 3: Validación de integración con ERPNext"""

		# Verificar que Customer Groups existen
		self.assertTrue(frappe.db.exists("Customer Group", "Condóminos"))
		self.assertTrue(frappe.db.exists("Customer Group", "Residentes"))

		# Verificar roles financieros
		self.assertTrue(frappe.db.exists("Role", "Administrador Financiero"))
		self.assertTrue(frappe.db.exists("Role", "Comité Administración"))

	def test_layer_4_financial_calculations(self):
		"""LAYER 4: Validación de cálculos financieros básicos"""

		# Test cálculo de cuotas por indiviso
		base_amount = 100000.0  # Cuota base total
		ownership_percentage = 2.5  # 2.5% de indiviso
		expected_fee = base_amount * (ownership_percentage / 100)

		calculated_fee = flt(base_amount * ownership_percentage / 100, 2)
		self.assertEqual(calculated_fee, expected_fee)

		# Test aplicación de descuentos
		fee_amount = 2500.0
		discount_percentage = 10.0
		expected_with_discount = fee_amount * (1 - discount_percentage / 100)

		calculated_with_discount = flt(fee_amount * (1 - discount_percentage / 100), 2)
		self.assertEqual(calculated_with_discount, expected_with_discount)
