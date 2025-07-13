# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
API Tester Module - Day 3 Portal Web
====================================

Backend para testing interactivo de APIs desde el portal web.
"""

import json
import time
from typing import Any, Optional

import frappe
import requests
from frappe import _


@frappe.whitelist()
def test_api_endpoint(
	api_name: str,
	method: str | None = None,
	parameters: dict[str, Any] | None = None,
	headers: dict[str, str] | None = None,
) -> dict[str, Any]:
	"""
	Ejecuta test de una API específica desde el portal.

	Args:
		api_name: Nombre/ID de la API a probar
		method: Método HTTP override (opcional)
		parameters: Parámetros para el request
		headers: Headers adicionales

	Returns:
		Dict con resultado del test
	"""
	try:
		# Obtener detalles de la API
		api_doc = frappe.get_doc("API Documentation", api_name)

		if not api_doc.sandbox_enabled:
			return {
				"success": False,
				"error": "Sandbox deshabilitado para esta API",
				"error_type": "sandbox_disabled",
			}

		# Preparar request
		base_url = frappe.utils.get_url()
		api_path = api_doc.api_path
		http_method = method or api_doc.http_method

		# Construir URL completa
		if api_path.startswith("/api/method/"):
			test_url = f"{base_url}{api_path}"
		else:
			test_url = f"{base_url}/api/method{api_path}"

		# Preparar headers
		request_headers = {"Content-Type": "application/json", "Accept": "application/json"}

		# Agregar autenticación si es requerida
		if api_doc.authentication_required:
			# Usar la sesión actual del usuario
			csrf_token = frappe.sessions.get_csrf_token()
			request_headers["X-Frappe-CSRF-Token"] = csrf_token

			# Agregar cookies de sesión
			sid = frappe.session.sid
			request_headers["Cookie"] = f"sid={sid}"

		# Agregar headers adicionales
		if headers:
			request_headers.update(headers)

		# Preparar parámetros
		request_params = parameters or {}

		# Verificar rate limiting
		rate_limit_check = _check_rate_limit(api_doc)
		if not rate_limit_check["allowed"]:
			return {
				"success": False,
				"error": "Rate limit excedido",
				"error_type": "rate_limit",
				"retry_after": rate_limit_check.get("retry_after", 60),
			}

		# Ejecutar request
		start_time = time.time()

		if http_method.upper() == "GET":
			response = requests.get(
				test_url,
				params=request_params,
				headers=request_headers,
				timeout=30,
				verify=False,  # TODO: PHASE2: TESTER - Configurar SSL apropiadamente
			)
		else:
			response = requests.request(
				http_method.upper(),
				test_url,
				json=request_params,
				headers=request_headers,
				timeout=30,
				verify=False,
			)

		end_time = time.time()
		response_time = round((end_time - start_time) * 1000, 2)  # en millisegundos

		# Procesar respuesta
		try:
			response_json = response.json()
		except json.JSONDecodeError:
			response_json = {"raw_response": response.text}

		# Log del test
		_log_api_test(
			api_doc,
			{
				"method": http_method,
				"parameters": request_params,
				"status_code": response.status_code,
				"response_time": response_time,
				"success": response.status_code < 400,
			},
		)

		return {
			"success": True,
			"test_result": {
				"status_code": response.status_code,
				"status_text": response.reason,
				"response_time_ms": response_time,
				"response_headers": dict(response.headers),
				"response_body": response_json,
				"request_url": test_url,
				"request_method": http_method.upper(),
				"request_headers": request_headers,
				"request_params": request_params,
			},
		}

	except requests.RequestException as e:
		return {"success": False, "error": f"Error de conexión: {e!s}", "error_type": "connection_error"}
	except Exception as e:
		frappe.log_error(f"Error testing API {api_name}: {e!s}", "API Tester")
		return {"success": False, "error": f"Error interno: {e!s}", "error_type": "internal_error"}


@frappe.whitelist()
def get_api_test_template(api_name: str) -> dict[str, Any]:
	"""
	Obtiene template de parámetros para testing de una API.

	Args:
		api_name: Nombre/ID de la API

	Returns:
		Dict con template de parámetros
	"""
	try:
		api_doc = frappe.get_doc("API Documentation", api_name)

		# Obtener parámetros de la API
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
			],
			order_by="idx",
		)

		# Generar template de request
		request_template = {}
		parameter_info = []

		for param in parameters:
			param_name = param["parameter_name"]
			param_type = param["data_type"]
			is_required = param["is_required"]
			default_value = param["default_value"]

			# Generar valor de ejemplo
			example_value = _generate_example_value(param_type, default_value)

			if is_required:
				request_template[param_name] = example_value

			parameter_info.append(
				{
					"name": param_name,
					"type": param_type,
					"required": is_required,
					"default": default_value,
					"description": param["parameter_description"],
					"example": example_value,
				}
			)

		return {
			"success": True,
			"template": {
				"api_name": api_doc.api_name,
				"api_path": api_doc.api_path,
				"http_method": api_doc.http_method,
				"authentication_required": api_doc.authentication_required,
				"request_template": request_template,
				"parameters": parameter_info,
				"headers_template": {"Content-Type": "application/json"},
			},
		}

	except Exception as e:
		frappe.log_error(f"Error getting test template for {api_name}: {e!s}", "API Tester")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_test_history(api_name: str | None = None, limit: int = 10) -> dict[str, Any]:
	"""
	Obtiene historial de tests de APIs.

	Args:
		api_name: API específica (opcional)
		limit: Límite de resultados

	Returns:
		Dict con historial de tests
	"""
	try:
		# TODO: PHASE2: TESTER - Implementar tabla de log de tests
		# Por ahora retornar mock data

		mock_history = [
			{
				"id": 1,
				"api_name": "Test API",
				"method": "GET",
				"status_code": 200,
				"response_time": 150,
				"timestamp": frappe.utils.now(),
				"success": True,
			}
		]

		return {"success": True, "history": mock_history, "count": len(mock_history)}

	except Exception as e:
		frappe.log_error(f"Error getting test history: {e!s}", "API Tester")
		return {"success": False, "error": str(e)}


def _check_rate_limit(api_doc) -> dict[str, Any]:
	"""
	Verifica rate limiting para la API.

	TODO: PHASE2: TESTER - Implementar rate limiting real
	"""
	# Por ahora, siempre permitir
	return {"allowed": True}


def _log_api_test(api_doc, test_result: dict[str, Any]) -> None:
	"""
	Registra el test de API para estadísticas.

	TODO: PHASE2: TESTER - Implementar logging de tests
	"""
	try:
		# Por ahora, solo log básico
		frappe.logger().info(
			f"API Test: {api_doc.api_name} - {test_result['status_code']} in {test_result['response_time']}ms"
		)
	except Exception:
		pass


def _generate_example_value(data_type: str, default_value: str | None = None):
	"""Genera valor de ejemplo para un tipo de dato"""
	if default_value:
		return default_value

	examples = {
		"string": "ejemplo",
		"integer": 1,
		"float": 1.0,
		"boolean": True,
		"object": {},
		"array": [],
		"date": frappe.utils.today(),
		"datetime": frappe.utils.now(),
	}

	return examples.get(data_type.lower(), "valor_ejemplo")
