# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


def validate(doc, method):
	"""Hook de validación para Physical Space"""
	try:
		# Validar jerarquía
		validate_hierarchy(doc)

		# Validar categoría si está configurada
		validate_category_requirements(doc)

		# Validar referencias de ubicación
		validate_location_references(doc)

	except Exception as e:
		frappe.log_error(f"Error en validación de Physical Space: {e!s}")
		raise


def before_save(doc, method):
	"""Hook antes de guardar Physical Space"""
	try:
		# Generar código si no existe
		if not doc.space_code:
			doc.generate_space_code()

		# Actualizar información de jerarquía
		doc.update_hierarchy_info()

	except Exception as e:
		frappe.log_error(f"Error en before_save de Physical Space: {e!s}")
		raise


def validate_hierarchy(doc):
	"""Validar jerarquía del espacio físico"""
	# Validar que no sea su propio padre
	if doc.parent_space == doc.name:
		frappe.throw("Un espacio no puede ser su propio padre")

	# Validar referencias circulares
	if doc.parent_space and has_circular_reference(doc):
		frappe.throw("Se detectó una referencia circular en la jerarquía")


def has_circular_reference(doc):
	"""Detectar referencias circulares en jerarquía"""
	visited = set()
	current = doc.parent_space

	while current:
		if current in visited:
			return True
		visited.add(current)

		parent_doc = frappe.get_doc("Physical Space", current)
		current = parent_doc.parent_space

		# Límite de seguridad
		if len(visited) > 100:
			frappe.throw("Jerarquía demasiado profunda")

	return False


def validate_category_requirements(doc):
	"""Validar requisitos de la categoría del espacio"""
	if not doc.space_category:
		return

	try:
		category = frappe.get_doc("Space Category", doc.space_category)

		# Validar campos obligatorios según categoría
		if category.requires_dimensions:
			if not doc.area_m2:
				frappe.throw(f"La categoría '{category.category_name}' requiere especificar el área en m²")

		if category.requires_capacity:
			if not doc.max_capacity:
				frappe.throw(
					f"La categoría '{category.category_name}' requiere especificar la capacidad máxima"
				)

		if category.requires_components:
			if not doc.space_components:
				frappe.throw(f"La categoría '{category.category_name}' requiere especificar componentes")

		# Validar jerarquía permitida
		validate_category_hierarchy(doc, category)

	except frappe.DoesNotExistError:
		frappe.throw(f"La categoría '{doc.space_category}' no existe")


def validate_category_hierarchy(doc, category):
	"""Validar jerarquía permitida por la categoría"""
	if doc.parent_space and category.allowed_parent_categories:
		parent_doc = frappe.get_doc("Physical Space", doc.parent_space)
		if parent_doc.space_category:
			allowed_parents = [row.parent_category for row in category.allowed_parent_categories]
			if parent_doc.space_category not in allowed_parents:
				frappe.throw(
					f"La categoría '{category.category_name}' no puede ser hija de "
					f"la categoría '{parent_doc.space_category}'"
				)


def validate_location_references(doc):
	"""Validar referencias de ubicación física"""
	# Validar que las referencias existen y están activas
	references = [("building_reference", "Edificio"), ("floor_reference", "Piso"), ("zone_reference", "Zona")]

	for field, label in references:
		ref_value = getattr(doc, field, None)
		if ref_value:
			try:
				ref_doc = frappe.get_doc("Physical Space", ref_value)
				if not ref_doc.is_active:
					frappe.throw(f"La referencia de {label} '{ref_value}' no está activa")
			except frappe.DoesNotExistError:
				frappe.throw(f"La referencia de {label} '{ref_value}' no existe")


def validate_cost_center(doc):
	"""Validar centro de costos"""
	if doc.cost_center:
		try:
			cost_center = frappe.get_doc("Cost Center", doc.cost_center)
			if not cost_center.is_group:
				# Validar que pertenece a la company correcta
				if cost_center.company != doc.company:
					frappe.throw(
						f"El centro de costos '{doc.cost_center}' no pertenece "
						f"a la company '{doc.company}'"
					)
		except frappe.DoesNotExistError:
			frappe.throw(f"El centro de costos '{doc.cost_center}' no existe")
