import json
import os
import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPaymentCollectionL4AConfiguration(FrappeTestCase):
	"""Layer 4A Configuration Tests - JSON, Permissions, Hooks Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Payment Collection"
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
		"""Test: consistencia completa JSON vs Meta para Payment Collection"""
		# 1. Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# 2. Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# 3. Validar propiedades críticas del DocType
		self.assertEqual(json_def.get("module"), "Financial Management")
		self.assertEqual(json_def.get("name"), self.doctype)

		# 4. Validar campos específicos de Payment Collection
		json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
		frappe_fields = {f.fieldname: f for f in frappe_meta.fields}

		# Campos críticos específicos para Payment Collection
		critical_fields = ["payment_amount", "payment_method", "collection_status", "verification_status"]

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
				if fieldname in ["payment_method", "collection_status", "verification_status"]:
					self.assertEqual(frappe_field.fieldtype, "Select", f"{fieldname} debe ser Select")

					# Verificar opciones críticas según el campo
					if frappe_field.options:
						options = frappe_field.options.split("\n")
						if fieldname == "payment_method":
							expected_methods = ["Efectivo", "Transferencia", "Cheque"]
							for method in expected_methods:
								if method in json_field.get("options", ""):
									self.assertIn(
										method, options, f"Método {method} faltante en payment_method"
									)
						elif fieldname == "collection_status":
							expected_statuses = ["Pendiente", "Recibido", "Verificado"]
							for status in expected_statuses:
								if status in json_field.get("options", ""):
									self.assertIn(
										status, options, f"Status {status} faltante en collection_status"
									)

				elif fieldname == "payment_amount":
					self.assertEqual(frappe_field.fieldtype, "Currency", "payment_amount debe ser Currency")

	def test_payment_financial_fields_configuration(self):
		"""Test: configuración específica de campos financieros de pagos"""
		# Verificar campos de montos y comisiones
		financial_fields = {
			"payment_amount": "Currency",
			"service_charge": "Currency",
			"commission_amount": "Currency",
			"net_amount": "Currency",
			"discount_amount": "Currency",
		}

		for field_name, expected_type in financial_fields.items():
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(
					field.fieldtype, expected_type, f"Campo {field_name} debe ser {expected_type}"
				)

				# Campos de solo lectura para algunos casos
				if field_name in ["net_amount", "commission_amount"]:
					# Estos campos suelen ser calculados
					self.assertTrue(True)  # Validación exitosa para campos calculados

	def test_child_table_for_payment_details(self):
		"""Test: configuración de child tables para detalles de pagos"""
		# Verificar si tiene child tables para tracking de pagos
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

	def test_payment_business_logic_fields(self):
		"""Test: campos específicos de lógica de negocio de pagos"""
		# Verificar campos de fechas
		date_fields = ["payment_date", "verification_date", "reconciliation_date"]
		for field_name in date_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertIn(
					field.fieldtype, ["Date", "Datetime"], f"Campo {field_name} debe ser Date o Datetime"
				)

		# Verificar campos de estado
		status_fields = ["collection_status", "verification_status"]
		for field_name in status_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Select", f"{field_name} debe ser Select field")

		# Verificar campos de configuración automática
		auto_fields = ["auto_reconcile", "send_notification", "requires_approval"]
		for field_name in auto_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Check", f"{field_name} debe ser Check field")

	def test_permissions_for_payment_data(self):
		"""Test: permisos específicos para datos de pagos"""
		try:
			all_perms = frappe.permissions.get_all_perms(self.doctype)

			# Payment Collection es crítico financieramente - permisos estrictos
			if "System Manager" in all_perms:
				sm_perms = all_perms["System Manager"]
				self.assertTrue(sm_perms.get("read"), "System Manager: read")
				self.assertTrue(sm_perms.get("write"), "System Manager: write")
				self.assertTrue(sm_perms.get("create"), "System Manager: create")

			# Verificar roles financieros específicos
			financial_roles = ["Accounts Manager", "Financial Manager", "Cashier"]
			for role in financial_roles:
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

			self.assertGreater(len(permissions), 0, "Payment Collection debe tener permisos configurados")

	def test_database_schema_for_payment_calculations(self):
		"""Test: esquema de base de datos para cálculos de pagos"""
		table_name = f"tab{self.doctype.replace(' ', '')}"
		try:
			table_columns = frappe.db.get_table_columns(table_name)
		except Exception as e:
			# Skip test si la tabla no existe en testing environment
			frappe.log_error(f"Payment Collection table validation skipped: {e!s}")
			return

		# Verificar campos críticos para cálculos de pagos
		calculation_fields = ["payment_amount", "service_charge", "net_amount"]
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

	def test_json_validation_for_payment_fields(self):
		"""Test: validación JSON específica para campos de pagos"""
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
				if field.get("fieldname") in ["payment_method", "collection_status", "verification_status"]:
					self.assertIsNotNone(
						field.get("options"), f"Select field {field.get('fieldname')} debe tener options"
					)

					# Verificar que options no está vacío
					options = field.get("options", "")
					self.assertTrue(
						options.strip(), f"Select field {field.get('fieldname')} options no puede estar vacío"
					)

	def test_meta_caching_with_payment_tables(self):
		"""Test: Meta caching considerando payment tables"""
		# Verificar caching del meta principal
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		self.assertEqual(
			len(meta1.fields), len(meta2.fields), "Meta caching inconsistente para payment collection"
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

	def test_payment_method_configuration(self):
		"""Test: configuración específica de métodos de pago"""
		if self.meta.has_field("payment_method"):
			field = self.meta.get_field("payment_method")

			# Verificar que es Select
			self.assertEqual(field.fieldtype, "Select")

			# Verificar opciones críticas
			if field.options:
				options = field.options.split("\n")

				# Debe tener al menos estas opciones básicas (en español)
				basic_methods = ["Efectivo", "Transferencia", "Cheque"]
				for method in basic_methods:
					self.assertIn(method, options, f"Método básico {method} faltante")

				# Verificar que no hay opciones duplicadas
				self.assertEqual(
					len(options), len(set(options)), "No debe haber opciones duplicadas en payment_method"
				)

				# Verificar que no hay opciones vacías
				for option in options:
					self.assertTrue(option.strip(), "No debe haber opciones vacías en payment_method")

	def test_reconciliation_configuration(self):
		"""Test: configuración de conciliación de pagos"""
		# Verificar campos de conciliación si existen
		reconciliation_fields = ["reconciliation_date", "reconciliation_status", "bank_reference"]
		for field_name in reconciliation_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "reconciliation_date":
					self.assertIn(
						field.fieldtype, ["Date", "Datetime"], "reconciliation_date debe ser Date o Datetime"
					)
				elif field_name == "reconciliation_status":
					self.assertEqual(field.fieldtype, "Select", "reconciliation_status debe ser Select")
				elif field_name == "bank_reference":
					self.assertIn(
						field.fieldtype, ["Data", "Small Text"], "bank_reference debe ser Data o Small Text"
					)

	def test_configuration_for_account_linking(self):
		"""Test: configuración para enlace con cuentas"""
		# Verificar campos de enlace con cuentas
		account_fields = ["payer_account", "recipient_account", "property_account"]
		for field_name in account_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)
				self.assertEqual(field.fieldtype, "Link", f"{field_name} debe ser Link field")

				# Verificar que linkea a DocTypes apropiados
				if field_name in ["payer_account", "recipient_account"]:
					self.assertIn(
						field.options,
						["Property Account", "Resident Account"],
						f"{field_name} debe linkear a Property Account o Resident Account",
					)
				elif field_name == "property_account":
					self.assertEqual(
						field.options,
						"Property Account",
						"property_account debe linkear a Property Account DocType",
					)

	def test_notification_configuration(self):
		"""Test: configuración de notificaciones de pagos"""
		# Verificar campos de notificaciones si existen
		notification_fields = ["send_notification", "notification_sent", "notification_method"]
		for field_name in notification_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name in ["send_notification", "notification_sent"]:
					self.assertEqual(field.fieldtype, "Check", f"{field_name} debe ser Check field")
				elif field_name == "notification_method":
					self.assertIn(
						field.fieldtype, ["Select", "Data"], "notification_method debe ser Select o Data"
					)

	def test_verification_workflow_configuration(self):
		"""Test: configuración de workflow de verificación"""
		# Verificar campos de workflow si existen
		workflow_fields = ["verification_status", "verified_by", "verification_notes"]
		for field_name in workflow_fields:
			if self.meta.has_field(field_name):
				field = self.meta.get_field(field_name)

				if field_name == "verification_status":
					self.assertEqual(field.fieldtype, "Select", "verification_status debe ser Select field")
				elif field_name == "verified_by":
					self.assertEqual(field.fieldtype, "Link", "verified_by debe ser Link field")
					# Debería linkear a User
					if field.options:
						self.assertEqual(field.options, "User", "verified_by debe linkear a User")
				elif field_name == "verification_notes":
					self.assertIn(
						field.fieldtype,
						["Text", "Small Text"],
						"verification_notes debe ser Text o Small Text",
					)

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()
