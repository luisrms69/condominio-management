# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import hashlib
import json
import time
from typing import Any

import frappe
from frappe.model.document import Document


class RegisteredContributorSite(Document):
	"""
	Gestión de sites administradoras registradas para contribuciones cross-site.

	Funcionalidades principales:
	- Registro y autenticación de sites administradoras
	- Generación y gestión de API keys
	- Seguimiento de estadísticas de contribuciones
	- Logs de seguridad y auditóría
	- Control de acceso y permisos

	Campos principales:
		site_url (Data): URL única del site administradora
		company_name (Data): Nombre de la empresa administradora
		api_key (Password): Clave de autenticación para APIs cross-site
		is_active (Check): Estado activo/inactivo del site
		total_contributions (Int): Contador de contribuciones enviadas

	Errores comunes:
		ValidationError: URL duplicada o formato inválido
		PermissionError: Acceso no autorizado a API key

	Ejemplo de uso:
		site = frappe.new_doc("Registered Contributor Site")
		site.site_url = "admin1.micondominio.com"
		site.company_name = "Administradora ABC"
		site.save()
	"""

	def before_insert(self):
		"""
		Configuración inicial antes de insertar el documento.

		Genera API key automáticamente y establece fecha de registro.
		"""
		if not self.api_key:
			self.api_key = self._generate_api_key()
			self.api_key_generated_date = frappe.utils.now()

		if not self.registration_date:
			self.registration_date = frappe.utils.now()

		# Inicializar estadísticas
		self.total_contributions = 0
		self.failed_requests_count = 0

		# Inicializar logs de seguridad
		self.security_logs = json.dumps(
			[
				{
					"action": "site_registered",
					"timestamp": frappe.utils.now(),
					"user": frappe.session.user,
					"details": "Site registrado inicialmente",
				}
			]
		)

	def validate(self):
		"""
		Validaciones de negocio del documento.

		Verifica formato de URL, email y restricciones de seguridad.
		"""
		self._validate_site_url()
		self._validate_email_format()
		self._validate_business_justification()

		# Si se desactiva el site, registrar en logs (solo si no es nuevo)
		if not self.is_new() and self.has_value_changed("is_active") and not self.is_active:
			self._log_security_event("site_deactivated", "Site desactivado por administrador")

	def on_update(self):
		"""
		Acciones después de actualizar el documento.

		Registra cambios importantes en logs de seguridad.
		"""
		# Solo log si no es la primera vez (insert) y realmente cambió
		if not self.is_new() and self.has_value_changed("api_key"):
			self._log_security_event("api_key_regenerated", "API key regenerado")

		if self.has_value_changed("is_active"):
			status = "activado" if self.is_active else "desactivado"
			self._log_security_event("status_changed", f"Site {status}")

	def _validate_site_url(self):
		"""
		Validar formato y unicidad de URL del site.

		Raises:
		    ValidationError: Si la URL es inválida o duplicada
		"""
		if not self.site_url:
			frappe.throw(frappe._("URL del site es obligatoria"))

		# Normalizar URL (remover trailing slash)
		self.site_url = self.site_url.rstrip("/")

		# Validar formato básico de URL
		if not (self.site_url.startswith("http://") or self.site_url.startswith("https://")):
			self.site_url = f"https://{self.site_url}"

		# Verificar unicidad
		existing = frappe.db.exists(
			"Registered Contributor Site", {"site_url": self.site_url, "name": ["!=", self.name or ""]}
		)

		if existing:
			frappe.throw(frappe._("Ya existe un site registrado con esta URL: {0}").format(self.site_url))

	def _validate_email_format(self):
		"""
		Validar formato del email de contacto.

		Raises:
		    ValidationError: Si el email es inválido
		"""
		if self.contact_email and "@" not in self.contact_email:
			frappe.throw(frappe._("Formato de email inválido: {0}").format(self.contact_email))

	def _validate_business_justification(self):
		"""
		Validar justificación de negocio para sitios nuevos.

		Para nuevos registros, la justificación es obligatoria.
		"""
		if self.is_new() and not self.business_justification:
			frappe.throw(frappe._("Justificación de negocio es obligatoria para nuevos registros"))

	def _generate_api_key(self) -> str:
		"""
		Generar API key único y seguro.

		Returns:
		    str: API key generado usando hash SHA-256
		"""
		timestamp = str(int(time.time()))
		random_hash = frappe.generate_hash()
		content = f"{self.site_url}:{self.company_name}:{timestamp}:{random_hash}"

		return hashlib.sha256(content.encode()).hexdigest()

	def regenerate_api_key(self):
		"""
		Regenerar API key para el site.

		Útil cuando se compromete la seguridad del API key actual.
		Solo accesible por System Manager.
		"""
		if not frappe.has_permission(self.doctype, "write"):
			frappe.throw(frappe._("No tiene permisos para regenerar API key"))

		old_key_partial = self.api_key[:8] + "***" if self.api_key else "None"

		self.api_key = self._generate_api_key()
		self.api_key_generated_date = frappe.utils.now()
		self.failed_requests_count = 0  # Reset contador de fallos

		self._log_security_event(
			"api_key_regenerated", f"API key regenerado. Key anterior: {old_key_partial}"
		)

		self.save()

		frappe.msgprint(frappe._("API key regenerado exitosamente"))

	def increment_contribution_count(self):
		"""
		Incrementar contador de contribuciones.

		Llamado automáticamente cuando se recibe una contribución del site.
		"""
		self.total_contributions = (self.total_contributions or 0) + 1
		self.last_contribution = frappe.utils.now()

		# Actualizar estadísticas
		stats = self._get_contribution_stats()
		stats["last_updated"] = frappe.utils.now()
		self.contribution_stats = json.dumps(stats)

		self.save(ignore_permissions=True)

	def increment_failed_requests(self):
		"""
		Incrementar contador de requests fallidos.

		Útil para monitoreo de seguridad y detección de ataques.
		"""
		self.failed_requests_count = (self.failed_requests_count or 0) + 1
		self.last_api_usage = frappe.utils.now()

		self._log_security_event("failed_request", "Request fallido registrado")

		# Auto-desactivar si hay muchos fallos (más de 100)
		if self.failed_requests_count > 100:
			self.is_active = 0
			self._log_security_event(
				"auto_deactivated",
				f"Site auto-desactivado por {self.failed_requests_count} requests fallidos",
			)

		self.save(ignore_permissions=True)

	def record_successful_api_usage(self):
		"""
		Registrar uso exitoso de API.

		Actualiza timestamp de último uso y resetea contadores si es necesario.
		"""
		self.last_api_usage = frappe.utils.now()

		# Reset contador de fallos en uso exitoso
		if self.failed_requests_count > 0:
			self.failed_requests_count = 0

		self.save(ignore_permissions=True)

	def _get_contribution_stats(self) -> dict[str, Any]:
		"""
		Obtener estadísticas detalladas de contribuciones del site.

		Returns:
		    dict: Estadísticas por estado, categoría y tiempo
		"""
		stats = {}

		# Contribuciones por estado
		statuses = ["Draft", "Submitted", "Under Review", "Approved", "Rejected", "Integrated"]
		for status in statuses:
			count = frappe.db.count("Contribution Request", {"source_site": self.site_url, "status": status})
			stats[f"status_{status.lower().replace(' ', '_')}"] = count

		# Contribuciones por mes (últimos 6 meses)
		monthly_stats = frappe.db.sql(
			"""
			SELECT DATE_FORMAT(creation, %s) as month, COUNT(*) as count
			FROM `tabContribution Request`
			WHERE source_site = %s AND creation >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
			GROUP BY DATE_FORMAT(creation, %s)
			ORDER BY month DESC
		""",
			("%Y-%m", self.site_url, "%Y-%m"),
			as_dict=True,
		)

		stats["monthly_contributions"] = {item["month"]: item["count"] for item in monthly_stats}

		return stats

	def _log_security_event(self, action: str, details: str):
		"""
		Registrar evento de seguridad en logs.

		Args:
		    action: Tipo de acción (ej: api_key_regenerated, site_deactivated)
		    details: Detalles adicionales del evento
		"""
		try:
			current_logs = json.loads(self.security_logs or "[]")
		except json.JSONDecodeError:
			current_logs = []

		new_event = {
			"action": action,
			"timestamp": frappe.utils.now(),
			"user": frappe.session.user,
			"details": details,
			"ip_address": getattr(frappe.local, "request_ip", None) or "unknown",
		}

		current_logs.insert(0, new_event)  # Más recientes primero

		# Mantener solo últimos 50 eventos
		if len(current_logs) > 50:
			current_logs = current_logs[:50]

		self.security_logs = json.dumps(current_logs)

	def get_masked_api_key(self) -> str:
		"""
		Obtener API key enmascarado para mostrar en UI.

		Returns:
		    str: API key con solo los primeros 8 caracteres visibles
		"""
		if not self.api_key:
			return "No generado"

		return f"{self.api_key[:8]}{'*' * (len(self.api_key) - 8)}"

	@frappe.whitelist()
	def get_connection_instructions(self) -> dict[str, Any]:
		"""
		Obtener instrucciones de conexión para el site administradora.

		Returns:
		    dict: Instrucciones de configuración e integración
		"""
		return {
			"site_url": self.site_url,
			"api_key": self.api_key,
			"target_site": "https://domika.dev",
			"api_endpoint": "/api/method/condominium_management.community_contributions.api.cross_site_api.receive_external_contribution",
			"test_endpoint": "/api/method/condominium_management.community_contributions.api.cross_site_api.test_cross_site_connection",
			"instructions": [
				"1. Configure el API key en su site administradora",
				"2. Use la API submit_contribution_to_domika para enviar contribuciones",
				"3. Las contribuciones aparecerán en domika.dev para revisión",
				"4. Recibirá notificaciones del estado de sus contribuciones",
			],
			"sample_code": f"""
// JavaScript - Ejemplo de envío de contribución
frappe.call({{
    method: "condominium_management.community_contributions.api.cross_site_api.submit_contribution_to_domika",
    args: {{
        contribution_data: JSON.stringify(your_contribution_data),
        target_site_url: "https://domika.dev",
        api_key: "{self.get_masked_api_key()}",
        contribution_title: "Mi Nueva Contribución"
    }},
    callback: function(r) {{
        if (r.message.success) {{
            frappe.msgprint("Contribución enviada exitosamente");
        }}
    }}
}});
			""",
		}
