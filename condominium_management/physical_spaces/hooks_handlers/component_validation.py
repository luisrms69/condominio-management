# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today


def validate(doc, method):
	"""Hook de validación para Space Component"""
	try:
		# Validar jerarquía de componentes
		validate_component_hierarchy(doc)

		# Validar requisitos del tipo de componente
		validate_component_type_requirements(doc)

		# Validar datos específicos del componente
		validate_component_data(doc)

		# Establecer valores por defecto
		set_default_values(doc)

	except Exception as e:
		frappe.log_error(f"Error en validación de Space Component: {e!s}")
		raise


def validate_component_hierarchy(doc):
	"""Validar jerarquía de componentes"""
	# Validar que no sea su propio padre
	if doc.parent_component == doc.name:
		frappe.throw("Un componente no puede ser su propio padre")

	# Validar referencias circulares
	if doc.parent_component and has_circular_reference(doc):
		frappe.throw("Se detectó una referencia circular en la jerarquía de componentes")


def has_circular_reference(doc):
	"""Detectar referencias circulares en jerarquía de componentes"""
	visited = set()
	current = doc.parent_component

	while current:
		if current in visited:
			return True
		visited.add(current)

		# Obtener componente padre - usar get_value para evitar cargar doc completo
		parent_component = frappe.db.get_value("Space Component", current, "parent_component")
		current = parent_component

		# Límite de seguridad
		if len(visited) > 50:
			frappe.throw("Jerarquía de componentes demasiado profunda")

	return False


def validate_component_type_requirements(doc):
	"""Validar requisitos específicos del tipo de componente"""
	if not doc.component_type:
		return

	try:
		component_type = frappe.get_doc("Component Type", doc.component_type)

		# Obtener reglas de validación del tipo
		validation_rules = component_type.get_validation_rules()

		# Validar campos obligatorios según el tipo
		errors = []

		if validation_rules.get("requires_brand") and not doc.brand:
			errors.append("La marca es obligatoria para este tipo de componente")

		if validation_rules.get("requires_model") and not doc.model:
			errors.append("El modelo es obligatorio para este tipo de componente")

		if validation_rules.get("requires_installation_date") and not doc.installation_date:
			errors.append("La fecha de instalación es obligatoria para este tipo de componente")

		if validation_rules.get("requires_warranty") and not doc.warranty_expiry_date:
			errors.append("La información de garantía es obligatoria para este tipo de componente")

		if validation_rules.get("requires_specifications") and not doc.technical_specifications:
			errors.append("Las especificaciones técnicas son obligatorias para este tipo de componente")

		# Reportar errores
		if errors:
			frappe.throw("<br>".join(errors))

	except frappe.DoesNotExistError:
		frappe.throw(f"El tipo de componente '{doc.component_type}' no existe")


def validate_component_data(doc):
	"""Validar datos específicos del componente"""
	# Validar cantidad
	if doc.quantity is not None and doc.quantity <= 0:
		frappe.throw("La cantidad debe ser mayor a cero")

	# Validar fechas
	validate_dates(doc)

	# Validar estado
	validate_status(doc)


def validate_dates(doc):
	"""Validar coherencia de fechas"""
	today_date = today()

	# La fecha de inventario no puede ser futura
	if doc.inventory_date and doc.inventory_date > today_date:
		frappe.throw("La fecha de entrada a inventario no puede ser futura")

	# La fecha de instalación debe ser posterior o igual a la de inventario
	if doc.installation_date and doc.inventory_date:
		if doc.installation_date < doc.inventory_date:
			frappe.throw("La fecha de instalación no puede ser anterior a la fecha de inventario")

	# La fecha de garantía debe ser posterior a la de instalación
	if doc.warranty_expiry_date and doc.installation_date:
		if doc.warranty_expiry_date <= doc.installation_date:
			frappe.throw("La fecha de vencimiento de garantía debe ser posterior a la fecha de instalación")


def validate_status(doc):
	"""Validar estado del componente"""
	valid_statuses = ["Activo", "Inactivo", "En Mantenimiento", "Fuera de Servicio", "Pendiente Instalación"]

	if doc.status and doc.status not in valid_statuses:
		frappe.throw(f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")

	# Validar coherencia del estado con fechas
	if doc.status == "Pendiente Instalación" and doc.installation_date:
		if doc.installation_date <= today():
			frappe.msgprint(
				"El componente tiene fecha de instalación pero está marcado como 'Pendiente Instalación'"
			)


def set_default_values(doc):
	"""Establecer valores por defecto"""
	# Establecer fecha de inventario por defecto
	if not doc.inventory_date:
		doc.inventory_date = today()

	# Establecer cantidad por defecto
	if doc.quantity is None:
		doc.quantity = 1

	# Establecer estado por defecto
	if not doc.status:
		if doc.installation_date:
			doc.status = "Activo"
		else:
			doc.status = "Pendiente Instalación"


def validate_inventory_code_uniqueness(doc):
	"""Validar unicidad del código de inventario"""
	if doc.inventory_code:
		# Verificar que no existe otro componente con el mismo código
		existing = frappe.db.get_value(
			"Space Component", filters={"inventory_code": doc.inventory_code, "name": ["!=", doc.name]}
		)
		if existing:
			frappe.throw(f"Ya existe un componente con el código de inventario '{doc.inventory_code}'")


def validate_parent_component_consistency(doc):
	"""Validar consistencia con componente padre"""
	if doc.parent_component:
		try:
			parent_doc = frappe.get_doc("Space Component", doc.parent_component)

			# El componente hijo debe tener el mismo o compatible tipo
			validate_compatible_types(doc, parent_doc)

			# Validar que el padre esté activo
			if parent_doc.status == "Fuera de Servicio":
				frappe.msgprint(
					f"Advertencia: El componente padre '{parent_doc.component_name}' está fuera de servicio"
				)

		except frappe.DoesNotExistError:
			frappe.throw(f"El componente padre '{doc.parent_component}' no existe")


def validate_compatible_types(child_doc, parent_doc):
	"""Validar que los tipos de componente sean compatibles"""
	# TODO: Implementar lógica de compatibilidad de tipos cuando esté disponible
	# Por ejemplo, un "Quemador" solo puede ser hijo de una "Caldera"
	pass


def validate_technical_specifications_format(doc):
	"""Validar formato de especificaciones técnicas"""
	if doc.technical_specifications:
		# Validación básica - debe tener cierta longitud mínima
		if len(doc.technical_specifications.strip()) < 10:
			frappe.msgprint(
				"Las especificaciones técnicas parecen muy breves. " "Considere proporcionar más detalles."
			)

		# TODO: Implementar validaciones más específicas según el tipo de componente
