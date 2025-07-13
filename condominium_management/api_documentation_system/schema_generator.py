# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Schema Generator Module - Day 2 Auto-Documentation System
=========================================================

Generador automático de esquemas JSON para requests y responses de APIs.
"""

import json
from typing import Any, Optional, Union

import frappe


class SchemaGenerator:
	"""
	Generador que crea esquemas JSON para APIs basado en:
	- Type hints de Python
	- Análisis de docstrings
	- Introspección de código existente
	- Patrones comunes de Frappe Framework
	"""

	def __init__(self):
		self.frappe_types = {
			"str": {"type": "string"},
			"int": {"type": "integer"},
			"float": {"type": "number"},
			"bool": {"type": "boolean"},
			"dict": {"type": "object"},
			"list": {"type": "array"},
			"None": {"type": "null"},
			"Any": {},  # Any type allowed
		}

		self.common_patterns = {
			"doctype": {"type": "string", "description": "Nombre del DocType de Frappe"},
			"name": {"type": "string", "description": "Nombre único del documento"},
			"filters": {"type": "object", "description": "Filtros para consultas"},
			"fields": {"type": "array", "items": {"type": "string"}, "description": "Campos a retornar"},
			"limit": {"type": "integer", "minimum": 1, "description": "Límite de resultados"},
			"offset": {"type": "integer", "minimum": 0, "description": "Offset para paginación"},
		}

	def generate_request_schema(self, parameters: list[dict[str, Any]]) -> dict[str, Any]:
		"""
		Genera esquema JSON para el request de una API.

		Args:
			parameters: Lista de parámetros extraídos del scanner/parser

		Returns:
			Dict con esquema JSON válido
		"""
		schema = {"type": "object", "properties": {}, "required": []}

		for param in parameters:
			param_name = param.get("name", "")
			param_type = param.get("type_annotation") or param.get("type")
			description = param.get("description", "")
			is_required = param.get("is_required", param.get("required", True))
			default_value = param.get("default_value")

			# Generar esquema para el parámetro
			param_schema = self._generate_parameter_schema(param_name, param_type, description, default_value)

			schema["properties"][param_name] = param_schema

			if is_required and default_value is None:
				schema["required"].append(param_name)

		return schema

	def generate_response_schema(
		self, return_info: dict[str, Any] | None, function_name: str
	) -> dict[str, Any]:
		"""
		Genera esquema JSON para el response de una API.

		Args:
			return_info: Información de retorno del parser
			function_name: Nombre de la función para inferir patrones

		Returns:
			Dict con esquema JSON de response
		"""
		if return_info and return_info.get("type"):
			return_type = return_info["type"]
			description = return_info.get("description", "")

			return self._generate_response_from_type(return_type, description, function_name)

		# Si no hay información específica, inferir del nombre de función
		return self._infer_response_from_function_name(function_name)

	def _generate_parameter_schema(
		self, param_name: str, param_type: str | None, description: str, default_value: Any
	) -> dict[str, Any]:
		"""Genera esquema para un parámetro específico"""

		# Verificar patrones comunes primero
		if param_name in self.common_patterns:
			schema = self.common_patterns[param_name].copy()
			if description:
				schema["description"] = description
			return schema

		# Inferir tipo si no está especificado
		if not param_type and default_value is not None:
			param_type = type(default_value).__name__

		# Generar esquema base del tipo
		if param_type:
			schema = self._python_type_to_json_schema(param_type)
		else:
			schema = {"type": "string"}  # Default fallback

		# Agregar descripción si existe
		if description:
			schema["description"] = description

		# Agregar default si existe
		if default_value is not None:
			schema["default"] = default_value

		# Patrones específicos por nombre de parámetro
		schema.update(self._apply_name_patterns(param_name))

		return schema

	def _python_type_to_json_schema(self, python_type: str) -> dict[str, Any]:
		"""Convierte tipo de Python a esquema JSON"""

		# Limpiar type annotation complejo
		clean_type = python_type.strip()

		# Manejar tipos Union (ej: Union[str, None])
		if "Union[" in clean_type:
			return self._handle_union_type(clean_type)

		# Manejar tipos List (ej: list[str])
		if "list[" in clean_type or "list[" in clean_type:
			return self._handle_list_type(clean_type)

		# Manejar tipos Dict (ej: dict[str, Any])
		if "dict[" in clean_type or "dict[" in clean_type:
			return self._handle_dict_type(clean_type)

		# Tipos básicos
		base_type = clean_type.split("[")[0]  # Remover generics

		return self.frappe_types.get(base_type, {"type": "string"})

	def _handle_union_type(self, type_str: str) -> dict[str, Any]:
		"""
		Maneja tipos Union.

		TODO: PHASE2: SCHEMA - Soporte completo para Union types con anyOf
		"""
		# Por ahora, simplificado
		if "None" in type_str:
			# Optional type
			base_type = type_str.replace("Union[", "").replace(", None]", "").replace("None, ", "")
			schema = self._python_type_to_json_schema(base_type)
			schema["nullable"] = True
			return schema

		return {"type": "string"}  # Fallback

	def _handle_list_type(self, type_str: str) -> dict[str, Any]:
		"""Maneja tipos List"""
		# Extraer tipo del item
		item_type_match = type_str[type_str.find("[") + 1 : type_str.rfind("]")]

		schema = {"type": "array"}

		if item_type_match:
			schema["items"] = self._python_type_to_json_schema(item_type_match)

		return schema

	def _handle_dict_type(self, type_str: str) -> dict[str, Any]:
		"""Maneja tipos Dict"""
		return {"type": "object", "additionalProperties": True}

	def _apply_name_patterns(self, param_name: str) -> dict[str, Any]:
		"""Aplica patrones específicos basados en el nombre del parámetro"""
		patterns = {}

		# Patrones por nombre
		if param_name.endswith("_email") or param_name == "email":
			patterns["format"] = "email"
		elif param_name.endswith("_date") or param_name == "date":
			patterns["format"] = "date"
		elif param_name.endswith("_datetime") or param_name in ["datetime", "timestamp"]:
			patterns["format"] = "date-time"
		elif param_name.endswith("_url") or param_name == "url":
			patterns["format"] = "uri"
		elif "password" in param_name.lower():
			patterns["format"] = "password"
		elif param_name == "limit":
			patterns.update({"minimum": 1, "maximum": 1000})
		elif param_name == "offset":
			patterns["minimum"] = 0

		return patterns

	def _generate_response_from_type(
		self, return_type: str, description: str, function_name: str
	) -> dict[str, Any]:
		"""Genera esquema de response a partir del tipo de retorno"""

		schema = self._python_type_to_json_schema(return_type)

		if description:
			schema["description"] = description

		# Envolver en estructura de respuesta estándar de Frappe
		if function_name.startswith("get_") or "list" in function_name:
			# APIs que retornan datos suelen usar message wrapper
			return {"type": "object", "properties": {"message": schema}, "required": ["message"]}

		return schema

	def _infer_response_from_function_name(self, function_name: str) -> dict[str, Any]:
		"""Infiere esquema de response basado en el nombre de la función"""

		function_lower = function_name.lower()

		# Patrones comunes de respuesta
		if any(pattern in function_lower for pattern in ["get_", "fetch_", "find_"]):
			if "list" in function_lower or function_lower.endswith("s"):
				# Lista de elementos
				return {
					"type": "object",
					"properties": {"message": {"type": "array", "items": {"type": "object"}}},
				}
			else:
				# Elemento único
				return {"type": "object", "properties": {"message": {"type": "object"}}}

		elif any(pattern in function_lower for pattern in ["create_", "add_", "new_"]):
			# Operación de creación
			return {
				"type": "object",
				"properties": {
					"message": {
						"type": "object",
						"properties": {
							"name": {"type": "string", "description": "ID del documento creado"},
							"status": {"type": "string", "enum": ["success"]},
						},
					}
				},
			}

		elif any(pattern in function_lower for pattern in ["update_", "edit_", "modify_"]):
			# Operación de actualización
			return {
				"type": "object",
				"properties": {
					"message": {
						"type": "object",
						"properties": {
							"status": {"type": "string", "enum": ["success"]},
							"updated": {"type": "boolean"},
						},
					}
				},
			}

		elif any(pattern in function_lower for pattern in ["delete_", "remove_"]):
			# Operación de eliminación
			return {
				"type": "object",
				"properties": {
					"message": {
						"type": "object",
						"properties": {
							"status": {"type": "string", "enum": ["success"]},
							"deleted": {"type": "boolean"},
						},
					}
				},
			}

		# Default: respuesta genérica de éxito
		return {"type": "object", "properties": {"message": {"type": "object"}}}

	def generate_full_api_schema(self, api_info: dict[str, Any]) -> dict[str, Any]:
		"""
		Genera esquema completo de una API (request + response).

		Args:
			api_info: Información completa de la API del scanner/parser

		Returns:
			Dict con esquemas de request y response
		"""
		parameters = api_info.get("parameters", [])
		docstring_info = api_info.get("docstring_parsed", {})
		function_name = api_info.get("function_name", "")

		# Combinar parámetros del scanner con info del parser
		if docstring_info.get("parameters"):
			# Enriquecer parámetros con info del docstring
			param_map = {p["name"]: p for p in docstring_info["parameters"]}
			for param in parameters:
				if param["name"] in param_map:
					param.update(param_map[param["name"]])

		request_schema = self.generate_request_schema(parameters)
		response_schema = self.generate_response_schema(docstring_info.get("returns"), function_name)

		return {
			"request_schema": request_schema,
			"response_schema": response_schema,
			"openapi_format": self._convert_to_openapi_format(request_schema, response_schema, api_info),
		}

	def _convert_to_openapi_format(
		self, request_schema: dict[str, Any], response_schema: dict[str, Any], api_info: dict[str, Any]
	) -> dict[str, Any]:
		"""
		Convierte a formato OpenAPI 3.0.

		TODO: PHASE2: SCHEMA - Implementar conversión completa a OpenAPI 3.0
		"""
		openapi_spec = {
			"openapi": "3.0.0",
			"paths": {
				api_info.get("inferred_api_path", "/api/unknown"): {
					api_info.get("inferred_http_method", "post").lower(): {
						"summary": api_info.get("api_documentation_metadata", {}).get(
							"name", api_info.get("function_name", "Unknown API")
						),
						"description": api_info.get("docstring_parsed", {}).get("description", ""),
						"requestBody": {"content": {"application/json": {"schema": request_schema}}},
						"responses": {
							"200": {
								"description": "Successful response",
								"content": {"application/json": {"schema": response_schema}},
							}
						},
					}
				}
			},
		}

		return openapi_spec


@frappe.whitelist()
def generate_api_schemas(api_info: dict[str, Any]) -> dict[str, Any]:
	"""
	API para generar esquemas de una API específica.

	Args:
		api_info: Información de la API

	Returns:
		Dict con esquemas generados
	"""
	generator = SchemaGenerator()
	schemas = generator.generate_full_api_schema(api_info)

	return {"success": True, "schemas": schemas}


def demo_schema_generator() -> None:
	"""
	Demostración del generador de esquemas.

	TODO: PHASE2: SCHEMA - Expandir demo con casos más complejos
	"""
	sample_api = {
		"function_name": "get_physical_spaces",
		"parameters": [
			{"name": "filters", "type_annotation": "dict", "is_required": False, "default_value": None},
			{"name": "limit", "type_annotation": "int", "is_required": False, "default_value": 20},
			{"name": "fields", "type_annotation": "list[str]", "is_required": False, "default_value": None},
		],
		"docstring_parsed": {
			"description": "Obtiene lista de espacios físicos con filtros opcionales",
			"parameters": [
				{"name": "filters", "type": "dict", "description": "Filtros de búsqueda"},
				{"name": "limit", "type": "int", "description": "Máximo número de resultados"},
			],
			"returns": {"type": "list", "description": "Lista de espacios físicos"},
		},
		"inferred_api_path": "/api/physical-spaces/get-physical-spaces",
		"inferred_http_method": "GET",
	}

	generator = SchemaGenerator()
	schemas = generator.generate_full_api_schema(sample_api)

	print("🔧 Schema Generator Demo")
	print("\nRequest Schema:")
	print(json.dumps(schemas["request_schema"], indent=2))
	print("\nResponse Schema:")
	print(json.dumps(schemas["response_schema"], indent=2))
