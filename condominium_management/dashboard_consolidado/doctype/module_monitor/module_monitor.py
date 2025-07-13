# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class ModuleMonitor(Document):
	"""Monitor de estado y métricas de módulos del sistema"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_module_configuration()
		self.set_initial_status()

	def before_save(self):
		"""Actualizaciones antes de guardar"""
		self.update_last_check()

	def validate_module_configuration(self):
		"""Valida configuración del módulo"""
		if not self.module_name:
			frappe.throw("El nombre del módulo es obligatorio")

		valid_modules = [
			"Companies",
			"Committee Management",
			"Physical Spaces",
			"Document Generation",
			"API Documentation System",
			"Dashboard Consolidado",
			"Community Contributions",
		]

		if self.module_name not in valid_modules:
			frappe.throw(f"Módulo inválido. Opciones: {', '.join(valid_modules)}")

	def set_initial_status(self):
		"""Establece estado inicial"""
		if not hasattr(self, "status") or not self.status:
			self.status = "Activo"

		if not hasattr(self, "last_check_date") or not self.last_check_date:
			self.last_check_date = now()

	def update_last_check(self):
		"""Actualiza fecha de última verificación"""
		self.last_check_date = now()

	def get_module_status(self):
		"""Obtiene estado actual del módulo"""
		try:
			# Verificar si el módulo está disponible
			module_status = self.check_module_availability()

			# Obtener métricas básicas
			metrics = self.get_module_metrics()

			# Verificar health checks
			health_status = self.run_health_checks()

			return {
				"module_name": self.module_name,
				"status": module_status,
				"metrics": metrics,
				"health": health_status,
				"last_check": self.last_check_date,
			}

		except Exception as e:
			frappe.log_error(f"Error getting module status for {self.module_name}: {e!s}")
			return {"module_name": self.module_name, "status": "Error", "error": str(e), "last_check": now()}

	def check_module_availability(self):
		"""Verifica disponibilidad del módulo"""
		try:
			# Verificar si las tablas principales del módulo existen
			main_doctypes = self.get_main_doctypes()

			for doctype in main_doctypes:
				if not frappe.db.exists("DocType", doctype):
					return "Inactivo"

			return "Activo"

		except Exception:
			return "Error"

	def get_main_doctypes(self):
		"""Obtiene DocTypes principales del módulo"""
		module_doctypes = {
			"Companies": ["Company", "Property Registry", "Condominium Information"],
			"Committee Management": ["Committee Meeting", "Committee Member", "Committee Poll"],
			"Physical Spaces": ["Physical Space", "Space Category", "Component Type"],
			"Document Generation": ["Master Template Registry", "Entity Configuration"],
			"API Documentation System": ["API Documentation", "API Parameter"],
			"Dashboard Consolidado": ["Dashboard Configuration", "KPI Definition", "Alert Configuration"],
			"Community Contributions": ["Contribution Request", "Contribution Category"],
		}

		return module_doctypes.get(self.module_name, [])

	def get_module_metrics(self):
		"""Obtiene métricas del módulo"""
		try:
			main_doctypes = self.get_main_doctypes()
			metrics = {}

			for doctype in main_doctypes:
				try:
					count = frappe.db.count(doctype)
					metrics[f"{doctype.lower().replace(' ', '_')}_count"] = count
				except Exception:
					metrics[f"{doctype.lower().replace(' ', '_')}_count"] = 0

			# Métricas adicionales específicas del módulo
			if self.module_name == "Dashboard Consolidado":
				metrics.update(self.get_dashboard_specific_metrics())

			return metrics

		except Exception as e:
			frappe.log_error(f"Error getting metrics for {self.module_name}: {e!s}")
			return {}

	def get_dashboard_specific_metrics(self):
		"""Obtiene métricas específicas del Dashboard Consolidado"""
		try:
			return {
				"active_dashboards": frappe.db.count("Dashboard Configuration", {"is_active": 1}),
				"total_kpis": frappe.db.count("KPI Definition", {"is_active": 1}),
				"active_alerts": frappe.db.count("Alert Configuration", {"is_active": 1}),
				"snapshots_today": frappe.db.count(
					"Dashboard Snapshot", {"snapshot_date": [">=", frappe.utils.today()]}
				),
			}
		except Exception:
			return {}

	def run_health_checks(self):
		"""Ejecuta verificaciones de salud del módulo"""
		health_checks = []

		try:
			# Verificar conectividad de base de datos
			health_checks.append(self.check_database_connectivity())

			# Verificar permisos
			health_checks.append(self.check_permissions())

			# Verificar configuración
			health_checks.append(self.check_configuration())

			# Determinar estado general
			if all(check["status"] == "OK" for check in health_checks):
				overall_status = "Saludable"
			elif any(check["status"] == "ERROR" for check in health_checks):
				overall_status = "Crítico"
			else:
				overall_status = "Advertencia"

			return {"overall_status": overall_status, "checks": health_checks}

		except Exception as e:
			return {"overall_status": "Error", "error": str(e), "checks": []}

	def check_database_connectivity(self):
		"""Verifica conectividad de base de datos"""
		try:
			frappe.db.sql("SELECT 1")
			return {
				"name": "Database Connectivity",
				"status": "OK",
				"message": "Database connection successful",
			}
		except Exception as e:
			return {
				"name": "Database Connectivity",
				"status": "ERROR",
				"message": f"Database connection failed: {e!s}",
			}

	def check_permissions(self):
		"""Verifica permisos del módulo"""
		try:
			# Verificar permisos básicos
			can_read = frappe.has_permission("Dashboard Configuration", "read")

			if can_read:
				return {
					"name": "Permissions",
					"status": "OK",
					"message": "Permissions are configured correctly",
				}
			else:
				return {
					"name": "Permissions",
					"status": "WARNING",
					"message": "Some permissions may be missing",
				}

		except Exception as e:
			return {"name": "Permissions", "status": "ERROR", "message": f"Permission check failed: {e!s}"}

	def check_configuration(self):
		"""Verifica configuración del módulo"""
		try:
			# Verificaciones específicas de configuración
			config_issues = []

			if self.module_name == "Dashboard Consolidado":
				# Verificar que hay al menos un dashboard configurado
				dashboard_count = frappe.db.count("Dashboard Configuration")
				if dashboard_count == 0:
					config_issues.append("No hay dashboards configurados")

			if config_issues:
				return {
					"name": "Configuration",
					"status": "WARNING",
					"message": f"Configuration issues: {', '.join(config_issues)}",
				}
			else:
				return {"name": "Configuration", "status": "OK", "message": "Configuration is valid"}

		except Exception as e:
			return {
				"name": "Configuration",
				"status": "ERROR",
				"message": f"Configuration check failed: {e!s}",
			}
