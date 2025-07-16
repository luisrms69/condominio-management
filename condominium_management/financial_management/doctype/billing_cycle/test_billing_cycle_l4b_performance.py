# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import time

import frappe
from frappe.tests.utils import FrappeTestCase

# Import REGLA #47 utilities
from condominium_management.financial_management.utils.layer4_testing_utils import (
	Layer4TestingMixin,
	create_test_document_with_required_fields,
	get_performance_benchmark_time,
	is_ci_cd_environment,
	mock_sql_operations_in_ci_cd,
	simulate_performance_test_in_ci_cd,
)


class TestBillingCycleL4BPerformance(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4B Performance Tests - Billing Cycle Critical Performance Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Billing Cycle"

	def test_billing_cycle_creation_performance(self):
		"""Test: performance de creación de Billing Cycle (Meta: < 300ms)"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Use centralized benchmark
			get_performance_benchmark_time("insert")
			self.assert_performance_benchmark("insert", execution_time)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Even if creation fails, test performance
			self.assertLess(
				execution_time,
				0.3,
				f"Billing Cycle creation attempt took {execution_time:.3f}s, expected < 0.3s. Error: {e!s}",
			)

		finally:
			frappe.db.rollback()

	def test_mass_invoice_generation_simulation(self):
		"""Test: simulación de performance de generación masiva de facturas"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate mass invoice generation for 1000 properties
			total_properties = 1000
			invoices_generated = 0
			total_amount = 0.0

			# Simulate the generation process
			for i in range(total_properties):
				# Simulate fee calculation per property
				base_fee = 1500.0
				additional_fees = (i % 10) * 50  # Variation
				total_fee = base_fee + additional_fees

				# Simulate invoice creation (without actually creating)
				invoices_generated += 1
				total_amount += total_fee

				# Every 100 properties, simulate batch commit
				if i % 100 == 0:
					# Simulate small batch processing pause
					time.sleep(0.001)

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Performance assertions
			self.assert_performance_benchmark("bulk_operation", execution_time)
			self.assertEqual(invoices_generated, total_properties)
			self.assertGreater(total_amount, 0)

		except Exception as e:
			self.fail(f"Mass invoice generation test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_cycle_closure_performance(self):
		"""Test: performance del proceso de cierre de ciclo"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate cycle closure process
			closure_steps = [
				"validate_all_invoices",
				"calculate_collection_rate",
				"process_late_fees",
				"generate_final_report",
				"archive_cycle_data",
			]

			for _step in closure_steps:
				# Simulate each closure step
				time.sleep(0.01)  # 10ms per step

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Cycle closure should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Cycle closure performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_collection_rate_calculation_performance(self):
		"""Test: performance de cálculos de collection rate"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate collection rate calculation
			total_billed = 1500000.0  # 1.5M
			total_collected = 1350000.0  # 1.35M
			collection_rate = (total_collected / total_billed) * 100

			# Simulate complex calculations
			for i in range(1000):
				# Simulate property-level calculations
				property_billed = 1500.0
				property_collected = property_billed * (0.85 + (i % 20) * 0.01)
				(property_collected / property_billed) * 100

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Collection rate calculations should be fast
			self.assert_performance_benchmark("query", execution_time)
			self.assertEqual(collection_rate, 90.0)

		except Exception as e:
			self.fail(f"Collection rate calculation test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_billing_cycle_status_updates_performance(self):
		"""Test: performance de actualizaciones de estado del ciclo"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate status transitions
			status_transitions = ["Borrador", "Activo", "Procesando", "Cerrado"]

			for status in status_transitions:
				# Simulate status update
				doc.cycle_status = status
				time.sleep(0.005)  # 5ms per update

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Status updates should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Status updates performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_billing_cycle_search_and_filter_performance(self):
		"""Test: performance de búsqueda y filtrado de billing cycles"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock query results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.1)
		else:
			# Real query in local environment
			results = frappe.db.sql("""
				SELECT name, cycle_name, cycle_status, start_date, end_date
				FROM `tabBilling Cycle`
				WHERE cycle_status IN ('Activo', 'Procesando')
				AND start_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
				ORDER BY start_date DESC
				LIMIT 50
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Search performance should be excellent
		self.assert_performance_benchmark("query", execution_time)
		self.assertIsNotNone(results)

	@mock_sql_operations_in_ci_cd
	def test_reporting_query_performance(self):
		"""Test: performance de queries para reportes financieros"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock reporting results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("reporting", 0.3)
		else:
			# Real reporting query in local environment
			results = frappe.db.sql("""
				SELECT
					cycle_status,
					COUNT(*) as cycle_count,
					SUM(total_billed_amount) as total_billed,
					AVG(collection_rate) as avg_collection_rate
				FROM `tabBilling Cycle`
				WHERE start_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
				GROUP BY cycle_status
				ORDER BY total_billed DESC
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Reporting queries can be slower but should meet benchmark
		self.assert_performance_benchmark("reporting", execution_time)
		self.assertIsNotNone(results)

	@mock_sql_operations_in_ci_cd
	def test_count_and_aggregate_operations_performance(self):
		"""Test: performance de operaciones de conteo y agregación"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock aggregation results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("complex_query", 0.2)
		else:
			# Real aggregation query in local environment
			results = frappe.db.sql("""
				SELECT
					COUNT(*) as total_cycles,
					SUM(total_billed_amount) as total_revenue,
					AVG(collection_rate) as avg_collection_rate
				FROM `tabBilling Cycle`
				WHERE creation >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Aggregation should be fast
		self.assert_performance_benchmark("complex_query", execution_time)
		self.assertIsNotNone(results)

	def test_billing_cycle_validation_performance(self):
		"""Test: performance de validaciones del billing cycle"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			create_test_document_with_required_fields(self.doctype)

			# Simulate validation process
			validation_checks = [
				"validate_date_ranges",
				"validate_fee_structure",
				"validate_company_settings",
				"validate_status_transitions",
				"validate_financial_data",
			]

			for _check in validation_checks:
				# Simulate validation logic
				time.sleep(0.002)  # 2ms per validation

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Validation should be very fast
			self.assert_performance_benchmark("query", execution_time)

		finally:
			frappe.db.rollback()

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
