# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json
import os

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


class TestPremiumServicesIntegrationL4AConfiguration(Layer4TestingMixin, FrappeTestCase):
	"""Layer 4A Configuration Tests - Premium Services Integration JSON vs Meta Consistency"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Premium Services Integration"
		cls.json_path = os.path.join(
			os.path.dirname(__file__), f"{cls.doctype.lower().replace(' ', '_')}.json"
		)

	def test_json_vs_meta_consistency(self):
		"""Test: consistencia completa JSON vs Meta object"""
		# Cargar JSON del DocType
		with open(self.json_path, encoding="utf-8") as f:
			json_def = json.load(f)

		# Obtener Meta de Frappe
		frappe_meta = frappe.get_meta(self.doctype)

		# Verificar consistencia de campos críticos
		critical_fields = ["naming_series", "service_name", "company", "service_type", "service_status"]

		for fieldname in critical_fields:
			# Buscar campo en JSON
			json_field = next(
				(f for f in json_def.get("fields", []) if f.get("fieldname") == fieldname), None
			)
			self.assertIsNotNone(json_field, f"Campo crítico {fieldname} no encontrado en JSON")

			# Obtener campo de Meta
			frappe_field = frappe_meta.get_field(fieldname)
			self.assertIsNotNone(frappe_field, f"Campo crítico {fieldname} no encontrado en Meta")

			# Validar consistencia
			self.assertEqual(json_field["fieldtype"], frappe_field.fieldtype)
			self.assertEqual(json_field.get("reqd", 0), int(frappe_field.reqd))

	def test_service_type_field_options_validation(self):
		"""Test: validación de opciones de service_type"""
		frappe_meta = frappe.get_meta(self.doctype)
		field = frappe_meta.get_field("service_type")

		# Get exact options from JSON
		expected_options = get_exact_field_options_from_json(self.doctype, "service_type")
		if expected_options:
			actual_options = [opt.strip() for opt in field.options.split("\n") if opt.strip()]

			for option in expected_options:
				self.assertIn(option, actual_options, f"Opción '{option}' faltante en service_type")
		else:
			# Fallback - expect basic service types
			expected_options = [
				"Spa y Bienestar",
				"Gimnasio",
				"Piscina",
				"Salón de Eventos",
				"Servicios Adicionales",
			]
			actual_options = [opt.strip() for opt in field.options.split("\n") if opt.strip()]

			for option in expected_options:
				self.assertIn(option, actual_options, f"Opción '{option}' faltante en service_type")

	def test_service_status_field_options_validation(self):
		"""Test: validación de opciones de service_status"""
		frappe_meta = frappe.get_meta(self.doctype)
		field = frappe_meta.get_field("service_status")

		# Get exact options from JSON
		expected_options = get_exact_field_options_from_json(self.doctype, "service_status")
		if expected_options:
			actual_options = [opt.strip() for opt in field.options.split("\n") if opt.strip()]

			for option in expected_options:
				self.assertIn(option, actual_options, f"Opción '{option}' faltante en service_status")
		else:
			# Fallback - expect basic status options
			expected_options = ["Activo", "Inactivo", "En Mantenimiento", "Suspendido"]
			actual_options = [opt.strip() for opt in field.options.split("\n") if opt.strip()]

			for option in expected_options:
				self.assertIn(option, actual_options, f"Opción '{option}' faltante en service_status")

	def test_permissions_configuration(self):
		"""Test: configuración de permisos del DocType"""
		perms = frappe.get_doc("DocType", self.doctype).permissions

		# Verificar que existen permisos configurados
		self.assertGreater(len(perms), 0, "No hay permisos configurados para Premium Services Integration")

		# Verificar permisos para roles administrativos
		admin_roles = ["System Manager", "Administrador Financiero", "Administrador de Servicios"]
		for perm in perms:
			if perm.role in admin_roles:
				# Roles administrativos deben tener permisos completos
				self.assertEqual(perm.read, 1, f"{perm.role} debe tener permiso de lectura")
				self.assertEqual(perm.write, 1, f"{perm.role} debe tener permiso de escritura")

	@skip_if_ci_cd
	def test_database_schema_validation(self):
		"""Test: validación de esquema de base de datos - ONLY LOCAL"""
		table_name = f"tab{self.doctype}"

		# This test ONLY runs in local environment
		table_columns = frappe.db.get_table_columns(table_name)

		# Verificar que las columnas críticas existen
		expected_columns = ["naming_series", "service_name", "company", "service_type", "service_status"]
		for column in expected_columns:
			self.assertIn(column, table_columns, f"Columna {column} faltante en tabla {table_name}")

	def test_meta_caching_consistency(self):
		"""Test: consistencia de caching de Meta objects"""
		# Obtener Meta dos veces
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		# Verificar que son consistentes
		self.assertEqual(len(meta1.fields), len(meta2.fields))
		self.assertEqual(meta1.autoname, meta2.autoname)
		self.assertEqual(meta1.naming_series, meta2.naming_series)

	def test_service_pricing_configuration(self):
		"""Test: configuración de precios de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos relacionados con pricing
		pricing_fields = ["base_price", "membership_price", "hourly_rate", "currency"]

		for field_name in pricing_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "currency":
					self.assertEqual(field.fieldtype, "Link", f"Campo {field_name} debe ser Link")
				else:
					self.assertEqual(field.fieldtype, "Currency", f"Campo {field_name} debe ser Currency")

	def test_service_integration_configuration(self):
		"""Test: configuración de integración con servicios externos"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de integración
		integration_fields = ["api_endpoint", "api_key", "integration_enabled", "sync_frequency"]

		for field_name in integration_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "integration_enabled":
					self.assertEqual(field.fieldtype, "Check", f"Campo {field_name} debe ser Check")
				elif field_name in ["api_endpoint", "api_key"]:
					self.assertIn(
						field.fieldtype, ["Data", "Password"], f"Campo {field_name} debe ser Data o Password"
					)

	def test_service_booking_configuration(self):
		"""Test: configuración de reservas de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de booking
		booking_fields = ["allow_booking", "booking_advance_days", "max_booking_duration", "booking_policy"]

		for field_name in booking_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "allow_booking":
					self.assertEqual(field.fieldtype, "Check", f"Campo {field_name} debe ser Check")
				elif field_name in ["booking_advance_days", "max_booking_duration"]:
					self.assertEqual(field.fieldtype, "Int", f"Campo {field_name} debe ser Int")
				elif field_name == "booking_policy":
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"Campo {field_name} debe ser Text"
					)

	def test_service_analytics_configuration(self):
		"""Test: configuración de análisis de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de analytics
		analytics_fields = [
			"usage_tracking",
			"revenue_tracking",
			"customer_satisfaction",
			"performance_metrics",
		]

		for field_name in analytics_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name in ["usage_tracking", "revenue_tracking"]:
					self.assertEqual(field.fieldtype, "Check", f"Campo {field_name} debe ser Check")
				elif field_name == "customer_satisfaction":
					self.assertIn(
						field.fieldtype, ["Float", "Percent"], f"Campo {field_name} debe ser Float o Percent"
					)

	def test_required_fields_validation(self):
		"""Test: validación de campos obligatorios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos que deben ser obligatorios
		required_fields = ["naming_series", "service_name", "company", "service_type", "service_status"]

		for fieldname in required_fields:
			field = frappe_meta.get_field(fieldname)
			if field:  # Solo validar si el campo existe
				self.assertEqual(field.reqd, 1, f"Campo {fieldname} debe ser obligatorio")

	def test_service_availability_configuration(self):
		"""Test: configuración de disponibilidad de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de disponibilidad
		availability_fields = [
			"operating_hours",
			"availability_calendar",
			"maintenance_schedule",
			"seasonal_availability",
		]

		for field_name in availability_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "operating_hours":
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"Campo {field_name} debe ser Text"
					)
				elif field_name == "availability_calendar":
					self.assertEqual(field.fieldtype, "Text", f"Campo {field_name} debe ser Text")

	def test_service_quality_configuration(self):
		"""Test: configuración de calidad de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de calidad
		quality_fields = [
			"quality_standards",
			"service_level_agreement",
			"quality_metrics",
			"feedback_system",
		]

		for field_name in quality_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "feedback_system":
					self.assertEqual(field.fieldtype, "Check", f"Campo {field_name} debe ser Check")
				else:
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"Campo {field_name} debe ser Text"
					)

	def test_service_staff_configuration(self):
		"""Test: configuración de personal de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de personal
		staff_fields = ["staff_required", "staff_qualifications", "staff_schedule", "staff_contact"]

		for field_name in staff_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "staff_required":
					self.assertEqual(field.fieldtype, "Int", f"Campo {field_name} debe ser Int")
				else:
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"Campo {field_name} debe ser Text"
					)

	def test_service_equipment_configuration(self):
		"""Test: configuración de equipamiento de servicios"""
		frappe_meta = frappe.get_meta(self.doctype)

		# Campos de equipamiento
		equipment_fields = [
			"equipment_list",
			"equipment_maintenance",
			"equipment_capacity",
			"equipment_safety",
		]

		for field_name in equipment_fields:
			field = frappe_meta.get_field(field_name)
			if field:  # Solo validar si el campo existe
				if field_name == "equipment_capacity":
					self.assertEqual(field.fieldtype, "Int", f"Campo {field_name} debe ser Int")
				else:
					self.assertIn(
						field.fieldtype, ["Text", "Small Text"], f"Campo {field_name} debe ser Text"
					)

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Call parent tearDown for CI/CD compatibility
		super().tearDown()
		frappe.db.rollback()
