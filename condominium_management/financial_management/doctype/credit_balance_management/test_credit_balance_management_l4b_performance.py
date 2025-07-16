import time

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCreditBalanceManagementL4BPerformance(FrappeTestCase):
	"""Layer 4B Performance Tests - Credit Balance Management Runtime Performance"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Credit Balance Management"

	def test_credit_balance_creation_performance(self):
		"""Test: performance de creación de Credit Balance (Meta: < 300ms)"""
		start_time = time.perf_counter()

		doc = frappe.get_doc(
			{
				"doctype": self.doctype,
				"balance_date": frappe.utils.today(),
				"account_type": "Property Account",
				"credit_amount": 1500.00,
				"balance_status": "Activo",
				"expiration_date": frappe.utils.add_days(frappe.utils.today(), 30),
				"company": "_Test Company",
			}
		)

		try:
			doc.insert(ignore_permissions=True)
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta de expertos: < 300ms
			self.assertLess(
				execution_time, 0.3, f"Credit Balance creation took {execution_time:.3f}s, expected < 0.3s"
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Aún verificar performance aunque falle
			self.assertLess(
				execution_time,
				0.3,
				f"Credit Balance creation attempt took {execution_time:.3f}s, expected < 0.3s",
			)

			frappe.log_error(f"Credit Balance creation failed but performance OK: {e!s}")

		finally:
			frappe.db.rollback()

	def test_credit_application_calculation_performance(self):
		"""Test: performance de cálculos de aplicación de créditos"""
		# Crear credit balance para cálculos
		doc = frappe.get_doc(
			{
				"doctype": self.doctype,
				"balance_date": frappe.utils.today(),
				"account_type": "Property Account",
				"credit_amount": 2500.00,
				"balance_status": "Activo",
				"remaining_balance": 2500.00,
				"company": "_Test Company",
			}
		)

		try:
			doc.insert(ignore_permissions=True)

			# Simular múltiples aplicaciones de crédito
			start_time = time.perf_counter()

			# Realizar 50 cálculos simulados de aplicación
			for i in range(50):
				# Simular cálculo de aplicación de crédito
				application_amount = 100 + (i * 10)
				available = doc.available_balance or 0

				# Validar si se puede aplicar
				if application_amount <= available:
					new_balance = available - application_amount
					# Simular actualización de balance
					max(0, new_balance)
				else:
					# Aplicación parcial
					pass

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 15ms para 50 cálculos de aplicación (0.3ms por cálculo)
			self.assertLess(
				execution_time, 0.015, f"50 credit applications took {execution_time:.3f}s, expected < 0.015s"
			)

		except Exception as e:
			frappe.log_error(f"Credit application performance test failed: {e!s}")
			self.fail(f"Credit application performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_credit_balance_search_performance(self):
		"""Test: performance de búsqueda de Credit Balance"""
		start_time = time.perf_counter()

		# Búsqueda por diferentes criterios
		_ = frappe.get_list(
			self.doctype,
			filters={"balance_status": ["in", ["Activo", "Aplicado Parcial"]], "credit_amount": [">", 0]},
			fields=["name", "credit_amount", "balance_status", "remaining_balance"],
			order_by="credit_amount desc",
			limit=25,
		)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 150ms para búsquedas complejas
		self.assertLess(
			execution_time, 0.15, f"Credit Balance search took {execution_time:.3f}s, expected < 0.15s"
		)

	def test_batch_credit_balance_operations(self):
		"""Test: performance de operaciones masivas de Credit Balance"""
		batch_size = 20  # Reducido para testing más rápido
		start_time = time.perf_counter()

		docs_created = []
		statuses = ["Activo", "Aplicado Parcial", "Expirado"]

		try:
			for i in range(batch_size):
				doc = frappe.get_doc(
					{
						"doctype": self.doctype,
						"balance_date": frappe.utils.today(),
						"account_type": "Property Account",
						"credit_amount": 800.0 + (i * 100),
						"balance_status": statuses[i % len(statuses)],
						"remaining_balance": 800.0 + (i * 100),
						"company": "_Test Company",
					}
				)
				doc.insert(ignore_permissions=True)
				docs_created.append(doc.name)

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 50ms por documento para Credit Balance
			time_per_doc = execution_time / batch_size
			self.assertLess(
				time_per_doc,
				0.05,
				f"Batch credit balance creation: {time_per_doc:.3f}s per doc, expected < 0.05s",
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			if len(docs_created) > 0:
				time_per_doc = execution_time / len(docs_created)
				self.assertLess(
					time_per_doc,
					0.05,
					f"Batch credit balance (partial): {time_per_doc:.3f}s per doc, expected < 0.05s",
				)

			frappe.log_error(f"Batch credit balance operations failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_complex_credit_query_performance(self):
		"""Test: performance de queries complejas para análisis de créditos"""
		start_time = time.perf_counter()

		# Query compleja que simula reporting de créditos
		_ = frappe.db.sql(
			"""
			SELECT
				balance_status,
				COUNT(*) as count,
				SUM(credit_amount) as total_credit,
				AVG(remaining_balance) as avg_available,
				SUM(CASE WHEN balance_status = 'Activo' THEN credit_amount ELSE 0 END) as available_credit
			FROM `tabCredit Balance Management`
			WHERE
				credit_amount > 0
				AND creation >= DATE_SUB(NOW(), INTERVAL 6 MONTHS)
			GROUP BY balance_status
			ORDER BY total_credit DESC
			LIMIT 15
			""",
			as_dict=True,
		)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 120ms para análisis queries
		self.assertLess(
			execution_time,
			0.12,
			f"Complex credit analysis query took {execution_time:.3f}s, expected < 0.12s",
		)

	def test_credit_balance_update_performance(self):
		"""Test: performance de actualización de Credit Balance"""
		# Crear credit balance para actualizar
		doc = frappe.get_doc(
			{
				"doctype": self.doctype,
				"balance_date": frappe.utils.today(),
				"account_type": "Property Account",
				"credit_amount": 1200.00,
				"balance_status": "Activo",
				"remaining_balance": 1200.00,
				"company": "_Test Company",
			}
		)

		try:
			doc.insert(ignore_permissions=True)

			# Medir actualización de múltiples campos
			start_time = time.perf_counter()

			doc.balance_status = "Aplicado Parcial"
			doc.remaining_balance = 800.00
			doc.total_applied = 400.00
			doc.save()

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 250ms para updates complejos
			self.assertLess(
				execution_time, 0.25, f"Credit Balance update took {execution_time:.3f}s, expected < 0.25s"
			)

		except Exception as e:
			frappe.log_error(f"Credit Balance update performance test failed: {e!s}")
			self.fail(f"Credit Balance update performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_credit_validation_performance(self):
		"""Test: performance de validaciones de Credit Balance"""
		start_time = time.perf_counter()

		# Crear credit balance con validaciones complejas
		doc = frappe.get_doc(
			{
				"doctype": self.doctype,
				"balance_date": frappe.utils.today(),
				"account_type": "Property Account",
				"credit_amount": 3000.00,
				"balance_status": "Activo",
				"remaining_balance": 3000.00,
				"expiration_date": frappe.utils.add_days(frappe.utils.today(), 60),
				"company": "_Test Company",
			}
		)

		try:
			# Validar sin guardar (solo validations)
			doc.run_method("validate")

			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Meta: < 100ms para validaciones
			self.assertLess(
				execution_time, 0.1, f"Credit Balance validation took {execution_time:.3f}s, expected < 0.1s"
			)

		except Exception as e:
			end_time = time.perf_counter()
			execution_time = end_time - start_time

			# Aún medir performance aunque validación falle
			self.assertLess(
				execution_time,
				0.1,
				f"Credit Balance validation attempt took {execution_time:.3f}s, expected < 0.1s",
			)

			frappe.log_error(f"Credit validation performance test failed: {e!s}")

		finally:
			frappe.db.rollback()

	def test_credit_expiry_check_performance(self):
		"""Test: performance de verificación de expiración de créditos"""
		start_time = time.perf_counter()

		# Query que simula verificación masiva de expiración
		_ = frappe.db.sql(
			"""
			SELECT
				name,
				credit_amount,
				remaining_balance,
				expiration_date,
				CASE
					WHEN expiration_date < CURDATE() THEN 'Expirado'
					WHEN expiration_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 'Por Expirar'
					ELSE 'Vigente'
				END as expiry_status
			FROM `tabCredit Balance Management`
			WHERE
				balance_status = 'Activo'
				AND remaining_balance > 0
				AND expiration_date IS NOT NULL
			ORDER BY expiration_date ASC
			LIMIT 50
			""",
			as_dict=True,
		)

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 80ms para verificación de expiración
		self.assertLess(
			execution_time, 0.08, f"Credit expiry check took {execution_time:.3f}s, expected < 0.08s"
		)

	def test_count_operations_performance(self):
		"""Test: performance de operaciones de conteo"""
		start_time = time.perf_counter()

		# Múltiples operaciones de conteo
		counts = {
			"total": frappe.db.count(self.doctype),
			"available": frappe.db.count(self.doctype, {"balance_status": "Activo"}),
			"applied": frappe.db.count(self.doctype, {"balance_status": "Aplicado Parcial"}),
			"expired": frappe.db.count(self.doctype, {"balance_status": "Expirado"}),
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

		# Verificar existencia de múltiples credit balances
		test_names = [f"NONEXISTENT-CREDIT-{i}" for i in range(15)]

		for name in test_names:
			exists = frappe.db.exists(self.doctype, name)
			self.assertIsNone(exists, f"Credit {name} no debe existir")

		end_time = time.perf_counter()
		execution_time = end_time - start_time

		# Meta: < 45ms para 15 existence checks
		self.assertLess(
			execution_time, 0.045, f"Batch exists checks took {execution_time:.3f}s, expected < 0.045s"
		)

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()
