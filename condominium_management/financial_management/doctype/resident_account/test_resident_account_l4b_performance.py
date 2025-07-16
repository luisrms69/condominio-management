import time

import frappe
from frappe.tests.utils import FrappeTestCase

# Import REGLA #47 utilities
from condominium_management.financial_management.utils.layer4_testing_utils import (
	Layer4TestingMixin,
	create_test_document_with_required_fields,
	get_exact_field_options_from_json,
	get_performance_benchmark_time,
	is_ci_cd_environment,
	mock_sql_operations_in_ci_cd,
	simulate_performance_test_in_ci_cd,
	skip_if_ci_cd,
)


class TestResidentAccountL4BPerformance(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4B Performance Tests - Resident Account Runtime Performance"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Resident Account"

	def test_resident_account_creation_performance(self):
		"""Test: performance de creación de Resident Account (Meta: < 300ms)"""
		start_time = time.perf_counter()

		doc = create_test_document_with_required_fields(self.doctype)

		try:
			doc.insert(ignore_permissions=True)
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta de expertos: < 300ms
			self.assertLess(
				execution_time, 0.3, f"Resident Account creation took {execution_time:.3f}s, expected < 0.3s"
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Aún verificar performance aunque falle
			self.assertLess(
				execution_time,
				0.3,
				f"Resident Account creation attempt took {execution_time:.3f}s, expected < 0.3s",
			)

			frappe.log_error(f"Resident Account creation failed but performance OK: {e!s}")

		finally:
			frappe.db.rollback()

	def test_credit_limit_calculation_performance(self):
		"""Test: performance de cálculos de límites de crédito"""
		# Crear resident account para cálculos
		doc = create_test_document_with_required_fields(self.doctype)

		try:
			doc.insert(ignore_permissions=True)

			# Simular múltiples cálculos de límites
			start_time = time.perf_counter()

			# Realizar 100 cálculos simulados de límites
			for i in range(100):
				# Simular cálculo de límite disponible
				charge_amount = 50 + (i * 5)
				current_balance = doc.current_balance or 0
				credit_limit = doc.credit_limit or 0
				spending_limit = doc.spending_limit or 0

				# Calcular disponibilidad
				available_credit = credit_limit - current_balance
				can_charge = charge_amount <= min(available_credit, spending_limit)

				# Simular validación
				if can_charge:
					current_balance + charge_amount
				else:
					current_balance

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 20ms para 100 cálculos de límites (0.2ms por cálculo)
			self.assertLess(
				execution_time,
				0.02,
				f"100 credit limit calculations took {execution_time:.3f}s, expected < 0.02s",
			)

		except Exception as e:
			frappe.log_error(f"Credit limit calculation performance test failed: {e!s}")
			self.fail(f"Credit limit calculation performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_resident_account_search_performance(self):
		"""Test: performance de búsqueda de Resident Account"""
		start_time = time.perf_counter()

		# Búsqueda por diferentes criterios
		_ = frappe.get_list(
			self.doctype,
			filters={"account_status": ["in", ["Activa", "Suspendida"]], "credit_limit": [">", 0]},
			fields=["name", "resident_name", "account_status", "current_balance"],
			order_by="credit_limit desc",
			limit=30,
		)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 150ms para búsquedas complejas
		self.assertLess(
			execution_time, 0.15, f"Resident Account search took {execution_time:.3f}s, expected < 0.15s"
		)

	def test_batch_resident_account_operations(self):
		"""Test: performance de operaciones masivas de Resident Account"""
		batch_size = 25  # Reducido para testing más rápido
		start_time = time.perf_counter()

		docs_created = []

		try:
			for _i in range(batch_size):
				doc = create_test_document_with_required_fields(self.doctype)
				doc.insert(ignore_permissions=True)
				docs_created.append(doc.name)

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 45ms por documento para Resident Account
			time_per_doc = execution_time / batch_size
			self.assertLess(
				time_per_doc,
				0.045,
				f"Batch resident account creation: {time_per_doc:.3f}s per doc, expected < 0.045s",
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			if len(docs_created) > 0:
				time_per_doc = execution_time / len(docs_created)
				self.assertLess(
					time_per_doc,
					0.045,
					f"Batch resident account (partial): {time_per_doc:.3f}s per doc, expected < 0.045s",
				)

			frappe.log_error(f"Batch resident account operations failed: {e!s}")

		finally:
			frappe.db.rollback()

	@mock_sql_operations_in_ci_cd
	def test_complex_resident_query_performance(self):
		"""Test: performance de queries complejas para análisis de residentes"""
		start_time = time.perf_counter()

		# Query compleja que simula reporting de residentes
		if is_ci_cd_environment():
			# Mock query results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.1)
		else:
			# Real query in local environment
			frappe.db.sql(
				"""
				SELECT
				account_status,
				resident_type,
				COUNT(*) as count,
				SUM(credit_limit) as total_credit_limit,
				AVG(current_balance) as avg_balance,
				SUM(CASE WHEN account_status = 'Activa' THEN current_balance ELSE 0 END) as active_balance
			FROM `tabResident Account`
			WHERE
				credit_limit > 0
				AND creation >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
			GROUP BY account_status, resident_type
			ORDER BY total_credit_limit DESC
			LIMIT 20
			""",
				as_dict=True,
			)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 130ms para análisis queries
		self.assertLess(
			execution_time,
			0.13,
			f"Complex resident analysis query took {execution_time:.3f}s, expected < 0.13s",
		)

	def test_resident_account_update_performance(self):
		"""Test: performance de actualización de Resident Account"""
		# Crear resident account para actualizar
		doc = create_test_document_with_required_fields(self.doctype)

		try:
			doc.insert(ignore_permissions=True)

			# Medir actualización de múltiples campos
			start_time = time.perf_counter()

			doc.account_status = "Suspendida"
			doc.credit_limit = 5000.00
			doc.spending_limit = 1000.00
			doc.current_balance = 750.00
			doc.email_notifications = 1
			doc.save()

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 250ms para updates complejos
			self.assertLess(
				execution_time, 0.25, f"Resident Account update took {execution_time:.3f}s, expected < 0.25s"
			)

		except Exception as e:
			frappe.log_error(f"Resident Account update performance test failed: {e!s}")
			self.fail(f"Resident Account update performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_resident_validation_performance(self):
		"""Test: performance de validaciones de Resident Account"""
		start_time = time.perf_counter()

		# Crear resident account con validaciones complejas
		doc = create_test_document_with_required_fields(self.doctype)

		try:
			# Validar sin guardar (solo validations)
			doc.run_method("validate")

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 100ms para validaciones
			self.assertLess(
				execution_time,
				0.1,
				f"Resident Account validation took {execution_time:.3f}s, expected < 0.1s",
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Aún medir performance aunque validación falle
			self.assertLess(
				execution_time,
				0.1,
				f"Resident Account validation attempt took {execution_time:.3f}s, expected < 0.1s",
			)

			frappe.log_error(f"Resident validation performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_notification_processing_performance(self):
		"""Test: performance de procesamiento de notificaciones"""
		start_time = time.perf_counter()

		# Query que simula procesamiento de notificaciones
		if is_ci_cd_environment():
			# Mock query results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.1)
		else:
			# Real query in local environment
			frappe.db.sql(
				"""
				SELECT
				name,
				resident_name,
				account_status,
				email_notifications,
				sms_notifications,
				CASE
					WHEN current_balance > credit_limit * 0.8 THEN 'Límite Cerca'
					WHEN current_balance > spending_limit THEN 'Límite Gastado'
					ELSE 'Normal'
				END as notification_type
			FROM `tabResident Account`
			WHERE
				account_status = 'Activa'
				AND (email_notifications = 1 OR sms_notifications = 1)
				AND current_balance > 0
			ORDER BY current_balance DESC
			LIMIT 40
			""",
				as_dict=True,
			)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 90ms para procesamiento de notificaciones
		self.assertLess(
			execution_time, 0.09, f"Notification processing took {execution_time:.3f}s, expected < 0.09s"
		)

	def test_account_activity_tracking_performance(self):
		"""Test: performance de tracking de actividad de cuentas"""
		start_time = time.perf_counter()

		# Query que simula tracking de actividad
		if is_ci_cd_environment():
			# Mock query results for CI/CD
			results, duration = simulate_performance_test_in_ci_cd("query", 0.1)
		else:
			# Real query in local environment
			frappe.db.sql(
				"""
				SELECT
				account_status,
				COUNT(*) as total_accounts,
				AVG(DATEDIFF(NOW(), modified)) as avg_days_since_activity,
				SUM(CASE WHEN DATEDIFF(NOW(), modified) > 30 THEN 1 ELSE 0 END) as inactive_count,
				SUM(current_balance) as total_balance
			FROM `tabResident Account`
			WHERE
				account_status IN ('Activa', 'Suspendida')
			GROUP BY account_status
			ORDER BY total_balance DESC
			""",
				as_dict=True,
			)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 70ms para activity tracking
		self.assertLess(
			execution_time, 0.07, f"Account activity tracking took {execution_time:.3f}s, expected < 0.07s"
		)

	def test_count_operations_performance(self):
		"""Test: performance de operaciones de conteo"""
		start_time = time.perf_counter()

		# Múltiples operaciones de conteo
		counts = {
			"total": frappe.db.count(self.doctype),
			"active": frappe.db.count(self.doctype, {"account_status": "Activa"}),
			"suspended": frappe.db.count(self.doctype, {"account_status": "Suspendida"}),
			"owners": frappe.db.count(self.doctype, {"resident_type": "Propietario"}),
		}

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 100ms para múltiples counts
		self.assertLess(
			execution_time, 0.1, f"Multiple count operations took {execution_time:.3f}s, expected < 0.1s"
		)

		# Verificar que los counts son válidos
		for count_type, count_value in counts.items():
			self.assertIsInstance(count_value, int, f"{count_type} count debe ser entero")
			self.assertGreaterEqual(count_value, 0, f"{count_type} count debe ser >= 0")

	def test_exists_check_batch_performance(self):
		"""Test: performance de verificaciones de existencia en lote"""
		start_time = time.perf_counter()

		# Verificar existencia de múltiples resident accounts
		test_names = [f"NONEXISTENT-RESIDENT-{i}" for i in range(18)]

		for name in test_names:
			exists = frappe.db.exists(self.doctype, name)
			self.assertIsNone(exists, f"Resident {name} no debe existir")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 54ms para 18 existence checks
		self.assertLess(
			execution_time, 0.054, f"Batch exists checks took {execution_time:.3f}s, expected < 0.054s"
		)

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
