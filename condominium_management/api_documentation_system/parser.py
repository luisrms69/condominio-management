# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
DocString Parser Module - Day 2 Auto-Documentation System
=========================================================

Parser especializado para extraer información estructurada de docstrings
y convertirla en documentación de API.
"""

import re
from typing import Any, Optional

import frappe


class DocstringParser:
	"""
	Parser que extrae información estructurada de docstrings.

	Soporta formatos:
	- Google Style (Args:, Returns:, Raises:)
	- Sphinx Style (:param:, :returns:, :raises:)
	- Numpy Style (Parameters, Returns, Raises)
	"""

	def __init__(self):
		self.google_patterns = {
			"args": re.compile(r"Args?:\s*\n(.*?)(?=\n\s*\w+:|$)", re.DOTALL | re.IGNORECASE),
			"returns": re.compile(r"Returns?:\s*\n(.*?)(?=\n\s*\w+:|$)", re.DOTALL | re.IGNORECASE),
			"raises": re.compile(r"Raises?:\s*\n(.*?)(?=\n\s*\w+:|$)", re.DOTALL | re.IGNORECASE),
			"examples": re.compile(r"Examples?:\s*\n(.*?)(?=\n\s*\w+:|$)", re.DOTALL | re.IGNORECASE),
		}

		self.sphinx_patterns = {
			"param": re.compile(r":param\s+(\w+):\s*(.*?)(?=\n\s*:|$)", re.DOTALL),
			"type": re.compile(r":type\s+(\w+):\s*(.*?)(?=\n\s*:|$)", re.DOTALL),
			"returns": re.compile(r":returns?:\s*(.*?)(?=\n\s*:|$)", re.DOTALL),
			"rtype": re.compile(r":rtype:\s*(.*?)(?=\n\s*:|$)", re.DOTALL),
			"raises": re.compile(r":raises?\s+(\w+):\s*(.*?)(?=\n\s*:|$)", re.DOTALL),
		}

	def parse_docstring(self, docstring: str) -> dict[str, Any]:
		"""
		Parsea un docstring y extrae información estructurada.

		Args:
			docstring: El docstring a parsear

		Returns:
			Dict con información parseada:
			- description: Descripción principal
			- parameters: Lista de parámetros con tipos y descripciones
			- returns: Información de retorno
			- raises: Excepciones que puede lanzar
			- examples: Ejemplos de uso
		"""
		if not docstring or not docstring.strip():
			return self._empty_result()

		# Limpiar y normalizar docstring
		clean_docstring = self._clean_docstring(docstring)

		# Detectar formato del docstring
		docstring_format = self._detect_format(clean_docstring)

		# Parsear según el formato detectado
		if docstring_format == "google":
			return self._parse_google_style(clean_docstring)
		elif docstring_format == "sphinx":
			return self._parse_sphinx_style(clean_docstring)
		elif docstring_format == "numpy":
			return self._parse_numpy_style(clean_docstring)
		else:
			return self._parse_plain_text(clean_docstring)

	def _clean_docstring(self, docstring: str) -> str:
		"""Limpia y normaliza el docstring"""
		# Remover indentación común
		lines = docstring.strip().split("\n")
		if len(lines) <= 1:
			return docstring.strip()

		# Encontrar indentación mínima (ignorando líneas vacías)
		min_indent = float("inf")
		for line in lines[1:]:  # Skip primera línea
			if line.strip():
				indent = len(line) - len(line.lstrip())
				min_indent = min(min_indent, indent)

		if min_indent == float("inf"):
			min_indent = 0

		# Remover indentación común
		cleaned_lines = [lines[0]]  # Primera línea sin modificar
		for line in lines[1:]:
			if line.strip():
				cleaned_lines.append(line[min_indent:])
			else:
				cleaned_lines.append("")

		return "\n".join(cleaned_lines)

	def _detect_format(self, docstring: str) -> str:
		"""Detecta el formato del docstring"""
		# Google style: Args:, Returns:, etc.
		if any(pattern.search(docstring) for pattern in self.google_patterns.values()):
			return "google"

		# Sphinx style: :param:, :returns:, etc.
		if any(pattern.search(docstring) for pattern in self.sphinx_patterns.values()):
			return "sphinx"

		# Numpy style: Parameters, Returns (con líneas de guiones)
		if re.search(r"\n\s*Parameters\s*\n\s*-+\s*\n", docstring, re.IGNORECASE):
			return "numpy"

		return "plain"

	def _parse_google_style(self, docstring: str) -> dict[str, Any]:
		"""Parsea docstring formato Google"""
		result = self._empty_result()

		# Extraer descripción (texto antes del primer Args:/Returns:/etc.)
		first_section = re.search(
			r"^(.*?)(?=\n\s*(?:Args?|Returns?|Raises?|Examples?):|$)", docstring, re.DOTALL | re.IGNORECASE
		)
		if first_section:
			result["description"] = first_section.group(1).strip()

		# Parsear Args
		args_match = self.google_patterns["args"].search(docstring)
		if args_match:
			result["parameters"] = self._parse_google_args(args_match.group(1))

		# Parsear Returns
		returns_match = self.google_patterns["returns"].search(docstring)
		if returns_match:
			result["returns"] = self._parse_google_returns(returns_match.group(1))

		# Parsear Raises
		raises_match = self.google_patterns["raises"].search(docstring)
		if raises_match:
			result["raises"] = self._parse_google_raises(raises_match.group(1))

		# Parsear Examples
		examples_match = self.google_patterns["examples"].search(docstring)
		if examples_match:
			result["examples"] = examples_match.group(1).strip()

		return result

	def _parse_google_args(self, args_text: str) -> list[dict[str, Any]]:
		"""Parsea sección Args del formato Google"""
		parameters = []

		# Buscar parámetros con formato: param_name (type): description
		param_pattern = re.compile(
			r"^\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.*?)(?=\n\s*\w+\s*(?:\([^)]*\))?\s*:|$)",
			re.MULTILINE | re.DOTALL,
		)

		for match in param_pattern.finditer(args_text):
			param_name = match.group(1)
			param_type = match.group(2) if match.group(2) else None
			description = match.group(3).strip() if match.group(3) else ""

			# Limpiar descripción multilínea
			description = re.sub(r"\n\s+", " ", description)

			parameters.append(
				{
					"name": param_name,
					"type": param_type,
					"description": description,
					"required": True,  # TODO: PHASE2: PARSER - Detectar parámetros opcionales
				}
			)

		return parameters

	def _parse_google_returns(self, returns_text: str) -> dict[str, Any]:
		"""Parsea sección Returns del formato Google"""
		# Formato: type: description
		returns_pattern = re.compile(r"^(?:([^:]+):\s*)?(.*?)$", re.DOTALL)
		match = returns_pattern.match(returns_text.strip())

		if match:
			return_type = match.group(1).strip() if match.group(1) else None
			description = match.group(2).strip() if match.group(2) else ""

			# Limpiar descripción multilínea
			description = re.sub(r"\n\s+", " ", description)

			return {"type": return_type, "description": description}

		return {"type": None, "description": returns_text.strip()}

	def _parse_google_raises(self, raises_text: str) -> list[dict[str, Any]]:
		"""Parsea sección Raises del formato Google"""
		raises = []

		# Formato: ExceptionType: description
		raises_pattern = re.compile(r"^\s*(\w+)\s*:\s*(.*?)(?=\n\s*\w+\s*:|$)", re.MULTILINE | re.DOTALL)

		for match in raises_pattern.finditer(raises_text):
			exception_type = match.group(1)
			description = match.group(2).strip() if match.group(2) else ""

			# Limpiar descripción multilínea
			description = re.sub(r"\n\s+", " ", description)

			raises.append({"exception": exception_type, "description": description})

		return raises

	def _parse_sphinx_style(self, docstring: str) -> dict[str, Any]:
		"""
		Parsea docstring formato Sphinx.

		TODO: PHASE2: PARSER - Implementar parser completo Sphinx
		"""
		result = self._empty_result()

		# Por ahora, implementación básica
		# Extraer descripción principal
		desc_match = re.match(r"^(.*?)(?=\n\s*:)", docstring, re.DOTALL)
		if desc_match:
			result["description"] = desc_match.group(1).strip()

		# Extraer parámetros
		params = []
		for match in self.sphinx_patterns["param"].finditer(docstring):
			param_name = match.group(1)
			description = match.group(2).strip()

			# Buscar tipo correspondiente
			param_type = None
			type_match = re.search(rf":type\s+{param_name}:\s*(.*?)(?=\n\s*:|$)", docstring, re.DOTALL)
			if type_match:
				param_type = type_match.group(1).strip()

			params.append(
				{"name": param_name, "type": param_type, "description": description, "required": True}
			)

		result["parameters"] = params

		# Extraer returns
		returns_match = self.sphinx_patterns["returns"].search(docstring)
		if returns_match:
			return_desc = returns_match.group(1).strip()

			# Buscar tipo de retorno
			return_type = None
			rtype_match = self.sphinx_patterns["rtype"].search(docstring)
			if rtype_match:
				return_type = rtype_match.group(1).strip()

			result["returns"] = {"type": return_type, "description": return_desc}

		return result

	def _parse_numpy_style(self, docstring: str) -> dict[str, Any]:
		"""
		Parsea docstring formato Numpy.

		TODO: PHASE2: PARSER - Implementar parser completo Numpy
		"""
		result = self._empty_result()

		# Implementación básica para numpy style
		result["description"] = "Numpy style docstring detected"

		return result

	def _parse_plain_text(self, docstring: str) -> dict[str, Any]:
		"""Parsea docstring de texto plano"""
		result = self._empty_result()
		result["description"] = docstring.strip()
		return result

	def _empty_result(self) -> dict[str, Any]:
		"""Retorna estructura vacía de resultado"""
		return {
			"description": "",
			"parameters": [],
			"returns": None,
			"raises": [],
			"examples": None,
			"format_detected": "unknown",
		}


@frappe.whitelist()
def parse_function_docstring(docstring: str) -> dict[str, Any]:
	"""
	API para parsear un docstring específico.

	Args:
		docstring: El docstring a parsear

	Returns:
		Dict con información parseada
	"""
	parser = DocstringParser()
	result = parser.parse_docstring(docstring)

	return {"success": True, "parsed_info": result}


def demo_parser() -> None:
	"""
	Función de demostración del parser.

	TODO: PHASE2: PARSER - Expandir demo con más ejemplos
	"""
	sample_docstrings = [
		"""
		Obtiene lista de espacios físicos con filtros.

		Args:
			filters (dict): Filtros a aplicar
			limit (int): Límite de resultados
			include_inactive (bool): Incluir espacios inactivos

		Returns:
			list: Lista de espacios físicos encontrados

		Raises:
			ValidationError: Si los filtros son inválidos
		""",
		"""
		Crea un nuevo espacio físico.

		:param name: Nombre del espacio
		:type name: str
		:param category: Categoría del espacio
		:type category: str
		:returns: Espacio creado
		:rtype: dict
		:raises ValidationError: Si faltan campos requeridos
		""",
	]

	parser = DocstringParser()

	for i, docstring in enumerate(sample_docstrings, 1):
		print(f"\n--- Ejemplo {i} ---")
		result = parser.parse_docstring(docstring)
		print(f"Descripción: {result['description']}")
		print(f"Parámetros: {len(result['parameters'])}")
		for param in result["parameters"]:
			print(f"  - {param['name']} ({param['type']}): {param['description']}")
		if result["returns"]:
			print(f"Retorna: {result['returns']['type']} - {result['returns']['description']}")
