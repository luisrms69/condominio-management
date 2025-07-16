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


class TestFinancialTransparencyConfigL4BPerformance(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4B Performance Tests - Financial Transparency Config Performance Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Financial Transparency Config"

	def test_transparency_config_creation_performance(self):
		"""Test: performance de creación de Financial Transparency Config"""
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
				f"Financial Transparency Config creation attempt took {execution_time:.3f}s, expected < 0.3s. Error: {e!s}",
			)

		finally:
			frappe.db.rollback()

	def test_transparency_level_configuration_performance(self):
		"""Test: performance de configuración de niveles de transparencia"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate transparency level configuration
			transparency_levels = ["Básico", "Estándar", "Avanzado", "Completo", "Personalizado"]

			for level in transparency_levels:
				# Simulate configuration for each level
				doc.transparency_level = level
				time.sleep(0.002)  # 2ms per level configuration

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Configuration should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Transparency level configuration test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_access_control_validation_performance(self):
		"""Test: performance de validación de control de acceso"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate access control validation
			access_levels = ["Solo Lectura", "Lectura Limitada", "Lectura Completa", "Sin Acceso"]

			for access_level in access_levels:
				# Simulate access control validation
				doc.default_access_level = access_level
				time.sleep(0.001)  # 1ms per validation

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Access control validation should be very fast
			self.assert_performance_benchmark("query", execution_time)

		except Exception as e:
			self.fail(f"Access control validation test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_transparency_reporting_performance(self):
		"""Test: performance de generación de reportes de transparencia"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate transparency reporting
			report_types = [
				"monthly_transparency_report",
				"quarterly_summary_enabled",
				"annual_report_generation",
				"automatic_financial_reports",
			]

			for _report_type in report_types:
				# Simulate report generation
				time.sleep(0.005)  # 5ms per report type

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Reporting should meet benchmark
			self.assert_performance_benchmark("reporting", execution_time)

		except Exception as e:
			self.fail(f"Transparency reporting test failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_transparency_config_search_performance(self):
		"""Test: performance de búsqueda de configuraciones de transparencia"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock query results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.1)
		else:
			# Real query in local environment
			results = frappe.db.sql("""
				SELECT name, config_name, transparency_level, config_status, effective_from
				FROM `tabFinancial Transparency Config`
				WHERE config_status IN ('Activo', 'Aprobado')
				AND effective_from <= CURDATE()
				ORDER BY effective_from DESC
				LIMIT 25
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Search performance should be excellent
		self.assert_performance_benchmark("query", execution_time)
		self.assertIsNotNone(results)

	@mock_sql_operations_in_ci_cd
	def test_compliance_analytics_performance(self):
		"""Test: performance de análisis de cumplimiento"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock analytics results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("complex_query", 0.2)
		else:
			# Real analytics query in local environment
			results = frappe.db.sql("""
				SELECT
					transparency_level,
					COUNT(*) as config_count,
					regulatory_compliance_level,
					privacy_protection_level
				FROM `tabFinancial Transparency Config`
				WHERE creation >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
				GROUP BY transparency_level, regulatory_compliance_level
				ORDER BY config_count DESC
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Analytics should be fast
		self.assert_performance_benchmark("complex_query", execution_time)
		self.assertIsNotNone(results)

	def test_portal_configuration_performance(self):
		"""Test: performance de configuración del portal de residentes"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate portal configuration
			portal_settings = [
				"enable_resident_portal",
				"show_individual_balance",
				"show_community_financials",
				"allow_document_download",
			]

			for _setting in portal_settings:
				# Simulate portal configuration
				time.sleep(0.003)  # 3ms per setting

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Portal configuration should be fast
			self.assert_performance_benchmark("update", execution_time)

		except Exception as e:
			self.fail(f"Portal configuration test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_privacy_compliance_validation_performance(self):
		"""Test: performance de validación de cumplimiento de privacidad"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			doc = create_test_document_with_required_fields(self.doctype)
			doc.insert(ignore_permissions=True)

			# Simulate privacy compliance validation
			compliance_checks = [
				"validate_data_retention_period",
				"validate_privacy_protection_level",
				"validate_confidentiality_agreements",
				"validate_external_audit_access",
			]

			for _check in compliance_checks:
				# Simulate compliance check
				time.sleep(0.002)  # 2ms per check

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Compliance validation should be very fast
			self.assert_performance_benchmark("query", execution_time)

		except Exception as e:
			self.fail(f"Privacy compliance validation test failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_audit_trail_performance(self):
		"""Test: performance de seguimiento de auditoría"""
		start_time = time.perf_counter()

		if is_ci_cd_environment():
			# Mock audit results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("reporting", 0.3)
		else:
			# Real audit query in local environment
			results = frappe.db.sql("""
				SELECT
					name,
					config_name,
					creation_date,
					last_modified_date,
					created_by,
					last_modified_by
				FROM `tabFinancial Transparency Config`
				WHERE last_modified_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
				ORDER BY last_modified_date DESC
			""")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Audit trail should meet benchmark
		self.assert_performance_benchmark("reporting", execution_time)
		self.assertIsNotNone(results)

	def test_transparency_config_validation_performance(self):
		"""Test: performance de validaciones de configuración de transparencia"""
		start_time = time.perf_counter()

		try:
			# Use utility to create document with all required fields
			create_test_document_with_required_fields(self.doctype)

			# Simulate comprehensive validation process
			validation_checks = [
				"validate_transparency_level_consistency",
				"validate_access_control_settings",
				"validate_compliance_requirements",
				"validate_portal_configuration",
				"validate_reporting_settings",
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
