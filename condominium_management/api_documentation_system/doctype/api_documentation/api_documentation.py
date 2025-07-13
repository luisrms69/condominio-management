# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class APIDocumentation(Document):
	"""DocType para documentar APIs del sistema automáticamente"""

	def validate(self):
		"""Validaciones antes de guardar"""
		self.validate_api_path()
		self.validate_deprecation()
		self.validate_rate_limit()

	def validate_api_path(self):
		"""Validar formato de la ruta de API"""
		if not self.api_path:
			return

		# TODO: PHASE2: VALIDACIÓN - Validar formato de URL más estricto
		if not self.api_path.startswith("/"):
			self.api_path = "/" + self.api_path

	def validate_deprecation(self):
		"""Validar datos de deprecación"""
		if self.is_deprecated:
			if not self.deprecation_date:
				frappe.throw("Fecha de deprecación es requerida para APIs deprecadas")

			if get_datetime(self.deprecation_date) < now_datetime():
				frappe.msgprint(
					"Advertencia: Esta API ya ha pasado su fecha de deprecación", indicator="orange"
				)

	def validate_rate_limit(self):
		"""Validar límites de rate limiting"""
		if self.rate_limit and self.rate_limit < 1:
			frappe.throw("El límite de requests debe ser mayor a 0")

		if self.cache_timeout and self.cache_timeout < 0:
			frappe.throw("El timeout de cache no puede ser negativo")

	def on_update(self):
		"""Ejecutado después de actualizar el documento"""
		# TODO: PHASE2: PORTAL - Invalidar cache del portal
		# TODO: PHASE2: ANALYTICS - Registrar cambio para analytics
		pass

	def get_full_url(self):
		"""Retorna la URL completa de la API"""
		base_url = frappe.utils.get_url()
		version_path = f"/api/{self.api_version}" if self.api_version else "/api"
		return f"{base_url}{version_path}{self.api_path}"

	def get_example_request(self, language="curl"):
		"""Genera ejemplo de request en el lenguaje especificado

		TODO: PHASE2: EJEMPLOS - Soportar más lenguajes (Python, JavaScript, etc.)
		"""
		url = self.get_full_url()

		if language == "curl":
			auth_header = ""
			if self.authentication_required:
				auth_header = ' -H "Authorization: Bearer YOUR_API_KEY"'

			return f'curl -X {self.http_method}{auth_header} "{url}"'

		# TODO: PHASE2: EJEMPLOS - Implementar Python, JavaScript, etc.
		return "Ejemplo no disponible para este lenguaje"

	@frappe.whitelist()
	def test_api_endpoint(self):
		"""Permite probar el endpoint desde el DocType

		TODO: PHASE2: TESTING - Implementar testing real del endpoint
		"""
		frappe.msgprint(f"Testing endpoint: {self.get_full_url()}")
		return {"status": "success", "message": "Endpoint tested successfully"}


@frappe.whitelist()
def get_api_documentation_by_path(api_path, method="GET"):
	"""Obtiene documentación de API por ruta y método"""
	return frappe.get_all(
		"API Documentation",
		filters={"api_path": api_path, "http_method": method, "is_active": 1},
		fields=["name", "api_name", "description", "api_version"],
	)


@frappe.whitelist()
def get_active_apis():
	"""Retorna todas las APIs activas para el portal"""
	return frappe.get_all(
		"API Documentation",
		filters={"is_active": 1, "is_deprecated": 0},
		fields=["name", "api_name", "api_path", "http_method", "api_version", "module", "description"],
		order_by="module, api_name",
	)


# TODO: PHASE2: AUTO-REGISTRO - Implementar decorador @api_documentation
def api_documentation(name, description="", version="v1", collection="general"):
	"""Decorador para auto-registro de APIs

	TODO: PHASE2: DECORADOR - Implementar auto-registro completo
	Uso:
	@api_documentation(name="Get Physical Spaces",
					   description="Returns list of spaces",
					   version="v1")
	@frappe.whitelist()
	def get_physical_spaces():
		pass
	"""

	def decorator(func):
		# TODO: PHASE2: AUTO-REGISTRO - Registrar automáticamente en API Documentation
		return func

	return decorator
