# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, getdate, nowdate

from condominium_management.financial_management.test_base import FinancialTestBaseGranular


class TestResidentAccount(FinancialTestBaseGranular):
	"""Testing granular REGLA #32 - 4 layers para Resident Account"""

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Field validation aislada sin dependencies"""
		# Crear documento sin guardarlo
		doc = frappe.new_doc("Resident Account")

		# Test field assignment básico
		doc.account_code = "TEST-RES01-JD"
		doc.resident_name = "Juan Pérez"
		doc.resident_type = "Propietario"
		doc.account_status = "Activa"
		doc.current_balance = 0.0
		doc.credit_limit = 5000.0
		doc.spending_limits = 1000.0
		doc.approval_required_amount = 2000.0

		# Verificar assignments exitosos
		self.assertEqual(doc.doctype, "Resident Account")
		self.assertEqual(doc.account_code, "TEST-RES01-JD")
		self.assertEqual(doc.resident_name, "Juan Pérez")
		self.assertEqual(doc.resident_type, "Propietario")
		self.assertEqual(doc.account_status, "Activa")
		self.assertEqual(flt(doc.current_balance), 0.0)
		self.assertEqual(flt(doc.credit_limit), 5000.0)
		self.assertEqual(flt(doc.spending_limits), 1000.0)
		self.assertEqual(flt(doc.approval_required_amount), 2000.0)

	def test_layer_2_business_logic_with_mocked_dependencies(self):
		"""LAYER 2: Business logic con dependencies mockeadas"""
		with (
			patch("frappe.get_doc") as mock_get_doc,
			patch("frappe.db.get_value") as mock_get_value,
			patch("frappe.db.count") as mock_count,
		):
			# Mock Property Account dependency
			mock_property = MagicMock()
			mock_property.account_status = "Activa"
			mock_property.company = "TEST COMPANY"
			mock_property.account_name = "PROP-001"
			mock_get_doc.return_value = mock_property

			# Mock uniqueness check
			mock_get_value.return_value = None

			# Mock count for sequence
			mock_count.return_value = 0

			# Crear documento REAL para testing
			doc = frappe.new_doc("Resident Account")
			doc.property_account = "PROP-001"
			doc.resident_name = "María García"
			doc.resident_type = "Inquilino"
			doc.current_balance = 1500.0
			doc.credit_limit = 3000.0
			doc.spending_limits = 800.0
			doc.approval_required_amount = 1500.0

			# Execute validation methods
			doc.validate_property_account()
			doc.validate_resident_data()
			doc.validate_financial_limits()
			doc.validate_credit_configuration()
			doc.calculate_credit_metrics()
			doc.set_default_values()
			doc.generate_account_code()

			# Verify business logic calculations
			self.assertEqual(doc.company, "TEST COMPANY")
			self.assertEqual(flt(doc.available_credit), 1500.0)  # 3000 - 1500
			self.assertEqual(flt(doc.credit_utilization_percentage), 50.0)  # (1500/3000)*100
			self.assertEqual(flt(doc.pending_charges), 0.0)  # positive balance
			self.assertIn("PROP-001-RES01-MG", doc.account_code)

	def test_layer_3_integration_with_real_dependencies(self):
		"""LAYER 3: Integration testing con dependencias reales"""
		# Setup dependencies usando base methods
		property_account = self.create_test_property_account()

		# Crear Resident Account vinculada
		resident_account = frappe.get_doc(
			{
				"doctype": "Resident Account",
				"property_account": property_account.name,
				"resident_name": "Carlos Mendoza",
				"resident_type": "Familiar",
				"current_balance": -500.0,  # Saldo negativo (debe dinero)
				"credit_limit": 2000.0,
				"spending_limits": 600.0,
				"approval_required_amount": 1000.0,
				"auto_charge_enabled": 1,
				"notifications_enabled": 1,
			}
		)

		# Test insert con dependencies reales
		resident_account.insert(ignore_permissions=True)

		# Verify successful creation
		self.assertTrue(resident_account.name)
		self.assertEqual(resident_account.company, property_account.company)
		self.assertEqual(flt(resident_account.available_credit), 1500.0)  # 2000 - 500
		self.assertEqual(flt(resident_account.credit_utilization_percentage), 25.0)  # (500/2000)*100
		self.assertEqual(flt(resident_account.pending_charges), 500.0)  # negative balance
		self.assertIn("Familiar", resident_account.transaction_summary)

	def test_layer_4_api_methods_and_permissions(self):
		"""LAYER 4: API methods y permissions enforcement"""
		# Setup
		property_account = self.create_test_property_account()
		resident_account = frappe.get_doc(
			{
				"doctype": "Resident Account",
				"property_account": property_account.name,
				"resident_name": "Ana Torres",
				"resident_type": "Propietario",
				"current_balance": 2000.0,  # Saldo positivo
				"credit_limit": 5000.0,
				"spending_limits": 1500.0,
				"approval_required_amount": 3000.0,
			}
		)
		resident_account.insert(ignore_permissions=True)

		# Test 1: add_transaction method - payment (positive)
		result = resident_account.add_transaction(
			amount=500.0, transaction_type="Pago", description="Pago recibido"
		)

		self.assertTrue(result["success"])
		self.assertEqual(flt(result["old_balance"]), 2000.0)
		self.assertEqual(flt(result["new_balance"]), 2500.0)
		self.assertEqual(flt(result["transaction_amount"]), 500.0)

		# Test 2: add_transaction method - charge (negative) within limits
		result = resident_account.add_transaction(
			amount=-800.0, transaction_type="Cargo", description="Consumo servicios"
		)

		self.assertTrue(result["success"])
		self.assertEqual(flt(result["old_balance"]), 2500.0)
		self.assertEqual(flt(result["new_balance"]), 1700.0)
		self.assertEqual(flt(result["transaction_amount"]), -800.0)

		# Test 3: transfer_to_property_account method
		transfer_result = resident_account.transfer_to_property_account(
			amount=1000.0, description="Transferencia a cuenta principal"
		)

		self.assertTrue(transfer_result["success"])
		self.assertEqual(flt(transfer_result["transferred_amount"]), 1000.0)
		self.assertEqual(flt(transfer_result["remaining_balance"]), 700.0)
		self.assertEqual(transfer_result["property_account"], property_account.name)

		# Test 4: get_spending_summary method
		summary = resident_account.get_spending_summary(period_days=30)

		self.assertEqual(summary["period_days"], 30)
		self.assertEqual(flt(summary["current_balance"]), 700.0)
		self.assertEqual(summary["account_status"], "Activa")
		self.assertIn("last_transaction", summary)

		# Test 5: request_credit_increase method
		credit_request = resident_account.request_credit_increase(
			requested_amount=7000.0, justification="Mayor capacidad de consumo"
		)

		self.assertTrue(credit_request["success"])
		self.assertEqual(flt(credit_request["current_limit"]), 5000.0)
		self.assertEqual(flt(credit_request["requested_limit"]), 7000.0)
		self.assertEqual(credit_request["status"], "Pendiente aprobación")

	def test_validation_errors(self):
		"""Test validation errors específicos"""
		# Test 1: Property Account obligatoria
		doc = frappe.new_doc("Resident Account")
		doc.resident_name = "Test User"

		with self.assertRaises(frappe.ValidationError):
			doc.validate_property_account()

		# Test 2: Nombre residente muy corto
		doc.property_account = "TEST-PROP"
		doc.resident_name = "A"  # Muy corto

		with patch("frappe.get_doc") as mock_get_doc:
			mock_property = MagicMock()
			mock_property.account_status = "Activa"
			mock_property.company = "TEST COMPANY"
			mock_get_doc.return_value = mock_property

			with self.assertRaises(frappe.ValidationError):
				doc.validate_resident_data()

		# Test 3: Tipo de residente inválido
		doc.resident_name = "Valid Name"
		doc.resident_type = "Tipo Inválido"

		with self.assertRaises(frappe.ValidationError):
			doc.validate_resident_data()

		# Test 4: Límite de crédito negativo
		doc.resident_type = "Propietario"
		doc.credit_limit = -1000.0

		with self.assertRaises(frappe.ValidationError):
			doc.validate_financial_limits()

	def test_spending_limits_enforcement(self):
		"""Test enforcement de límites de gastos"""
		# Setup
		property_account = self.create_test_property_account()
		resident_account = frappe.get_doc(
			{
				"doctype": "Resident Account",
				"property_account": property_account.name,
				"resident_name": "Test Limits",
				"resident_type": "Huésped",
				"current_balance": 0.0,
				"credit_limit": 1000.0,
				"spending_limits": 500.0,  # Límite diario
				"approval_required_amount": 800.0,
			}
		)
		resident_account.insert(ignore_permissions=True)

		# Test 1: Cargo que excede límite diario
		with self.assertRaises(frappe.ValidationError):
			resident_account.add_transaction(
				amount=-600.0,  # Excede 500 límite
				transaction_type="Cargo",
				description="Excede límite",
			)

		# Test 2: Cargo que requiere aprobación
		with self.assertRaises(frappe.ValidationError):
			resident_account.add_transaction(
				amount=-900.0,  # Excede 800 approval limit
				transaction_type="Cargo",
				description="Requiere aprobación",
			)

		# Test 3: Cargo que excede límite de crédito
		resident_account.current_balance = -800.0  # Ya debe 800
		resident_account.save()

		with self.assertRaises(frappe.ValidationError):
			resident_account.add_transaction(
				amount=-300.0,  # Total sería -1100, excede 1000 credit limit
				transaction_type="Cargo",
				description="Excede crédito",
			)

	def test_credit_calculations(self):
		"""Test cálculos de crédito específicos"""
		doc = frappe.new_doc("Resident Account")
		doc.credit_limit = 2000.0

		# Test 1: Saldo positivo (no usa crédito)
		doc.current_balance = 500.0
		doc.calculate_credit_metrics()

		self.assertEqual(flt(doc.available_credit), 2000.0)
		self.assertEqual(flt(doc.credit_utilization_percentage), 0.0)
		self.assertEqual(flt(doc.pending_charges), 0.0)

		# Test 2: Saldo negativo (usa crédito)
		doc.current_balance = -800.0
		doc.calculate_credit_metrics()

		self.assertEqual(flt(doc.available_credit), 1200.0)  # 2000 - 800
		self.assertEqual(flt(doc.credit_utilization_percentage), 40.0)  # (800/2000)*100
		self.assertEqual(flt(doc.pending_charges), 800.0)

		# Test 3: Sin límite de crédito
		doc.credit_limit = 0
		doc.calculate_credit_metrics()

		self.assertEqual(flt(doc.available_credit), 0.0)
		self.assertEqual(flt(doc.credit_utilization_percentage), 0.0)

	def test_account_code_generation(self):
		"""Test generación de código de cuenta"""
		with patch("frappe.get_doc") as mock_get_doc, patch("frappe.db.count") as mock_count:
			# Mock Property Account
			mock_property = MagicMock()
			mock_property.account_name = "TORRE-A-101"
			mock_get_doc.return_value = mock_property

			# Mock count (first resident)
			mock_count.return_value = 0

			doc = frappe.new_doc("Resident Account")
			doc.property_account = "TORRE-A-101"
			doc.resident_name = "Juan Carlos Pérez"

			doc.generate_account_code()

			# Verify code generation pattern
			expected_code = "TORRE-A-101-RES01-JC"
			self.assertEqual(doc.account_code, expected_code)

			# Test second resident
			mock_count.return_value = 1
			doc2 = frappe.new_doc("Resident Account")
			doc2.property_account = "TORRE-A-101"
			doc2.resident_name = "María Elena García"

			doc2.generate_account_code()

			expected_code2 = "TORRE-A-101-RES02-ME"
			self.assertEqual(doc2.account_code, expected_code2)

	def test_loyalty_points_calculation(self):
		"""Test cálculo de puntos de lealtad"""
		doc = frappe.new_doc("Resident Account")

		# Test 1: Saldo positivo genera puntos
		doc.current_balance = 1500.0
		doc.calculate_loyalty_points()

		self.assertEqual(doc.loyalty_points, 15)  # 1500/100 = 15

		# Test 2: Saldo negativo no genera puntos
		doc.current_balance = -500.0
		doc.calculate_loyalty_points()

		self.assertEqual(doc.loyalty_points, 0)

		# Test 3: Saldo exacto múltiplo de 100
		doc.current_balance = 1000.0
		doc.calculate_loyalty_points()

		self.assertEqual(doc.loyalty_points, 10)

	def test_default_values_by_resident_type(self):
		"""Test valores por defecto según tipo de residente"""
		doc = frappe.new_doc("Resident Account")

		# Test Propietario
		doc.resident_type = "Propietario"
		doc.set_default_values()

		self.assertEqual(flt(doc.spending_limits), 5000.0)
		self.assertEqual(flt(doc.approval_required_amount), 10000.0)

		# Test Huésped
		doc = frappe.new_doc("Resident Account")
		doc.resident_type = "Huésped"
		doc.set_default_values()

		self.assertEqual(flt(doc.spending_limits), 500.0)
		self.assertEqual(flt(doc.approval_required_amount), 1000.0)

		# Test Empleado Doméstico
		doc = frappe.new_doc("Resident Account")
		doc.resident_type = "Empleado Doméstico"
		doc.set_default_values()

		self.assertEqual(flt(doc.spending_limits), 200.0)
		self.assertEqual(flt(doc.approval_required_amount), 500.0)

	def test_diagnostic_hooks_field_validation(self):
		"""DIAGNOSTIC: Verificar fields disponibles para hooks"""
		doc = frappe.new_doc("Resident Account")

		# Campos críticos para hooks
		critical_fields = [
			"account_code",
			"resident_name",
			"property_account",
			"company",
			"resident_type",
			"account_status",
			"current_balance",
			"credit_limit",
			"available_credit",
			"credit_utilization_percentage",
			"spending_limits",
			"approval_required_amount",
			"last_transaction_date",
			"last_transaction_amount",
		]

		for field in critical_fields:
			self.assertTrue(hasattr(doc, field), f"Field '{field}' not found in Resident Account")

		# Verificar que campos computed se pueden calcular
		doc.current_balance = 1000.0
		doc.credit_limit = 2000.0
		doc.calculate_credit_metrics()

		self.assertTrue(hasattr(doc, "available_credit"))
		self.assertTrue(hasattr(doc, "credit_utilization_percentage"))
		self.assertTrue(hasattr(doc, "pending_charges"))
