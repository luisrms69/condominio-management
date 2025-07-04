# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json
from typing import Any, Optional

import frappe


class BaseContributionHandler:
	"""
	Interfaz base que cada módulo debe implementar para contribuciones.

	Cada módulo específico debe heredar de esta clase e implementar
	los métodos abstractos según sus necesidades particulares.
	"""

	def validate_contribution(self, contribution_data: dict[str, Any]) -> None:
		"""
		Validar datos específicos del módulo.

		Args:
		    contribution_data: Datos de la contribución a validar

		Raises:
		    ValidationError: Si los datos no son válidos
		"""
		raise NotImplementedError("Cada módulo debe implementar validate_contribution")

	def export_to_fixtures(self, contribution_data: dict[str, Any]) -> dict[str, Any]:
		"""
		Convertir contribución a formato fixture.

		Args:
		    contribution_data: Datos de la contribución

		Returns:
		    dict: Datos en formato fixture listo para integración
		"""
		raise NotImplementedError("Cada módulo debe implementar export_to_fixtures")

	def preview_contribution(self, contribution_data: dict[str, Any]) -> dict[str, Any]:
		"""
		Generar preview de la contribución.

		Args:
		    contribution_data: Datos de la contribución

		Returns:
		    dict: Preview de cómo se vería la contribución
		"""
		raise NotImplementedError("Cada módulo debe implementar preview_contribution")

	def get_sample_data(self) -> dict[str, Any]:
		"""
		Obtener datos de muestra para el tipo de contribución.

		Returns:
		    dict: Estructura de datos de muestra
		"""
		return {"message": "Implementar get_sample_data en el handler específico"}


@frappe.whitelist()
def create_contribution_request(
	module_name: str, contribution_type: str, title: str, business_justification: str, contribution_data: str
) -> str:
	"""
	API para crear nueva solicitud de contribución.

	Args:
	    module_name: Nombre del módulo
	    contribution_type: Tipo de contribución
	    title: Título descriptivo
	    business_justification: Justificación de negocio
	    contribution_data: Datos de la contribución en JSON

	Returns:
	    str: Nombre del documento creado
	"""
	# Buscar categoría de contribución
	category_name = f"{module_name}-{contribution_type}"
	category = frappe.db.exists("Contribution Category", category_name)

	if not category:
		frappe.throw(frappe._("Categoría de contribución no encontrada: {0}").format(category_name))

	# Validar JSON
	try:
		json.loads(contribution_data)
	except json.JSONDecodeError:
		frappe.throw(frappe._("Los datos de contribución deben ser JSON válido"))

	# Crear solicitud de contribución
	contribution_request = frappe.new_doc("Contribution Request")
	contribution_request.update(
		{
			"title": title,
			"contribution_category": category,
			"business_justification": business_justification,
			"contribution_data": contribution_data,
			"company": frappe.defaults.get_user_default("Company") or frappe.get_all("Company")[0].name,
		}
	)

	contribution_request.insert()

	return contribution_request.name


@frappe.whitelist()
def get_contribution_categories(module_name: str | None = None) -> list[dict[str, Any]]:
	"""
	Obtener categorías de contribución disponibles.

	Args:
	    module_name: Filtrar por módulo específico (opcional)

	Returns:
	    list: Lista de categorías disponibles
	"""
	filters = {"is_active": 1}
	if module_name:
		filters["module_name"] = module_name

	categories = frappe.get_all(
		"Contribution Category",
		filters=filters,
		fields=["name", "module_name", "contribution_type", "description", "required_fields"],
	)

	return categories


@frappe.whitelist()
def validate_contribution_data(category_name: str, contribution_data: str) -> dict[str, Any]:
	"""
	Validar datos de contribución contra una categoría específica.

	Args:
	    category_name: Nombre de la categoría
	    contribution_data: Datos en JSON para validar

	Returns:
	    dict: Resultado de la validación
	"""
	try:
		data = json.loads(contribution_data)
	except json.JSONDecodeError:
		return {"valid": False, "error": "JSON inválido"}

	try:
		category = frappe.get_doc("Contribution Category", category_name)
		category.validate_contribution_data(data)

		# Validar con handler específico si está disponible
		handler_path = category.get_module_handler_path()
		if handler_path:
			try:
				handler = frappe.get_attr(handler_path + ".ContributionHandler")()
				handler.validate_contribution(data)
			except (ImportError, AttributeError):
				pass  # Handler no disponible, solo validación básica

		return {"valid": True, "message": "Datos válidos"}

	except Exception as e:
		return {"valid": False, "error": str(e)}


@frappe.whitelist()
def preview_contribution(category_name: str, contribution_data: str) -> dict[str, Any]:
	"""
	Generar preview de una contribución.

	Args:
	    category_name: Nombre de la categoría
	    contribution_data: Datos de la contribución

	Returns:
	    dict: Preview de la contribución
	"""
	try:
		data = json.loads(contribution_data)
		category = frappe.get_doc("Contribution Category", category_name)

		handler_path = category.get_module_handler_path()
		if not handler_path:
			return {"error": "Handler del módulo no configurado"}

		handler = frappe.get_attr(handler_path + ".ContributionHandler")()
		return handler.preview_contribution(data)

	except Exception as e:
		return {"error": str(e)}


@frappe.whitelist()
def get_sample_contribution_data(category_name: str) -> dict[str, Any]:
	"""
	Obtener datos de muestra para una categoría de contribución.

	Args:
	    category_name: Nombre de la categoría

	Returns:
	    dict: Estructura de datos de muestra
	"""
	try:
		category = frappe.get_doc("Contribution Category", category_name)

		handler_path = category.get_module_handler_path()
		if not handler_path:
			return {"error": "Handler del módulo no configurado"}

		handler = frappe.get_attr(handler_path + ".ContributionHandler")()
		return handler.get_sample_data()

	except Exception as e:
		return {"error": str(e)}


@frappe.whitelist()
def export_contribution_fixtures(contribution_request_name: str) -> dict[str, Any]:
	"""
	Exportar contribución aprobada a formato fixtures.

	Args:
	    contribution_request_name: Nombre de la solicitud de contribución

	Returns:
	    dict: Datos exportados para fixtures
	"""
	contribution = frappe.get_doc("Contribution Request", contribution_request_name)

	if contribution.status != "Approved":
		frappe.throw(frappe._("Solo se pueden exportar contribuciones aprobadas"))

	return contribution.export_to_fixtures()


def get_contribution_stats() -> dict[str, int]:
	"""
	Obtener estadísticas de contribuciones del sistema.

	Returns:
	    dict: Estadísticas por estado
	"""
	stats = {}

	# Contar por estado
	for status in ["Draft", "Submitted", "Under Review", "Approved", "Rejected", "Integrated"]:
		count = frappe.db.count("Contribution Request", {"status": status})
		stats[status.lower().replace(" ", "_")] = count

	# Contar por módulo
	module_stats = frappe.db.sql(
		"""
        SELECT cc.module_name, COUNT(cr.name) as count
        FROM `tabContribution Request` cr
        JOIN `tabContribution Category` cc ON cr.contribution_category = cc.name
        GROUP BY cc.module_name
    """,
		as_dict=True,
	)

	stats["by_module"] = {item["module_name"]: item["count"] for item in module_stats}

	return stats
