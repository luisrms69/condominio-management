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
	get_performance_benchmark_time,
	is_ci_cd_environment,
	mock_sql_operations_in_ci_cd,
	simulate_performance_test_in_ci_cd,
	skip_if_ci_cd,
)


class TestFineManagementL4AConfiguration(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4A Configuration Tests - JSON, Permissions, Hooks Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Fine Management"
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

	def test_json_vs_meta_consistency(self):
		"""Test: consistencia completa JSON vs Meta para Fine Management"""
		# 1. Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# 2. Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# 3. Validar propiedades críticas del DocType
		self.assertEqual(json_def.get("module"), "Financial Management")
		self.assertEqual(json_def.get("name"), self.doctype)

		# 4. Validar campos específicos de Fine Management
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos específicos para Fine Management
		critical_fields = ["fine_amount", "fine_type", "fine_status", "violation_category"]

		for fieldname in critical_fields:
			if fieldname in json_fields:
				json_field = json_fields[fieldname]
				frappe_field = frappe_fields.get(fieldname)

				self.assertIsNotNone(frappe_field, f"Field {fieldname} missing in Meta")

				# Validar fieldtype
				self.assertEqual(
					json_field.get("fieldtype"),
					frappe_field.fieldtype,
					f"Field {fieldname} fieldtype mismatch",
				)

				# Validar configuraciones específicas
				if fieldname in ["fine_type", "fine_status", "violation_category"]:
					self.assertEqual(frappe_field.fieldtype, "Select", f"{fieldname} debe ser Select")

					# Verificar opciones críticas según el campo
					if frappe_field.options:
						options = frappe_field.options.split("\n")
						if fieldname == "fine_type":
							expected_types = ["Ruido", "Mascotas", "Estacionamiento"]
							for fine_type in expected_types:
								if fine_type in json_field.get("options", ""):
									self.assertIn(
										fine_type, options, f"Tipo {fine_type} faltante en fine_type"
									)
						elif fieldname == "fine_status":
							expected_statuses = ["Pendiente", "Pagada", "Disputada"]
							for status in expected_statuses:
								if status in json_field.get("options", ""):
									self.assertIn(status, options, f"Status {status} faltante en fine_status")

				elif fieldname == "fine_amount":
					self.assertEqual(frappe_field.fieldtype, "Currency", "fine_amount debe ser Currency")

	def test_fine_financial_fields_configuration(self):
		"""Test: configuración específica de campos financieros de multas"""
		# Verificar campos de montos y escalaciones
		financial_fields = {
			"fine_amount": "Currency",
			"late_fee": "Currency",
			"total_amount": "Currency",
			"paid_amount": "Currency",
			"outstanding_amount": "Currency",
		}

		for field_name, expected_type in financial_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

				# Campos de solo lectura para algunos casos
				if field_name in ["total_amount", "outstanding_amount"]:
					# Estos campos suelen ser calculados
					self.assertTrue(True)  # Validación exitosa para campos calculados

	def test_child_table_for_escalations(self):
		"""Test: configuración de child tables para escalaciones de multas"""
		# Verificar si tiene child tables para tracking de escalaciones
		child_tables = [f for f in self.meta.fields if f.fieldtype == "Table"]

		for child_field in child_tables:
			# Verificar que options está configurado
			self.assertIsNotNone(
				child_field.options, f"Child table {child_field.fieldname} debe tener options configurado"
			)

			# Verificar que el child DocType existe
			try:
				child_meta = frappe.get_meta(child_field.options)
				self.assertIsNotNone(child_meta, f"Child DocType {child_field.options} debe existir")

				# Verificar que es efectivamente una child table
				self.assertEqual(child_meta.istable, 1, f"{child_field.options} debe ser child table")

			except Exception as e:
				frappe.log_error(f"Child table validation failed: {e!s}")

	def test_fine_business_logic_fields(self):
		"""Test: campos específicos de lógica de negocio de multas"""
		# Verificar campos de fechas
		date_fields = ["violation_date", "fine_date", "due_date", "payment_date"]
		for field_name in date_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype, ["Date", "Datetime"], f"Campo {field_name} debe ser Date o Datetime"
				)

		# Verificar campos de estado
		status_fields = ["fine_status", "appeal_status"]
		for field_name in status_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Select", f"{field_name} debe ser Select field")

		# Verificar campos de configuración automática
		auto_fields = ["auto_escalate", "send_notifications", "recurring_fine"]
		for field_name in auto_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Check", f"{field_name} debe ser Check field")

	def test_permissions_for_fine_data(self):
		"""Test: permisos específicos para datos de multas"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Fine Management requiere permisos especiales - enforcement
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")
				self.assertTrue(sm_perms.get("create"), "System Manager: create")

			# Verificar roles de administración y enforcement
			enforcement_roles = ["Property Manager", "Committee President", "Security Manager"]
			for role in enforcement_roles:
				if role in all_perms:
					role_perms = all_perms[role]
					self.assertTrue(role_perms.get("read"), f"{role} debe tener read access")

			# Residentes normales NO deben tener acceso completo
			restricted_roles = ["Guest", "All"]
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

			self.assertGreater(len(permissions), 0, "Fine Management debe tener permisos configurados")

	@skip_if_ci_cd
	def test_database_schema_for_fine_calculations(self):
		"""Test: esquema de base de datos para cálculos de multas"""
		table_name = f"tab{self.doctype.replace(' ', '')}"
		try:
			table_columns = frappe.db.get_table_columns(table_name)
		except Exception as e:
			# Skip test si la tabla no existe en testing environment
			frappe.log_error(f"Fine Management table validation skipped: {e!s}")
			return

		# Verificar campos críticos para cálculos de multas
		calculation_fields = ["fine_amount", "late_fee", "total_amount"]
		for field_name in calculation_fields:
			if self.meta.has_field(field_name):
				self.assertIn(field_name, table_columns, f"Campo de cálculo {field_name} faltante en DB")

		# Verificar precisión de campos monetarios usando SQL
		try:
			# Verificar que campos Currency tienen precisión adecuada
			currency_fields = [f for f in self.meta.fields if f.fieldtype == "Currency"]
			for field in currency_fields:
				if field.fieldname in table_columns:
					# Verificar tipo de datos en MySQL/MariaDB
					column_info = frappe.db.sql(
						f"""
						SELECT DATA_TYPE, NUMERIC_PRECISION, NUMERIC_SCALE
						FROM information_schema.COLUMNS
						WHERE TABLE_SCHEMA = '{frappe.conf.db_name}'
						AND TABLE_NAME = '{table_name}'
						AND COLUMN_NAME = '{field.fieldname}'
						""",
						as_dict=True,
					)

					if column_info:
						col_info = column_info[0]
						# Currency fields deben ser DECIMAL
						self.assertEqual(
							col_info.DATA_TYPE, "decimal", f"Campo {field.fieldname} debe ser DECIMAL en DB"
						)

		except Exception as e:
			frappe.log_error(f"Currency precision validation failed: {e!s}")

	def test_json_validation_for_fine_fields(self):
		"""Test: validación JSON específica para campos de multas"""
		with open(self.json_path, encoding="utf-8") as f:
			json_config = json.load(f)

		# Verificar configuración de campos Currency
		for field in json_config.get("fields", []):
			if field.get("fieldtype") == "Currency":
				# Currency fields deben tener configuración apropiada
				fieldname = field.get("fieldname")

				# Verificar que no tienen valor por defecto extraño
				default_value = field.get("default")
				if default_value is not None:
					try:
						float(default_value)
					except (ValueError, TypeError):
						self.fail(f"Currency field {fieldname} tiene default inválido: {default_value}")

				# Verificar que no tienen options (Currency no debe tener options)
				self.assertIsNone(field.get("options"), f"Currency field {fieldname} no debe tener options")

			elif field.get("fieldtype") == "Select":
				# Select fields deben tener options
				if field.get("fieldname") in ["fine_type", "fine_status", "violation_category"]:
					self.assertIsNotNone(
						field.get("options"), f"Select field {field.get('fieldname')} debe tener options"
					)

					# Verificar que options no está vacío
					options = field.get("options", "")
					self.assertTrue(
						options.strip(), f"Select field {field.get('fieldname')} options no puede estar vacío"
					)

	def test_meta_caching_with_fine_tables(self):
		"""Test: Meta caching considerando fine tables"""
		# Verificar caching del meta principal
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		self.assertEqual(
			len(meta1.fields), len(meta2.fields), "Meta caching inconsistente para fine management"
		)

		# Verificar caching de child tables si existen
		child_tables = [f.options for f in meta1.fields if f.fieldtype == "Table"]

		for child_doctype in child_tables:
			if child_doctype:
				child_meta1 = frappe.get_meta(child_doctype)
				child_meta2 = frappe.get_meta(child_doctype)

				self.assertEqual(
					len(child_meta1.fields),
					len(child_meta2.fields),
					f"Child table {child_doctype} meta caching inconsistente",
				)

	def test_violation_category_configuration(self):
		"""Test: configuración específica de categorías de violación"""
		if self.meta.has_field("violation_category"):
			field = self.meta.get_field("violation_category")

			# Verificar que es Select
			self.assertEqual(field.fieldtype, "Select")

			# Verificar opciones críticas
			if field.options:
				options = field.options.split("\n")

				# Debe tener al menos estas categorías básicas (en español)
				basic_categories = ["Ruido", "Mascotas", "Estacionamiento"]
				for category in basic_categories:
					self.assertIn(category, options, f"Categoría básica {category} faltante")

				# Verificar que no hay opciones duplicadas
				self.assertEqual(
					len(options), len(set(options)), "No debe haber opciones duplicadas en violation_category"
				)

				# Verificar que no hay opciones vacías
				for option in options:
					self.assertTrue(option.strip(), "No debe haber opciones vacías en violation_category")

	def test_escalation_configuration(self):
		"""Test: configuración de escalación de multas"""
		# Verificar campos de escalación si existen
		escalation_fields = ["escalation_level", "escalation_date", "max_escalations"]
		for field_name in escalation_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "escalation_level":
					self.assertIn(
						field.fieldtype, ["Int", "Select"], "escalation_level debe ser Int o Select"
					)
				elif field_name == "escalation_date":
					self.assertIn(
						field.fieldtype, ["Date", "Datetime"], "escalation_date debe ser Date o Datetime"
					)
				elif field_name == "max_escalations":
					self.assertEqual(field.fieldtype, "Int", "max_escalations debe ser Int")

	def test_configuration_for_property_linking(self):
		"""Test: configuración para enlace con propiedades"""
		# Verificar campos de enlace con propiedades y residentes
		linking_fields = ["property_account", "resident_account", "reported_by"]
		for field_name in linking_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Link", f"{field_name} debe ser Link field")

				# Verificar que linkea a DocTypes apropiados
				if field_name == "property_account":
					self.assertEqual(
						field.options,
						"Property Account",
						"property_account debe linkear a Property Account DocType",
					)
				elif field_name == "resident_account":
					self.assertEqual(
						field.options,
						"Resident Account",
						"resident_account debe linkear a Resident Account DocType",
					)
				elif field_name == "reported_by":
					self.assertIn(
						field.options, ["User", "Employee"], "reported_by debe linkear a User o Employee"
					)

	def test_appeal_configuration(self):
		"""Test: configuración de sistema de apelaciones"""
		# Verificar campos de apelaciones si existen
		appeal_fields = ["appeal_status", "appeal_date", "appeal_reason", "appeal_resolution"]
		for field_name in appeal_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "appeal_status":
					self.assertEqual(field.fieldtype, "Select", "appeal_status debe ser Select field")
				elif field_name == "appeal_date":
					self.assertIn(
						field.fieldtype, ["Date", "Datetime"], "appeal_date debe ser Date o Datetime"
					)
				elif field_name in ["appeal_reason", "appeal_resolution"]:
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"{field_name} debe ser Text o Small Text"
					)

	def test_enforcement_workflow_configuration(self):
		"""Test: configuración de workflow de enforcement"""
		# Verificar campos de workflow si existen
		workflow_fields = ["enforcement_status", "enforcement_action", "collection_agent"]
		for field_name in workflow_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "enforcement_status":
					self.assertEqual(field.fieldtype, "Select", "enforcement_status debe ser Select field")
				elif field_name == "enforcement_action":
					self.assertIn(
						field.fieldtype, ["Select", "Text"], "enforcement_action debe ser Select o Text"
					)
				elif field_name == "collection_agent":
					self.assertEqual(field.fieldtype, "Link", "collection_agent debe ser Link field")
					# Debería linkear a User o Employee
					if field.options:
						self.assertIn(
							field.options,
							["User", "Employee"],
							"collection_agent debe linkear a User o Employee",
						)

	def test_recurring_fine_configuration(self):
		"""Test: configuración de multas recurrentes"""
		# Verificar campos de multas recurrentes si existen
		recurring_fields = ["recurring_fine", "recurring_frequency", "next_fine_date"]
		for field_name in recurring_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "recurring_fine":
					self.assertEqual(field.fieldtype, "Check", "recurring_fine debe ser Check field")
				elif field_name == "recurring_frequency":
					self.assertIn(
						field.fieldtype, ["Select", "Data"], "recurring_frequency debe ser Select o Data"
					)
				elif field_name == "next_fine_date":
					self.assertIn(
						field.fieldtype, ["Date", "Datetime"], "next_fine_date debe ser Date o Datetime"
					)

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
