# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
API Documentation Portal Backend - Day 3 Portal Web
===================================================

Backend APIs para el portal web de documentación de APIs.
"""

from typing import Any, Optional

import frappe
from frappe import _


@frappe.whitelist()
def get_api_collections() -> dict[str, Any]:
	"""
	Obtiene todas las colecciones de APIs agrupadas por módulo.

	Returns:
		Dict con colecciones organizadas por módulo
	"""
	try:
		# Obtener todas las APIs activas
		apis = frappe.get_all(
			"API Documentation",
			filters={"is_active": 1},
			fields=[
				"name",
				"api_name",
				"api_path",
				"api_version",
				"http_method",
				"description",
				"module_path",
				"auto_generated",
				"needs_manual_review",
			],
			order_by="module_path, api_name",
		)

		# Agrupar por módulo
		collections = {}
		for api in apis:
			module = api.get("module_path", "Unknown")

			# Crear estructura jerárquica
			if module not in collections:
				collections[module] = {
					"module_name": module,
					"display_name": _get_module_display_name(module),
					"api_count": 0,
					"auto_generated_count": 0,
					"needs_review_count": 0,
					"apis": [],
				}

			collections[module]["apis"].append(api)
			collections[module]["api_count"] += 1

			if api.get("auto_generated"):
				collections[module]["auto_generated_count"] += 1

			if api.get("needs_manual_review"):
				collections[module]["needs_review_count"] += 1

		return {
			"success": True,
			"collections": list(collections.values()),
			"total_apis": len(apis),
			"total_modules": len(collections),
		}

	except Exception as e:
		frappe.log_error(f"Error getting API collections: {e!s}", "API Portal")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_api_details(api_name: str) -> dict[str, Any]:
	"""
	Obtiene detalles completos de una API específica.

	Args:
		api_name: Nombre/ID de la API

	Returns:
		Dict con detalles completos de la API
	"""
	try:
		# Obtener documento principal
		api_doc = frappe.get_doc("API Documentation", api_name)

		# Obtener child tables
		parameters = frappe.get_all(
			"API Parameter",
			filters={"parent": api_name},
			fields=[
				"parameter_name",
				"parameter_type",
				"data_type",
				"is_required",
				"default_value",
				"parameter_description",
				"validation_rules",
			],
			order_by="idx",
		)

		response_codes = frappe.get_all(
			"API Response Code",
			filters={"parent": api_name},
			fields=["status_code", "response_description", "response_example"],
			order_by="status_code",
		)

		code_examples = frappe.get_all(
			"API Code Example",
			filters={"parent": api_name},
			fields=["language", "example_description", "example_code"],
			order_by="idx",
		)

		# Parsear esquemas JSON
		request_schema = {}
		response_schema = {}

		if api_doc.request_schema:
			try:
				request_schema = frappe.parse_json(api_doc.request_schema)
			except Exception:
				pass

		if api_doc.response_schema:
			try:
				response_schema = frappe.parse_json(api_doc.response_schema)
			except Exception:
				pass

		return {
			"success": True,
			"api": {
				# Información básica
				"name": api_doc.name,
				"api_name": api_doc.api_name,
				"api_path": api_doc.api_path,
				"api_version": api_doc.api_version,
				"http_method": api_doc.http_method,
				"description": api_doc.description,
				"module_path": api_doc.module_path,
				"function_name": api_doc.function_name,
				# Estado
				"is_active": api_doc.is_active,
				"is_deprecated": api_doc.is_deprecated,
				"deprecation_date": api_doc.deprecation_date,
				"replacement_api": api_doc.replacement_api,
				# Configuración
				"authentication_required": api_doc.authentication_required,
				"permissions_required": api_doc.permissions_required,
				"sandbox_enabled": api_doc.sandbox_enabled,
				"rate_limit": api_doc.rate_limit,
				"cache_timeout": api_doc.cache_timeout,
				# Auto-generación
				"auto_generated": api_doc.auto_generated,
				"needs_manual_review": api_doc.needs_manual_review,
				"generation_source": api_doc.generation_source,
				"last_auto_update": api_doc.last_auto_update,
				# Esquemas
				"request_schema": request_schema,
				"response_schema": response_schema,
				# Child tables
				"parameters": parameters,
				"response_codes": response_codes,
				"code_examples": code_examples,
				# URLs
				"full_url": _get_full_api_url(api_doc.api_path, api_doc.api_version),
				"test_url": _get_test_url(api_doc.api_path, api_doc.api_version),
			},
		}

	except Exception as e:
		frappe.log_error(f"Error getting API details for {api_name}: {e!s}", "API Portal")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def search_apis(query: str, filters: dict | None = None) -> dict[str, Any]:
	"""
	Búsqueda de APIs con filtros.

	Args:
		query: Término de búsqueda
		filters: Filtros adicionales (módulo, método HTTP, etc.)

	Returns:
		Dict con resultados de búsqueda
	"""
	try:
		if not filters:
			filters = {}

		# Filtros base
		base_filters = {"is_active": 1}
		base_filters.update(filters)

		# Campos para búsqueda
		search_fields = ["api_name", "api_path", "description", "module_path"]

		if query:
			# Búsqueda fuzzy en múltiples campos
			or_filters = []
			for field in search_fields:
				or_filters.append([field, "like", f"%{query}%"])

			apis = frappe.get_all(
				"API Documentation",
				filters=base_filters,
				or_filters=or_filters,
				fields=[
					"name",
					"api_name",
					"api_path",
					"api_version",
					"http_method",
					"description",
					"module_path",
					"auto_generated",
				],
				limit=50,
				order_by="api_name",
			)
		else:
			apis = frappe.get_all(
				"API Documentation",
				filters=base_filters,
				fields=[
					"name",
					"api_name",
					"api_path",
					"api_version",
					"http_method",
					"description",
					"module_path",
					"auto_generated",
				],
				limit=50,
				order_by="api_name",
			)

		# Agregar URLs completas
		for api in apis:
			api["full_url"] = _get_full_api_url(api["api_path"], api["api_version"])

		return {"success": True, "results": apis, "count": len(apis), "query": query, "filters": filters}

	except Exception as e:
		frappe.log_error(f"Error searching APIs: {e!s}", "API Portal")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_portal_stats() -> dict[str, Any]:
	"""
	Obtiene estadísticas generales del portal.

	Returns:
		Dict con estadísticas del sistema
	"""
	try:
		# Estadísticas básicas
		total_apis = frappe.db.count("API Documentation", {"is_active": 1})
		auto_generated = frappe.db.count("API Documentation", {"is_active": 1, "auto_generated": 1})
		needs_review = frappe.db.count("API Documentation", {"is_active": 1, "needs_manual_review": 1})
		deprecated = frappe.db.count("API Documentation", {"is_active": 1, "is_deprecated": 1})

		# Estadísticas por método HTTP
		methods_stats = frappe.db.sql(
			"""
			SELECT http_method, COUNT(*) as count
			FROM `tabAPI Documentation`
			WHERE is_active = 1
			GROUP BY http_method
			ORDER BY count DESC
		""",
			as_dict=True,
		)

		# Estadísticas por módulo
		modules_stats = frappe.db.sql(
			"""
			SELECT
				COALESCE(module_path, 'Unknown') as module_name,
				COUNT(*) as api_count,
				SUM(CASE WHEN auto_generated = 1 THEN 1 ELSE 0 END) as auto_generated_count,
				SUM(CASE WHEN needs_manual_review = 1 THEN 1 ELSE 0 END) as needs_review_count
			FROM `tabAPI Documentation`
			WHERE is_active = 1
			GROUP BY module_path
			ORDER BY api_count DESC
			LIMIT 10
		""",
			as_dict=True,
		)

		return {
			"success": True,
			"stats": {
				"total_apis": total_apis,
				"auto_generated": auto_generated,
				"needs_review": needs_review,
				"deprecated": deprecated,
				"manual_apis": total_apis - auto_generated,
				"completion_rate": round((total_apis - needs_review) / total_apis * 100, 1)
				if total_apis > 0
				else 0,
				"methods": methods_stats,
				"modules": modules_stats,
			},
		}

	except Exception as e:
		frappe.log_error(f"Error getting portal stats: {e!s}", "API Portal")
		return {"success": False, "error": str(e)}


def _get_module_display_name(module_path: str) -> str:
	"""Genera nombre para mostrar del módulo"""
	if not module_path or module_path == "Unknown":
		return "APIs Sin Categorizar"

	parts = module_path.split(".")
	if len(parts) > 1:
		# Tomar la última parte y formatear
		return parts[-1].replace("_", " ").title()

	return module_path.replace("_", " ").title()


def _get_full_api_url(api_path: str, api_version: str = "v1") -> str:
	"""Genera URL completa de la API"""
	base_url = frappe.utils.get_url()
	return f"{base_url}/api/method{api_path}"


def _get_test_url(api_path: str, api_version: str = "v1") -> str:
	"""
	Genera URL para testing de la API.

	TODO: PHASE2: PORTAL - Integrar con sandbox environment
	"""
	return _get_full_api_url(api_path, api_version)
