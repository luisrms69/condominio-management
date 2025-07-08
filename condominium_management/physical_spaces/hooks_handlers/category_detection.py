# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


def on_update(doc, method):
	"""Hook al actualizar Space Category"""
	try:
		# Actualizar espacios existentes que usen esta categoría
		if category_configuration_changed(doc):
			update_existing_spaces(doc)

		# Actualizar template system si cambió el template
		if doc.has_value_changed("ps_template_code") or doc.has_value_changed("template_version"):
			update_template_system(doc)

		# Log de auditoría
		create_audit_log(doc)

	except Exception as e:
		frappe.log_error(f"Error en on_update de Space Category: {e!s}")


def category_configuration_changed(doc):
	"""Detectar si cambió la configuración que afecta espacios existentes"""
	critical_fields = [
		"ps_template_code",
		"template_version",
		"auto_load_template",
		"requires_components",
		"requires_dimensions",
		"requires_capacity",
	]

	return any(doc.has_value_changed(field) for field in critical_fields)


def update_existing_spaces(doc):
	"""Actualizar espacios existentes que usen esta categoría"""
	spaces = frappe.get_all(
		"Physical Space", filters={"space_category": doc.name}, fields=["name", "space_name"]
	)

	if not spaces:
		return

	frappe.msgprint(f"Actualizando {len(spaces)} espacios que usan la categoría '{doc.category_name}'")

	for space in spaces:
		try:
			space_doc = frappe.get_doc("Physical Space", space.name)

			# Actualizar campos del template si es necesario
			if doc.ps_template_code and doc.auto_load_template:
				update_space_template_fields(space_doc, doc)

			# Validar nuevos requisitos
			validate_space_against_new_requirements(space_doc, doc)

			# Guardar sin ejecutar hooks completos para evitar recursión
			space_doc.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(f"Error actualizando espacio {space.name}: {e!s}")
			frappe.msgprint(f"Error actualizando espacio '{space.space_name}': {e!s}")


def update_space_template_fields(space_doc, category_doc):
	"""Actualizar campos del template en el espacio"""
	try:
		# TODO: Implementar cuando esté disponible el template system
		# space_doc.template_fields = get_template_fields(category_doc.ps_template_code)

		# Por ahora, solo inicializar el campo si no existe
		if not space_doc.template_fields:
			space_doc.template_fields = {}

	except Exception as e:
		frappe.log_error(f"Error actualizando template fields: {e!s}")


def validate_space_against_new_requirements(space_doc, category_doc):
	"""Validar espacio contra nuevos requisitos de la categoría"""
	errors = []

	# Validar nuevos requisitos
	if category_doc.requires_dimensions and not space_doc.area_m2:
		errors.append(f"El espacio '{space_doc.space_name}' ahora requiere especificar área en m²")

	if category_doc.requires_capacity and not space_doc.max_capacity:
		errors.append(f"El espacio '{space_doc.space_name}' ahora requiere especificar capacidad máxima")

	if category_doc.requires_components and not space_doc.space_components:
		errors.append(f"El espacio '{space_doc.space_name}' ahora requiere especificar componentes")

	# Reportar errores como advertencias (no bloquear la actualización)
	if errors:
		frappe.msgprint(
			f"Advertencias para el espacio '{space_doc.space_name}':<br>" + "<br>".join(errors),
			title="Requisitos de Categoría Actualizados",
		)


def update_template_system(doc):
	"""Actualizar sistema de templates"""
	try:
		# TODO: Integrar con template system cuando esté disponible
		# Esto notificará al sistema de templates sobre cambios en la configuración

		# Log del cambio
		frappe.logger().info(
			f"Template configuration updated for category {doc.name}: "
			f"template_code={doc.ps_template_code}, version={doc.template_version}"
		)

	except Exception as e:
		frappe.log_error(f"Error actualizando template system: {e!s}")


def create_audit_log(doc):
	"""Crear log de auditoría para la categoría"""
	try:
		changes = []

		# Detectar cambios específicos
		if doc.has_value_changed("ps_template_code"):
			old_val = doc.get_db_value("ps_template_code") or "None"
			changes.append(f"Template: {old_val} → {doc.ps_template_code or 'None'}")

		if doc.has_value_changed("requires_components"):
			changes.append(
				f"Requires Components: {doc.get_db_value('requires_components')} → {doc.requires_components}"
			)

		if doc.has_value_changed("requires_dimensions"):
			changes.append(
				f"Requires Dimensions: {doc.get_db_value('requires_dimensions')} → {doc.requires_dimensions}"
			)

		if doc.has_value_changed("requires_capacity"):
			changes.append(
				f"Requires Capacity: {doc.get_db_value('requires_capacity')} → {doc.requires_capacity}"
			)

		if changes:
			frappe.logger().info(
				f"Space Category updated: {doc.name} - Changes: {', '.join(changes)} "
				f"by {frappe.session.user} at {now_datetime()}"
			)

	except Exception as e:
		# No fallar por errores de auditoría
		frappe.log_error(f"Error en audit log de category: {e!s}")


def notify_dependent_modules(doc):
	"""Notificar a módulos dependientes sobre cambios"""
	try:
		# TODO: Notificar a módulos que dependen de Physical Spaces
		# Por ejemplo: Maintenance, Access Control, etc.

		# Ejemplo de notificación
		if doc.has_value_changed("ps_template_code"):
			# Notificar al módulo de mantenimiento si existe
			pass

		if doc.has_value_changed("requires_components"):
			# Notificar al módulo de componentes si existe
			pass

	except Exception as e:
		frappe.log_error(f"Error notificando módulos dependientes: {e!s}")


def validate_hierarchy_impact(doc):
	"""Validar impacto en jerarquías existentes"""
	if doc.has_value_changed("allowed_parent_categories") or doc.has_value_changed(
		"allowed_child_categories"
	):
		# Verificar que los espacios existentes no violan las nuevas reglas
		spaces = frappe.get_all(
			"Physical Space",
			filters={"space_category": doc.name},
			fields=["name", "space_name", "parent_space"],
		)

		invalid_spaces = []

		for space in spaces:
			if space.parent_space:
				parent_doc = frappe.get_doc("Physical Space", space.parent_space)
				if parent_doc.space_category:
					# Validar que la nueva configuración no rompe la jerarquía
					if doc.allowed_parent_categories:
						allowed_parents = [row.parent_category for row in doc.allowed_parent_categories]
						if parent_doc.space_category not in allowed_parents:
							invalid_spaces.append(space.space_name)

		if invalid_spaces:
			frappe.msgprint(
				f"Advertencia: Los siguientes espacios tienen jerarquías que no cumplen "
				f"con las nuevas reglas: {', '.join(invalid_spaces)}",
				title="Impacto en Jerarquías",
			)
