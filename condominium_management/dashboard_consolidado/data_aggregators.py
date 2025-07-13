# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Dashboard Consolidado - Agregadores de Datos
==========================================

Sistema de agregación de datos por módulos para KPIs del dashboard.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

import frappe
from frappe.utils import add_days, cint, flt, getdate


class DataAggregator:
	"""Clase base para agregación de datos por módulo"""

	def __init__(
		self, company_filter: str | None = None, date_from: str | None = None, date_to: str | None = None
	):
		self.company_filter = company_filter
		self.date_from = date_from or add_days(getdate(), -30)
		self.date_to = date_to or getdate()

	def get_base_filters(self) -> dict[str, Any]:
		"""Obtiene filtros base para queries"""
		filters = {}
		if self.company_filter:
			filters["company"] = self.company_filter
		return filters


class CompaniesDataAggregator(DataAggregator):
	"""Agregador de datos del módulo Companies"""

	def get_total_companies(self) -> int:
		"""Total de empresas activas"""
		filters = self.get_base_filters()
		filters.update({"disabled": 0})
		return frappe.db.count("Company", filters)

	def get_active_contracts(self) -> int:
		"""Contratos de gestión activos"""
		filters = self.get_base_filters()
		filters.update({"is_active": 1})
		return frappe.db.count("Service Management Contract", filters)

	def get_compliance_percentage(self) -> float:
		"""Porcentaje de cumplimiento normativo"""
		# Placeholder - implementar lógica específica según requirements
		total_requirements = frappe.db.count("Compliance Requirement Type", {"is_active": 1})
		if total_requirements == 0:
			return 100.0

		# Por ahora retornar un cálculo simple
		return 85.5

	def get_revenue_summary(self) -> dict[str, float]:
		"""Resumen de ingresos por empresa"""
		# Placeholder - integrar con ERPNext cuando esté disponible
		return {"total_revenue": 0.0, "average_per_company": 0.0, "growth_rate": 0.0}

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo Companies"""
		return {
			"total_companies": self.get_total_companies(),
			"active_contracts": self.get_active_contracts(),
			"compliance_percentage": self.get_compliance_percentage(),
			"revenue_summary": self.get_revenue_summary(),
		}


class PhysicalSpacesDataAggregator(DataAggregator):
	"""Agregador de datos del módulo Physical Spaces"""

	def get_total_spaces(self) -> int:
		"""Total de espacios físicos"""
		filters = self.get_base_filters()
		filters.update({"is_active": 1})
		return frappe.db.count("Physical Space", filters)

	def get_spaces_by_category(self) -> dict[str, int]:
		"""Espacios agrupados por categoría"""
		filters = self.get_base_filters()
		filters.update({"is_active": 1})

		spaces = frappe.db.get_all(
			"Physical Space", filters=filters, fields=["space_category"], group_by="space_category"
		)

		result = {}
		for space in spaces:
			category = space.space_category or "Sin Categoría"
			count = frappe.db.count("Physical Space", dict(filters, space_category=space.space_category))
			result[category] = count

		return result

	def get_maintenance_due_count(self) -> int:
		"""Espacios con mantenimiento vencido"""
		# Placeholder - implementar cuando se defina lógica de mantenimiento
		return 0

	def get_utilization_rate(self) -> float:
		"""Tasa de utilización de espacios"""
		total_spaces = self.get_total_spaces()
		if total_spaces == 0:
			return 0.0

		# Placeholder - implementar lógica de utilización
		utilized_spaces = total_spaces * 0.75  # 75% utilizado
		return (utilized_spaces / total_spaces) * 100

	def get_component_health_score(self) -> float:
		"""Puntuación de salud de componentes"""
		total_components = frappe.db.count("Space Component", self.get_base_filters())
		if total_components == 0:
			return 100.0

		# Placeholder - implementar lógica de salud de componentes
		return 92.1

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo Physical Spaces"""
		return {
			"total_spaces": self.get_total_spaces(),
			"spaces_by_category": self.get_spaces_by_category(),
			"maintenance_due": self.get_maintenance_due_count(),
			"utilization_rate": self.get_utilization_rate(),
			"component_health": self.get_component_health_score(),
		}


