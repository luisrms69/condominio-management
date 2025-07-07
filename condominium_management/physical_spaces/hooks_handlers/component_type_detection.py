# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


def on_update(doc, method):
	"""Hook al actualizar Component Type"""
	try:
		# Actualizar componentes existentes que usen este tipo
		if type_configuration_changed(doc):
			update_existing_components(doc)

		# Actualizar template system si cambió el template
		if doc.has_value_changed("component_template_code") or doc.has_value_changed("template_version"):
			update_template_system(doc)

		# Actualizar validaciones si cambiaron los requisitos
		if validation_requirements_changed(doc):
			notify_validation_changes(doc)

		# Log de auditoría
		create_audit_log(doc)

	except Exception as e:
		frappe.log_error(f"Error en on_update de Component Type: {e!s}")


def type_configuration_changed(doc):
	"""Detectar si cambió la configuración que afecta componentes existentes"""
	critical_fields = [
		"component_template_code",
		"template_version",
		"auto_load_template",
		"requires_brand",
		"requires_model",
		"requires_installation_date",
		"requires_warranty",
		"requires_specifications",
		"code_prefix",
	]

	return any(doc.has_value_changed(field) for field in critical_fields)


def validation_requirements_changed(doc):
	"""Detectar si cambiaron los requisitos de validación"""
	validation_fields = [
		"requires_brand",
		"requires_model",
		"requires_installation_date",
		"requires_warranty",
		"requires_specifications",
	]

	return any(doc.has_value_changed(field) for field in validation_fields)


def update_existing_components(doc):
	"""Actualizar componentes existentes que usen este tipo"""
	components = frappe.get_all(
		"Space Component",
		filters={"component_type": doc.name},
		fields=["name", "component_name", "inventory_code"],
	)

	if not components:
		return

	frappe.msgprint(f"Actualizando {len(components)} componentes del tipo '{doc.component_type_name}'")

	for component in components:
		try:
			component_doc = frappe.get_doc("Space Component", component.name)

			# Actualizar código de inventario si cambió el prefijo
			if doc.has_value_changed("code_prefix"):
				update_component_inventory_code(component_doc, doc)

			# Actualizar campos del template si es necesario
			if doc.component_template_code and doc.auto_load_template:
				update_component_template_fields(component_doc, doc)

			# Validar nuevos requisitos (sin bloquear)
			validate_component_against_new_requirements(component_doc, doc)

			# Guardar sin ejecutar hooks completos para evitar recursión
			component_doc.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"Error actualizando componente {component.name}: {e!s}")
			frappe.msgprint(f"Error actualizando componente '{component.component_name}': {e!s}")


def update_component_inventory_code(component_doc, type_doc):
	"""Actualizar código de inventario del componente"""
	if component_doc.inventory_code and type_doc.has_value_changed("code_prefix"):
		old_prefix = type_doc.get_db_value("code_prefix")
		new_prefix = type_doc.code_prefix

		# Solo actualizar si el código actual usa el prefijo viejo
		if component_doc.inventory_code.startswith(old_prefix):
			new_code = component_doc.inventory_code.replace(old_prefix, new_prefix, 1)

			# Verificar que el nuevo código no existe
			if not frappe.db.exists("Space Component", {"inventory_code": new_code}):
				component_doc.inventory_code = new_code
				frappe.msgprint(
					f"Código actualizado: {old_prefix} → {new_prefix} para {component_doc.component_name}"
				)
			else:
				frappe.msgprint(
					f"No se pudo actualizar código para {component_doc.component_name} - código {new_code} ya existe"
				)


def update_component_template_fields(component_doc, type_doc):
	"""Actualizar campos del template en el componente"""
	try:
		# TODO: Implementar cuando esté disponible el template system
		frappe.logger().info(f"Updating template fields for component {component_doc.name}")

	except Exception as e:
		frappe.log_error(f"Error actualizando template fields: {e!s}")


def validate_component_against_new_requirements(component_doc, type_doc):
	"""Validar componente contra nuevos requisitos del tipo"""
	errors = []

	# Validar nuevos requisitos
	if type_doc.requires_brand and not component_doc.brand:
		if type_doc.has_value_changed("requires_brand") and type_doc.requires_brand:
			errors.append("Ahora requiere especificar marca")

	if type_doc.requires_model and not component_doc.model:
		if type_doc.has_value_changed("requires_model") and type_doc.requires_model:
			errors.append("Ahora requiere especificar modelo")

	if type_doc.requires_installation_date and not component_doc.installation_date:
		if type_doc.has_value_changed("requires_installation_date") and type_doc.requires_installation_date:
			errors.append("Ahora requiere especificar fecha de instalación")

	if type_doc.requires_warranty and not component_doc.warranty_expiry_date:
		if type_doc.has_value_changed("requires_warranty") and type_doc.requires_warranty:
			errors.append("Ahora requiere especificar información de garantía")

	if type_doc.requires_specifications and not component_doc.technical_specifications:
		if type_doc.has_value_changed("requires_specifications") and type_doc.requires_specifications:
			errors.append("Ahora requiere especificar especificaciones técnicas")

	# Reportar errores como advertencias (no bloquear la actualización)
	if errors:
		frappe.msgprint(
			f"Advertencias para el componente '{component_doc.component_name}':<br>" + "<br>".join(errors),
			title="Requisitos de Tipo Actualizados",
		)


