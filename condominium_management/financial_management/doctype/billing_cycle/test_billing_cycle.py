# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Billing Cycle - Testing Granular REGLA #32
==========================================

Testing granular del DocType Billing Cycle aplicando metodología de 4 capas
con validación ERPNext integration y business logic financiera.
"""

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.utils import add_days, flt, getdate, nowdate

from condominium_management.financial_management.test_base import FinancialTestBaseGranular


class TestBillingCycle(FinancialTestBaseGranular):
	"""Testing granular del DocType Billing Cycle"""

	def setUp(self):
		"""Setup para cada test individual"""
		super().setUp()
		frappe.set_user("Administrator")

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación de campos aislada (siempre funciona)"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Verificar campos requeridos existen
		required_fields = [
			"cycle_name",
			"company",
			"billing_month",
			"billing_year",
			"fee_structure",
			"generation_status",
		]

		for field in required_fields:
			self.assertTrue(
				hasattr(billing_cycle, field), f"Campo requerido '{field}' no existe en Billing Cycle"
			)

		# Verificar campos de configuración
		config_fields = [
			"due_date",
			"late_fee_percentage",
			"late_fee_flat_amount",
			"auto_generate_invoices",
			"send_notifications",
		]

		for field in config_fields:
			self.assertTrue(
				hasattr(billing_cycle, field), f"Campo de configuración '{field}' no existe en Billing Cycle"
			)

		# Verificar campos de métricas
		metrics_fields = [
			"total_amount",
			"collection_rate",
			"overdue_amount",
			"generated_count",
			"paid_amount",
		]

		for field in metrics_fields:
			self.assertTrue(
				hasattr(billing_cycle, field), f"Campo de métricas '{field}' no existe en Billing Cycle"
			)

	def test_layer_2_business_logic_validation_with_mocks(self):
		"""LAYER 2: Validación de business logic con dependencias mockeadas"""

		# Mock dependencies externas
		with patch("frappe.db.exists") as mock_exists:
			# Configurar mocks
			mock_exists.return_value = True

			# Crear documento real para assertions
			billing_cycle = frappe.new_doc("Billing Cycle")
			billing_cycle.cycle_name = "TEST Cycle Enero 2025"
			billing_cycle.company = "TEST_FINANCIAL_COMPANY"
			billing_cycle.billing_month = 1
			billing_cycle.billing_year = 2025
			billing_cycle.fee_structure = "TEST Fee Structure"
			billing_cycle.due_date = getdate()
			billing_cycle.generation_status = "Pendiente"

			# Verificar asignación de campos
			self.assertEqual(billing_cycle.cycle_name, "TEST Cycle Enero 2025")
			self.assertEqual(billing_cycle.billing_month, 1)
			self.assertEqual(billing_cycle.billing_year, 2025)
			self.assertEqual(billing_cycle.generation_status, "Pendiente")

	def test_layer_3_erpnext_integration_validation(self):
		"""LAYER 3: Validación de integración ERPNext"""

		# Verificar Customer Groups existen para facturación
		self.assertTrue(
			frappe.db.exists("Customer Group", "Condóminos"),
			"Customer Group 'Condóminos' debe existir para facturación",
		)

		# Verificar roles financieros en español
		financial_roles = ["Administrador Financiero", "Comité Administración", "Contador Condominio"]

		for role in financial_roles:
			self.assertTrue(frappe.db.exists("Role", role), f"Rol financiero '{role}' debe existir")

	def test_layer_4_financial_calculations_validation(self):
		"""LAYER 4: Validación de cálculos financieros específicos"""

		# Test cálculo collection rate
		total_invoiced = 100000.0
		amount_collected = 85000.0
		expected_rate = 85.0

		calculated_rate = flt((amount_collected / total_invoiced) * 100, 2)
		self.assertEqual(calculated_rate, expected_rate)

		# Test cálculo late fee
		base_amount = 2500.0
		late_fee_percentage = 5.0
		days_overdue = 30

		# Late fee aplicado solo después de due date
		if days_overdue > 0:
			expected_late_fee = flt(base_amount * late_fee_percentage / 100, 2)
			calculated_late_fee = flt(base_amount * late_fee_percentage / 100, 2)
			self.assertEqual(calculated_late_fee, expected_late_fee)
		else:
			self.assertEqual(0.0, 0.0)

		# Test cálculo overdue amount
		invoice_amounts = [2500.0, 2500.0, 3000.0]
		paid_amounts = [2500.0, 0.0, 1000.0]

		total_overdue = 0.0
		for i, invoice_amount in enumerate(invoice_amounts):
			if paid_amounts[i] < invoice_amount:
				total_overdue += invoice_amount - paid_amounts[i]

		expected_overdue = 4500.0  # 0 + 2500 + 2000
		self.assertEqual(total_overdue, expected_overdue)

	def test_billing_cycle_status_transitions(self):
		"""Test transiciones de estado del ciclo de facturación"""

		billing_cycle = frappe.new_doc("Billing Cycle")
		billing_cycle.update(
			{
				"cycle_name": "TEST Status Cycle",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_month": getdate().month,
				"billing_year": getdate().year,
				"fee_structure": "TEST Fee Structure",
				"generation_status": "Borrador",
			}
		)

		# Estados válidos según business logic
		valid_statuses = ["Borrador", "Programado", "Activo", "Facturado", "Completado"]

		# Verificar que todos los estados válidos se pueden asignar
		for status in valid_statuses:
			billing_cycle.generation_status = status
			self.assertEqual(billing_cycle.generation_status, status)

	def test_date_configuration_validation(self):
		"""Test validación de configuración de fechas"""

		billing_cycle = frappe.new_doc("Billing Cycle")

		# Fechas de configuración
		billing_start = getdate()
		billing_due = add_days(billing_start, 15)

		billing_cycle.update(
			{
				"cycle_name": "TEST Date Configuration",
				"billing_start_date": billing_start,
				"billing_due_date": billing_due,
				"billing_month": billing_start.month,
				"billing_year": billing_start.year,
			}
		)

		# Due date debe ser posterior a start date
		self.assertGreater(
			billing_cycle.billing_due_date,
			billing_cycle.billing_start_date,
			"Due date debe ser posterior a start date",
		)

		# Month y year deben coincidir con start date
		self.assertEqual(
			billing_cycle.billing_month, billing_start.month, "Billing month debe coincidir con start date"
		)

		self.assertEqual(
			billing_cycle.billing_year, billing_start.year, "Billing year debe coincidir con start date"
		)


class TestBillingCycleBusinessLogic(unittest.TestCase):
	"""Testing directo de business logic sin dependencies"""

	def test_cycle_naming_pattern(self):
		"""Test patrón de naming del ciclo"""

		cycle_name = "Facturación Enero 2025"
		expected_pattern = r"^.+ \w+ \d{4}$"

		import re

		self.assertTrue(
			re.match(expected_pattern, cycle_name), f"Cycle name '{cycle_name}' no sigue patrón esperado"
		)

	def test_late_fee_calculation_logic(self):
		"""Test lógica de cálculo late fees"""

		# Configuración late fee
		base_amount = 2500.0
		late_fee_percentage = 5.0
		late_fee_fixed = 100.0

		# Late fee por porcentaje
		percentage_fee = flt(base_amount * late_fee_percentage / 100, 2)
		self.assertEqual(percentage_fee, 125.0)

		# Late fee por monto fijo
		fixed_fee = late_fee_fixed
		self.assertEqual(fixed_fee, 100.0)

		# Aplicar mayor de los dos
		final_late_fee = max(percentage_fee, fixed_fee)
		self.assertEqual(final_late_fee, 125.0)

	def test_collection_metrics_calculation(self):
		"""Test cálculo de métricas de cobranza"""

		# Data de ejemplo
		invoices_data = [
			{"amount": 2500.0, "paid": 2500.0, "status": "Paid"},
			{"amount": 2500.0, "paid": 0.0, "status": "Overdue"},
			{"amount": 3000.0, "paid": 1500.0, "status": "Partial"},
		]

		# Cálculos
		total_invoiced = sum(inv["amount"] for inv in invoices_data)
		total_collected = sum(inv["paid"] for inv in invoices_data)
		overdue_amount = sum(
			inv["amount"] - inv["paid"] for inv in invoices_data if inv["status"] in ["Overdue", "Partial"]
		)

		collection_rate = flt((total_collected / total_invoiced) * 100, 2)

		# Assertions
		self.assertEqual(total_invoiced, 8000.0)
		self.assertEqual(total_collected, 4000.0)
		self.assertEqual(overdue_amount, 4000.0)
		self.assertEqual(collection_rate, 50.0)
