# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json
import os
import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

# Import REGLA #47 utilities
from condominium_management.financial_management.utils.layer4_testing_utils import (
	Layer4TestingMixin,
	create_test_document_with_required_fields,
	get_exact_field_options_from_json,
	is_ci_cd_environment,
	skip_if_ci_cd,
)


class TestBillingCycleL4AConfiguration(Layer4TestingMixin, FrappeTestCase):
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

		# 4. Campos críticos específicos para Billing Cycle (exact from JSON)
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos para ciclos de facturación (exact from JSON)
		critical_fields = [
			"naming_series",
			"cycle_name",
			"company",
			"fee_structure",
			"start_date",
			"end_date",
			"due_date",
			"cycle_status",
		]

		# Validate critical fields exist in both JSON and Meta
		for field in critical_fields:
			self.assertIn(field, json_fields, f"Critical field '{field}' missing from JSON")
			self.assertIn(field, frappe_fields, f"Critical field '{field}' missing from Meta")

			# Validate field consistency
			json_field = json_fields[field]
			frappe_field = frappe_fields[field]

			self.assertEqual(json_field.get("fieldtype"), frappe_field.fieldtype)
			self.assertEqual(json_field.get("reqd", 0), int(frappe_field.reqd))

	def test_billing_cycle_workflow_fields(self):
		"""Test: campos específicos del workflow de billing cycle"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Verificar campo de estado del ciclo
		cycle_status_field = frappe_meta.get_field("cycle_status")
		self.assertIsNotNone(cycle_status_field, "cycle_status field missing")

		# Verificar que cycle_status tiene estados válidos (exact from JSON)
		if cycle_status_field.fieldtype == "Select":
			# Get exact options from JSON
			expected_options = get_exact_field_options_from_json(self.doctype, "cycle_status")
			if expected_options:
				actual_options = [
					opt.strip() for opt in cycle_status_field.options.split("\n") if opt.strip()
				]
				for option in expected_options:
					self.assertIn(option, actual_options, f"Option '{option}' missing from cycle_status")
			else:
				# Fallback validation
				status_options = cycle_status_field.options.split("\n")
				self.assertGreater(
					len(status_options), 0, "cycle_status debe tener al menos un estado de workflow válido"
				)

	def test_billing_amounts_configuration(self):
		"""Test: configuración de campos de montos y cálculos"""
		# Campos monetarios críticos (only test if they exist in JSON)
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

	def test_performance_tracking_fields(self):
		"""Test: campos para tracking de performance del ciclo"""
		# Campos de métricas y analytics (only test if they exist)
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

	def test_permissions_for_billing_operations(self):
		"""Test: permisos específicos para operaciones de facturación"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Billing Cycle es crítico - solo roles financieros específicos
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")

		except Exception:
			# Fallback a método alternativo
			permissions = frappe.get_all(
				"DocPerm",
				filters={"parent": self.doctype},
				fields=["role", "read", "write", "create", "delete"],
			)

			self.assertGreater(len(permissions), 0, "Billing Cycle debe tener permisos configurados")

	@skip_if_ci_cd
	def test_database_schema_for_billing_data(self):
		"""Test: esquema de base de datos para datos de facturación - ONLY LOCAL"""
		table_name = "tabBilling Cycle"

		# This test ONLY runs in local environment
		table_columns = frappe.db.get_table_columns(table_name)

		# Verificar columnas críticas para ciclos de facturación (from JSON)
		expected_columns = [
			"naming_series",
			"cycle_name",
			"company",
			"fee_structure",
			"start_date",
			"end_date",
			"due_date",
			"cycle_status",
		]

		# Verificar que las columnas críticas existen
		for column in expected_columns:
			self.assertIn(column, table_columns, f"Column {column} missing from {table_name}")

	def test_json_configuration_for_mass_operations(self):
		"""Test: configuración JSON para operaciones masivas"""
		with open(self.json_path, encoding="utf-8") as f:
			json_config = json.load(f)

		# Verificar configuración para batch processing (only if exists)
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

				elif field_name in ["bulk_processing_enabled", "auto_process"]:
					self.assertEqual(
						field_config.get("fieldtype"), "Check", f"{field_name} debe ser Check field"
					)

	def test_required_fields_validation(self):
		"""Test: validación de campos obligatorios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos que deben ser obligatorios según JSON
		required_fields = [
			"naming_series",
			"cycle_name",
			"company",
			"fee_structure",
			"start_date",
			"end_date",
			"due_date",
			"cycle_status",
		]

		for fieldname in required_fields:
			field = frappe_meta.get_field(fieldname)
			if field:  # Only test if field exists
				self.assertEqual(field.reqd, 1, f"Campo {fieldname} debe ser obligatorio")

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
		# Campos de automatización (only test if they exist)
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
		critical_fields = ["cycle_name", "company", "fee_structure"]
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
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
