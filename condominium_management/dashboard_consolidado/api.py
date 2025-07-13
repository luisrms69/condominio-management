# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Dashboard Consolidado Multi-Módulo - APIs Backend
================================================

Centro de Control Ejecutivo del Sistema que consolida información
de todos los módulos implementados.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

import frappe
import redis
from frappe import _
from frappe.utils import add_days, flt, getdate, now


@frappe.whitelist()
def get_dashboard_overview(dashboard_config: str | None = None, company: str | None = None) -> dict[str, Any]:
	"""
	Obtiene vista general del dashboard con KPIs principales

	Args:
		dashboard_config: ID de configuración específica
		company: Filtro por empresa específica

	Returns:
		Dict con overview completo del dashboard
	"""
	try:
		# Obtener configuración del dashboard
		config = _get_dashboard_config(dashboard_config)

		# Aplicar filtro de empresa si es necesario
		company_filter = company or config.get("company_filter")

		# Obtener KPIs principales de cada módulo
		overview_data = {
			"timestamp": now(),
			"dashboard_config": dashboard_config,
			"company_filter": company_filter,
			"modules": {
				"companies": _get_companies_overview(company_filter),
				"physical_spaces": _get_physical_spaces_overview(company_filter),
				"document_generation": _get_document_generation_overview(company_filter),
				"community_contributions": _get_community_contributions_overview(company_filter),
				"committee_management": _get_committee_management_overview(company_filter),
				"api_documentation_system": _get_api_documentation_overview(company_filter),
			},
			"system_health": _get_system_health(),
			"active_alerts": _get_active_alerts(company_filter),
		}

		return {"success": True, "data": overview_data}

	except Exception as e:
		frappe.log_error(f"Error en get_dashboard_overview: {e!s}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_kpi_data(
	kpi_code: str, company: str | None = None, date_range: str = "last_30_days"
) -> dict[str, Any]:
	"""
	Obtiene datos específicos de un KPI con histórico

	Args:
		kpi_code: Código del KPI a consultar
		company: Filtro por empresa
		date_range: Rango de fechas (last_7_days, last_30_days, last_90_days)

	Returns:
		Dict con datos del KPI y tendencias
	"""
	try:
		# Obtener definición del KPI
		kpi_def = frappe.get_doc("KPI Definition", kpi_code)

		if not kpi_def or not kpi_def.is_active:
			return {"success": False, "error": f"KPI {kpi_code} no encontrado o inactivo"}

		# Calcular rango de fechas
		end_date = getdate()
		if date_range == "last_7_days":
			start_date = add_days(end_date, -7)
		elif date_range == "last_30_days":
			start_date = add_days(end_date, -30)
		elif date_range == "last_90_days":
			start_date = add_days(end_date, -90)
		else:
			start_date = add_days(end_date, -30)

		# Obtener datos del KPI
		kpi_data = _calculate_kpi_value(kpi_def, company, start_date, end_date)

		return {"success": True, "data": kpi_data}

	except Exception as e:
		frappe.log_error(f"Error en get_kpi_data: {e!s}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_widget_data(widget_config: str, company: str | None = None) -> dict[str, Any]:
	"""
	Obtiene datos específicos para un widget del dashboard

	Args:
		widget_config: Configuración JSON del widget
		company: Filtro por empresa

	Returns:
		Dict con datos formateados para el widget
	"""
	try:
		# Parsear configuración del widget
		config = json.loads(widget_config) if isinstance(widget_config, str) else widget_config
		widget_type = config.get("widget_type")
		config.get("data_source")

		# Enrutar según tipo de widget
		if widget_type == "Tarjeta KPI":
			return _get_kpi_card_data(config, company)
		elif widget_type == "Gráfico":
			return _get_chart_data(config, company)
		elif widget_type == "Tabla":
			return _get_table_data(config, company)
		elif widget_type == "Mapa":
			return _get_map_data(config, company)
		elif widget_type == "Alerta":
			return _get_alert_data(config, company)
		else:
			return {"success": False, "error": f"Tipo de widget {widget_type} no soportado"}

	except Exception as e:
		frappe.log_error(f"Error en get_widget_data: {e!s}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dashboard_data(dashboard_config: str | None = None, company: str | None = None) -> dict[str, Any]:
	"""
	Obtiene datos completos del dashboard - wrapper para get_dashboard_overview

	Args:
		dashboard_config: ID de configuración del dashboard
		company: Filtro por empresa

	Returns:
		Dict con datos del dashboard
	"""
	return get_dashboard_overview(dashboard_config, company)


@frappe.whitelist()
def create_dashboard_snapshot(
	dashboard_config: str, company: str | None = None, notes: str = ""
) -> dict[str, Any]:
	"""
	Crea un snapshot del estado actual del dashboard

	Args:
		dashboard_config: ID de configuración del dashboard
		company: Filtro por empresa
		notes: Notas del snapshot

	Returns:
		Dict con resultado de creación del snapshot
	"""
	try:
		# Obtener datos actuales del dashboard
		overview_data = get_dashboard_overview(dashboard_config, company)

		if not overview_data.get("success"):
			return overview_data

		# Crear documento snapshot
		snapshot = frappe.new_doc("Dashboard Snapshot")
		snapshot.update(
			{
				"snapshot_date": now(),
				"dashboard_config": dashboard_config,
				"company": company,
				"snapshot_type": "Manual",
				"triggered_by": frappe.session.user,
				"kpi_values": json.dumps(overview_data["data"]["modules"]),
				"active_alerts": json.dumps(overview_data["data"]["active_alerts"]),
				"system_health": json.dumps(overview_data["data"]["system_health"]),
				"notes": notes,
			}
		)

		snapshot.insert()
		frappe.db.commit()

		return {"success": True, "snapshot_id": snapshot.name, "message": "Snapshot creado exitosamente"}

	except Exception as e:
		frappe.log_error(f"Error en create_dashboard_snapshot: {e!s}")
		return {"success": False, "error": str(e)}


# Funciones auxiliares privadas


def _get_dashboard_config(dashboard_config: str | None = None) -> dict[str, Any]:
	"""Obtiene configuración del dashboard"""
	if not dashboard_config:
		# Buscar dashboard por defecto para el rol del usuario
		user_roles = frappe.get_roles()
		default_config = frappe.db.get_value(
			"Dashboard Configuration",
			{"user_role": ["in", user_roles], "is_default": 1, "is_active": 1},
			["name", "dashboard_type", "refresh_interval", "company_filter"],
			as_dict=True,
		)
		return default_config or {}
	else:
		return frappe.get_doc("Dashboard Configuration", dashboard_config).as_dict()


def _get_companies_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo Companies"""
	filters = {}
	if company_filter:
		filters["company"] = company_filter

	return {
		"total_companies": frappe.db.count("Company", filters),
		"active_contracts": frappe.db.count("Service Management Contract", dict(filters, **{"is_active": 1})),
		"compliance_rate": _calculate_compliance_rate(company_filter),
		"last_sync": frappe.db.get_value("Master Data Sync Configuration", filters, "last_sync_date"),
	}


def _get_physical_spaces_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo Physical Spaces"""
	filters = {}
	if company_filter:
		filters["company"] = company_filter

	return {
		"total_spaces": frappe.db.count("Physical Space", filters),
		"maintenance_due": _get_maintenance_due_count(company_filter),
		"utilization_rate": _calculate_space_utilization(company_filter),
		"component_health": _calculate_component_health(company_filter),
	}


def _get_document_generation_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo Document Generation"""
	today = getdate()

	return {
		"documents_today": frappe.db.count("Master Template Registry", {"creation": [">=", today]}),
		"template_count": frappe.db.count("Master Template Registry", {"is_active": 1}),
		"success_rate": _calculate_generation_success_rate(),
		"pending_generations": _get_pending_generations_count(),
	}


def _get_community_contributions_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo Community Contributions"""
	filters = {}
	if company_filter:
		filters["company"] = company_filter

	return {
		"total_contributions": frappe.db.count("Contribution Request", filters),
		"active_contributors": frappe.db.count(
			"Registered Contributor Site", dict(filters, **{"is_active": 1})
		),
		"contribution_categories": frappe.db.count("Contribution Category", {"is_active": 1}),
		"recent_activity": _get_recent_contributions(company_filter),
	}


def _get_committee_management_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo Committee Management"""
	filters = {}
	if company_filter:
		filters["company"] = company_filter

	return {
		"active_committees": frappe.db.count("Committee Member", dict(filters, **{"is_active": 1})),
		"upcoming_meetings": _get_upcoming_meetings_count(company_filter),
		"pending_agreements": frappe.db.count("Agreement Tracking", dict(filters, **{"status": "Pendiente"})),
		"active_polls": frappe.db.count("Committee Poll", dict(filters, **{"status": "Abierta"})),
	}


def _get_api_documentation_overview(company_filter: str | None = None) -> dict[str, Any]:
	"""Obtiene overview del módulo API Documentation System"""
	return {
		"documented_apis": frappe.db.count("API Documentation", {"is_active": 1}),
		"code_examples": frappe.db.count("API Code Example"),
		"portal_visits": _get_portal_visit_count(),
		"api_usage_trend": _get_api_usage_trend(),
	}


def _get_system_health() -> dict[str, Any]:
	"""Obtiene estado general del sistema"""
	return {
		"database_size": _get_database_size(),
		"active_users": _get_active_users_count(),
		"system_load": _get_system_load(),
		"last_backup": _get_last_backup_date(),
	}


def _get_active_alerts(company_filter: str | None = None) -> list[dict[str, Any]]:
	"""Obtiene alertas activas del sistema"""
	# Por ahora retornar array vacío, se implementará con el sistema de alertas
	return []


# Funciones de cálculo específicas (stubs para implementación posterior)


def _calculate_compliance_rate(company_filter: str | None = None) -> float:
	"""Calcula tasa de cumplimiento"""
	return 85.5  # Placeholder


def _get_maintenance_due_count(company_filter: str | None = None) -> int:
	"""Cuenta mantenimientos vencidos"""
	return 0  # Placeholder


def _calculate_space_utilization(company_filter: str | None = None) -> float:
	"""Calcula utilización de espacios"""
	return 75.2  # Placeholder


def _calculate_component_health(company_filter: str | None = None) -> float:
	"""Calcula salud de componentes"""
	return 92.1  # Placeholder


def _calculate_generation_success_rate() -> float:
	"""Calcula tasa de éxito de generación"""
	return 98.5  # Placeholder


def _get_pending_generations_count() -> int:
	"""Cuenta generaciones pendientes"""
	return 0  # Placeholder


def _get_recent_contributions(company_filter: str | None = None) -> int:
	"""Obtiene contribuciones recientes"""
	return 5  # Placeholder


def _get_upcoming_meetings_count(company_filter: str | None = None) -> int:
	"""Cuenta reuniones próximas"""
	return 3  # Placeholder


def _get_portal_visit_count() -> int:
	"""Cuenta visitas al portal"""
	return 150  # Placeholder


def _get_api_usage_trend() -> str:
	"""Obtiene tendencia de uso de APIs"""
	return "Creciente"  # Placeholder


def _get_database_size() -> str:
	"""Obtiene tamaño de base de datos"""
	return "2.5 GB"  # Placeholder


def _get_active_users_count() -> int:
	"""Cuenta usuarios activos"""
	return 25  # Placeholder


def _get_system_load() -> str:
	"""Obtiene carga del sistema"""
	return "Normal"  # Placeholder


def _get_last_backup_date() -> str:
	"""Obtiene fecha del último backup"""
	return "2025-01-13 02:00:00"  # Placeholder


def _calculate_kpi_value(kpi_def, company, start_date, end_date):
	"""Calcula valor de KPI específico"""
	return {
		"current_value": 100,
		"previous_value": 95,
		"trend": "up",
		"change_percentage": 5.26,
	}  # Placeholder


def _get_kpi_card_data(config, company):
	"""Obtiene datos para tarjeta KPI"""
	return {"success": True, "data": {"value": 100, "trend": "up"}}


def _get_chart_data(config, company):
	"""Obtiene datos para gráfico"""
	return {"success": True, "data": {"labels": [], "datasets": []}}


def _get_table_data(config, company):
	"""Obtiene datos para tabla"""
	return {"success": True, "data": {"headers": [], "rows": []}}


def _get_map_data(config, company):
	"""Obtiene datos para mapa"""
	return {"success": True, "data": {"locations": []}}


def _get_alert_data(config, company):
	"""Obtiene datos de alertas"""
	return {"success": True, "data": {"alerts": []}}
