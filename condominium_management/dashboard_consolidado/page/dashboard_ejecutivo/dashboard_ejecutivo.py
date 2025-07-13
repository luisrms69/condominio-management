# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Dashboard Ejecutivo - Backend de la Página
=========================================

Funciones backend para la página del Dashboard Ejecutivo.
"""

import frappe
from frappe import _


def get_context(context):
	"""Contexto para la página del Dashboard Ejecutivo"""

	# Verificar permisos
	if not frappe.has_permission("Dashboard Configuration", "read"):
		frappe.throw(_("No tiene permisos para acceder al Dashboard Ejecutivo"))

	# Configuración básica
	context.no_cache = 1
	context.title = _("Dashboard Ejecutivo - Centro de Control")

	# Datos del usuario
	context.user = frappe.session.user
	context.user_roles = frappe.get_roles()

	# Configuraciones disponibles para el usuario
	context.available_dashboards = get_user_dashboards()

	# Configuración por defecto
	context.default_dashboard = get_default_dashboard_config()

	return context


@frappe.whitelist()
def get_user_dashboards():
	"""Obtiene dashboards disponibles para el usuario actual"""

	user_roles = frappe.get_roles()

	dashboards = frappe.get_all(
		"Dashboard Configuration",
		filters={"user_role": ["in", user_roles], "is_active": 1},
		fields=["name", "dashboard_name", "dashboard_type", "is_default"],
		order_by="is_default DESC, dashboard_name ASC",
	)

	return dashboards


@frappe.whitelist()
def get_default_dashboard_config():
	"""Obtiene configuración por defecto del dashboard para el usuario"""

	user_roles = frappe.get_roles()

	# Buscar dashboard por defecto
	default_config = frappe.db.get_value(
		"Dashboard Configuration",
		{"user_role": ["in", user_roles], "is_default": 1, "is_active": 1},
		["name", "dashboard_name", "dashboard_type", "refresh_interval", "theme", "color_scheme"],
		as_dict=True,
		order_by="creation DESC",
	)

	if not default_config:
		# Si no hay configuración por defecto, usar la primera disponible
		default_config = frappe.db.get_value(
			"Dashboard Configuration",
			{"user_role": ["in", user_roles], "is_active": 1},
			["name", "dashboard_name", "dashboard_type", "refresh_interval", "theme", "color_scheme"],
			as_dict=True,
			order_by="creation DESC",
		)

	# Si aún no hay configuración, crear una básica
	if not default_config:
		default_config = {
			"name": None,
			"dashboard_name": "Dashboard Básico",
			"dashboard_type": "Ejecutivo",
			"refresh_interval": 30,
			"theme": "Claro",
			"color_scheme": "Predeterminado",
		}

	return default_config


@frappe.whitelist()
def get_dashboard_widgets(dashboard_config_name: str):
	"""Obtiene widgets configurados para un dashboard específico"""

	if not dashboard_config_name:
		return []

	try:
		dashboard_config = frappe.get_doc("Dashboard Configuration", dashboard_config_name)

		widgets = []
		for widget in dashboard_config.dashboard_widgets or []:
			widget_data = {
				"widget_type": widget.widget_type,
				"widget_name": widget.widget_name,
				"data_source": widget.data_source,
				"position_x": widget.position_x,
				"position_y": widget.position_y,
				"width": widget.width,
				"height": widget.height,
				"widget_config": widget.widget_config,
				"refresh_override": widget.refresh_override,
			}
			widgets.append(widget_data)

		return widgets

	except Exception as e:
		frappe.log_error(f"Error obteniendo widgets: {e!s}")
		return []


@frappe.whitelist()
def get_system_status():
	"""Obtiene estado general del sistema para el dashboard"""

	try:
		from ..api import get_dashboard_overview

		# Obtener overview general
		overview = get_dashboard_overview()

		if overview.get("success"):
			return {
				"success": True,
				"status": "healthy",
				"last_update": overview["data"]["timestamp"],
				"modules_count": len(overview["data"]["modules"]),
				"active_alerts": len(overview["data"]["active_alerts"]),
			}
		else:
			return {"success": False, "status": "error", "error": overview.get("error", "Error desconocido")}

	except Exception as e:
		frappe.log_error(f"Error obteniendo estado del sistema: {e!s}")
		return {"success": False, "status": "error", "error": str(e)}
