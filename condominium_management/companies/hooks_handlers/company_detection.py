# companies/hooks_handlers/company_detection.py
# Auto-generado desde TEMPLATE_MODULE_HOOKS.py

import frappe

from condominium_management.document_generation.api.entity_detection import auto_detect_configuration_needed


def after_insert(doc, method):
	"""
	Hook ejecutado después de insertar Company.
	Detectar nuevas empresas administradoras que necesitan configuración.

	Args:
	    doc: Documento Company insertado
	    method: Método que activó el hook
	"""
	try:
		# Verificar si es una empresa administradora
		if doc.get("company_type") == "Administradora" or "administradora" in doc.company_name.lower():
			# Buscar configuración de entidad para Company
			entity_config = frappe.db.get_value(
				"Entity Type Configuration", {"entity_doctype": "Company"}, "name"
			)

			if entity_config:
				entity_config_doc = frappe.get_doc("Entity Type Configuration", entity_config)
				result = auto_detect_configuration_needed(doc, entity_config_doc)

				if result.get("needs_configuration"):
					frappe.msgprint(
						f"✅ Se detectó que la empresa {doc.company_name} requiere configuración de templates automática",
						title="Configuración Automática Detectada",
					)

					# Log para auditoría
					frappe.log_error(
						f"Auto-detección ejecutada para Company {doc.name}: {result}",
						"Companies Hook - Auto Detection",
					)

	except Exception as e:
		frappe.log_error(f"Error en hook after_insert para Company {doc.name}: {e!s}")


def on_update(doc, method):
	"""
	Hook ejecutado al actualizar Company.
	Verificar cambios que requieren reconfiguración.

	Args:
	    doc: Documento Company actualizado
	    method: Método que activó el hook
	"""
	try:
		# Verificar si cambió el tipo de empresa
		if doc.has_value_changed("company_type") or doc.has_value_changed("company_name"):
			# Re-evaluar configuración si cambió a/desde administradora
			if doc.get("company_type") == "Administradora" or "administradora" in doc.company_name.lower():
				entity_config = frappe.db.get_value(
					"Entity Type Configuration", {"entity_doctype": "Company"}, "name"
				)

				if entity_config:
					entity_config_doc = frappe.get_doc("Entity Type Configuration", entity_config)
					result = auto_detect_configuration_needed(doc, entity_config_doc)

					if result.get("needs_configuration"):
						frappe.msgprint(
							f"⚠️ Los cambios en {doc.company_name} requieren actualización de configuración",
							title="Reconfiguración Necesaria",
						)

	except Exception as e:
		frappe.log_error(f"Error en hook on_update para Company {doc.name}: {e!s}")
