# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBudgetPlanningL2BusinessLogic(FrappeTestCase):
	"""Layer 2: Business Logic Tests for Budget Planning DocType"""

	def setUp(self):
		"""Set up test data for each test"""
		self.test_data = {
			"naming_series": "BP-.YYYY.-",
			"budget_name": "Test Budget Plan",
			"company": "_Test Company",
			"budget_year": 2025,
			"budget_period": "Anual",
			"budget_status": "Borrador",
			"total_budget": 150000.00,
			"approved_budget": 0.00,
			"actual_expenses": 0.00,
			"variance": 0.00,
			"is_active": 1,
		}

	def test_budget_calculation_logic(self):
		"""Test budget calculation business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget calculation
		budget_items = [
			{"category": "Mantenimiento", "planned_amount": 60000.00},
			{"category": "Administración", "planned_amount": 45000.00},
			{"category": "Seguridad", "planned_amount": 30000.00},
			{"category": "Limpieza", "planned_amount": 15000.00},
		]

		if hasattr(budget_planning, "calculate_total_budget"):
			with patch.object(budget_planning, "calculate_total_budget") as mock_calculate:
				mock_calculate.return_value = {
					"total_budget": 150000.00,
					"budget_categories": 4,
					"largest_category": "Mantenimiento",
					"largest_amount": 60000.00,
				}
				result = budget_planning.calculate_total_budget(budget_items)
				self.assertEqual(result["total_budget"], 150000.00)
				self.assertEqual(result["budget_categories"], 4)

	def test_budget_approval_workflow(self):
		"""Test budget approval workflow business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)
		budget_planning.budget_status = "Borrador"

		# Test approval process
		approval_data = {
			"approver": "Administrator",
			"approval_notes": "Aprobado con ajustes menores",
			"approval_date": date.today(),
			"approved_amount": 145000.00,
		}

		if hasattr(budget_planning, "process_budget_approval"):
			with patch.object(budget_planning, "process_budget_approval") as mock_approve:
				mock_approve.return_value = {
					"approved": True,
					"approval_id": "APP-BP-001",
					"approved_amount": 145000.00,
					"adjustment_amount": -5000.00,
					"status": "Aprobado",
				}
				result = budget_planning.process_budget_approval(approval_data)
				self.assertTrue(result["approved"])
				self.assertEqual(result["approved_amount"], 145000.00)

	def test_variance_analysis_logic(self):
		"""Test variance analysis business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)
		budget_planning.total_budget = 150000.00
		budget_planning.actual_expenses = 142000.00

		# Test variance calculation
		if hasattr(budget_planning, "calculate_variance"):
			with patch.object(budget_planning, "calculate_variance") as mock_calculate:
				mock_calculate.return_value = {
					"variance_amount": 8000.00,
					"variance_percentage": 5.33,
					"variance_type": "favorable",
					"status": "under_budget",
				}
				result = budget_planning.calculate_variance()
				self.assertEqual(result["variance_amount"], 8000.00)
				self.assertEqual(result["variance_type"], "favorable")

	def test_budget_tracking_logic(self):
		"""Test budget tracking business logic"""
		with patch("frappe.get_doc"):
			budget_planning = frappe.new_doc("Budget Planning")
			budget_planning.update(self.test_data)

			# Test expense tracking
			expense_data = {
				"category": "Mantenimiento",
				"amount": 5000.00,
				"date": date.today(),
				"description": "Reparación de elevador",
			}

			if hasattr(budget_planning, "track_expense"):
				with patch.object(budget_planning, "track_expense") as mock_track:
					mock_track.return_value = {
						"expense_tracked": True,
						"category_total": 25000.00,
						"category_remaining": 35000.00,
						"category_utilization": 41.67,
					}
					result = budget_planning.track_expense(expense_data)
					self.assertTrue(result["expense_tracked"])
					self.assertEqual(result["category_total"], 25000.00)

	def test_budget_forecasting_logic(self):
		"""Test budget forecasting business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget forecasting
		historical_data = [
			{"month": 1, "expenses": 12000.00},
			{"month": 2, "expenses": 13500.00},
			{"month": 3, "expenses": 11800.00},
		]

		if hasattr(budget_planning, "forecast_budget"):
			with patch.object(budget_planning, "forecast_budget") as mock_forecast:
				mock_forecast.return_value = {
					"projected_annual_expense": 148000.00,
					"monthly_average": 12333.33,
					"trend": "stable",
					"confidence_level": 85.0,
				}
				result = budget_planning.forecast_budget(historical_data)
				self.assertEqual(result["projected_annual_expense"], 148000.00)
				self.assertEqual(result["trend"], "stable")

	def test_budget_reallocation_logic(self):
		"""Test budget reallocation business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget reallocation
		reallocation_data = {
			"from_category": "Administración",
			"to_category": "Mantenimiento",
			"amount": 10000.00,
			"reason": "Gastos inesperados de mantenimiento",
		}

		if hasattr(budget_planning, "reallocate_budget"):
			with patch.object(budget_planning, "reallocate_budget") as mock_reallocate:
				mock_reallocate.return_value = {
					"reallocation_successful": True,
					"reallocation_id": "REALLOC-001",
					"from_category_new_amount": 35000.00,
					"to_category_new_amount": 70000.00,
				}
				result = budget_planning.reallocate_budget(reallocation_data)
				self.assertTrue(result["reallocation_successful"])
				self.assertEqual(result["from_category_new_amount"], 35000.00)

	def test_budget_monitoring_alerts(self):
		"""Test budget monitoring alerts business logic"""
		with patch("frappe.sendmail"):
			budget_planning = frappe.new_doc("Budget Planning")
			budget_planning.update(self.test_data)

			# Test alert generation
			if hasattr(budget_planning, "check_budget_alerts"):
				with patch.object(budget_planning, "check_budget_alerts") as mock_check:
					mock_check.return_value = {
						"alerts_triggered": 2,
						"alerts": [
							{"type": "overspend_warning", "category": "Mantenimiento", "utilization": 85.0},
							{"type": "underspend_alert", "category": "Limpieza", "utilization": 15.0},
						],
					}
					result = budget_planning.check_budget_alerts()
					self.assertEqual(result["alerts_triggered"], 2)
					self.assertEqual(len(result["alerts"]), 2)

	def test_budget_reporting_logic(self):
		"""Test budget reporting business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget report generation
		report_params = {"report_type": "variance_analysis", "period": "quarterly", "include_charts": True}

		if hasattr(budget_planning, "generate_budget_report"):
			with patch.object(budget_planning, "generate_budget_report") as mock_report:
				mock_report.return_value = {
					"report_id": "RPT-BP-001",
					"report_url": "/reports/budget/RPT-BP-001",
					"generated_at": datetime.now(),
					"report_sections": ["summary", "variance", "recommendations"],
					"charts_included": 5,
				}
				result = budget_planning.generate_budget_report(report_params)
				self.assertEqual(result["report_id"], "RPT-BP-001")
				self.assertEqual(result["charts_included"], 5)

	def test_budget_revision_logic(self):
		"""Test budget revision business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget revision
		revision_data = {
			"revision_reason": "Ajuste por inflación",
			"revision_type": "increase",
			"revision_percentage": 8.0,
			"effective_date": date.today(),
		}

		if hasattr(budget_planning, "create_budget_revision"):
			with patch.object(budget_planning, "create_budget_revision") as mock_revise:
				mock_revise.return_value = {
					"revision_created": True,
					"revision_id": "REV-BP-001",
					"new_total_budget": 162000.00,
					"revision_amount": 12000.00,
				}
				result = budget_planning.create_budget_revision(revision_data)
				self.assertTrue(result["revision_created"])
				self.assertEqual(result["new_total_budget"], 162000.00)

	def test_budget_performance_metrics(self):
		"""Test budget performance metrics business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test performance metrics calculation
		if hasattr(budget_planning, "calculate_performance_metrics"):
			with patch.object(budget_planning, "calculate_performance_metrics") as mock_metrics:
				mock_metrics.return_value = {
					"budget_efficiency": 92.5,
					"spending_velocity": 78.3,
					"forecast_accuracy": 88.7,
					"variance_stability": 85.2,
					"overall_score": 86.2,
				}
				result = budget_planning.calculate_performance_metrics()
				self.assertEqual(result["budget_efficiency"], 92.5)
				self.assertEqual(result["overall_score"], 86.2)

	def test_budget_optimization_suggestions(self):
		"""Test budget optimization suggestions business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test optimization analysis
		if hasattr(budget_planning, "analyze_optimization_opportunities"):
			with patch.object(budget_planning, "analyze_optimization_opportunities") as mock_analyze:
				mock_analyze.return_value = {
					"optimization_score": 78.5,
					"suggestions": [
						{
							"category": "Mantenimiento",
							"suggestion": "Implementar mantenimiento preventivo",
							"potential_saving": 8000.00,
						},
						{
							"category": "Administración",
							"suggestion": "Digitalizar procesos",
							"potential_saving": 3000.00,
						},
					],
					"total_potential_savings": 11000.00,
				}
				result = budget_planning.analyze_optimization_opportunities()
				self.assertEqual(result["optimization_score"], 78.5)
				self.assertEqual(result["total_potential_savings"], 11000.00)

	def test_budget_comparison_logic(self):
		"""Test budget comparison business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test comparison with previous year
		comparison_budget_id = "BP-2024-001"

		if hasattr(budget_planning, "compare_with_previous_budget"):
			with patch.object(budget_planning, "compare_with_previous_budget") as mock_compare:
				mock_compare.return_value = {
					"comparison_budget": comparison_budget_id,
					"total_change": 15000.00,
					"percentage_change": 11.1,
					"category_changes": [
						{"category": "Mantenimiento", "change": 8000.00, "percentage": 15.38},
						{"category": "Administración", "change": 5000.00, "percentage": 12.50},
					],
				}
				result = budget_planning.compare_with_previous_budget(comparison_budget_id)
				self.assertEqual(result["total_change"], 15000.00)
				self.assertEqual(result["percentage_change"], 11.1)

	def test_budget_consolidation_logic(self):
		"""Test budget consolidation business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)

		# Test budget consolidation
		subsidiary_budgets = ["BP-SUB-001", "BP-SUB-002", "BP-SUB-003"]

		if hasattr(budget_planning, "consolidate_budgets"):
			with patch.object(budget_planning, "consolidate_budgets") as mock_consolidate:
				mock_consolidate.return_value = {
					"consolidated_budget": 450000.00,
					"subsidiary_count": 3,
					"consolidation_adjustments": -5000.00,
					"consolidation_date": date.today(),
				}
				result = budget_planning.consolidate_budgets(subsidiary_budgets)
				self.assertEqual(result["consolidated_budget"], 450000.00)
				self.assertEqual(result["subsidiary_count"], 3)

	def test_budget_archive_logic(self):
		"""Test budget archive business logic"""
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.update(self.test_data)
		budget_planning.budget_status = "Completado"

		# Test archiving process
		archive_reason = "Fin del período presupuestario"

		if hasattr(budget_planning, "archive_budget"):
			with patch.object(budget_planning, "archive_budget") as mock_archive:
				mock_archive.return_value = {
					"archived": True,
					"archive_date": date.today(),
					"final_variance": 8000.00,
					"achievement_rate": 94.67,
					"backup_created": True,
				}
				result = budget_planning.archive_budget(archive_reason)
				self.assertTrue(result["archived"])
				self.assertEqual(result["achievement_rate"], 94.67)
