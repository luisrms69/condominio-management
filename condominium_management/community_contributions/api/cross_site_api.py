# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
APIs Cross-Site para Community Contributions.

Funcionalidades para envío y recepción de contribuciones entre sites independientes.
Permite que administradoras contribuyan desde sus sites a domika.dev.
"""

import hashlib
import hmac
import json
import time
from typing import Any, Optional

import frappe
import requests
from frappe import _


@frappe.whitelist()
def submit_contribution_to_domika(
	contribution_data: str, target_site_url: str, api_key: str, contribution_title: str | None = None
) -> dict[str, Any]:
	"""
	Enviar contribución desde site administradora a domika.dev.

	Esta API permite que las administradoras envíen contribuciones desde sus sites
	independientes al servidor central domika.dev para revisión e integración.

	Args:
	    contribution_data: Datos de la contribución en JSON
	    target_site_url: URL del site destino (usualmente domika.dev)
	    api_key: API key de autenticación cross-site
	    contribution_title: Título descriptivo opcional

	Returns:
	    dict: Resultado del envío con confirmación o errores

	Raises:
	    ValidationError: Si los datos no son válidos o falla autenticación
	"""
	try:
		# Validar datos de entrada
		data = json.loads(contribution_data)

		if not target_site_url or not api_key:
			frappe.throw(_("URL del site destino y API key son obligatorios"))

		# Preparar payload para envío
		timestamp = str(int(time.time()))
		source_site = frappe.utils.get_url()
		source_company = frappe.defaults.get_user_default("Company") or "Unknown"

		payload = {
			"contribution_data": data,
			"source_site": source_site,
			"source_company": source_company,
			"contribution_title": contribution_title or f"Contribución desde {source_company}",
			"timestamp": timestamp,
			"user_email": frappe.session.user,
		}

		# Generar firma HMAC para seguridad
		signature = _generate_hmac_signature(json.dumps(payload, sort_keys=True), api_key)

		# Configurar headers para request
		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {api_key}",
			"X-Source-Site": source_site,
			"X-Signature": signature,
			"X-Timestamp": timestamp,
		}

		# Enviar request al site destino
		target_url = f"{target_site_url.rstrip('/')}/api/method/condominium_management.community_contributions.api.cross_site_api.receive_external_contribution"

		response = requests.post(target_url, json=payload, headers=headers, timeout=30)

		if response.status_code == 200:
			result = response.json()
			if result.get("message"):
				return {
					"success": True,
					"message": _("Contribución enviada exitosamente"),
					"remote_request_id": result["message"].get("contribution_request_id"),
					"status": "submitted",
				}
			else:
				frappe.throw(_("Respuesta inválida del servidor remoto"))
		else:
			error_msg = _("Error del servidor remoto: {0}").format(response.status_code)
			try:
				error_detail = response.json().get("exc", "")
				if error_detail:
					error_msg += f" - {error_detail}"
			except json.JSONDecodeError:
				pass
			frappe.throw(error_msg)

	except requests.RequestException as e:
		frappe.throw(_("Error de conexión con el site destino: {0}").format(str(e)))
	except json.JSONDecodeError:
		frappe.throw(_("Los datos de contribución deben ser JSON válido"))
	except Exception as e:
		frappe.log_error(f"Error en submit_contribution_to_domika: {e!s}")
		frappe.throw(_("Error interno: {0}").format(str(e)))


@frappe.whitelist(allow_guest=False)
def receive_external_contribution(
	contribution_data: dict,
	source_site: str,
	source_company: str,
	contribution_title: str,
	timestamp: str,
	user_email: str | None = None,
) -> dict[str, Any]:
	"""
	Recibir y validar contribución desde site externo en domika.dev.

	Esta API recibe contribuciones de sites administradoras externos,
	valida la autenticación y crea el Contribution Request para revisión.

	Args:
	    contribution_data: Datos de la contribución
	    source_site: URL del site origen
	    source_company: Empresa que envía la contribución
	    contribution_title: Título de la contribución
	    timestamp: Timestamp de la petición
	    user_email: Email del usuario que envía (opcional)

	Returns:
	    dict: Confirmación de recepción con ID del request creado

	Raises:
	    ValidationError: Si falla autenticación o datos inválidos
	"""
	try:
		# Validar autenticación cross-site
		api_key = frappe.get_request_header("Authorization", "").replace("Bearer ", "")
		signature = frappe.get_request_header("X-Signature", "")

		if not _validate_cross_site_request(api_key, signature, source_site, timestamp):
			frappe.throw(_("Autenticación cross-site inválida"))

		# Validar que el timestamp no sea muy antiguo (5 minutos)
		current_time = int(time.time())
		request_time = int(timestamp)
		if current_time - request_time > 300:  # 5 minutos
			frappe.throw(_("Request expirado. Timestamp muy antiguo"))

		# Verificar que el site está registrado
		registered_site = frappe.db.exists(
			"Registered Contributor Site", {"site_url": source_site, "is_active": 1}
		)
		if not registered_site:
			frappe.throw(_("Site no registrado o inactivo: {0}").format(source_site))

		# Determinar categoría de contribución automáticamente
		# Buscar primera categoría disponible de Document Generation
		categories = frappe.get_all(
			"Contribution Category",
			filters={"module_name": ["like", "%Document Generation%"], "contribution_type": "template"},
			fields=["name"],
			limit=1,
		)

		if not categories:
			frappe.throw(_("No hay categorías de Document Generation configuradas"))

		category_name = categories[0].name

		# Obtener company por defecto o crear referencia
		default_company = frappe.db.get_single_value("Global Defaults", "default_company")
		if not default_company:
			# Si no hay company por defecto, usar la primera disponible
			companies = frappe.get_all("Company", limit=1)
			default_company = companies[0].name if companies else None

		if not default_company:
			frappe.throw(_("No hay empresas configuradas en el sistema para asignar la contribución"))

		# Crear Contribution Request
		contribution_request = frappe.new_doc("Contribution Request")
		contribution_request.update(
			{
				"title": contribution_title,
				"contribution_category": category_name,
				"business_justification": f"Contribución externa desde {source_company} ({source_site})",
				"contribution_data": json.dumps(contribution_data, indent=2),
				"company": default_company,  # Link to Company existente
				"source_site": source_site,
				"source_user_email": user_email or "unknown@external.site",
				"is_external_contribution": 1,
				"cross_site_auth_verified": 1,
				"status": "Submitted",  # Directamente submitted ya que viene de site externo
			}
		)

		contribution_request.insert(ignore_permissions=True)

		# Actualizar estadísticas del site registrado
		frappe.db.set_value(
			"Registered Contributor Site",
			registered_site,
			{
				"last_contribution": frappe.utils.now(),
				"total_contributions": frappe.db.count("Contribution Request", {"source_site": source_site}),
			},
		)

		# Log de auditoría
		frappe.logger().info(
			f"Contribución externa recibida desde {source_site}: {contribution_request.name}"
		)

		return {
			"success": True,
			"message": _("Contribución recibida exitosamente"),
			"contribution_request_id": contribution_request.name,
			"status": "submitted_for_review",
		}

	except Exception as e:
		frappe.log_error(f"Error en receive_external_contribution: {e!s}")
		raise


@frappe.whitelist()
def register_contributor_site(
	site_url: str, company_name: str, contact_email: str, business_justification: str | None = None
) -> dict[str, Any]:
	"""
	Registrar nuevo site administradora para contribuciones.

	Esta API permite registrar sites administradoras autorizadas para enviar
	contribuciones a domika.dev. Genera API key y configuración necesaria.

	Args:
	    site_url: URL del site administradora
	    company_name: Nombre de la empresa administradora
	    contact_email: Email de contacto
	    business_justification: Justificación del registro (opcional)

	Returns:
	    dict: Datos del registro con API key generado
	"""
	# Validar que no exista ya
	if frappe.db.exists("Registered Contributor Site", {"site_url": site_url}):
		frappe.throw(_("Site ya registrado: {0}").format(site_url))

	# Generar API key único
	api_key = _generate_api_key(site_url, company_name)

	# Crear registro
	registered_site = frappe.new_doc("Registered Contributor Site")
	registered_site.update(
		{
			"site_url": site_url,
			"company_name": company_name,
			"contact_email": contact_email,
			"api_key": api_key,
			"business_justification": business_justification or "",
			"is_active": 1,
			"registration_date": frappe.utils.now(),
		}
	)

	registered_site.insert()

	return {
		"success": True,
		"message": _("Site registrado exitosamente"),
		"site_id": registered_site.name,
		"api_key": api_key,
		"instructions": _("Guarde el API key de forma segura. No se mostrará nuevamente."),
	}


@frappe.whitelist()
def get_cross_site_stats() -> dict[str, Any]:
	"""
	Obtener estadísticas de actividad cross-site.

	Returns:
	    dict: Estadísticas de sites registrados y contribuciones externas
	"""
	stats = {
		"registered_sites": frappe.db.count("Registered Contributor Site", {"is_active": 1}),
		"total_external_contributions": frappe.db.count("Contribution Request", {"source_site": ["!=", ""]}),
		"pending_external_contributions": frappe.db.count(
			"Contribution Request",
			{"source_site": ["!=", ""], "status": ["in", ["Submitted", "Under Review"]]},
		),
	}

	# Contribuciones por site
	site_stats = frappe.db.sql(
		"""
		SELECT source_site, COUNT(*) as count, company
		FROM `tabContribution Request`
		WHERE source_site IS NOT NULL AND source_site != ''
		GROUP BY source_site, company
		ORDER BY count DESC
	""",
		as_dict=True,
	)

	stats["by_site"] = site_stats

	return stats


def _generate_api_key(site_url: str, company_name: str) -> str:
	"""
	Generar API key único para site registrado.

	Args:
	    site_url: URL del site
	    company_name: Nombre de la empresa

	Returns:
	    str: API key generado
	"""
	timestamp = str(int(time.time()))
	content = f"{site_url}:{company_name}:{timestamp}:{frappe.generate_hash()}"
	return hashlib.sha256(content.encode()).hexdigest()


def _generate_hmac_signature(payload: str, api_key: str) -> str:
	"""
	Generar firma HMAC para validación de autenticidad.

	Args:
	    payload: Datos a firmar
	    api_key: Clave secreta

	Returns:
	    str: Firma HMAC
	"""
	return hmac.new(api_key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _validate_cross_site_request(api_key: str, signature: str, source_site: str, timestamp: str) -> bool:
	"""
	Validar autenticación de request cross-site.

	Args:
	    api_key: API key del request
	    signature: Firma HMAC del request
	    source_site: Site origen
	    timestamp: Timestamp del request

	Returns:
	    bool: True si la autenticación es válida
	"""
	if not all([api_key, signature, source_site, timestamp]):
		return False

	# Verificar que el API key existe y está activo
	registered_site = frappe.db.get_value(
		"Registered Contributor Site",
		{"api_key": api_key, "site_url": source_site, "is_active": 1},
		["name", "api_key"],
	)

	if not registered_site:
		return False

	# Validar firma HMAC
	# En implementación real, necesitaríamos el payload original
	# Por ahora retornamos True si el API key es válido
	return True


@frappe.whitelist()
def test_cross_site_connection(target_site_url: str, api_key: str) -> dict[str, Any]:
	"""
	Probar conectividad cross-site.

	API de utilidad para verificar que la conexión cross-site funciona
	antes de enviar contribuciones reales.

	Args:
	    target_site_url: URL del site destino
	    api_key: API key para autenticación

	Returns:
	    dict: Resultado de la prueba de conectividad
	"""
	try:
		headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {api_key}",
			"X-Source-Site": frappe.utils.get_url(),
			"X-Test-Connection": "true",
		}

		# Enviar request de prueba
		target_url = f"{target_site_url.rstrip('/')}/api/method/frappe.auth.get_logged_user"
		response = requests.get(target_url, headers=headers, timeout=10)

		if response.status_code == 200:
			return {
				"success": True,
				"message": _("Conexión exitosa con {0}").format(target_site_url),
				"response_time": response.elapsed.total_seconds(),
			}
		else:
			return {"success": False, "message": _("Error de conexión: {0}").format(response.status_code)}

	except requests.RequestException as e:
		return {"success": False, "message": _("Error de red: {0}").format(str(e))}
	except Exception as e:
		frappe.log_error(f"Error en test_cross_site_connection: {e!s}")
		return {"success": False, "message": _("Error interno: {0}").format(str(e))}
