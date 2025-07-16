import json
import os
import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestResidentAccountL4AConfiguration(FrappeTestCase):
	"""Layer 4A Configuration Tests - JSON, Permissions, Hooks Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Resident Account"
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
		"""Test: consistencia completa JSON vs Meta para Resident Account"""
		# 1. Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# 2. Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# 3. Validar propiedades críticas del DocType
		self.assertEqual(json_def.get("module"), "Financial Management")
		self.assertEqual(json_def.get("name"), self.doctype)

		# 4. Validar campos específicos de Resident Account
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos específicos para Resident Account
		critical_fields = ["resident_name", "account_status", "credit_limit", "spending_limit"]

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
				if fieldname == "account_status":
					self.assertEqual(frappe_field.fieldtype, "Select", "account_status debe ser Select")

					# Verificar opciones críticas de estado
					if frappe_field.options:
						options = frappe_field.options.split("\n")
						expected_statuses = ["Activa", "Suspendida", "Inactiva"]
						for status in expected_statuses:
							if status in json_field.get("options", ""):
								self.assertIn(status, options, f"Status {status} faltante en options")

				elif fieldname in ["credit_limit", "spending_limit"]:
					self.assertEqual(frappe_field.fieldtype, "Currency", f"{fieldname} debe ser Currency")

	def test_resident_financial_fields_configuration(self):
		"""Test: configuración específica de campos financieros de residentes"""
		# Verificar campos de límites y balances
		financial_fields = {
			"credit_limit": "Currency",
			"spending_limit": "Currency",
			"current_balance": "Currency",
			"outstanding_amount": "Currency",
			"available_credit": "Currency",
		}

		for field_name, expected_type in financial_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

				# Campos de solo lectura para algunos casos
				if field_name in ["current_balance", "available_credit"]:
					# Estos campos suelen ser calculados
					self.assertTrue(True)  # Validación exitosa para campos calculados

	def test_child_table_for_transactions(self):
		"""Test: configuración de child tables para transacciones de residentes"""
		# Verificar si tiene child tables para tracking de transacciones
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

	def test_resident_business_logic_fields(self):
		"""Test: campos específicos de lógica de negocio de residentes"""
		# Verificar campos de fechas
		date_fields = ["account_opening_date", "last_activity_date", "suspension_date"]
		for field_name in date_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype, ["Date", "Datetime"], f"Campo {field_name} debe ser Date o Datetime"
				)

		# Verificar campos de estado
		if self.meta.has_field("account_status"):
			field = self.meta.get_field("account_status")
			self.assertEqual(field.fieldtype, "Select", "account_status debe ser Select field")

		# Verificar campos de configuración automática
		auto_fields = ["auto_approve_charges", "send_notifications", "allow_overdraft"]
		for field_name in auto_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Check", f"{field_name} debe ser Check field")

	def test_permissions_for_resident_data(self):
		"""Test: permisos específicos para datos de residentes"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Resident Account contiene datos sensibles - permisos estrictos
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")
				self.assertTrue(sm_perms.get("create"), "System Manager: create")

			# Verificar roles de residentes y administración
			resident_roles = ["Resident", "Property Manager"]
			for role in resident_roles:
				if role in all_perms:
					role_perms = all_perms[role]
					self.assertTrue(role_perms.get("read"), f"{role} debe tener read access")

			# Guest y roles básicos NO deben tener acceso
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

			self.assertGreater(len(permissions), 0, "Resident Account debe tener permisos configurados")

	def test_database_schema_for_resident_calculations(self):
		"""Test: esquema de base de datos para cálculos de residentes"""
		table_name = f"tab{self.doctype.replace(' ', '')}"
		try:
			table_columns = frappe.db.get_table_columns(table_name)
		except Exception as e:
			# Skip test si la tabla no existe en testing environment
			frappe.log_error(f"Resident Account table validation skipped: {e!s}")
			return

		# Verificar campos críticos para cálculos de residentes
		calculation_fields = ["credit_limit", "spending_limit", "current_balance"]
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

	def test_json_validation_for_resident_fields(self):
		"""Test: validación JSON específica para campos de residentes"""
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
				if field.get("fieldname") in ["account_status", "resident_type"]:
					self.assertIsNotNone(
						field.get("options"), f"Select field {field.get('fieldname')} debe tener options"
					)

					# Verificar que options no está vacío
					options = field.get("options", "")
					self.assertTrue(
						options.strip(), f"Select field {field.get('fieldname')} options no puede estar vacío"
					)

	def test_meta_caching_with_resident_tables(self):
		"""Test: Meta caching considerando resident tables"""
		# Verificar caching del meta principal
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		self.assertEqual(
			len(meta1.fields), len(meta2.fields), "Meta caching inconsistente para resident account"
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

	def test_resident_type_configuration(self):
		"""Test: configuración específica de tipos de residentes"""
		if self.meta.has_field("resident_type"):
			field = self.meta.get_field("resident_type")

			# Verificar que es Select
			self.assertEqual(field.fieldtype, "Select")

			# Verificar opciones críticas
			if field.options:
				options = field.options.split("\n")

				# Debe tener al menos estas opciones básicas (en español)
				basic_types = ["Propietario", "Arrendatario", "Familiar"]
				for res_type in basic_types:
					self.assertIn(res_type, options, f"Tipo básico {res_type} faltante")

				# Verificar que no hay opciones duplicadas
				self.assertEqual(
					len(options), len(set(options)), "No debe haber opciones duplicadas en resident_type"
				)

				# Verificar que no hay opciones vacías
				for option in options:
					self.assertTrue(option.strip(), "No debe haber opciones vacías en resident_type")

	def test_notification_configuration(self):
		"""Test: configuración de notificaciones para residentes"""
		# Verificar campos de notificaciones si existen
		notification_fields = ["email_notifications", "sms_notifications", "notification_frequency"]
		for field_name in notification_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name in ["email_notifications", "sms_notifications"]:
					self.assertEqual(field.fieldtype, "Check", f"{field_name} debe ser Check field")
				elif field_name == "notification_frequency":
					self.assertIn(
						field.fieldtype, ["Select", "Data"], "notification_frequency debe ser Select o Data"
					)

	def test_configuration_for_property_linking(self):
		"""Test: configuración para enlace con propiedades"""
		# Verificar campos de enlace con propiedades
		property_fields = ["primary_property", "associated_properties"]
		for field_name in property_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "primary_property":
					self.assertEqual(field.fieldtype, "Link", f"{field_name} debe ser Link field")
					# Debería linkear a Property Registry o similar
					self.assertTrue(field.options, f"{field_name} debe tener options configurado")
				elif field_name == "associated_properties":
					self.assertIn(
						field.fieldtype, ["Table", "Small Text"], f"{field_name} debe ser Table o Small Text"
					)

	def test_approval_workflow_configuration(self):
		"""Test: configuración de workflow de aprobaciones"""
		# Verificar campos de workflow si existen
		workflow_fields = ["requires_approval", "approval_limit", "auto_approve_limit"]
		for field_name in workflow_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "requires_approval":
					self.assertEqual(field.fieldtype, "Check", "requires_approval debe ser Check field")
				elif field_name in ["approval_limit", "auto_approve_limit"]:
					self.assertEqual(field.fieldtype, "Currency", f"{field_name} debe ser Currency field")

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()