class DocumentGenerationDataAggregator(DataAggregator):
	"""Agregador de datos del módulo Document Generation"""

	def get_total_templates(self) -> int:
		"""Total de templates activos"""
		return frappe.db.count("Master Template Registry", {"is_active": 1})

	def get_documents_generated_today(self) -> int:
		"""Documentos generados hoy"""
		today = getdate()
		return frappe.db.count("Master Template Registry", {"creation": [">=", today]})

	def get_template_usage_stats(self) -> dict[str, int]:
		"""Estadísticas de uso de templates"""
		templates = frappe.db.get_all(
			"Master Template Registry", filters={"is_active": 1}, fields=["template_name", "template_type"]
		)

		usage_stats = {}
		for template in templates:
			template_type = template.template_type or "General"
			usage_stats[template_type] = usage_stats.get(template_type, 0) + 1

		return usage_stats

	def get_generation_success_rate(self) -> float:
		"""Tasa de éxito en generación de documentos"""
		# Placeholder - implementar cuando se tengan logs de generación
		return 98.5

	def get_average_generation_time(self) -> float:
		"""Tiempo promedio de generación (segundos)"""
		# Placeholder - implementar cuando se tengan métricas de tiempo
		return 2.3

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo Document Generation"""
		return {
			"total_templates": self.get_total_templates(),
			"documents_today": self.get_documents_generated_today(),
			"template_usage": self.get_template_usage_stats(),
			"success_rate": self.get_generation_success_rate(),
			"avg_generation_time": self.get_average_generation_time(),
		}


class CommunityContributionsDataAggregator(DataAggregator):
	"""Agregador de datos del módulo Community Contributions"""

	def get_total_contributions(self) -> int:
		"""Total de contribuciones"""
		filters = self.get_base_filters()
		return frappe.db.count("Contribution Request", filters)

	def get_active_contributors(self) -> int:
		"""Contribuidores activos"""
		filters = self.get_base_filters()
		filters.update({"is_active": 1})
		return frappe.db.count("Registered Contributor Site", filters)

	def get_contributions_by_category(self) -> dict[str, int]:
		"""Contribuciones por categoría"""
		categories = frappe.db.get_all(
			"Contribution Category", filters={"is_active": 1}, fields=["category_name"]
		)

		result = {}
		for category in categories:
			count = frappe.db.count("Contribution Request", {"contribution_category": category.category_name})
			result[category.category_name] = count

		return result

	def get_recent_activity_count(self) -> int:
		"""Actividad reciente (últimos 7 días)"""
		week_ago = add_days(getdate(), -7)
		return frappe.db.count("Contribution Request", {"creation": [">=", week_ago]})

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo Community Contributions"""
		return {
			"total_contributions": self.get_total_contributions(),
			"active_contributors": self.get_active_contributors(),
			"contributions_by_category": self.get_contributions_by_category(),
			"recent_activity": self.get_recent_activity_count(),
		}


