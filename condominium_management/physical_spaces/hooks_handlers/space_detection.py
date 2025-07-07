# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


def after_insert(doc, method):
	"""Hook después de insertar Physical Space"""
	try:
		# Integrar con Document Generation si está disponible
		trigger_document_generation(doc)

		# Crear configuración inicial si es necesario
		create_initial_configuration(doc)

		# Log de auditoría
		create_audit_log(doc, "inserted")

	except Exception as e:
		frappe.log_error(f"Error en after_insert de Physical Space: {e!s}")


def on_update(doc, method):
	"""Hook al actualizar Physical Space"""
	try:
		# Actualizar jerarquía de espacios hijos
		update_children_hierarchy(doc)

		# Actualizar templates si cambió la categoría
		if doc.has_value_changed("space_category"):
			update_template_fields(doc)

		# Integrar con Document Generation si cambió información crítica
		if has_critical_changes(doc):
			trigger_document_generation(doc)

		# Log de auditoría
		create_audit_log(doc, "updated")

	except Exception as e:
		frappe.log_error(f"Error en on_update de Physical Space: {e!s}")


def trigger_document_generation(doc):
	"""Integrar con módulo Document Generation"""
	# TODO: Implementar cuando esté disponible la integración
	# Esta función se conectará con el sistema de Document Generation
	# para actualizar automáticamente estatutos y manuales
	pass


def create_initial_configuration(doc):
	"""Crear configuración inicial para el espacio"""
	# Cargar campos del template si tiene categoría
	if doc.space_category:
		# TODO: Implementar cuando esté disponible el template system
		pass

	# Crear entradas de auditoría iniciales
	if not doc.template_fields:
		doc.template_fields = {}


def update_children_hierarchy(doc):
	"""Actualizar jerarquía de espacios hijos"""
	if doc.has_value_changed("space_name") or doc.has_value_changed("space_path"):
		children = frappe.get_all("Physical Space", filters={"parent_space": doc.name}, fields=["name"])

		for child in children:
			try:
				child_doc = frappe.get_doc("Physical Space", child.name)
				child_doc.update_hierarchy_info()
				child_doc.save()
			except Exception as e:
				frappe.log_error(f"Error actualizando hijo {child.name}: {e!s}")


def update_template_fields(doc):
	"""Actualizar campos del template cuando cambia la categoría"""
	if doc.space_category:
		try:
			category = frappe.get_doc("Space Category", doc.space_category)
			if category.ps_template_code and category.auto_load_template:
				# TODO: Implementar cuando esté disponible el template system
				# doc.template_fields = get_template_fields(category.ps_template_code)
				pass
		except Exception as e:
			frappe.log_error(f"Error actualizando template fields: {e!s}")


def has_critical_changes(doc):
	"""Detectar si hubo cambios críticos que requieren actualizar documentos"""
	critical_fields = ["space_name", "space_category", "area_m2", "max_capacity", "parent_space"]

	return any(doc.has_value_changed(field) for field in critical_fields)


def create_audit_log(doc, action):
	"""Crear log de auditoría para el espacio"""
	try:
		# Log básico en sistema Frappe
		frappe.logger().info(
			f"Physical Space {action}: {doc.name} - {doc.space_name} "
			f"by {frappe.session.user} at {now_datetime()}"
		)

		# TODO: Integrar con sistema de auditoría más robusto si es necesario

	except Exception as e:
		# No fallar por errores de auditoría
		frappe.log_error(f"Error en audit log: {e!s}")


def validate_business_rules(doc):
	"""Validar reglas de negocio específicas"""
	# Validar que no hay más de X espacios por company (configurable)
	max_spaces = frappe.db.get_single_value("Physical Spaces Settings", "max_spaces_per_company")
	if max_spaces:
		current_count = frappe.db.count("Physical Space", {"company": doc.company})
		if current_count >= max_spaces:
			frappe.throw(f"Se alcanzó el límite máximo de {max_spaces} espacios para esta company")

	# Validar nomenclatura específica si está configurada
	validate_naming_convention(doc)


def validate_naming_convention(doc):
	"""Validar convención de nomenclatura"""
	# TODO: Implementar validaciones específicas de nomenclatura si es necesario
	# Por ejemplo, validar que ciertos tipos de espacios sigan patrones específicos
	pass
