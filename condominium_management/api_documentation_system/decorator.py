# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Decorador para auto-registro de APIs en el sistema de documentación
"""

import inspect
import json
from functools import wraps
from typing import Any, Optional

import frappe


def api_documentation(
	name: str,
	description: str = "",
	version: str = "v1",
	collection: str = "general",
	method: str = "GET",
	auto_register: bool = True,
):
	"""
	Decorador para documentar APIs automáticamente

	Args:
	    name: Nombre descriptivo de la API
	    description: Descripción de la funcionalidad
	    version: Versión de la API (v1, v2, etc.)
	    collection: Colección a la que pertenece
	    method: Método HTTP (GET, POST, etc.)
	    auto_register: Si debe registrarse automáticamente

	Uso:
	    @api_documentation(
	        name="Obtener Espacios Físicos",
	        description="Retorna lista de espacios con filtros",
	        version="v1",
	        collection="physical-spaces"
	    )
	    @frappe.whitelist()
	    def get_physical_spaces(filters=None):
	        pass
	"""

	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)

		# Almacenar metadatos en la función
		wrapper._api_documentation = {
			"name": name,
			"description": description,
			"version": version,
			"collection": collection,
			"method": method,
			"function_name": func.__name__,
			"module_path": func.__module__,
			"auto_register": auto_register,
		}

		# Auto-registro si está habilitado
		if auto_register:
			try:
				_auto_register_api(func, wrapper._api_documentation)
			except Exception as e:
				# TODO: PHASE2: LOGGING - Mejorar logging de errores
				frappe.log_error(f"Error auto-registering API {name}: {e!s}", "API Auto-Registration")

		return wrapper

	return decorator


def _auto_register_api(func, metadata: dict[str, Any]):
	"""
	Registra automáticamente la API en el DocType API Documentation

	TODO: PHASE2: AUTO-REGISTRO - Mejorar extracción de parámetros
	TODO: PHASE2: AUTO-REGISTRO - Inferir tipos automáticamente
	"""
	try:
		# Construir la ruta de la API
		api_path = f"/{metadata['function_name']}"

		# Verificar si ya existe
		existing = frappe.db.exists(
			"API Documentation", {"api_path": api_path, "http_method": metadata["method"]}
		)

		if existing:
			# Actualizar existente
			doc = frappe.get_doc("API Documentation", existing)
		else:
			# Crear nuevo
			doc = frappe.new_doc("API Documentation")
			doc.api_path = api_path
			doc.http_method = metadata["method"]

		# Actualizar campos
		doc.api_name = metadata["name"]
		doc.description = metadata["description"]
		doc.api_version = metadata["version"]
		doc.is_active = 1
		doc.is_deprecated = 0

		# TODO: PHASE2: PARÁMETROS - Extraer parámetros del docstring
		# TODO: PHASE2: ESQUEMAS - Generar esquemas automáticamente

		# Extraer información básica de la función
		signature = inspect.signature(func)
		parameters = []

		for param_name, param in signature.parameters.items():
			if param_name not in ["self", "cls"]:  # Excluir parámetros internos
				param_info = {
					"parameter_name": param_name,
					"parameter_type": "query",  # Por defecto
					"data_type": "string",  # Por defecto
					"is_required": param.default == param.empty,
					"default_value": str(param.default) if param.default != param.empty else "",
					"parameter_description": f"Parámetro {param_name}",
				}
				parameters.append(param_info)

		# Agregar parámetros básicos
		# TODO: PHASE2: CHILD-TABLES - Mejorar manejo de child tables
		doc.parameters = []
		for param in parameters:
			doc.append("parameters", param)

		# Códigos de respuesta básicos
		doc.response_codes = []
		doc.append(
			"response_codes",
			{
				"status_code": 200,
				"response_description": "Éxito",
				"response_example": '{"status": "success", "data": {}}',
			},
		)
		doc.append(
			"response_codes",
			{
				"status_code": 400,
				"response_description": "Error en los parámetros",
				"response_example": '{"status": "error", "message": "Invalid parameters"}',
			},
		)
		doc.append(
			"response_codes",
			{
				"status_code": 401,
				"response_description": "No autorizado",
				"response_example": '{"status": "error", "message": "Unauthorized"}',
			},
		)

		# Guardar
		if existing:
			doc.save()
		else:
			doc.insert()

		frappe.db.commit()

	except Exception as e:
		# No fallar si hay error en el auto-registro
		frappe.log_error(
			f"Auto-registration failed for {metadata['name']}: {e!s}", "API Auto-Registration Error"
		)


@frappe.whitelist()
def scan_and_register_apis():
	"""
	Escanea el código en busca de APIs marcadas y las registra

	TODO: PHASE2: SCANNER - Implementar scanner completo de código
	TODO: PHASE2: SCANNER - Detectar @frappe.whitelist() sin decorador
	"""
	registered_count = 0

	try:
		# TODO: PHASE2: SCANNER - Implementar scanner de archivos Python
		# Por ahora, solo registrar APIs que ya tienen el decorador

		frappe.msgprint(f"APIs registradas: {registered_count}")
		return {"status": "success", "registered": registered_count}

	except Exception as e:
		frappe.throw(f"Error escaneando APIs: {e!s}")


@frappe.whitelist()
def get_api_registry():
	"""Retorna registro de todas las APIs decoradas en memoria"""
	# TODO: PHASE2: REGISTRY - Mantener registry en memoria para mejor performance
	return frappe.get_all(
		"API Documentation",
		filters={"is_active": 1},
		fields=["name", "api_name", "api_path", "http_method", "api_version"],
	)


# Ejemplo de uso del decorador
@api_documentation(
	name="Test API Documentation",
	description="API de prueba para el sistema de documentación",
	version="v1",
	collection="testing",
)
@frappe.whitelist()
def test_api_documentation():
	"""API de prueba para validar el sistema de documentación"""
	return {
		"status": "success",
		"message": "API Documentation system working!",
		"timestamp": frappe.utils.now(),
	}
