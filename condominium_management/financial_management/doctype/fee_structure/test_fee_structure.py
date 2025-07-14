# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import os
import sys
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate

# Add the financial_management path for imports
current_dir = os.path.dirname(__file__)
if not current_dir.endswith("financial_management"):
	current_dir = os.path.join(current_dir, "..", "..")
sys.path.insert(0, current_dir)

from condominium_management.financial_management.test_base import FinancialTestBaseGranular


class TestFeeStructure(FinancialTestBaseGranular):
	"""Tests granulares para Fee Structure - REGLA #32"""

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación de campos aislada (siempre funciona)"""
		doc = frappe.new_doc("Fee Structure")

		# Verificar campos requeridos existen
		required_fields = ["fee_structure_name", "company", "calculation_method", "base_amount"]
		for field in required_fields:
			self.assertTrue(hasattr(doc, field), f"Campo '{field}' debe existir")

		# Verificar opciones de Select fields
		meta = frappe.get_meta("Fee Structure")
		calculation_method_field = meta.get_field("calculation_method")
		self.assertIn("Por Indiviso", calculation_method_field.options)
		self.assertIn("Monto Fijo", calculation_method_field.options)
		self.assertIn("Por M2", calculation_method_field.options)

		approval_status_field = meta.get_field("approval_status")
		self.assertIn("Pendiente", approval_status_field.options)
		self.assertIn("Aprobado", approval_status_field.options)
		self.assertIn("Rechazado", approval_status_field.options)

	def test_layer_2_basic_document_creation(self):
		"""LAYER 2: Creación básica de documento con campos mínimos"""
		doc = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Estructura Básica",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 50000.00,
				"effective_from": getdate(),
			},
		)

		self.assertEqual(doc.doctype, "Fee Structure")
		self.assertEqual(doc.fee_structure_name, "TEST Estructura Básica")
		self.assertEqual(doc.calculation_method, "Por Indiviso")
		self.assertEqual(doc.base_amount, 50000.00)
		self.assertEqual(doc.is_active, 1)  # Default value

	def test_layer_2_validation_methods(self):
		"""LAYER 2: Validación de métodos de negocio"""
		# Test validación de monto base
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Fee Structure",
					"fee_structure_name": "TEST Invalid Amount",
					"company": "Test Condominium",
					"calculation_method": "Por Indiviso",
					"base_amount": 0,  # Inválido
					"effective_from": getdate(),
				}
			)
			doc.save()

		# Test validación de fechas
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Fee Structure",
					"fee_structure_name": "TEST Invalid Dates",
					"company": "Test Condominium",
					"calculation_method": "Por Indiviso",
					"base_amount": 25000.00,
					"effective_from": getdate(),
					"effective_to": add_days(getdate(), -10),  # Fecha fin anterior
				}
			)
			doc.save()

	def test_layer_2_reserve_fund_validation(self):
		"""LAYER 2: Validación de fondo de reserva"""
		# Test configuración correcta
		doc = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Reserve Fund",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 30000.00,
				"effective_from": getdate(),
				"include_reserve_fund": 1,
				"reserve_fund_percentage": 15.0,
			},
		)
		self.assertTrue(doc.include_reserve_fund)
		self.assertEqual(doc.reserve_fund_percentage, 15.0)

		# Test porcentaje inválido
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Fee Structure",
					"fee_structure_name": "TEST Invalid Reserve",
					"company": "Test Condominium",
					"calculation_method": "Por Indiviso",
					"base_amount": 25000.00,
					"effective_from": getdate(),
					"include_reserve_fund": 1,
					"reserve_fund_percentage": 60.0,  # Excede 50%
				}
			)
			doc.save()

	def test_layer_2_adjustment_validation(self):
		"""LAYER 2: Validación de descuentos y recargos"""
		# Test descuento pronto pago válido
		doc = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Early Payment",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 25000.00,
				"effective_from": getdate(),
				"early_payment_discount": 10.0,
				"early_payment_days": 5,
				"late_payment_charge": 3.0,
				"grace_period_days": 7,
			},
		)
		self.assertEqual(doc.early_payment_discount, 10.0)
		self.assertEqual(doc.late_payment_charge, 3.0)

		# Test descuento inválido
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Fee Structure",
					"fee_structure_name": "TEST Invalid Discount",
					"company": "Test Condominium",
					"calculation_method": "Por Indiviso",
					"base_amount": 25000.00,
					"effective_from": getdate(),
					"early_payment_discount": 25.0,  # Excede 20%
					"early_payment_days": 5,
				}
			)
			doc.save()

	def test_layer_3_fee_calculation_integration(self):
		"""LAYER 3: Integración con cálculo de cuotas"""
		# Crear estructura de prueba
		fee_structure = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Calculation Structure",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 100000.00,
				"effective_from": getdate(),
				"include_reserve_fund": 1,
				"reserve_fund_percentage": 10.0,
			},
		)

		# Mock property registry para testing
		with patch("frappe.get_doc") as mock_get_doc:
			mock_property = type(
				"MockProperty",
				(),
				{"ownership_percentage": 2.5, "built_area_sqm": 85.0, "property_type": "Departamento"},
			)()
			mock_get_doc.return_value = mock_property

			# Test cálculo por indiviso
			calculation = fee_structure.calculate_fee_for_property("TEST_PROP_001")

			expected_base = 100000.00 * (2.5 / 100)  # 2500
			expected_reserve = expected_base * 0.10  # 250
			expected_total = expected_base + expected_reserve  # 2750

			self.assertEqual(calculation["base_fee"], expected_base)
			self.assertEqual(calculation["reserve_fund"], expected_reserve)
			self.assertEqual(calculation["total_fee"], expected_total)
			self.assertEqual(calculation["calculation_method"], "Por Indiviso")

	def test_layer_3_committee_approval_workflow(self):
		"""LAYER 3: Workflow de aprobación del comité"""
		# Test estructura que requiere aprobación
		doc = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Committee Approval",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 25000.00,
				"effective_from": getdate(),
				"requires_committee_approval": 1,
			},
		)

		# Verificar estado inicial
		self.assertTrue(doc.requires_committee_approval)
		self.assertEqual(doc.approval_status, "Pendiente")

		# Test que no se puede enviar sin aprobación
		with self.assertRaises(frappe.ValidationError):
			doc.submit()

		# Test aprobación
		doc.approval_status = "Aprobado"
		doc.approved_by = "Administrator"
		doc.approval_date = getdate()

		# REGLA #35: Reload document para evitar TimestampMismatchError
		if doc.name:
			doc = frappe.get_doc("Fee Structure", doc.name)
			doc.approval_status = "Aprobado"
			doc.approved_by = "Administrator"
			doc.approval_date = getdate()

		doc.save()

		# Verificar que ahora se puede enviar
		doc.reload()
		self.assertEqual(doc.approval_status, "Aprobado")

	@patch("frappe.get_all")
	def test_layer_3_total_income_calculation(self, mock_get_all):
		"""LAYER 3: Cálculo de ingreso total mensual"""
		# Mock properties data
		mock_get_all.return_value = [
			{
				"name": "PROP_001",
				"ownership_percentage": 2.5,
				"built_area_sqm": 85.0,
				"property_type": "Departamento",
			},
			{
				"name": "PROP_002",
				"ownership_percentage": 3.0,
				"built_area_sqm": 95.0,
				"property_type": "Casa",
			},
		]

		fee_structure = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Total Income",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 100000.00,
				"effective_from": getdate(),
			},
		)

		# Mock calculate_fee_for_property method
		with patch.object(fee_structure, "calculate_fee_for_property") as mock_calc:
			mock_calc.side_effect = [
				{"total_fee": 2500.00},  # Prop 1
				{"total_fee": 3000.00},  # Prop 2
			]

			total_income = fee_structure.get_total_monthly_income()
			self.assertEqual(total_income, 5500.00)

	def test_layer_4_overlapping_structures_validation(self):
		"""LAYER 4: Validación de estructuras superpuestas"""
		# Crear primera estructura
		structure1 = self.create_test_document(
			"Fee Structure",
			{
				"fee_structure_name": "TEST Structure 1",
				"company": "Test Condominium",
				"calculation_method": "Por Indiviso",
				"base_amount": 25000.00,
				"effective_from": getdate(),
				"effective_to": add_days(getdate(), 365),
				"is_active": 1,
			},
		)
		structure1.submit()

		# Intentar crear estructura superpuesta debe fallar
		with self.assertRaises(frappe.ValidationError):
			structure2 = frappe.get_doc(
				{
					"doctype": "Fee Structure",
					"fee_structure_name": "TEST Structure 2",
					"company": "Test Condominium",
					"calculation_method": "Por Indiviso",
					"base_amount": 30000.00,
					"effective_from": add_days(getdate(), 30),  # Superpuesta
					"effective_to": add_days(getdate(), 400),
					"is_active": 1,
				}
			)
			structure2.insert()
			structure2.submit()

	def test_layer_4_permissions_enforcement(self):
		"""LAYER 4: Verificación de enforcement de permisos"""
		# Verificar permisos definidos en JSON
		meta = frappe.get_meta("Fee Structure")
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

		# Comité Administración debe poder aprobar
		comite_perms = next((p for p in permissions if p.role == "Comité Administración"), None)
		self.assertIsNotNone(comite_perms, "Rol 'Comité Administración' debe existir en permisos")
		self.assertEqual(comite_perms.read, 1)
		self.assertEqual(comite_perms.submit, 1)

		# Contador solo debe poder leer
		contador_perms = next((p for p in permissions if p.role == "Contador Condominio"), None)
		self.assertIsNotNone(contador_perms, "Rol 'Contador Condominio' debe existir en permisos")
		self.assertEqual(contador_perms.read, 1)
		self.assertEqual(contador_perms.create, 0)


if __name__ == "__main__":
	unittest.main()
