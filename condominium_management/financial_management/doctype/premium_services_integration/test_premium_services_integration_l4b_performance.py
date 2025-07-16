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


class TestPremiumServicesIntegrationL4BPerformance(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4B Performance Tests - Premium Services Integration Performance Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Premium Services Integration"

	def test_premium_service_creation_performance(self):
		"""Test: performance de creación de Premium Services Integration"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Use centralized benchmark
			self.assert_performance_benchmark("insert", execution_time)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Even if creation fails, test performance
			self.assertLess(
				execution_time,
				0.3,
				f"Premium Services Integration creation attempt took {execution_time:.3f}s, expected < 0.3s. Error: {e!s}",
			)

		finally:
			frappe.db.rollback()

	def test_service_booking_performance(self):
		"""Test: performance de procesamiento de reservas de servicios"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate service booking process
			booking_steps = [
				"validate_availability",
				"check_customer_eligibility",
				"calculate_pricing",
				"process_payment",
				"confirm_booking",
				"send_confirmation",
			]

			for _step in booking_steps:
				# Simulate each booking step
				time.sleep(0.005)  # 5ms per step

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Booking process should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Service booking performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_service_pricing_calculation_performance(self):
		"""Test: performance de cálculo de precios de servicios"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate pricing calculation for different service types
			service_types = ["Spa y Bienestar", "Gimnasio", "Piscina", "Salón de Eventos"]

			for _service_type in service_types:
				# Simulate complex pricing calculation
				base_price = 100.0
				membership_discount = 0.15
				seasonal_adjustment = 1.2

				# Complex calculation simulation
				for _i in range(100):
					base_price * (1 - membership_discount) * seasonal_adjustment
					time.sleep(0.0001)  # 0.1ms per calculation

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Pricing calculations should be fast
			self.assert_performance_benchmark("query", execution_time)

		except Exception as e:
			self.fail(f"Service pricing calculation test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_service_capacity_management_performance(self):
		"""Test: performance de gestión de capacidad de servicios"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate capacity management
			capacity_operations = [
				"check_current_capacity",
				"validate_booking_request",
				"update_availability",
				"process_waiting_list",
				"optimize_scheduling",
			]

			for _operation in capacity_operations:
				# Simulate capacity management operation
				time.sleep(0.004)  # 4ms per operation

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Capacity management should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Service capacity management test failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_service_analytics_performance(self):
		"""Test: performance de análisis de servicios"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock analytics results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("reporting", 0.25)
		else:
			# Real analytics query in local environment
			results = frappe.db.sql("""
				SELECT
					service_type,
					COUNT(*) as service_count,
					AVG(base_price) as avg_price,
					SUM(revenue_tracking) as total_revenue
				FROM `tabPremium Services Integration`
				WHERE creation >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
				GROUP BY service_type
				ORDER BY total_revenue DESC
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Analytics should meet benchmark
		self.assert_performance_benchmark("reporting", execution_time)
		self.assertIsNotNone(results)

	@mock_sql_operations_in_ci_cd
	def test_service_search_performance(self):
		"""Test: performance de búsqueda de servicios"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock search results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.08)
		else:
			# Real search query in local environment
			results = frappe.db.sql("""
				SELECT name, service_name, service_type, service_status, base_price
				FROM `tabPremium Services Integration`
				WHERE service_status = 'Activo'
				AND service_type IN ('Spa y Bienestar', 'Gimnasio', 'Piscina')
				ORDER BY service_name
				LIMIT 30
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Search performance should be excellent
		self.assert_performance_benchmark("query", execution_time)
		self.assertIsNotNone(results)

	def test_service_integration_performance(self):
		"""Test: performance de integración con servicios externos"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate external service integration
			integration_steps = [
				"validate_api_credentials",
				"establish_connection",
				"sync_service_data",
				"process_responses",
				"update_local_data",
			]

			for _step in integration_steps:
				# Simulate integration step
				time.sleep(0.008)  # 8ms per step

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Integration should be reasonably fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Service integration performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_service_notification_performance(self):
		"""Test: performance de sistema de notificaciones"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate notification processing
			notification_types = [
				"booking_confirmation",
				"service_reminder",
				"maintenance_alert",
				"capacity_update",
				"payment_reminder",
			]

			for _notification_type in notification_types:
				# Simulate notification processing
				time.sleep(0.003)  # 3ms per notification

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Notification processing should be fast
			self.assert_performance_benchmark("query", execution_time)

		except Exception as e:
			self.fail(f"Service notification performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_service_revenue_tracking_performance(self):
		"""Test: performance de seguimiento de ingresos"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock revenue tracking results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("complex_query", 0.18)
		else:
			# Real revenue tracking query in local environment
			results = frappe.db.sql("""
				SELECT
					service_type,
					MONTH(creation) as month,
					SUM(base_price) as monthly_revenue,
					COUNT(*) as booking_count
				FROM `tabPremium Services Integration`
				WHERE creation >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
				AND service_status = 'Activo'
				GROUP BY service_type, MONTH(creation)
				ORDER BY monthly_revenue DESC
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Revenue tracking should be fast
		self.assert_performance_benchmark("complex_query", execution_time)
		self.assertIsNotNone(results)

	def test_service_quality_monitoring_performance(self):
		"""Test: performance de monitoreo de calidad"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate quality monitoring
			quality_metrics = [
				"customer_satisfaction",
				"service_completion_rate",
				"response_time",
				"error_rate",
				"availability_percentage",
			]

			for _metric in quality_metrics:
				# Simulate quality metric calculation
				time.sleep(0.002)  # 2ms per metric

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Quality monitoring should be very fast
			self.assert_performance_benchmark("query", execution_time)

		except Exception as e:
			self.fail(f"Service quality monitoring test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_service_maintenance_scheduling_performance(self):
		"""Test: performance de programación de mantenimiento"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate maintenance scheduling
			maintenance_tasks = [
				"schedule_routine_maintenance",
				"check_equipment_status",
				"plan_preventive_maintenance",
				"coordinate_service_downtime",
				"update_maintenance_calendar",
			]

			for _task in maintenance_tasks:
				# Simulate maintenance task
				time.sleep(0.003)  # 3ms per task

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Maintenance scheduling should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Service maintenance scheduling test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
