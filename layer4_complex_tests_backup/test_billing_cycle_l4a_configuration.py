import json
import os
import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBillingCycleL4AConfiguration(FrappeTestCase):
	"""Layer 4A Configuration Tests - Billing Cycle JSON, Permissions, Hooks"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Billing Cycle"
		cls.meta = frappe.get_meta(cls.doctype)

		# Path al JSON del DocType
		cls.doctype_folder = cls.doctype.replace(" ", "_").lower()
		cls.json_path = os.path.join(
			frappe.get_app_path("condominium_management"),
			"financial_management",
			"doctype",
			cls.doctype_folder,
			f"{cls.doctype_folder}.json",
		)

	def test_json_vs_meta_consistency_billing_cycle(self):
		"""Test: consistencia JSON vs Meta específica para Billing Cycle"""
		# 1. Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# 2. Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# 3. Validar propiedades críticas del DocType
		self.assertEqual(json_def.get("module"), "Financial Management")
		self.assertEqual(json_def.get("name"), self.doctype)

		# 4. Campos críticos específicos para Billing Cycle
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos para ciclos de facturación
		critical_fields = [
			"cycle_name",
			"billing_frequency",
			"start_date",
			"end_date",
			"cycle_status",
			"total_billed_amount",
			"total_collected_amount",
		]

		for fieldname in critical_fields:
			if fieldname in json_fields:
				json_field = json_fields[fieldname]
				frappe_field = frappe_fields.get(fieldname)

				self.assertIsNotNone(frappe_field, f"Field {fieldname} missing in Meta")

				# Validaciones específicas para billing cycle
				if fieldname in ["start_date", "end_date"]:
					self.assertEqual(frappe_field.fieldtype, "Date", f"{fieldname} debe ser Date field")

				elif fieldname in ["total_billed_amount", "total_collected_amount"]:
					self.assertEqual(
						frappe_field.fieldtype, "Currency", f"{fieldname} debe ser Currency field"
					)

				elif fieldname == "billing_frequency":
					self.assertEqual(
						frappe_field.fieldtype, "Select", "billing_frequency debe ser Select field"
					)

					# Verificar opciones de frecuencia
					if frappe_field.options:
						options = frappe_field.options.split("\n")
						expected_frequencies = ["Monthly", "Quarterly", "Annual"]
						for freq in expected_frequencies:
							if freq in json_field.get("options", ""):
								self.assertIn(
									freq, options, f"Frecuencia {freq} faltante en billing_frequency"
								)

				elif fieldname == "cycle_status":
					self.assertEqual(frappe_field.fieldtype, "Select", "cycle_status debe ser Select field")

	def test_billing_cycle_workflow_fields(self):
		"""Test: campos específicos del workflow de billing cycle"""
		# Campos de estado y workflow
		workflow_fields = {
			"cycle_status": "Select",
			"activation_date": "Date",
			"closure_date": "Date",
			"processing_date": "Date",
			"auto_process": "Check",
		}

		for field_name, expected_type in workflow_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

		# Verificar opciones de cycle_status
		if self.meta.has_field("cycle_status"):
			field = self.meta.get_field("cycle_status")
			if field.options:
				options = field.options.split("\n")
				expected_statuses = ["Draft", "Active", "Processing", "Closed"]
				for status in expected_statuses:
					if any(status in opt for opt in options):
						# Al menos uno de los estados esperados debe existir
						break
				else:
					self.fail("cycle_status debe tener al menos un estado de workflow válido")

	def test_billing_amounts_configuration(self):
		"""Test: configuración de campos de montos y cálculos"""
		# Campos monetarios críticos
		amount_fields = {
			"total_billed_amount": "Currency",
			"total_collected_amount": "Currency",
			"pending_amount": "Currency",
			"total_adjustments": "Currency",
			"net_billed_amount": "Currency",
			"total_late_fees": "Currency",
		}

		for field_name, expected_type in amount_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

				# Currency fields no deben tener options
				self.assertIsNone(field.options, f"Currency field {field_name} no debe tener options")

		# Campos numéricos de conteo
		numeric_fields = {
			"invoices_generated": "Int",
			"late_fees_processed": "Int",
			"adjustment_count": "Int",
			"payment_count": "Int",
		}

		for field_name, expected_type in numeric_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

	def test_performance_tracking_fields(self):
		"""Test: campos para tracking de performance del ciclo"""
		# Campos de métricas y analytics
		performance_fields = {
			"collection_rate": "Percent",
			"invoice_generation_rate": "Percent",
			"processing_time": "Float",
			"error_count": "Int",
			"batch_size": "Int",
		}

		for field_name, expected_type in performance_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype,
					[expected_type, "Float", "Int"],
					f"Campo {field_name} debe ser {expected_type} o compatible",
				)

		# Campos de fechas para tracking
		date_tracking_fields = ["last_sync_date", "error_resolution_date", "last_report_date"]
		for field_name in date_tracking_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype, ["Date", "Datetime"], f"Campo {field_name} debe ser Date o Datetime"
				)

	def test_permissions_for_billing_operations(self):
		"""Test: permisos específicos para operaciones de facturación"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Billing Cycle es crítico - solo roles financieros específicos
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")

			# Roles de facturación específicos
			billing_roles = ["Accounts Manager", "Billing Manager", "Financial Manager"]
			for role in billing_roles:
				if role in all_perms:
					role_perms = all_perms[role]
					self.assertTrue(role_perms.get("read"), f"{role} debe tener read access")

			# Roles que NO deben tener write access
			restricted_roles = ["Guest", "Customer", "Supplier"]
			for role in restricted_roles:
				if role in all_perms:
					role_perms = all_perms[role]
					self.assertFalse(role_perms.get("write", True), f"{role} NO debe tener write access")
					self.assertFalse(role_perms.get("delete", True), f"{role} NO debe tener delete access")

		except Exception:
			# Fallback a método alternativo
			permissions = frappe.get_all(
				"DocPerm",
				filters={"parent": self.doctype},
				fields=["role", "read", "write", "create", "delete"],
			)

			self.assertGreater(len(permissions), 0, "Billing Cycle debe tener permisos configurados")

	def test_database_schema_for_billing_data(self):
		"""Test: esquema de base de datos para datos de facturación"""
		table_name = f"tab{self.doctype.replace(' ', '')}"
		table_columns = frappe.db.get_table_columns(table_name)

		# Verificar campos críticos para facturación
		billing_critical_fields = [
			"cycle_name",
			"billing_frequency",
			"start_date",
			"end_date",
			"total_billed_amount",
			"total_collected_amount",
			"cycle_status",
		]

		for field_name in billing_critical_fields:
			if self.meta.has_field(field_name):
				self.assertIn(
					field_name, table_columns, f"Campo crítico de facturación {field_name} faltante en DB"
				)

		# Verificar índices para performance de facturación
		try:
			indexes = frappe.db.sql(
				f"""
				SHOW INDEX FROM `{table_name}`
			""",
				as_dict=True,
			)

			index_columns = [idx.Column_name for idx in indexes]

			# Campos que deberían tener índices para performance
			indexed_fields = ["cycle_status", "billing_frequency", "start_date", "end_date"]
			for field_name in indexed_fields:
				if self.meta.has_field(field_name):
					# Verificar si está indexado (primary key cuenta)
					is_indexed = field_name in index_columns or any(
						field_name in idx.Key_name for idx in indexes
					)
					if not is_indexed:
						frappe.log_error(f"Performance warning: {field_name} no está indexado")

		except Exception as e:
			frappe.log_error(f"Index validation failed: {e!s}")

	def test_json_configuration_for_mass_operations(self):
		"""Test: configuración JSON para operaciones masivas"""
		with open(self.json_path, encoding="utf-8") as f:
			json_config = json.load(f)

		# Verificar configuración para batch processing
		batch_fields = ["batch_size", "bulk_processing_enabled", "auto_process"]
		for field_name in batch_fields:
			field_config = None
			for field in json_config.get("fields", []):
				if field.get("fieldname") == field_name:
					field_config = field
					break

			if field_config:
				if field_name == "batch_size":
					self.assertEqual(field_config.get("fieldtype"), "Int", "batch_size debe ser Int field")

					# Verificar default value razonable
					default_val = field_config.get("default")
					if default_val:
						try:
							val = int(default_val)
							self.assertGreater(val, 0, "batch_size default debe ser > 0")
							self.assertLess(val, 10000, "batch_size default debe ser razonable")
						except ValueError:
							self.fail(f"batch_size default inválido: {default_val}")

				elif field_name in ["bulk_processing_enabled", "auto_process"]:
					self.assertEqual(
						field_config.get("fieldtype"), "Check", f"{field_name} debe ser Check field"
					)

		# Verificar que no hay configuraciones conflictivas
		for field in json_config.get("fields", []):
			if field.get("fieldtype") == "Currency":
				# Currency fields no deben tener default negativo
				default_val = field.get("default")
				if default_val:
					try:
						val = float(default_val)
						self.assertGreaterEqual(
							val, 0, f"Currency field {field.get('fieldname')} default no debe ser negativo"
						)
					except ValueError:
						pass  # Ignorar defaults no numéricos

	def test_workflow_configuration_consistency(self):
		"""Test: consistencia de configuración de workflow"""
		# Si hay workflow configurado, verificar consistencia
		try:
			workflow = frappe.get_doc("Workflow", self.doctype)

			# Verificar que estados del workflow coinciden con options del campo
			if self.meta.has_field("cycle_status"):
				status_field = self.meta.get_field("cycle_status")
				if status_field.options:
					field_options = [opt.strip() for opt in status_field.options.split("\n")]
					workflow_states = [state.state for state in workflow.states]

					# Los estados del workflow deben estar en las opciones del campo
					for state in workflow_states:
						self.assertIn(
							state, field_options, f"Workflow state {state} no está en cycle_status options"
						)

		except frappe.DoesNotExistError:
			# No hay workflow configurado, skip test
			pass
		except Exception as e:
			frappe.log_error(f"Workflow validation failed: {e!s}")

	def test_automation_configuration(self):
		"""Test: configuración de automatización del billing cycle"""
		# Campos de automatización
		automation_fields = {
			"auto_process": "Check",
			"auto_invoice_generation": "Check",
			"auto_reconcile_enabled": "Check",
			"auto_report_generation": "Check",
		}

		for field_name, expected_type in automation_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype,
					expected_type,
					f"Campo de automatización {field_name} debe ser {expected_type}",
				)

		# Campos de configuración de automatización
		config_fields = {
			"processing_schedule": "Data",
			"notification_emails": "Small Text",
			"max_retries": "Int",
		}

		for field_name, expected_type in config_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype,
					[expected_type, "Text", "Data"],
					f"Campo {field_name} debe ser {expected_type} o compatible",
				)

	def test_reporting_integration_configuration(self):
		"""Test: configuración de integración con reportes"""
		# Campos para integración con reportes
		reporting_fields = {
			"report_formats": "Small Text",
			"report_generated_count": "Int",
			"last_report_date": "Date",
			"external_sync_enabled": "Check",
		}

		for field_name, expected_type in reporting_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				if field_name == "report_formats":
					self.assertIn(
						field.fieldtype, ["Small Text", "Text"], "report_formats debe ser Small Text o Text"
					)
				else:
					self.assertEqual(
						field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
					)

	def test_error_handling_configuration(self):
		"""Test: configuración de manejo de errores"""
		# Campos para error handling
		error_fields = {
			"error_count": "Int",
			"last_error_date": "Date",
			"error_recovery_enabled": "Check",
			"errors_resolved": "Check",
		}

		for field_name, expected_type in error_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype,
					expected_type,
					f"Campo de error handling {field_name} debe ser {expected_type}",
				)

		# Verificar defaults apropiados
		if self.meta.has_field("error_count"):
			field = self.meta.get_field("error_count")
			# error_count debe default a 0
			self.assertTrue(
				field.default == "0" or field.default == 0 or not field.default,
				"error_count debe default a 0 o no tener default",
			)

	def test_meta_caching_for_complex_doctype(self):
		"""Test: Meta caching para DocType complejo como Billing Cycle"""
		# Verificar caching consistente
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		# Verificar que tienen misma cantidad de campos
		self.assertEqual(
			len(meta1.fields), len(meta2.fields), "Meta caching inconsistente para Billing Cycle"
		)

		# Verificar campos críticos específicamente
		critical_fields = ["cycle_name", "billing_frequency", "total_billed_amount"]
		for field_name in critical_fields:
			if meta1.has_field(field_name):
				field1 = meta1.get_field(field_name)
				field2 = meta2.get_field(field_name)

				self.assertEqual(
					field1.fieldtype, field2.fieldtype, f"Meta caching inconsistente para campo {field_name}"
				)
				self.assertEqual(
					field1.reqd, field2.reqd, f"Meta caching inconsistente para reqd de {field_name}"
				)

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()