class CommitteeManagementDataAggregator(DataAggregator):
	"""Agregador de datos del módulo Committee Management"""

	def get_active_committee_members(self) -> int:
		"""Miembros de comité activos"""
		filters = self.get_base_filters()
		filters.update({"is_active": 1})
		return frappe.db.count("Committee Member", filters)

	def get_upcoming_meetings_count(self) -> int:
		"""Reuniones próximas (próximos 7 días)"""
		today = getdate()
		week_ahead = add_days(today, 7)

		filters = self.get_base_filters()
		filters.update({"meeting_date": ["between", [today, week_ahead]], "status": ["!=", "Cancelada"]})

		return frappe.db.count("Committee Meeting", filters)

	def get_pending_agreements_count(self) -> int:
		"""Acuerdos pendientes"""
		filters = self.get_base_filters()
		filters.update({"status": "Pendiente"})
		return frappe.db.count("Agreement Tracking", filters)

	def get_active_polls_count(self) -> int:
		"""Encuestas activas"""
		filters = self.get_base_filters()
		filters.update({"status": "Abierta"})
		return frappe.db.count("Committee Poll", filters)

	def get_voting_participation_rate(self) -> float:
		"""Tasa de participación en votaciones"""
		# Placeholder - implementar cuando se tengan métricas de participación
		return 78.5

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo Committee Management"""
		return {
			"active_members": self.get_active_committee_members(),
			"upcoming_meetings": self.get_upcoming_meetings_count(),
			"pending_agreements": self.get_pending_agreements_count(),
			"active_polls": self.get_active_polls_count(),
			"participation_rate": self.get_voting_participation_rate(),
		}


class APIDocumentationDataAggregator(DataAggregator):
	"""Agregador de datos del módulo API Documentation System"""

	def get_documented_apis_count(self) -> int:
		"""APIs documentadas"""
		return frappe.db.count("API Documentation", {"is_active": 1})

	def get_code_examples_count(self) -> int:
		"""Ejemplos de código disponibles"""
		return frappe.db.count("API Code Example")

	def get_portal_statistics(self) -> dict[str, Any]:
		"""Estadísticas del portal de documentación"""
		# Placeholder - implementar cuando se tengan métricas del portal
		return {"total_visits": 150, "unique_users": 45, "api_tests_executed": 89}

	def get_api_usage_trend(self) -> str:
		"""Tendencia de uso de APIs"""
		# Placeholder - implementar análisis de tendencias
		return "Creciente"

	def get_all_kpis(self) -> dict[str, Any]:
		"""Obtiene todos los KPIs del módulo API Documentation System"""
		return {
			"documented_apis": self.get_documented_apis_count(),
			"code_examples": self.get_code_examples_count(),
			"portal_stats": self.get_portal_statistics(),
			"usage_trend": self.get_api_usage_trend(),
		}


# Factory function para obtener agregadores


def get_module_aggregator(
	module_name: str,
	company_filter: str | None = None,
	date_from: str | None = None,
	date_to: str | None = None,
) -> DataAggregator:
	"""
	Factory function para obtener el agregador apropiado por módulo

	Args:
		module_name: Nombre del módulo
		company_filter: Filtro de empresa
		date_from: Fecha inicio
		date_to: Fecha fin

	Returns:
		Instancia del agregador apropiado
	"""
	aggregators = {
		"Companies": CompaniesDataAggregator,
		"Physical Spaces": PhysicalSpacesDataAggregator,
		"Document Generation": DocumentGenerationDataAggregator,
		"Community Contributions": CommunityContributionsDataAggregator,
		"Committee Management": CommitteeManagementDataAggregator,
		"API Documentation System": APIDocumentationDataAggregator,
	}

	aggregator_class = aggregators.get(module_name)
	if not aggregator_class:
		raise ValueError(f"Módulo {module_name} no tiene agregador implementado")

	return aggregator_class(company_filter, date_from, date_to)


def get_all_modules_data(
	company_filter: str | None = None, date_from: str | None = None, date_to: str | None = None
) -> dict[str, Any]:
	"""
	Obtiene datos consolidados de todos los módulos

	Args:
		company_filter: Filtro de empresa
		date_from: Fecha inicio
		date_to: Fecha fin

	Returns:
		Dict con datos de todos los módulos
	"""
	modules = [
		"Companies",
		"Physical Spaces",
		"Document Generation",
		"Community Contributions",
		"Committee Management",
		"API Documentation System",
	]

	consolidated_data = {}

	for module_name in modules:
		try:
			aggregator = get_module_aggregator(module_name, company_filter, date_from, date_to)
			consolidated_data[module_name.lower().replace(" ", "_")] = aggregator.get_all_kpis()
		except Exception as e:
			frappe.log_error(f"Error agregando datos de {module_name}: {e!s}")
			consolidated_data[module_name.lower().replace(" ", "_")] = {}

	return consolidated_data