def update_template_system(doc):
	"""Actualizar sistema de templates"""
	try:
		# TODO: Integrar con template system cuando esté disponible
		frappe.logger().info(
			f"Template configuration updated for component type {doc.name}: "
			f"template_code={doc.component_template_code}, version={doc.template_version}"
		)

	except Exception as e:
		frappe.log_error(f"Error actualizando template system: {e!s}")


def notify_validation_changes(doc):
	"""Notificar cambios en requisitos de validación"""
	try:
		changed_requirements = []

		if doc.has_value_changed("requires_brand"):
			status = "requerida" if doc.requires_brand else "opcional"
			changed_requirements.append(f"Marca: {status}")

		if doc.has_value_changed("requires_model"):
			status = "requerido" if doc.requires_model else "opcional"
			changed_requirements.append(f"Modelo: {status}")

		if doc.has_value_changed("requires_installation_date"):
			status = "requerida" if doc.requires_installation_date else "opcional"
			changed_requirements.append(f"Fecha de instalación: {status}")

		if doc.has_value_changed("requires_warranty"):
			status = "requerida" if doc.requires_warranty else "opcional"
			changed_requirements.append(f"Garantía: {status}")

		if doc.has_value_changed("requires_specifications"):
			status = "requeridas" if doc.requires_specifications else "opcionales"
			changed_requirements.append(f"Especificaciones técnicas: {status}")

		if changed_requirements:
			frappe.msgprint(
				f"Requisitos actualizados para tipo '{doc.component_type_name}':<br>"
				+ "<br>".join(changed_requirements),
				title="Cambios en Validaciones",
			)

	except Exception as e:
		frappe.log_error(f"Error notificando cambios de validación: {e!s}")


def create_audit_log(doc):
	"""Crear log de auditoría para el tipo de componente"""
	try:
		changes = []

		# Detectar cambios específicos
		if doc.has_value_changed("code_prefix"):
			old_val = doc.get_db_value("code_prefix")
			changes.append(f"Prefix: {old_val} → {doc.code_prefix}")

		if doc.has_value_changed("component_template_code"):
			old_val = doc.get_db_value("component_template_code") or "None"
			changes.append(f"Template: {old_val} → {doc.component_template_code or 'None'}")

		if doc.has_value_changed("critical_component"):
			changes.append(f"Critical: {doc.get_db_value('critical_component')} → {doc.critical_component}")

		# Log requisitos de validación
		validation_fields = [
			("requires_brand", "Brand Required"),
			("requires_model", "Model Required"),
			("requires_installation_date", "Install Date Required"),
			("requires_warranty", "Warranty Required"),
			("requires_specifications", "Specs Required"),
		]

		for field, label in validation_fields:
			if doc.has_value_changed(field):
				old_val = doc.get_db_value(field)
				changes.append(f"{label}: {old_val} → {getattr(doc, field)}")

		if changes:
			frappe.logger().info(
				f"Component Type updated: {doc.name} - Changes: {', '.join(changes)} "
				f"by {frappe.session.user} at {now_datetime()}"
			)

	except Exception as e:
		# No fallar por errores de auditoría
		frappe.log_error(f"Error en audit log de component type: {e!s}")


def notify_dependent_modules(doc):
	"""Notificar a módulos dependientes sobre cambios"""
	try:
		# TODO: Notificar a módulos que dependen de Component Types
		# Por ejemplo: Maintenance, Inventory, etc.

		if doc.has_value_changed("critical_component"):
			# Notificar al módulo de mantenimiento si cambió criticidad
			notify_maintenance_module(doc)

		if doc.has_value_changed("requires_certification"):
			# Notificar al módulo de compliance si cambió requisito de certificación
			notify_compliance_module(doc)

	except Exception as e:
		frappe.log_error(f"Error notificando módulos dependientes: {e!s}")


def notify_maintenance_module(doc):
	"""Notificar al módulo de mantenimiento"""
	frappe.logger().info(f"Critical component status changed for type: {doc.component_type_name}")
	# TODO: Integrar con módulo de mantenimiento


def notify_compliance_module(doc):
	"""Notificar al módulo de compliance"""
	frappe.logger().info(f"Certification requirement changed for type: {doc.component_type_name}")
	# TODO: Integrar con módulo de compliance


def update_maintenance_schedules(doc):
	"""Actualizar programaciones de mantenimiento si cambió la configuración"""
	if doc.has_value_changed("default_maintenance_frequency") or doc.has_value_changed("maintenance_type"):
		# TODO: Actualizar programaciones existentes cuando esté disponible el módulo
		frappe.logger().info(f"Maintenance configuration updated for type: {doc.component_type_name}")

		# Obtener componentes que usen este tipo
		components = frappe.get_all(
			"Space Component", filters={"component_type": doc.name}, fields=["name", "component_name"]
		)

		if components:
			frappe.msgprint(
				f"La configuración de mantenimiento cambió. "
				f"Esto puede afectar {len(components)} componentes existentes.",
				title="Configuración de Mantenimiento Actualizada",
			)
