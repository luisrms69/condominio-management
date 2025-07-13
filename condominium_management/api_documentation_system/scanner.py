# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
API Scanner Module - Day 2 Auto-Documentation System
====================================================

Scanner de código para detectar automáticamente APIs con @frappe.whitelist()
y generar documentación automática.
"""

import ast
import inspect
import os
import re
from typing import Any, Optional

import frappe
from frappe import _


class APIScanner:
	"""
	Scanner que analiza código Python para encontrar APIs documentables.

	Detecta:
	- Funciones con @frappe.whitelist()
	- Funciones con @api_documentation()
	- Docstrings y type hints
	- Parámetros y sus tipos
	- Rutas y métodos HTTP
	"""

	def __init__(self, app_name: str = "condominium_management"):
		self.app_name = app_name
		self.app_path = frappe.get_app_path(app_name)
		self.found_apis: list[dict[str, Any]] = []

	def scan_entire_app(self) -> list[dict[str, Any]]:
		"""
		Escanea toda la aplicación buscando APIs.

		Returns:
			list[Dict]: Lista de APIs encontradas con metadata
		"""
		self.found_apis = []

		# Escanear todos los archivos Python en el app
		for root, dirs, files in os.walk(self.app_path):
			# Saltar directorios no relevantes
			dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

			for file in files:
				if file.endswith(".py") and not file.startswith("__"):
					file_path = os.path.join(root, file)
					self._scan_file(file_path)

		return self.found_apis

	def scan_module(self, module_path: str) -> list[dict[str, Any]]:
		"""
		Escanea un módulo específico.

		Args:
			module_path: Path relativo al módulo (ej: "committee_management.api")

		Returns:
			list[Dict]: APIs encontradas en el módulo
		"""
		self.found_apis = []
		full_path = os.path.join(self.app_path, *module_path.split("."))

		if os.path.isfile(full_path + ".py"):
			self._scan_file(full_path + ".py")
		elif os.path.isdir(full_path):
			for file in os.listdir(full_path):
				if file.endswith(".py") and not file.startswith("__"):
					self._scan_file(os.path.join(full_path, file))

		return self.found_apis

	def _scan_file(self, file_path: str) -> None:
		"""
		Escanea un archivo Python específico.

		Args:
			file_path: Ruta completa al archivo
		"""
		try:
			with open(file_path, encoding="utf-8") as f:
				content = f.read()

			# Parsear AST del archivo
			tree = ast.parse(content)

			# Obtener path relativo para módulo
			rel_path = os.path.relpath(file_path, self.app_path)
			module_path = rel_path.replace(os.sep, ".").replace(".py", "")

			# Buscar funciones con decoradores relevantes
			for node in ast.walk(tree):
				if isinstance(node, ast.FunctionDef):
					api_info = self._analyze_function(node, module_path, content)
					if api_info:
						self.found_apis.append(api_info)

		except Exception as e:
			frappe.log_error(f"Error scanning file {file_path}: {e!s}", "API Scanner")

	def _analyze_function(
		self, node: ast.FunctionDef, module_path: str, file_content: str
	) -> dict[str, Any] | None:
		"""
		Analiza una función para ver si es una API documentable.

		Args:
			node: Nodo AST de la función
			module_path: Path del módulo
			file_content: Contenido completo del archivo

		Returns:
			Dict con metadata de la API o None si no es API
		"""
		# Verificar decoradores
		has_whitelist = False
		has_api_doc = False
		api_doc_metadata = {}

		for decorator in node.decorator_list:
			# Verificar @frappe.whitelist()
			if (
				isinstance(decorator, ast.Call)
				and isinstance(decorator.func, ast.Attribute)
				and decorator.func.attr == "whitelist"
			):
				has_whitelist = True

			# Verificar @api_documentation()
			elif (
				isinstance(decorator, ast.Call)
				and isinstance(decorator.func, ast.Name)
				and decorator.func.id == "api_documentation"
			):
				has_api_doc = True
				api_doc_metadata = self._extract_decorator_args(decorator)

		# Solo procesar si tiene @frappe.whitelist()
		if not has_whitelist:
			return None

		# Extraer información de la función
		function_info = {
			"function_name": node.name,
			"module_path": module_path,
			"line_number": node.lineno,
			"has_api_documentation_decorator": has_api_doc,
			"api_documentation_metadata": api_doc_metadata,
			"parameters": self._extract_parameters(node),
			"docstring": self._extract_docstring(node),
			"type_hints": self._extract_type_hints(node),
			"inferred_api_path": self._infer_api_path(module_path, node.name),
			"inferred_http_method": self._infer_http_method(node.name),
		}

		return function_info

	def _extract_decorator_args(self, decorator: ast.Call) -> dict[str, Any]:
		"""Extrae argumentos del decorador @api_documentation()"""
		metadata = {}

		# Argumentos posicionales (aunque no se usan en este decorador)
		for arg in decorator.args:
			if isinstance(arg, ast.Constant):
				metadata["_positional_args"] = metadata.get("_positional_args", [])
				metadata["_positional_args"].append(arg.value)

		# Argumentos con keyword
		for keyword in decorator.keywords:
			if isinstance(keyword.value, ast.Constant):
				metadata[keyword.arg] = keyword.value.value

		return metadata

	def _extract_parameters(self, node: ast.FunctionDef) -> list[dict[str, Any]]:
		"""Extrae parámetros de la función"""
		params = []

		for arg in node.args.args:
			if arg.arg not in ["self", "cls"]:  # Skip self/cls
				param_info = {
					"name": arg.arg,
					"type_annotation": None,
					"default_value": None,
					"is_required": True,
				}

				# Extraer type annotation si existe
				if arg.annotation:
					param_info["type_annotation"] = ast.unparse(arg.annotation)

				params.append(param_info)

		# Manejar defaults
		defaults = node.args.defaults
		if defaults:
			# Los defaults se aplican a los últimos parámetros
			num_defaults = len(defaults)
			for i, default in enumerate(defaults):
				param_index = len(params) - num_defaults + i
				if param_index >= 0 and param_index < len(params):
					params[param_index]["is_required"] = False
					if isinstance(default, ast.Constant):
						params[param_index]["default_value"] = default.value
					else:
						params[param_index]["default_value"] = ast.unparse(default)

		return params

	def _extract_docstring(self, node: ast.FunctionDef) -> str | None:
		"""Extrae docstring de la función"""
		if (
			node.body
			and isinstance(node.body[0], ast.Expr)
			and isinstance(node.body[0].value, ast.Constant)
			and isinstance(node.body[0].value.value, str)
		):
			return node.body[0].value.value.strip()
		return None

	def _extract_type_hints(self, node: ast.FunctionDef) -> dict[str, str]:
		"""Extrae type hints de la función"""
		type_hints = {}

		# Return type
		if node.returns:
			type_hints["return"] = ast.unparse(node.returns)

		# Parameter types (ya se manejan en _extract_parameters)
		return type_hints

	def _infer_api_path(self, module_path: str, function_name: str) -> str:
		"""
		Infiere la ruta de API basada en el módulo y función.

		TODO: PHASE2: SCANNER - Mejorar inferencia de rutas con patrones más complejos
		"""
		# Remover prefijo del app
		clean_path = module_path.replace(f"{self.app_name}.", "")

		# Convertir a path de API
		path_parts = clean_path.split(".")

		# Casos especiales para APIs
		if "api" in path_parts:
			# Remover 'api' del path
			path_parts = [p for p in path_parts if p != "api"]

		# Agregar función al final
		path_parts.append(function_name)

		# Crear path con guiones en lugar de underscores
		api_path = "/" + "/".join([part.replace("_", "-") for part in path_parts])

		return api_path

	def _infer_http_method(self, function_name: str) -> str:
		"""
		Infiere método HTTP basado en el nombre de la función.

		TODO: PHASE2: SCANNER - Mejorar inferencia con análisis de código
		"""
		function_lower = function_name.lower()

		if any(verb in function_lower for verb in ["get", "fetch", "find", "list", "search"]):
			return "GET"
		elif any(verb in function_lower for verb in ["create", "add", "new", "insert"]):
			return "POST"
		elif any(verb in function_lower for verb in ["update", "edit", "modify", "change"]):
			return "PUT"
		elif any(verb in function_lower for verb in ["delete", "remove", "del"]):
			return "DELETE"
		else:
			return "POST"  # Default para APIs que modifican datos


@frappe.whitelist()
def scan_apis_in_app(app_name: str = "condominium_management") -> dict[str, Any]:
	"""
	API para escanear todas las APIs en una aplicación.

	Args:
		app_name: Nombre de la aplicación a escanear

	Returns:
		Dict con APIs encontradas y estadísticas
	"""
	scanner = APIScanner(app_name)
	found_apis = scanner.scan_entire_app()

	# Estadísticas
	stats = {
		"total_apis_found": len(found_apis),
		"apis_with_documentation": len([api for api in found_apis if api["has_api_documentation_decorator"]]),
		"apis_without_documentation": len(
			[api for api in found_apis if not api["has_api_documentation_decorator"]]
		),
		"modules_scanned": len(set(api["module_path"] for api in found_apis)),
	}

	return {"success": True, "apis": found_apis, "statistics": stats}


@frappe.whitelist()
def scan_apis_in_module(module_path: str) -> dict[str, Any]:
	"""
	API para escanear APIs en un módulo específico.

	Args:
		module_path: Path del módulo (ej: "committee_management.api")

	Returns:
		Dict con APIs encontradas
	"""
	scanner = APIScanner()
	found_apis = scanner.scan_module(module_path)

	return {"success": True, "apis": found_apis, "count": len(found_apis)}


def preview_api_scan(limit: int = 10) -> None:
	"""
	Función de utilidad para preview del scanner en consola.

	TODO: PHASE2: SCANNER - Mejorar preview con más detalles
	"""
	scanner = APIScanner()
	apis = scanner.scan_entire_app()

	print(f"\n🔍 API Scanner Preview - Found {len(apis)} APIs\n")

	for i, api in enumerate(apis[:limit]):
		print(f"{i+1}. {api['function_name']} ({api['module_path']})")
		print(f"   Path: {api['inferred_api_path']}")
		print(f"   Method: {api['inferred_http_method']}")
		print(f"   Has Doc: {'✅' if api['has_api_documentation_decorator'] else '❌'}")
		print(f"   Params: {len(api['parameters'])}")
		if api["docstring"]:
			print(f"   Docstring: {api['docstring'][:50]}...")
		print()

	if len(apis) > limit:
		print(f"... and {len(apis) - limit} more APIs")
