# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Dashboard Consolidado - Motor de KPIs
===================================

Sistema para cálculo y evaluación de KPIs configurables.
"""

import ast
import json
import operator
from datetime import datetime
from typing import Any, Optional, Union

import frappe
from frappe.utils import add_days, cint, flt, getdate, now

from .data_aggregators import get_all_modules_data, get_module_aggregator


class KPIEngine:
	"""Motor de cálculo y evaluación de KPIs"""

	def __init__(self):
		self.operators = {
			"+": operator.add,
			"-": operator.sub,
			"*": operator.mul,
			"/": operator.truediv,
			"sum": sum,
			"avg": lambda x: sum(x) / len(x) if x else 0,
			"count": len,
			"min": min,
			"max": max,
		}

	def calculate_kpi(
		self,
		kpi_code: str,
		company_filter: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> dict[str, Any]:
		"""
		Calcula un KPI específico

		Args:
			kpi_code: Código del KPI a calcular
			company_filter: Filtro de empresa
			date_from: Fecha inicio
			date_to: Fecha fin

		Returns:
			Dict con valor calculado y metadatos
		"""
		try:
			# Obtener definición del KPI
			kpi_def = frappe.get_doc("KPI Definition", kpi_code)

			if not kpi_def.is_active:
				return {"success": False, "error": f"KPI {kpi_code} está inactivo"}

			# Verificar cache
			cached_result = self._get_cached_result(kpi_def, company_filter)
			if cached_result:
				return cached_result

			# Calcular valor según tipo de cálculo
			if kpi_def.calculation_type == "Personalizado" and kpi_def.calculation_formula:
				result = self._calculate_custom_kpi(kpi_def, company_filter, date_from, date_to)
			else:
				result = self._calculate_standard_kpi(kpi_def, company_filter, date_from, date_to)

			# Evaluar umbrales
			threshold_status = self._evaluate_thresholds(result["value"], kpi_def)
			result["threshold_status"] = threshold_status

			# Cachear resultado
			self._cache_result(kpi_def, company_filter, result)

			return {
				"success": True,
				"kpi_code": kpi_code,
				"kpi_name": kpi_def.kpi_name,
				"data": result,
				"calculated_at": now(),
			}

		except Exception as e:
			frappe.log_error(f"Error calculando KPI {kpi_code}: {e!s}")
			return {"success": False, "error": str(e)}

	def _calculate_standard_kpi(
		self,
		kpi_def,
		company_filter: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> dict[str, Any]:
		"""Calcula KPI usando fuentes de datos estándar"""

		if not kpi_def.data_sources:
			return {"value": 0, "unit_type": kpi_def.unit_type}

		total_value = 0
		values = []

		for data_source in kpi_def.data_sources:
			try:
				# Obtener datos del módulo
				if data_source.source_module in [
					"Companies",
					"Physical Spaces",
					"Document Generation",
					"Community Contributions",
					"Committee Management",
					"API Documentation System",
				]:
					aggregator = get_module_aggregator(
						data_source.source_module, company_filter, date_from, date_to
					)
					module_data = aggregator.get_all_kpis()

					# Extraer valor específico del campo
					field_value = self._extract_field_value(module_data, data_source.source_field)
				else:
					# Query directo a DocType
					field_value = self._query_doctype_field(data_source, company_filter, date_from, date_to)

				# Aplicar agregación
				if data_source.aggregation == "Suma":
					total_value += flt(field_value)
				elif data_source.aggregation == "Conteo":
					values.append(1 if field_value else 0)
				else:
					values.append(flt(field_value))

			except Exception as e:
				frappe.log_error(f"Error procesando fuente de datos: {e!s}")
				continue

		# Calcular valor final según tipo de cálculo
		if kpi_def.calculation_type == "Suma":
			final_value = total_value + sum(values)
		elif kpi_def.calculation_type == "Promedio":
			all_values = [total_value, *values] if total_value > 0 else values
			final_value = sum(all_values) / len(all_values) if all_values else 0
		elif kpi_def.calculation_type == "Conteo":
			final_value = len(values)
		else:
			final_value = total_value

		return {
			"value": final_value,
			"unit_type": kpi_def.unit_type,
			"display_format": kpi_def.display_format,
			"trend_period": kpi_def.trend_period,
		}

	def _calculate_custom_kpi(
		self,
		kpi_def,
		company_filter: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> dict[str, Any]:
		"""Calcula KPI usando fórmula personalizada"""

		try:
			# Preparar contexto para la fórmula
			context = self._build_formula_context(kpi_def, company_filter, date_from, date_to)

			# Ejecutar fórmula de forma segura
			result = self._safe_eval(kpi_def.calculation_formula, context)

			return {
				"value": flt(result),
				"unit_type": kpi_def.unit_type,
				"display_format": kpi_def.display_format,
				"trend_period": kpi_def.trend_period,
				"custom_calculation": True,
			}

		except Exception as e:
			frappe.log_error(f"Error en cálculo personalizado: {e!s}")
			return {"value": 0, "unit_type": kpi_def.unit_type, "error": str(e)}

	def _build_formula_context(
		self,
		kpi_def,
		company_filter: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> dict[str, Any]:
		"""Construye contexto para ejecución de fórmulas personalizadas"""

		context = {
			# Funciones seguras
			"sum": sum,
			"len": len,
			"min": min,
			"max": max,
			"avg": lambda x: sum(x) / len(x) if x else 0,
			"flt": flt,
			"cint": cint,
			# Datos de módulos
			"modules_data": get_all_modules_data(company_filter, date_from, date_to),
			# Utilidades de fecha
			"today": getdate(),
			"date_from": date_from,
			"date_to": date_to,
			"company_filter": company_filter,
		}

		# Agregar datos específicos de las fuentes
		for data_source in kpi_def.data_sources or []:
			try:
				if data_source.source_module:
					aggregator = get_module_aggregator(
						data_source.source_module, company_filter, date_from, date_to
					)
					field_name = data_source.source_field.replace(".", "_")
					context[field_name] = aggregator.get_all_kpis()
			except Exception:
				continue

		return context

	def _safe_eval(self, formula: str, context: dict[str, Any]) -> float | int:
		"""Evalúa fórmula de forma segura"""

		# Lista de nombres permitidos
		allowed_names = set(context.keys()) | {"sum", "len", "min", "max", "flt", "cint", "avg"}

		try:
			# Parsear AST y validar
			tree = ast.parse(formula, mode="eval")

			# Verificar que solo se usen nombres permitidos
			for node in ast.walk(tree):
				if isinstance(node, ast.Name) and node.id not in allowed_names:
					raise ValueError(f"Nombre no permitido en fórmula: {node.id}")
				elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
					if node.func.id not in allowed_names:
						raise ValueError(f"Función no permitida: {node.func.id}")

			# Ejecutar fórmula
			return eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, context)

		except Exception as e:
			frappe.log_error(f"Error evaluando fórmula: {e!s}")
			return 0

	def _extract_field_value(self, data: dict[str, Any], field_path: str) -> Any:
		"""Extrae valor de campo usando notación de punto"""

		parts = field_path.split(".")
		current = data

		for part in parts:
			if isinstance(current, dict) and part in current:
				current = current[part]
			else:
				return 0

		return current

	def _query_doctype_field(
		self,
		data_source,
		company_filter: str | None = None,
		date_from: str | None = None,
		date_to: str | None = None,
	) -> Any:
		"""Query directo a DocType para obtener valor de campo"""

		filters = {}

		# Aplicar filtros de la fuente de datos
		if data_source.filters:
			try:
				source_filters = (
					json.loads(data_source.filters)
					if isinstance(data_source.filters, str)
					else data_source.filters
				)
				filters.update(source_filters)
			except Exception:
				pass

		# Aplicar filtro de empresa
		if company_filter:
			filters["company"] = company_filter

		# Aplicar filtros de fecha
		if date_from and date_to:
			filters["creation"] = ["between", [date_from, date_to]]

		# Ejecutar agregación
		try:
			if data_source.aggregation == "Suma":
				result = frappe.db.get_value(
					data_source.source_doctype, filters, f"SUM({data_source.source_field})"
				)
				return flt(result) if result else 0

			elif data_source.aggregation == "Promedio":
				result = frappe.db.get_value(
					data_source.source_doctype, filters, f"AVG({data_source.source_field})"
				)
				return flt(result) if result else 0

			elif data_source.aggregation == "Conteo":
				return frappe.db.count(data_source.source_doctype, filters)

			elif data_source.aggregation == "Mínimo":
				result = frappe.db.get_value(
					data_source.source_doctype, filters, f"MIN({data_source.source_field})"
				)
				return flt(result) if result else 0

			elif data_source.aggregation == "Máximo":
				result = frappe.db.get_value(
					data_source.source_doctype, filters, f"MAX({data_source.source_field})"
				)
				return flt(result) if result else 0

		except Exception as e:
			frappe.log_error(f"Error en query directo: {e!s}")
			return 0

	def _evaluate_thresholds(self, value: float, kpi_def) -> str:
		"""Evalúa umbrales del KPI"""

		if not any([kpi_def.threshold_critical, kpi_def.threshold_warning, kpi_def.threshold_good]):
			return "neutral"

		# Determinar si menor es mejor
		inverse = kpi_def.inverse_threshold

		if kpi_def.threshold_critical is not None:
			if inverse:
				if value <= kpi_def.threshold_critical:
					return "critical"
			else:
				if value >= kpi_def.threshold_critical:
					return "critical"

		if kpi_def.threshold_warning is not None:
			if inverse:
				if value <= kpi_def.threshold_warning:
					return "warning"
			else:
				if value >= kpi_def.threshold_warning:
					return "warning"

		if kpi_def.threshold_good is not None:
			if inverse:
				if value <= kpi_def.threshold_good:
					return "good"
			else:
				if value >= kpi_def.threshold_good:
					return "good"

		return "neutral"

	def _get_cached_result(self, kpi_def, company_filter: str | None = None) -> dict[str, Any] | None:
		"""Obtiene resultado cacheado si está disponible"""

		if not kpi_def.cache_duration or kpi_def.cache_duration <= 0:
			return None

		# Por ahora no implementar cache - agregar Redis después
		return None

	def _cache_result(self, kpi_def, company_filter: str | None = None, result: dict[str, Any] | None = None):
		"""Cachea resultado del KPI"""

		if not kpi_def.cache_duration or kpi_def.cache_duration <= 0:
			return

		# Por ahora no implementar cache - agregar Redis después
		pass


# API pública


@frappe.whitelist()
def calculate_kpi_value(
	kpi_code: str, company_filter: str | None = None, date_from: str | None = None, date_to: str | None = None
) -> dict[str, Any]:
	"""
	API pública para calcular valor de KPI

	Args:
		kpi_code: Código del KPI
		company_filter: Filtro de empresa
		date_from: Fecha inicio
		date_to: Fecha fin

	Returns:
		Dict con resultado del cálculo
	"""
	engine = KPIEngine()
	return engine.calculate_kpi(kpi_code, company_filter, date_from, date_to)


@frappe.whitelist()
def get_kpi_trend(kpi_code: str, periods: int = 7, company_filter: str | None = None) -> dict[str, Any]:
	"""
	Obtiene tendencia de un KPI por períodos

	Args:
		kpi_code: Código del KPI
		periods: Número de períodos a calcular
		company_filter: Filtro de empresa

	Returns:
		Dict con datos de tendencia
	"""
	try:
		engine = KPIEngine()
		trend_data = []

		for i in range(periods):
			date_to = add_days(getdate(), -i)
			date_from = add_days(date_to, -1)

			result = engine.calculate_kpi(kpi_code, company_filter, date_from, date_to)

			if result.get("success"):
				trend_data.append(
					{
						"date": date_to,
						"value": result["data"]["value"],
						"threshold_status": result["data"].get("threshold_status", "neutral"),
					}
				)

		# Ordenar por fecha
		trend_data.sort(key=lambda x: x["date"])

		return {"success": True, "kpi_code": kpi_code, "trend_data": trend_data}

	except Exception as e:
		frappe.log_error(f"Error obteniendo tendencia de KPI: {e!s}")
		return {"success": False, "error": str(e)}
