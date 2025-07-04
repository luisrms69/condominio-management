# companies/hooks_handlers/account_detection.py
# Auto-generado desde TEMPLATE_MODULE_HOOKS.py

import frappe

from condominium_management.document_generation.api.entity_detection import auto_detect_configuration_needed


def after_insert(doc, method):
	"""
	Hook ejecutado después de insertar Company Account.
	Detectar nuevas cuentas que requieren templates.

	Args:
	    doc: Documento Company Account insertado
	    method: Método que activó el hook
	"""
	try:
		# Verificar si la cuenta pertenece a una empresa administradora
		if doc.get("company"):
			company = frappe.get_doc("Company", doc.company)

			if (
				company.get("company_type") == "Administradora"
				or "administradora" in company.company_name.lower()
			):
				# Buscar configuración de entidad para Company Account
				entity_config = frappe.db.get_value(
					"Entity Type Configuration", {"entity_doctype": "Company Account"}, "name"
				)

				if entity_config:
					entity_config_doc = frappe.get_doc("Entity Type Configuration", entity_config)
					result = auto_detect_configuration_needed(doc, entity_config_doc)

					if result.get("needs_configuration"):
						frappe.msgprint(
							f"📊 La cuenta {doc.get('account_name', doc.name)} requiere configuración de templates",
							title="Template de Cuenta Detectado",
						)

						# Log para auditoría
						frappe.log_error(
							f"Auto-detección ejecutada para Company Account {doc.name}: {result}",
							"Companies Hook - Account Detection",
						)

	except Exception as e:
		frappe.log_error(f"Error en hook after_insert para Company Account {doc.name}: {e!s}")
