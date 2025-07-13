# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Auto Importer Module - Day 2 Auto-Documentation System
======================================================

Importador masivo que combina scanner, parser y schema generator
para documentar automáticamente todas las APIs existentes.
"""

from typing import Any, Optional

import frappe
from frappe import _

from .parser import DocstringParser
from .scanner import APIScanner
from .schema_generator import SchemaGenerator


class AutoAPIImporter:
	"""
	Importador que procesa automáticamente APIs y las registra en API Documentation.

	Pipeline:
	1. Scanner → Encuentra APIs con @frappe.whitelist()
	2. Parser → Extrae información de docstrings
	3. Schema Generator → Crea esquemas JSON
	4. Auto Registration → Registra en DocType
	"""

	def __init__(self, app_name: str = "condominium_management"):
		self.app_name = app_name
		self.scanner = APIScanner(app_name)
		self.parser = DocstringParser()
		self.schema_generator = SchemaGenerator()

		self.processed_apis: list[dict[str, Any]] = []
		self.import_stats = {
			"total_scanned": 0,
			"successfully_imported": 0,
			"updated_existing": 0,
			"failed_imports": 0,
			"skipped_decorated": 0,
			"errors": [],
		}

	def import_all_apis(self, skip_existing_decorated: bool = True, dry_run: bool = False) -> dict[str, Any]:
		"""
		Importa todas las APIs de la aplicación.

		Args:
			skip_existing_decorated: Si True, omite APIs que ya tienen @api_documentation
			dry_run: Si True, solo simula la importación sin guardar

		Returns:
			Dict con estadísticas de la importación
		"""
		frappe.logger().info("🚀 Iniciando importación masiva de APIs")

		# 1. Escanear todas las APIs
		found_apis = self.scanner.scan_entire_app()
		self.import_stats["total_scanned"] = len(found_apis)

		frappe.logger().info(f"📊 APIs encontradas: {len(found_apis)}")

		# 2. Procesar cada API
		for api_info in found_apis:
			try:
				processed_api = self._process_single_api(api_info)

				# Verificar si saltar APIs ya decoradas
				if skip_existing_decorated and api_info.get("has_api_documentation_decorator"):
					self.import_stats["skipped_decorated"] += 1
					continue

				# 3. Registrar en DocType (si no es dry run)
				if not dry_run:
					result = self._register_api_documentation(processed_api)
					if result["success"]:
						if result["action"] == "created":
							self.import_stats["successfully_imported"] += 1
						else:
							self.import_stats["updated_existing"] += 1
					else:
						self.import_stats["failed_imports"] += 1
						self.import_stats["errors"].append(
							{"api": api_info["function_name"], "error": result["error"]}
						)
				else:
					self.import_stats["successfully_imported"] += 1

				self.processed_apis.append(processed_api)

			except Exception as e:
				self.import_stats["failed_imports"] += 1
				self.import_stats["errors"].append(
					{"api": api_info.get("function_name", "unknown"), "error": str(e)}
				)
				frappe.log_error(
					f"Error processing API {api_info.get('function_name')}: {e!s}", "Auto Importer"
				)

		return {
			"success": True,
			"statistics": self.import_stats,
			"processed_apis": self.processed_apis if dry_run else [],
		}

	def import_module_apis(self, module_path: str, **kwargs) -> dict[str, Any]:
		"""
		Importa APIs de un módulo específico.

		Args:
			module_path: Path del módulo a importar
			**kwargs: Argumentos adicionales para import_all_apis

		Returns:
			Dict con resultados de la importación
		"""
		# Temporal: cambiar scanner para escanear solo el módulo
		found_apis = self.scanner.scan_module(module_path)

		# Procesar solo las APIs del módulo
		original_scan = self.scanner.scan_entire_app
		self.scanner.scan_entire_app = lambda: found_apis

		try:
			return self.import_all_apis(**kwargs)
		finally:
			self.scanner.scan_entire_app = original_scan

	def _process_single_api(self, api_info: dict[str, Any]) -> dict[str, Any]:
		"""
		Procesa una sola API a través del pipeline completo.

		Args:
			api_info: Información de la API del scanner

		Returns:
			Dict con información completa procesada
		"""
		# 1. Parsear docstring si existe
		docstring_info = {}
		if api_info.get("docstring"):
			docstring_info = self.parser.parse_docstring(api_info["docstring"])

		# 2. Generar esquemas
		api_with_docstring = api_info.copy()
		api_with_docstring["docstring_parsed"] = docstring_info

		schemas = self.schema_generator.generate_full_api_schema(api_with_docstring)

		# 3. Combinar toda la información
		processed_api = {
			# Información base del scanner
			**api_info,
			# Información del parser
			"docstring_parsed": docstring_info,
			# Esquemas generados
			"request_schema": schemas["request_schema"],
			"response_schema": schemas["response_schema"],
			"openapi_format": schemas["openapi_format"],
			# Metadatos de procesamiento
			"auto_generated": True,
			"generation_source": "auto_importer",
			"needs_manual_review": self._needs_manual_review(api_info, docstring_info),
		}

		return processed_api

	def _needs_manual_review(self, api_info: dict[str, Any], docstring_info: dict[str, Any]) -> bool:
		"""
		Determina si una API necesita revisión manual.

		Args:
			api_info: Información del scanner
			docstring_info: Información del parser

		Returns:
			bool: True si necesita revisión manual
		"""
		# Criterios para revisión manual
		needs_review = False

		# Sin docstring o docstring muy corto
		if not docstring_info.get("description") or len(docstring_info["description"]) < 20:
			needs_review = True

		# Sin parámetros documentados pero con parámetros en función
		if api_info.get("parameters") and not docstring_info.get("parameters"):
			needs_review = True

		# Parámetros sin tipos
		for param in api_info.get("parameters", []):
			if not param.get("type_annotation") and not param.get("type"):
				needs_review = True
				break

		# Funciones complejas (muchos parámetros)
		if len(api_info.get("parameters", [])) > 5:
			needs_review = True

		return needs_review

	def _register_api_documentation(self, processed_api: dict[str, Any]) -> dict[str, Any]:
		"""
		Registra la API procesada en el DocType API Documentation.

		Args:
			processed_api: API completamente procesada

		Returns:
			Dict con resultado de la operación
		"""
		try:
			# Preparar datos para el DocType
			api_name = self._generate_api_name(processed_api)
			api_path = processed_api.get("inferred_api_path", "/api/unknown")

			# Verificar si ya existe
			existing = frappe.db.get_value("API Documentation", {"api_path": api_path}, "name")

			if existing:
				# Actualizar existente
				doc = frappe.get_doc("API Documentation", existing)
				action = "updated"
			else:
				# Crear nuevo
				doc = frappe.new_doc("API Documentation")
				action = "created"

			# Actualizar campos básicos
			doc.update(
				{
					"api_name": api_name,
					"api_path": api_path,
					"api_version": "v1",  # TODO: PHASE2: VERSIONADO - Detectar versión automáticamente
					"http_method": processed_api.get("inferred_http_method", "POST"),
					"description": self._generate_description(processed_api),
					"module_path": processed_api.get("module_path", ""),
					"function_name": processed_api.get("function_name", ""),
					"is_active": 1,
					"auto_generated": 1,
					"needs_manual_review": processed_api.get("needs_manual_review", False),
					# Esquemas como JSON
					"request_schema": frappe.as_json(processed_api.get("request_schema", {})),
					"response_schema": frappe.as_json(processed_api.get("response_schema", {})),
					# Metadatos adicionales
					"generation_source": "auto_importer",
					"last_auto_update": frappe.utils.now(),
				}
			)

			# Crear child tables
			self._populate_child_tables(doc, processed_api)

			# Guardar documento
			if action == "created":
				doc.insert(ignore_permissions=True)
			else:
				doc.save(ignore_permissions=True)

			frappe.db.commit()

			return {"success": True, "action": action, "document_name": doc.name, "api_name": api_name}

		except Exception as e:
			frappe.db.rollback()
			return {"success": False, "error": str(e)}

	def _generate_api_name(self, processed_api: dict[str, Any]) -> str:
		"""Genera nombre descriptivo para la API"""
		# Usar metadata del decorador si existe
		if processed_api.get("api_documentation_metadata", {}).get("name"):
			return processed_api["api_documentation_metadata"]["name"]

		# Generar desde nombre de función
		function_name = processed_api.get("function_name", "unknown")

		# Convertir snake_case a Title Case
		words = function_name.replace("_", " ").split()
		return " ".join(word.capitalize() for word in words)

	def _generate_description(self, processed_api: dict[str, Any]) -> str:
		"""Genera descripción para la API"""
		# Usar descripción del docstring si existe
		docstring_desc = processed_api.get("docstring_parsed", {}).get("description", "")
		if docstring_desc:
			return docstring_desc

		# Usar metadata del decorador
		if processed_api.get("api_documentation_metadata", {}).get("description"):
			return processed_api["api_documentation_metadata"]["description"]

		# Generar descripción básica
		function_name = processed_api.get("function_name", "unknown")
		return f"API generada automáticamente para la función {function_name}"

	def _populate_child_tables(
		self, doc: "frappe.model.document.Document", processed_api: dict[str, Any]
	) -> None:
		"""
		Popula las child tables con información de parámetros y responses.

		TODO: PHASE2: IMPORTER - Generar ejemplos de código automáticamente
		"""
		# Limpiar child tables existentes
		doc.parameters = []
		doc.response_codes = []
		doc.code_examples = []

		# Agregar parámetros
		for param in processed_api.get("parameters", []):
			doc.append(
				"parameters",
				{
					"parameter_name": param.get("name", ""),
					"parameter_type": "body",  # TODO: PHASE2: IMPORTER - Detectar tipo de parámetro
					"data_type": self._convert_python_type_to_api_type(
						param.get("type_annotation") or param.get("type", "string")
					),
					"is_required": param.get("is_required", param.get("required", True)),
					"default_value": str(param.get("default_value", ""))
					if param.get("default_value") is not None
					else "",
					"parameter_description": param.get("description", ""),
				},
			)

		# Agregar códigos de respuesta estándar
		doc.append(
			"response_codes",
			{
				"status_code": 200,
				"response_description": "Operación exitosa",
				"response_example": frappe.as_json(processed_api.get("response_schema", {}), indent=2),
			},
		)

		if processed_api.get("needs_manual_review"):
			doc.append(
				"response_codes",
				{
					"status_code": 400,
					"response_description": "Error de validación",
					"response_example": '{"exc": "ValidationError: Campo requerido faltante"}',
				},
			)

	def _convert_python_type_to_api_type(self, python_type: str) -> str:
		"""Convierte tipos de Python a tipos de API Documentation"""
		type_mapping = {
			"str": "string",
			"int": "integer",
			"float": "float",
			"bool": "boolean",
			"dict": "object",
			"list": "array",
			"List": "array",
			"Dict": "object",
			"Any": "string",
		}

		# Limpiar tipo (remover list[...], etc.)
		clean_type = python_type.split("[")[0] if "[" in python_type else python_type

		return type_mapping.get(clean_type, "string")


@frappe.whitelist()
def import_all_apis(
	app_name: str = "condominium_management", skip_existing_decorated: bool = True, dry_run: bool = False
) -> dict[str, Any]:
	"""
	API para importar todas las APIs de una aplicación.

	Args:
		app_name: Nombre de la aplicación
		skip_existing_decorated: Omitir APIs ya decoradas
		dry_run: Solo simular sin guardar

	Returns:
		Dict con resultados de la importación
	"""
	importer = AutoAPIImporter(app_name)
	result = importer.import_all_apis(skip_existing_decorated, dry_run)

	# Log del resultado
	stats = result["statistics"]
	frappe.logger().info(
		f"✅ Importación completada: {stats['successfully_imported']} exitosas, "
		f"{stats['failed_imports']} fallos, {stats['skipped_decorated']} omitidas"
	)

	return result


@frappe.whitelist()
def import_module_apis(module_path: str, **kwargs) -> dict[str, Any]:
	"""
	API para importar APIs de un módulo específico.

	Args:
		module_path: Path del módulo
		**kwargs: Argumentos adicionales

	Returns:
		Dict con resultados
	"""
	importer = AutoAPIImporter()
	return importer.import_module_apis(module_path, **kwargs)


@frappe.whitelist()
def get_import_preview(app_name: str = "condominium_management", limit: int = 10) -> dict[str, Any]:
	"""
	Obtiene preview de qué APIs serían importadas.

	Args:
		app_name: Nombre de la aplicación
		limit: Límite de APIs a mostrar en preview

	Returns:
		Dict con preview de importación
	"""
	importer = AutoAPIImporter(app_name)
	result = importer.import_all_apis(dry_run=True)

	# Limitar resultados para preview
	preview_apis = result["processed_apis"][:limit]

	return {
		"success": True,
		"statistics": result["statistics"],
		"preview_apis": preview_apis,
		"total_apis": len(result["processed_apis"]),
		"showing_limit": limit,
	}
