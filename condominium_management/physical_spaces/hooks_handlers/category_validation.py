# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr


def validate(doc, method):
	"""Hook de validación para Space Category"""
	try:
		# Generar código de categoría si no existe
		if not doc.category_code:
			doc.generate_category_code()

		# Validar configuración de template
		validate_template_configuration(doc)

		# Validar jerarquías permitidas
		validate_allowed_hierarchies(doc)

		# Validar configuración UI
		validate_ui_configuration(doc)

	except Exception as e:
		frappe.log_error(f"Error en validación de Space Category: {e!s}")
		raise


def validate_template_configuration(doc):
	"""Validar configuración del template"""
	if doc.ps_template_code:
		# Validar formato del código de template
		if not doc.ps_template_code.replace("_", "").replace("-", "").isalnum():
			frappe.throw(
				"El código del template solo puede contener letras, números, guiones y guiones bajos"
			)

		# Establecer versión por defecto
		if not doc.template_version:
			doc.template_version = "1.0"

		# TODO: Validar que el template existe cuando esté implementado el template system
		if doc.auto_load_template:
			validate_template_exists(doc.ps_template_code)


def validate_template_exists(template_code):
	"""Validar que el template especificado existe"""
	# TODO: Implementar cuando esté disponible el template system
	# Por ahora solo validamos el formato
	pass


def validate_allowed_hierarchies(doc):
	"""Validar configuración de jerarquías permitidas"""
	# Validar que no hay duplicados en categorías padre permitidas
	if doc.allowed_parent_categories:
		parent_categories = [row.parent_category for row in doc.allowed_parent_categories]
		if len(parent_categories) != len(set(parent_categories)):
			frappe.throw("No puede haber categorías padre duplicadas")

		# Validar que la categoría no se incluya a sí misma como padre
		if doc.name in parent_categories:
			frappe.throw("Una categoría no puede ser su propia categoría padre")

	# Validar que no hay duplicados en categorías hijo permitidas
	if doc.allowed_child_categories:
		child_categories = [row.child_category for row in doc.allowed_child_categories]
		if len(child_categories) != len(set(child_categories)):
			frappe.throw("No puede haber categorías hijo duplicadas")

		# Validar que la categoría no se incluya a sí misma como hijo
		if doc.name in child_categories:
			frappe.throw("Una categoría no puede ser su propia categoría hijo")


def validate_ui_configuration(doc):
	"""Validar configuración de UI"""
	# Validar código de color
	if doc.color_code:
		if not doc.color_code.startswith("#") or len(doc.color_code) not in [4, 7]:
			frappe.throw("El código de color debe ser un color hexadecimal válido (ej: #FF0000 o #F00)")

	# Validar clase de icono
	if doc.icon_class:
		# Validación básica - debe contener al menos "fa" o "octicon"
		if not any(prefix in doc.icon_class.lower() for prefix in ["fa", "octicon", "icon"]):
			frappe.msgprint(
				"Advertencia: La clase de icono no parece ser válida. "
				"Use clases como 'fa fa-home' o 'octicon octicon-home'"
			)

	# Validar orden de visualización
	if doc.display_order is not None and doc.display_order < 0:
		frappe.throw("El orden de visualización debe ser un número positivo")


def validate_category_type(doc):
	"""Validar tipo de categoría"""
	valid_types = [
		"Estructura",
		"Área Común",
		"Área Privada",
		"Instalaciones",
		"Equipamiento",
		"Seguridad",
		"Mantenimiento",
		"Servicios",
	]

	if doc.category_type and doc.category_type not in valid_types:
		frappe.throw(f"Tipo de categoría inválido. Debe ser uno de: {', '.join(valid_types)}")


def validate_requirements_consistency(doc):
	"""Validar consistencia de requisitos"""
	# Si requiere componentes, asegurar que la configuración sea consistente
	if doc.requires_components and not doc.ps_template_code:
		frappe.msgprint(
			"Recomendación: Las categorías que requieren componentes "
			"deberían tener un template configurado para mejor experiencia de usuario"
		)

	# Validar que los requisitos tengan sentido para el tipo de categoría
	if doc.category_type == "Estructura" and not doc.requires_dimensions:
		frappe.msgprint(
			"Recomendación: Las categorías de tipo 'Estructura' normalmente requieren especificar dimensiones"
		)


def validate_business_logic(doc):
	"""Validar lógica de negocio específica"""
	# Validar que ciertas combinaciones sean lógicas
	if doc.category_type == "Área Privada" and doc.requires_capacity:
		# Es lógico que áreas privadas requieran capacidad
		pass
	elif doc.category_type == "Equipamiento" and not doc.requires_components:
		frappe.msgprint(
			"Advertencia: Las categorías de 'Equipamiento' normalmente requieren especificar componentes"
		)
