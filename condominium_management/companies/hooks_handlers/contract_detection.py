# companies/hooks_handlers/contract_detection.py
# Auto-generado desde TEMPLATE_MODULE_HOOKS.py

import frappe

from condominium_management.document_generation.api.entity_detection import auto_detect_configuration_needed


def validate(doc, method):
	"""
	Hook ejecutado al validar Service Management Contract.
	Validar contratos y detectar configuraciones automáticas.

	Args:
	    doc: Documento Service Management Contract a validar
	    method: Método que activó el hook
	"""
	try:
		# Validar que la empresa administradora existe
		if doc.get("managing_company"):
			company = frappe.get_doc("Company", doc.managing_company)
			if not company:
				frappe.throw(f"Empresa administradora {doc.managing_company} no encontrada")

		# Validar que el contrato tenga configuración adecuada
		if doc.get("contract_status") == "Activo":
			entity_config = frappe.db.get_value(
				"Entity Type Configuration", {"entity_doctype": "Service Management Contract"}, "name"
			)

			if entity_config:
				entity_config_doc = frappe.get_doc("Entity Type Configuration", entity_config)
				result = auto_detect_configuration_needed(doc, entity_config_doc)

				if result.get("needs_configuration"):
					frappe.msgprint(
						f"💡 El contrato {doc.contract_name} puede beneficiarse de configuración automática",
						title="Configuración Recomendada",
					)

	except Exception as e:
		frappe.throw(f"Error en validación de contrato {doc.name}: {e!s}")


def on_update(doc, method):
	"""
	Hook ejecutado al actualizar Service Management Contract.
	Detectar cambios que requieren reconfiguración.

	Args:
	    doc: Documento Service Management Contract actualizado
	    method: Método que activó el hook
	"""
	try:
		# Verificar si cambió el estado del contrato
		if doc.has_value_changed("contract_status"):
			if doc.contract_status == "Activo":
				# Contrato activado - verificar configuración
				entity_config = frappe.db.get_value(
					"Entity Type Configuration", {"entity_doctype": "Service Management Contract"}, "name"
				)

				if entity_config:
					entity_config_doc = frappe.get_doc("Entity Type Configuration", entity_config)
					result = auto_detect_configuration_needed(doc, entity_config_doc)

					if result.get("needs_configuration"):
						frappe.msgprint(
							f"✅ Contrato {doc.contract_name} activado - configuración automática aplicada",
							title="Configuración Automática",
						)

			elif doc.contract_status in ["Terminado", "Suspendido"]:
				# Contrato desactivado - log para auditoría
				frappe.log_error(
					f"Contrato {doc.contract_name} cambió a estado {doc.contract_status}",
					"Companies Hook - Contract Status Change",
				)

	except Exception as e:
		frappe.log_error(f"Error en hook on_update para Service Management Contract {doc.name}: {e!s}")
