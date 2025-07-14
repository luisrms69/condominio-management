# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime


def after_insert(doc, method):
	"""Hook después de insertar Space Component"""
	try:
		# Generar código de inventario si no existe
		if not doc.inventory_code:
			generate_inventory_code(doc)

		# Crear configuración inicial
		create_initial_configuration(doc)

		# Integrar con módulo de mantenimiento si está disponible
		integrate_with_maintenance(doc)

		# Log de auditoría
		create_audit_log(doc, "inserted")

	except Exception as e:
		frappe.log_error(f"Error en after_insert de Space Component: {e!s}")


def generate_inventory_code(doc):
	"""Generar código de inventario automáticamente"""
	try:
		if doc.component_type:
			component_type = frappe.get_doc("Component Type", doc.component_type)
			next_code = component_type.get_next_inventory_code()

			# Actualizar el documento
			frappe.db.set_value("Space Component", doc.name, "inventory_code", next_code)
			doc.inventory_code = next_code

		else:
			# Generar código genérico
			next_code = get_generic_inventory_code()
			frappe.db.set_value("Space Component", doc.name, "inventory_code", next_code)
			doc.inventory_code = next_code

	except Exception as e:
		frappe.log_error(f"Error generando código de inventario: {e!s}")


def get_generic_inventory_code():
	"""Generar código de inventario genérico"""
	# Buscar el último código genérico usado
	last_code = frappe.db.sql("""
        SELECT inventory_code
        FROM `tabSpace Component`
        WHERE inventory_code LIKE 'COMP-%'
        ORDER BY inventory_code DESC
        LIMIT 1
    """)

	if last_code:
		# Extraer número y incrementar
		last_num = last_code[0][0].replace("COMP-", "")
		try:
			next_num = int(last_num) + 1
			return f"COMP-{next_num:04d}"
		except ValueError:
			# Si no se puede convertir, usar timestamp
			return f"COMP-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
	else:
		# Primer código
		return "COMP-0001"


def create_initial_configuration(doc):
	"""Crear configuración inicial para el componente"""
	try:
		# Cargar configuración del tipo de componente
		if doc.component_type:
			component_type = frappe.get_doc("Component Type", doc.component_type)

			# Aplicar configuración de mantenimiento por defecto
			apply_default_maintenance_config(doc, component_type)

			# TODO: Cargar campos del template si está configurado
			if component_type.component_template_code:
				load_component_template(doc, component_type)

	except Exception as e:
		frappe.log_error(f"Error en configuración inicial: {e!s}")


def apply_default_maintenance_config(doc, component_type):
	"""Aplicar configuración de mantenimiento por defecto"""
	try:
		maintenance_config = component_type.get_maintenance_configuration()

		# TODO: Integrar con módulo de mantenimiento cuando esté disponible
		# Crear programación de mantenimiento automática si es crítico
		if maintenance_config.get("critical_component"):
			create_maintenance_schedule(doc, maintenance_config)

	except Exception as e:
		frappe.log_error(f"Error aplicando configuración de mantenimiento: {e!s}")


def create_maintenance_schedule(doc, maintenance_config):
	"""Crear programación de mantenimiento automática"""
	# TODO: Implementar cuando esté disponible el módulo de mantenimiento
	frappe.logger().info(
		f"Component {doc.component_name} marcado para mantenimiento automático: "
		f"frequency={maintenance_config.get('default_frequency')}, "
		f"type={maintenance_config.get('maintenance_type')}"
	)


def load_component_template(doc, component_type):
	"""Cargar template del componente"""
	# TODO: Implementar cuando esté disponible el template system
	frappe.logger().info(
		f"Loading template {component_type.component_template_code} for component {doc.component_name}"
	)


def integrate_with_maintenance(doc):
	"""Integrar con módulo de mantenimiento"""
	try:
		# TODO: Notificar al módulo de mantenimiento sobre nuevo componente
		# Esto permitirá crear automáticamente:
		# - Programaciones de mantenimiento
		# - Alertas de garantía
		# - Inspecciones periódicas

		# Por ahora, solo log
		frappe.logger().info(f"New component created for maintenance tracking: {doc.component_name}")

	except Exception as e:
		frappe.log_error(f"Error integrando con mantenimiento: {e!s}")


def create_audit_log(doc, action):
	"""Crear log de auditoría para el componente"""
	try:
		frappe.logger().info(
			f"Space Component {action}: {doc.name} - {doc.component_name} "
			f"(Type: {doc.component_type or 'N/A'}, Code: {doc.inventory_code or 'N/A'}) "
			f"by {frappe.session.user} at {now_datetime()}"
		)

		# TODO: Integrar con sistema de auditoría más robusto si es necesario

	except Exception as e:
		# No fallar por errores de auditoría
		frappe.log_error(f"Error en audit log de component: {e!s}")


def validate_business_rules(doc):
	"""Validar reglas de negocio específicas para componentes"""
	try:
		# Validar límites por tipo de componente
		validate_component_limits(doc)

		# Validar compatibilidad con el espacio físico padre
		validate_space_compatibility(doc)

	except Exception as e:
		frappe.log_error(f"Error validando reglas de negocio: {e!s}")


def validate_component_limits(doc):
	"""Validar límites de componentes por tipo"""
	if doc.component_type:
		# TODO: Implementar validaciones específicas
		# Por ejemplo, no más de X elevadores por building
		pass


def validate_space_compatibility(doc):
	"""Validar compatibilidad con el espacio físico"""
	# TODO: Validar que el tipo de componente sea compatible con la categoría del espacio
	# Por ejemplo, un elevador solo puede estar en ciertos tipos de espacios
	pass


def notify_related_systems(doc):
	"""Notificar a sistemas relacionados"""
	try:
		# TODO: Notificar a módulos dependientes
		# - Access Control: si es un componente de seguridad
		# - Maintenance: para programar mantenimientos
		# - Compliance: si requiere certificaciones

		if doc.component_type:
			component_type = frappe.get_doc("Component Type", doc.component_type)

			# Notificar si es componente crítico
			if component_type.critical_component:
				notify_critical_component_created(doc)

			# Notificar si requiere certificación
			if component_type.requires_certification:
				notify_certification_required(doc)

	except Exception as e:
		frappe.log_error(f"Error notificando sistemas relacionados: {e!s}")


def notify_critical_component_created(doc):
	"""Notificar creación de componente crítico"""
	frappe.logger().info(f"Critical component created: {doc.component_name}")
	# TODO: Enviar notificación a administradores


def notify_certification_required(doc):
	"""Notificar que se requiere certificación"""
	frappe.logger().info(f"Certification required for component: {doc.component_name}")
	# TODO: Crear tarea de certificación automáticamente
