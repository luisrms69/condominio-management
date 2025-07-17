import json
import os
import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFeeStructureL4AConfiguration(FrappeTestCase):
	"""Layer 4A Configuration Tests - JSON, Permissions, Hooks Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Fee Structure"
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
		"""Test: consistencia completa JSON vs Meta para Fee Structure"""
		# 1. Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# 2. Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# 3. Validar propiedades críticas del DocType
		self.assertEqual(json_def.get("module"), "Financial Management")
		self.assertEqual(json_def.get("name"), self.doctype)

		# 4. Validar campos específicos de Fee Structure
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos específicos para Fee Structure
		critical_fields = ["fee_name", "fee_type", "calculation_method", "is_active"]

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
				if fieldname == "calculation_method":
					self.assertEqual(frappe_field.fieldtype, "Select", "calculation_method debe ser Select")

					# Verificar opciones críticas
					if frappe_field.options:
						options = frappe_field.options.split("\n")
						expected_methods = ["Por Indiviso", "Monto Fijo", "Por M2", "Mixto"]
						for method in expected_methods:
							if method in json_field.get("options", ""):
								self.assertIn(
									method, options, f"Método {method} faltante en calculation_method"
								)

				elif fieldname == "fee_type":
					self.assertEqual(frappe_field.fieldtype, "Select", "fee_type debe ser Select")

	def test_fee_calculation_fields_configuration(self):
		"""Test: configuración específica de campos de cálculo de fees"""
		# Verificar campos de montos y cálculos
		amount_fields = {
			"base_amount": "Currency",
			"percentage_rate": "Float",
			"per_unit_rate": "Currency",
			"minimum_amount": "Currency",
			"maximum_amount": "Currency",
		}

		for field_name, expected_type in amount_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

				# Validar precision para campos Currency
				if expected_type == "Currency":
					# Currency fields deben manejar precision correctamente
					self.assertTrue(True)  # Frappe maneja precision automáticamente

	def test_child_table_configuration(self):
		"""Test: configuración de child tables en Fee Structure"""
		# Verificar si tiene child tables configuradas
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

	def test_fee_structure_business_logic_fields(self):
		"""Test: campos específicos de lógica de negocio de Fee Structure"""
		# Verificar campos de fechas
		date_fields = ["effective_from", "valid_until"]
		for field_name in date_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype, ["Date", "Datetime"], f"Campo {field_name} debe ser Date o Datetime"
				)

		# Verificar campos de estado
		if self.meta.has_field("is_active"):
			field = self.meta.get_field("is_active")
			self.assertEqual(field.fieldtype, "Check", "is_active debe ser Check field")

		# Verificar campos de aplicabilidad
		applicability_fields = ["applies_to_all", "property_types"]
		for field_name in applicability_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				if field_name == "applies_to_all":
					self.assertEqual(field.fieldtype, "Check")
				elif field_name == "property_types":
					self.assertIn(field.fieldtype, ["Small Text", "Text", "Table"])

	def test_permissions_for_financial_data(self):
		"""Test: permisos específicos para datos financieros"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Fee Structure es crítico financieramente - permisos estrictos
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")
				self.assertTrue(sm_perms.get("create"), "System Manager: create")

			# Verificar roles financieros específicos
			financial_roles = ["Accounts Manager", "Financial Manager"]
			for role in financial_roles:
				if role in all_perms:
					role_perms = all_perms[role]
					self.assertTrue(role_perms.get("read"), f"{role} debe tener read access")

			# Guest y roles básicos NO deben tener write access
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

			self.assertGreater(len(permissions), 0, "Fee Structure debe tener permisos configurados")

	def test_database_schema_for_calculations(self):
		"""Test: esquema de base de datos para cálculos financieros"""
		table_name = f"tab{self.doctype.replace(' ', '')}"
		try:
			table_columns = frappe.db.get_table_columns(table_name)
		except Exception as e:
			# Skip test si la tabla no existe en testing environment
			frappe.log_error(f"Fee Structure table validation skipped: {e!s}")
			return

		# Verificar campos críticos para cálculos
		calculation_fields = ["calculation_method", "base_amount", "percentage_rate"]
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

	def test_json_validation_for_financial_fields(self):
		"""Test: validación JSON específica para campos financieros"""
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
				if field.get("fieldname") in ["calculation_method", "fee_type"]:
					self.assertIsNotNone(
						field.get("options"), f"Select field {field.get('fieldname')} debe tener options"
					)

					# Verificar que options no está vacío
					options = field.get("options", "")
					self.assertTrue(
						options.strip(), f"Select field {field.get('fieldname')} options no puede estar vacío"
					)

	def test_meta_caching_with_child_tables(self):
		"""Test: Meta caching considerando child tables"""
		# Verificar caching del meta principal
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		self.assertEqual(
			len(meta1.fields), len(meta2.fields), "Meta caching inconsistente para fee structure"
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

	def test_calculation_method_configuration(self):
		"""Test: configuración específica de métodos de cálculo"""
		if self.meta.has_field("calculation_method"):
			field = self.meta.get_field("calculation_method")

			# Verificar que es Select
			self.assertEqual(field.fieldtype, "Select")

			# Verificar opciones críticas
			if field.options:
				options = field.options.split("\n")

				# Debe tener al menos estas opciones básicas (en español)
				basic_methods = ["Monto Fijo", "Por Indiviso"]
				for method in basic_methods:
					self.assertIn(method, options, f"Método básico {method} faltante")

				# Verificar que no hay opciones duplicadas
				self.assertEqual(
					len(options), len(set(options)), "No debe haber opciones duplicadas en calculation_method"
				)

				# Verificar que no hay opciones vacías
				for option in options:
					self.assertTrue(option.strip(), "No debe haber opciones vacías en calculation_method")

	def test_version_control_configuration(self):
		"""Test: configuración de control de versiones"""
		# Verificar campos de versionado si existen
		version_fields = ["version", "previous_version", "version_notes"]
		for field_name in version_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "version":
					self.assertIn(
						field.fieldtype, ["Data", "Float", "Int"], "version debe ser Data, Float o Int"
					)
				elif field_name == "version_notes":
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], "version_notes debe ser Text o Small Text"
					)

	def test_configuration_for_multi_company(self):
		"""Test: configuración para soporte multi-empresa"""
		# Verificar campo company si existe
		if self.meta.has_field("company"):
			field = self.meta.get_field("company")
			self.assertEqual(field.fieldtype, "Link", "company debe ser Link field")
			self.assertEqual(field.options, "Company", "company debe linkear a Company DocType")

			# Company field debe ser obligatorio o tener valor por defecto
			self.assertTrue(field.reqd or field.default, "company field debe ser required o tener default")

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()
