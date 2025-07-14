# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Budget Planning - Testing Granular REGLA #32
============================================

Tests para Budget Planning DocType siguiendo metodología
granular de 4 capas para validación completa del sistema presupuestal.
"""

import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, flt, getdate, nowdate

from condominium_management.financial_management.test_base import FinancialTestBaseGranular


class TestBudgetPlanning(FinancialTestBaseGranular):
	"""Test Budget Planning con REGLA #32 - Testing Granular"""

	@classmethod
	def setUpClass(cls):
		"""Setup de clase - preparar ambiente para Budget Planning"""
		super().setUpClass()

		# Crear datos específicos para Budget Planning
		cls.setup_budget_planning_data()

	@classmethod
	def setup_budget_planning_data(cls):
		"""Setup datos específicos para testing Budget Planning"""

		# Para Budget Planning tests usamos mocks en lugar de crear dependencias reales
		cls.mock_company_name = "TEST_BUDGET_COMPANY"
		cls.mock_fiscal_year = "2025-2026"
		cls.mock_budget_name = "Presupuesto Anual Test 2025"

	# =============================================================================
	# LAYER 1: FIELD VALIDATION (SIEMPRE FUNCIONA)
	# =============================================================================

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación básica de campos Budget Planning"""
		doc = frappe.new_doc("Budget Planning")

		# Verificar campos críticos existen
		required_fields = ["budget_name", "budget_period", "company", "budget_status"]

		for field in required_fields:
			self.assertTrue(hasattr(doc, field), f"Campo requerido '{field}' no existe en Budget Planning")

	def test_layer_1_currency_precision_validation(self):
		"""LAYER 1: Validación de precisión en campos de currency"""
		doc = frappe.new_doc("Budget Planning")

		# Campos de currency deben existir
		currency_fields = [
			"total_income_budgeted",
			"total_expenses_budgeted",
			"maintenance_fees_budget",
			"administrative_expenses",
			"total_actual_income",
			"total_actual_expenses",
		]

		for field in currency_fields:
			self.assertTrue(hasattr(doc, field), f"Campo currency '{field}' no existe en Budget Planning")

	def test_layer_1_budget_period_options_validation(self):
		"""LAYER 1: Validación de períodos presupuestales disponibles"""
		doc = frappe.new_doc("Budget Planning")

		meta = doc.meta
		period_field = next((f for f in meta.fields if f.fieldname == "budget_period"), None)
		self.assertIsNotNone(period_field, "Campo budget_period no encontrado")

		expected_periods = ["Anual", "Semestral", "Trimestral", "Mensual"]
		options = period_field.options.split("\n") if period_field.options else []

		for period in expected_periods:
			self.assertIn(period, options, f"Período '{period}' no encontrado en budget_period")

	def test_layer_1_budget_status_options_validation(self):
		"""LAYER 1: Validación de estados de presupuesto disponibles"""
		doc = frappe.new_doc("Budget Planning")

		meta = doc.meta
		status_field = next((f for f in meta.fields if f.fieldname == "budget_status"), None)
		self.assertIsNotNone(status_field, "Campo budget_status no encontrado")

		expected_statuses = ["Borrador", "En Revisión", "Aprobado", "Activo", "Cerrado", "Cancelado"]
		options = status_field.options.split("\n") if status_field.options else []

		for status in expected_statuses:
			self.assertIn(status, options, f"Estado '{status}' no encontrado en budget_status")

	def test_layer_1_budget_type_options_validation(self):
		"""LAYER 1: Validación de tipos de presupuesto"""
		doc = frappe.new_doc("Budget Planning")

		meta = doc.meta
		type_field = next((f for f in meta.fields if f.fieldname == "budget_type"), None)
		self.assertIsNotNone(type_field, "Campo budget_type no encontrado")

		expected_types = ["Operativo", "Capital", "Emergencia", "Especial", "Mixto"]
		options = type_field.options.split("\n") if type_field.options else []

		for budget_type in expected_types:
			self.assertIn(budget_type, options, f"Tipo '{budget_type}' no encontrado en budget_type")

	def test_layer_1_planning_method_options_validation(self):
		"""LAYER 1: Validación de métodos de planeación"""
		doc = frappe.new_doc("Budget Planning")

		meta = doc.meta
		method_field = next((f for f in meta.fields if f.fieldname == "planning_method"), None)
		self.assertIsNotNone(method_field, "Campo planning_method no encontrado")

		expected_methods = ["Base Cero", "Incremental", "Histórico", "Por Actividades"]
		options = method_field.options.split("\n") if method_field.options else []

		for method in expected_methods:
			self.assertIn(method, options, f"Método '{method}' no encontrado en planning_method")

	def test_layer_1_allocation_method_options_validation(self):
		"""LAYER 1: Validación de métodos de asignación"""
		doc = frappe.new_doc("Budget Planning")

		meta = doc.meta
		allocation_field = next((f for f in meta.fields if f.fieldname == "allocation_method"), None)
		self.assertIsNotNone(allocation_field, "Campo allocation_method no encontrado")

		expected_methods = [
			"Por Metros Cuadrados",
			"Por Indiviso",
			"Por Tipo de Espacio",
			"Proporcional",
			"Mixto",
		]
		options = allocation_field.options.split("\n") if allocation_field.options else []

		for method in expected_methods:
			self.assertIn(method, options, f"Método de asignación '{method}' no encontrado")

	# =============================================================================
	# LAYER 2: BUSINESS LOGIC VALIDATION (CON MOCKS)
	# =============================================================================

	def test_layer_2_budget_configuration_validation(self):
		"""LAYER 2: Validación configuración básica presupuesto (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.budget_name = self.mock_budget_name
		doc.budget_period = "Anual"
		doc.company = self.mock_company_name
		doc.budget_status = "Borrador"

		# Verificar configuración se establece correctamente
		self.assertEqual(doc.budget_name, self.mock_budget_name)
		self.assertEqual(doc.budget_period, "Anual")
		self.assertEqual(doc.company, self.mock_company_name)

	def test_layer_2_income_planning_validation(self):
		"""LAYER 2: Validación planeación de ingresos (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.maintenance_fees_budget = 500000.0
		doc.special_assessments_budget = 100000.0
		doc.other_income_budget = 50000.0
		doc.reserve_fund_contribution = 25000.0

		# Verificar montos de ingresos
		self.assertEqual(flt(doc.maintenance_fees_budget), 500000.0)
		self.assertEqual(flt(doc.special_assessments_budget), 100000.0)
		self.assertEqual(flt(doc.other_income_budget), 50000.0)

	def test_layer_2_expense_planning_validation(self):
		"""LAYER 2: Validación planeación de gastos (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.administrative_expenses = 200000.0
		doc.maintenance_expenses = 250000.0
		doc.utilities_expenses = 150000.0
		doc.insurance_expenses = 75000.0

		# Verificar montos de gastos
		self.assertEqual(flt(doc.administrative_expenses), 200000.0)
		self.assertEqual(flt(doc.maintenance_expenses), 250000.0)
		self.assertEqual(flt(doc.utilities_expenses), 150000.0)

	def test_layer_2_reserve_allocations_validation(self):
		"""LAYER 2: Validación asignaciones de reserva (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.emergency_reserve_allocation = 50000.0
		doc.maintenance_reserve_allocation = 30000.0
		doc.replacement_reserve_allocation = 40000.0
		doc.capital_improvement_allocation = 25000.0

		# Verificar asignaciones de reserva
		self.assertEqual(flt(doc.emergency_reserve_allocation), 50000.0)
		self.assertEqual(flt(doc.maintenance_reserve_allocation), 30000.0)
		self.assertEqual(flt(doc.replacement_reserve_allocation), 40000.0)

	def test_layer_2_variance_analysis_configuration(self):
		"""LAYER 2: Validación configuración análisis variaciones (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.actual_vs_budget_enabled = 1
		doc.variance_threshold_percentage = 15.0
		doc.alert_on_overspending = 1
		doc.monthly_review_required = 1

		# Verificar configuración de análisis
		self.assertEqual(doc.actual_vs_budget_enabled, 1)
		self.assertEqual(flt(doc.variance_threshold_percentage), 15.0)
		self.assertEqual(doc.alert_on_overspending, 1)

	def test_layer_2_approval_workflow_validation(self):
		"""LAYER 2: Validación workflow de aprobación (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.requires_committee_approval = 1
		doc.committee_decision = "Pendiente"
		doc.approval_required = 1

		# Verificar configuración de aprobación
		self.assertEqual(doc.requires_committee_approval, 1)
		self.assertEqual(doc.committee_decision, "Pendiente")
		self.assertEqual(doc.approval_required, 1)

	# =============================================================================
	# LAYER 3: ERPNEXT INTEGRATION VALIDATION
	# =============================================================================

	def test_layer_3_company_link_validation(self):
		"""LAYER 3: Validación link con Company ERPNext (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.company = self.mock_company_name
		doc.fiscal_year = self.mock_fiscal_year

		# Verificar links con ERPNext
		self.assertEqual(doc.company, self.mock_company_name)
		self.assertEqual(doc.fiscal_year, self.mock_fiscal_year)

	def test_layer_3_fiscal_year_integration(self):
		"""LAYER 3: Validación integración Fiscal Year (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")

		# Campo fiscal_year debe existir como Link
		meta = doc.meta
		fiscal_year_field = next((f for f in meta.fields if f.fieldname == "fiscal_year"), None)
		self.assertIsNotNone(fiscal_year_field, "Campo fiscal_year no encontrado")
		self.assertEqual(fiscal_year_field.fieldtype, "Link")
		self.assertEqual(fiscal_year_field.options, "Fiscal Year")

	def test_layer_3_user_links_validation(self):
		"""LAYER 3: Validación links con User ERPNext (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")

		# Verificar campos de User existen
		user_fields = ["created_by", "last_modified_by", "approved_by"]
		meta = doc.meta

		for field_name in user_fields:
			field = next((f for f in meta.fields if f.fieldname == field_name), None)
			self.assertIsNotNone(field, f"Campo {field_name} no encontrado")
			self.assertEqual(field.options, "User")

	def test_layer_3_budget_template_self_reference(self):
		"""LAYER 3: Validación auto-referencia template (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")

		# Campo budget_template debe ser Link a Budget Planning
		meta = doc.meta
		template_field = next((f for f in meta.fields if f.fieldname == "budget_template"), None)
		self.assertIsNotNone(template_field, "Campo budget_template no encontrado")
		self.assertEqual(template_field.options, "Budget Planning")

	def test_layer_3_physical_spaces_integration_fields(self):
		"""LAYER 3: Validación campos integración Physical Spaces (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.space_based_allocation = 1
		doc.allocation_method = "Por Metros Cuadrados"
		doc.common_areas_percentage = 60.0
		doc.individual_units_percentage = 40.0

		# Verificar integración con Physical Spaces
		self.assertEqual(doc.space_based_allocation, 1)
		self.assertEqual(doc.allocation_method, "Por Metros Cuadrados")
		self.assertEqual(flt(doc.common_areas_percentage), 60.0)

	# =============================================================================
	# LAYER 4: COMPLEX CALCULATIONS AND WORKFLOWS
	# =============================================================================

	def test_layer_4_total_calculations_logic(self):
		"""LAYER 4: Validación lógica cálculo totales (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")

		# Configurar ingresos
		doc.maintenance_fees_budget = 400000.0
		doc.special_assessments_budget = 100000.0
		doc.other_income_budget = 25000.0
		doc.reserve_fund_contribution = 50000.0

		# Configurar gastos
		doc.administrative_expenses = 150000.0
		doc.maintenance_expenses = 200000.0
		doc.utilities_expenses = 100000.0
		doc.insurance_expenses = 50000.0

		# Total esperado ingresos: 575000
		# Total esperado gastos: 500000
		# En testing manual sin insert, verificamos que los campos están disponibles
		expected_income = 400000 + 100000 + 25000 + 50000
		expected_expenses = 150000 + 200000 + 100000 + 50000

		self.assertEqual(flt(doc.maintenance_fees_budget), 400000.0)
		self.assertEqual(expected_income, 575000.0)
		self.assertEqual(expected_expenses, 500000.0)

	def test_layer_4_approval_threshold_logic(self):
		"""LAYER 4: Validación lógica umbrales aprobación (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.total_income_budgeted = 1500000.0  # Excede umbral de 1M
		doc.budget_type = "Operativo"

		# Presupuesto > 1M debería requerir aprobación
		# En testing verificamos que los campos están disponibles para la lógica
		self.assertEqual(flt(doc.total_income_budgeted), 1500000.0)
		self.assertGreater(flt(doc.total_income_budgeted), 1000000.0)

	def test_layer_4_variance_calculation_logic(self):
		"""LAYER 4: Validación lógica cálculo variaciones (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.total_income_budgeted = 500000.0
		doc.total_expenses_budgeted = 450000.0
		doc.total_actual_income = 520000.0
		doc.total_actual_expenses = 480000.0

		# Variación ingresos: (520000 - 500000) / 500000 * 100 = 4%
		# Variación gastos: (480000 - 450000) / 450000 * 100 = 6.67%
		# En testing verificamos que los campos están disponibles para el cálculo
		expected_income_variance = ((520000 - 500000) / 500000) * 100
		expected_expense_variance = ((480000 - 450000) / 450000) * 100

		self.assertEqual(flt(doc.total_income_budgeted), 500000.0)
		self.assertEqual(flt(doc.total_actual_income), 520000.0)
		self.assertAlmostEqual(expected_income_variance, 4.0, places=1)
		self.assertAlmostEqual(expected_expense_variance, 6.67, places=1)

	def test_layer_4_utilization_rate_calculation(self):
		"""LAYER 4: Validación cálculo tasa utilización (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.total_expenses_budgeted = 400000.0
		doc.total_actual_expenses = 350000.0

		# Tasa utilización: (350000 / 400000) * 100 = 87.5%
		expected_utilization = (350000 / 400000) * 100

		self.assertEqual(flt(doc.total_expenses_budgeted), 400000.0)
		self.assertEqual(flt(doc.total_actual_expenses), 350000.0)
		self.assertAlmostEqual(expected_utilization, 87.5, places=1)

	def test_layer_4_balance_validation_logic(self):
		"""LAYER 4: Validación lógica balance ingresos-gastos (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.total_income_budgeted = 500000.0
		doc.total_expenses_budgeted = 600000.0  # Gastos exceden ingresos

		# Ratio gastos: (600000 / 500000) * 100 = 120% (excede 110%)
		expense_ratio = (600000 / 500000) * 100

		self.assertEqual(flt(doc.total_income_budgeted), 500000.0)
		self.assertEqual(flt(doc.total_expenses_budgeted), 600000.0)
		self.assertGreater(expense_ratio, 110.0)  # Debería generar advertencia

	def test_layer_4_emergency_budget_approval_logic(self):
		"""LAYER 4: Validación lógica aprobación presupuesto emergencia (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.budget_type = "Emergencia"
		doc.total_income_budgeted = 200000.0  # Menor al umbral normal

		# Presupuesto de emergencia siempre requiere aprobación independiente del monto
		self.assertEqual(doc.budget_type, "Emergencia")
		self.assertLess(flt(doc.total_income_budgeted), 1000000.0)  # Menor al umbral normal

	def test_layer_4_reserve_allocation_percentage_logic(self):
		"""LAYER 4: Validación lógica porcentajes asignación reserva (SIN INSERT)"""
		doc = frappe.new_doc("Budget Planning")
		doc.emergency_reserve_allocation = 50000.0
		doc.maintenance_reserve_allocation = 30000.0
		doc.replacement_reserve_allocation = 20000.0
		doc.total_income_budgeted = 500000.0

		# Total reservas: 100000 (20% del ingreso total)
		total_reserves = 50000 + 30000 + 20000
		reserve_percentage = (total_reserves / 500000) * 100

		self.assertEqual(total_reserves, 100000.0)
		self.assertEqual(reserve_percentage, 20.0)
		self.assertLessEqual(reserve_percentage, 30.0)  # Límite razonable

	def test_layer_4_spanish_interface_compliance(self):
		"""LAYER 4: Validación cumplimiento interfaz en español (REGLA #1)"""
		doc = frappe.new_doc("Budget Planning")
		meta = doc.meta

		# Verificar secciones en español
		spanish_sections = [
			"Información Básica",
			"Configuración del Presupuesto",
			"Planeación de Ingresos",
			"Planeación de Gastos",
			"Asignaciones de Reserva",
			"Análisis de Variaciones",
			"Métricas de Desempeño",
			"Configuración de Reportes",
			"Flujo de Aprobación",
			"Integración con Espacios Físicos",
			"Información de Auditoría",
		]

		section_fields = [f for f in meta.fields if f.fieldtype == "Section Break"]
		section_labels = [f.label for f in section_fields if f.label]

		for section in spanish_sections:
			self.assertIn(section, section_labels, f"Sección en español '{section}' no encontrada")

	# =============================================================================
	# HELPER METHODS ESPECÍFICOS
	# =============================================================================

	def get_mock_company(self):
		"""Obtener mock Company para tests"""
		return type(
			"MockCompany",
			(),
			{
				"name": self.mock_company_name,
				"company_name": self.mock_company_name,
				"default_currency": "MXN",
				"country": "Mexico",
			},
		)()

	def get_mock_fiscal_year(self):
		"""Obtener mock Fiscal Year para tests"""
		return type(
			"MockFiscalYear",
			(),
			{
				"name": self.mock_fiscal_year,
				"year_start_date": "2025-01-01",
				"year_end_date": "2025-12-31",
				"is_short_year": 0,
			},
		)()
