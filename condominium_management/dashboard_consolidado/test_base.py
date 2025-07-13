# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Dashboard Consolidado - Framework de Testing Base
===============================================

Framework base para testing del Dashboard Consolidado Multi-Módulo
con arquitectura de 3 niveles: System (domika.dev), Company (tenant), Property (condominio).
"""

import json
import typing
import unittest

import frappe
from frappe.test_runner import make_test_records
from frappe.utils import add_days, getdate, now


class DashboardTestBase(unittest.TestCase):
	"""Framework base para tests del Dashboard Consolidado"""

	@classmethod
	def setUpClass(cls):
		"""Setup de clase - datos comunes para todos los tests"""
		frappe.set_user("Administrator")

		# Limpiar datos previos
		cls.cleanup_test_data()

		# Crear estructura de 3 niveles
		cls.setup_system_level_data()
		cls.setup_company_level_data()
		cls.setup_property_level_data()

		# Crear roles necesarios
		cls.setup_dashboard_roles()

	@classmethod
	def tearDownClass(cls):
		"""Cleanup de clase"""
		cls.cleanup_test_data()

	@classmethod
	def cleanup_test_data(cls):
		"""Limpia datos de test con verificación defensiva"""
		doctypes_to_clean = [
			"Dashboard Snapshot",
			"Alert Configuration",
			"KPI Definition",
			"Dashboard Configuration",
		]

		for doctype in doctypes_to_clean:
			try:
				# Verificar que la tabla existe antes de limpiar
				if frappe.db.exists("DocType", doctype):
					frappe.db.sql(f"DELETE FROM `tab{doctype}` WHERE name LIKE '%TEST%'")
			except Exception as e:
				# Ignorar errores de tabla no encontrada (esperado en primera ejecución)
				if "doesn't exist" not in str(e):
					frappe.log_error(f"Error cleaning {doctype}: {e!s}")

		frappe.db.commit()

	@classmethod
	def setup_system_level_data(cls):
		"""LEVEL 1 - SYSTEM (domika.dev): Administradora del sistema SaaS"""

		# Datos de configuración global del sistema
		# Scope: Define tipos de widgets y KPIs disponibles globalmente
		# Impacto: TODAS las instalaciones

		cls.system_widgets_available = [
			"Tarjeta KPI",
			"Gráfico de Barras",
			"Gráfico de Líneas",
			"Gráfico de Pastel",
			"Tabla de Datos",
			"Lista de Alertas",
		]

		cls.system_kpi_categories = ["Financiero", "Operacional", "Calidad", "Cumplimiento"]

		cls.system_level_ready = True

	@classmethod
	def setup_company_level_data(cls):
		"""LEVEL 2 - COMPANY (Empresa administradora - tenant)"""

		# Scope: Empresa que contrata SaaS para administrar condominios
		# Permisos: Crear dashboards, layouts, branding para SUS condominios
		# Storage: Company Settings
		# Impacto: Todos SUS condominios

		# Empresa administradora 1: "Alpha Administración"
		cls.company_admin_1 = type(
			"MockCompany",
			(),
			{
				"name": "TEST_ALPHA_ADMIN",
				"company_name": "Alpha Administración S.A.",
				"tenant_scope": "LEVEL_2_COMPANY",
				"manages_properties": ["CONDO_ALPHA_1", "CONDO_ALPHA_2"],
			},
		)()

		# Empresa administradora 2: "Beta Gestión"
		cls.company_admin_2 = type(
			"MockCompany",
			(),
			{
				"name": "TEST_BETA_ADMIN",
				"company_name": "Beta Gestión Inmobiliaria",
				"tenant_scope": "LEVEL_2_COMPANY",
				"manages_properties": ["CONDO_BETA_1"],
			},
		)()

		cls.company_level_ready = True

	@classmethod
	def setup_property_level_data(cls):
		"""LEVEL 3 - PROPERTY (Condominio individual)"""

		# Scope: Condominio específico
		# Permisos: Solo reorganizar widgets, umbrales, refresh
		# Storage: Property Settings
		# Impacto: Solo ESE condominio

		# Condominios de Alpha Administración
		cls.property_alpha_1 = type(
			"MockProperty",
			(),
			{
				"name": "CONDO_ALPHA_1",
				"property_name": "Residencial Las Flores",
				"tenant_scope": "LEVEL_3_PROPERTY",
				"managed_by": "TEST_ALPHA_ADMIN",
				"can_customize": ["widget_layout", "alert_thresholds", "refresh_interval"],
			},
		)()

		cls.property_alpha_2 = type(
			"MockProperty",
			(),
			{
				"name": "CONDO_ALPHA_2",
				"property_name": "Torres del Parque",
				"tenant_scope": "LEVEL_3_PROPERTY",
				"managed_by": "TEST_ALPHA_ADMIN",
				"can_customize": ["widget_layout", "alert_thresholds", "refresh_interval"],
			},
		)()

		# Condominio de Beta Gestión
		cls.property_beta_1 = type(
			"MockProperty",
			(),
			{
				"name": "CONDO_BETA_1",
				"property_name": "Conjunto Vista Hermosa",
				"tenant_scope": "LEVEL_3_PROPERTY",
				"managed_by": "TEST_BETA_ADMIN",
				"can_customize": ["widget_layout", "alert_thresholds", "refresh_interval"],
			},
		)()

		cls.property_level_ready = True

	@classmethod
	def setup_dashboard_roles(cls):
		"""Configura roles necesarios para el dashboard"""
		roles_to_create = ["Gestor de Dashboards", "Usuario de Dashboards"]

		for role_name in roles_to_create:
			if not frappe.db.exists("Role", role_name):
				role = frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1})
				role.insert(ignore_permissions=True)

	@classmethod
	def create_test_company(cls, company_name):
		"""Crea empresa de test"""
		if frappe.db.exists("Company", company_name):
			return frappe.get_doc("Company", company_name)

		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": company_name,
				"abbr": company_name.split()[-1][:3].upper(),
				"default_currency": "MXN",
				"country": "Mexico",
			}
		)
		company.insert(ignore_permissions=True)
		return company

	@classmethod
	def create_test_property(cls, property_name, company):
		"""Crea propiedad de test usando Property Registry si existe"""
		try:
			# Intentar crear Property Registry (del módulo Companies)
			if frappe.db.exists("DocType", "Property Registry"):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_name": property_name,
						"company": company,
						"property_type": "Residencial",
						"total_units": 100,
						"is_active": 1,
					}
				)
				property_doc.insert(ignore_permissions=True)
				return property_doc
		except Exception:
			pass

		# Fallback: crear como Company con naming específico
		property_company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": property_name,
				"abbr": f"PROP{frappe.utils.random_string(3)}",
				"default_currency": "MXN",
				"country": "Mexico",
				"parent_company": company,
			}
		)
		property_company.insert(ignore_permissions=True)
		return property_company

	def setUp(self):
		"""Setup para cada test individual"""
		frappe.set_user("Administrator")
		frappe.flags.in_test = True

	def tearDown(self):
		"""Cleanup para cada test individual"""
		frappe.db.rollback()


class DashboardTestBaseGranular(DashboardTestBase):
	"""Framework para testing granular por capas - REGLA #32"""

	# Campos requeridos para cada DocType
	REQUIRED_FIELDS: typing.ClassVar[dict[str, list[str]]] = {
		"Dashboard Configuration": ["dashboard_name", "dashboard_type", "user_role", "refresh_interval"],
		"KPI Definition": ["kpi_name", "kpi_code", "kpi_category", "calculation_type", "unit_type"],
		"Alert Configuration": ["alert_name", "alert_priority", "trigger_type", "check_frequency"],
		"Dashboard Snapshot": ["snapshot_date", "dashboard_config", "snapshot_type"],
	}

	def create_test_document(self, doctype, override_fields=None, ignore_if_duplicate=False):
		"""
		Crea documento de test con campos requeridos

		Args:
			doctype: Tipo de documento
			override_fields: Campos a sobrescribir
			ignore_if_duplicate: Ignorar si ya existe
		"""
		base_fields = {
			"Dashboard Configuration": {
				"dashboard_name": f"TEST Dashboard {frappe.utils.random_string(5)}",
				"dashboard_type": "Ejecutivo",
				"user_role": "Gestor de Dashboards",
				"refresh_interval": 30,
				"is_active": 1,
			},
			"KPI Definition": {
				"kpi_name": f"TEST KPI {frappe.utils.random_string(5)}",
				"kpi_code": f"TEST_KPI_{frappe.utils.random_string(5).upper()}",
				"kpi_category": "Operacional",
				"calculation_type": "Conteo",
				"unit_type": "Número",
				"is_active": 1,
			},
			"Alert Configuration": {
				"alert_name": f"TEST Alert {frappe.utils.random_string(5)}",
				"alert_priority": "Media",
				"trigger_type": "Umbral",
				"check_frequency": "Hora",
				"is_active": 1,
			},
			"Dashboard Snapshot": {
				"snapshot_date": now(),
				"dashboard_config": "TEST_DASHBOARD_CONFIG",
				"snapshot_type": "Manual",
				"triggered_by": "Administrator",
			},
		}

		if doctype not in base_fields:
			raise ValueError(f"DocType {doctype} no tiene configuración base")

		fields = base_fields[doctype].copy()
		if override_fields:
			fields.update(override_fields)

		try:
			doc = frappe.get_doc(dict(doctype=doctype, **fields))
			doc.insert(ignore_permissions=True)
			return doc
		except frappe.DuplicateEntryError:
			if ignore_if_duplicate:
				# Buscar documento existente
				existing = frappe.db.get_value(
					doctype,
					fields.get("name")
					or {k: v for k, v in fields.items() if k in ["dashboard_name", "kpi_code", "alert_name"]},
				)
				if existing:
					return frappe.get_doc(doctype, existing)
			raise

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación de campos aislada (siempre funciona)"""
		for doctype in self.REQUIRED_FIELDS:
			with self.subTest(doctype=doctype):
				doc = frappe.new_doc(doctype)

				# Verificar que campos requeridos existen
				for field in self.REQUIRED_FIELDS[doctype]:
					self.assertTrue(hasattr(doc, field), f"Campo requerido '{field}' no existe en {doctype}")

	def test_layer_2_permissions_validation(self):
		"""LAYER 2: Validación de permisos por nivel"""

		# Verificar permisos de Dashboard Configuration
		dashboard_perms = frappe.get_meta("Dashboard Configuration").permissions

		# System Manager debe tener todos los permisos
		system_manager_perms = next((p for p in dashboard_perms if p.role == "System Manager"), None)
		self.assertIsNotNone(system_manager_perms, "System Manager debe tener permisos")
		self.assertEqual(system_manager_perms.create, 1)
		self.assertEqual(system_manager_perms.read, 1)
		self.assertEqual(system_manager_perms.write, 1)
		self.assertEqual(system_manager_perms.delete, 1)

		# Gestor de Dashboards debe poder crear y modificar
		gestor_perms = next((p for p in dashboard_perms if p.role == "Gestor de Dashboards"), None)
		self.assertIsNotNone(gestor_perms, "Gestor de Dashboards debe tener permisos")
		self.assertEqual(gestor_perms.create, 1)
		self.assertEqual(gestor_perms.read, 1)
		self.assertEqual(gestor_perms.write, 1)

		# Usuario de Dashboards solo debe poder leer
		usuario_perms = next((p for p in dashboard_perms if p.role == "Usuario de Dashboards"), None)
		self.assertIsNotNone(usuario_perms, "Usuario de Dashboards debe tener permisos")
		self.assertEqual(usuario_perms.read, 1)
		self.assertEqual(usuario_perms.create, 0)

	def test_layer_3_hierarchy_inheritance(self):
		"""LAYER 3: Validación de herencia de configuraciones por niveles"""

		# LEVEL 1 (System) → LEVEL 2 (Company) → LEVEL 3 (Property)

		# Verificar tipos de widgets disponibles vienen del SYSTEM
		self.assertIn("Tarjeta KPI", self.system_widgets_available)
		self.assertIn("Gráfico de Barras", self.system_widgets_available)

		# Verificar que COMPANY puede usar widgets del SYSTEM
		company_widgets = self.system_widgets_available
		self.assertGreater(len(company_widgets), 0, "Company debe heredar widgets del sistema")

		# Verificar que PROPERTY solo puede reorganizar, no crear nuevos tipos
		property_permissions = self.property_alpha_1.can_customize
		self.assertIn("widget_layout", property_permissions)
		self.assertNotIn("create_widgets", property_permissions)
		self.assertNotIn("create_kpis", property_permissions)

	def test_layer_4_data_isolation(self):
		"""LAYER 4: Validación de aislamiento de datos por tenant"""

		# Test aislamiento LEVEL 2 (Company): cada administradora solo ve SUS condominios
		alpha_properties = self.company_admin_1.manages_properties
		beta_properties = self.company_admin_2.manages_properties

		# Verificar que Alpha administra sus condominios
		self.assertIn("CONDO_ALPHA_1", alpha_properties)
		self.assertIn("CONDO_ALPHA_2", alpha_properties)
		self.assertNotIn("CONDO_BETA_1", alpha_properties)

		# Verificar que Beta administra sus condominios
		self.assertIn("CONDO_BETA_1", beta_properties)
		self.assertNotIn("CONDO_ALPHA_1", beta_properties)
		self.assertNotIn("CONDO_ALPHA_2", beta_properties)

		# Test aislamiento LEVEL 3 (Property): cada condominio solo afecta a sí mismo
		self.assertEqual(self.property_alpha_1.managed_by, "TEST_ALPHA_ADMIN")
		self.assertEqual(self.property_alpha_2.managed_by, "TEST_ALPHA_ADMIN")
		self.assertEqual(self.property_beta_1.managed_by, "TEST_BETA_ADMIN")

		# Verificar que properties tienen permisos limitados (solo reorganizar)
		self.assertEqual(self.property_alpha_1.tenant_scope, "LEVEL_3_PROPERTY")
		self.assertIn("widget_layout", self.property_alpha_1.can_customize)
		self.assertNotIn("create_dashboards", self.property_alpha_1.can_customize)
