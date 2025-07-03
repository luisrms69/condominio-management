# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Template Propagation Handler para Document Generation Module
===========================================================

Maneja la propagación de cambios en templates maestros a configuraciones
existentes en todos los condominios.
"""

import frappe
from frappe import _


def on_template_update(doc, method):
	"""
	Hook ejecutado cuando Master Template Registry se actualiza.

	Detecta cambios en templates y programa propagación automática
	a todas las configuraciones existentes.

	Args:
	    doc (Document): Master Template Registry actualizado
	    method (str): Método que disparó el hook ('on_update')
	"""

	if doc.update_propagation_status != "Pendiente":
		return

	try:
		# Obtener estadísticas de configuraciones afectadas
		stats = get_affected_configurations_stats(doc)

		if stats["total_configurations"] == 0:
			# No hay configuraciones que propagar
			doc.db_set("update_propagation_status", "Completado", update_modified=False)
			return

		# Programar propagación asíncrona
		frappe.enqueue(
			"condominium_management.document_generation.api.template_propagation.propagate_template_changes",
			queue="default",
			timeout=900,  # 15 minutos para propagación
			registry_name=doc.name,
			template_version=doc.template_version,
			affected_stats=stats,
		)

		# Actualizar estado y crear notificaciones
		doc.db_set("update_propagation_status", "En Progreso", update_modified=False)
		create_update_notifications(doc, stats)

		frappe.msgprint(
			_("Propagación de templates iniciada. {0} configuraciones serán actualizadas.").format(
				stats["total_configurations"]
			),
			indicator="blue",
		)

	except Exception as e:
		frappe.log_error(f"Error iniciando propagación de templates: {e!s}", "Template Propagation Handler")
		doc.db_set("update_propagation_status", "Fallido", update_modified=False)


def propagate_template_changes(registry_name, template_version, affected_stats):
	"""
	Función asíncrona para propagar cambios de templates.

	Args:
	    registry_name (str): Nombre del Master Template Registry
	    template_version (str): Versión de templates
	    affected_stats (dict): Estadísticas de configuraciones afectadas
	"""

	try:
		registry = frappe.get_single("Master Template Registry")

		# Obtener todas las configuraciones que usan templates actualizados
		affected_configs = get_affected_configurations(registry)

		total_updated = 0
		total_errors = 0

		for config_name in affected_configs:
			try:
				config = frappe.get_doc("Entity Configuration", config_name)

				# Sincronizar campos con template actualizado
				if sync_configuration_fields(config, registry):
					# Marcar como pendiente de aprobación si estaba aprobado
					if config.configuration_status == "Aprobado":
						config.configuration_status = "Pendiente Aprobación"

					config.save()
					total_updated += 1

			except Exception as e:
				frappe.log_error(
					f"Error propagando cambios a configuración {config_name}: {e!s}",
					"Template Propagation",
				)
				total_errors += 1

		# Actualizar estado final
		if total_errors == 0:
			registry.db_set("update_propagation_status", "Completado", update_modified=False)
			status_message = "completada exitosamente"
		else:
			registry.db_set("update_propagation_status", "Completado con Errores", update_modified=False)
			status_message = f"completada con {total_errors} errores"

		# Notificar resultado
		frappe.publish_realtime(
			event="template_propagation_completed",
			message={
				"registry": registry_name,
				"template_version": template_version,
				"total_updated": total_updated,
				"total_errors": total_errors,
				"status": status_message,
			},
		)

		frappe.db.commit()

	except Exception as e:
		frappe.log_error(f"Error crítico en propagación de templates: {e!s}", "Template Propagation Critical")

		# Marcar como fallido
		registry = frappe.get_single("Master Template Registry")
		registry.db_set("update_propagation_status", "Fallido", update_modified=False)
		frappe.db.commit()


def get_affected_configurations(registry):
	"""
	Obtener configuraciones afectadas por cambios en templates.

	Args:
	    registry (Document): Master Template Registry

	Returns:
	    list: Lista de nombres de Entity Configuration afectadas
	"""

	# Obtener códigos de templates que han cambiado
	template_codes = [t.template_code for t in registry.infrastructure_templates]

	if not template_codes:
		return []

	# Buscar configuraciones que usan estos templates
	affected_configs = frappe.get_all(
		"Entity Configuration",
		filters={
			"applied_template": ["in", template_codes],
			"configuration_status": ["in", ["Borrador", "Pendiente Aprobación", "Aprobado"]],
		},
		fields=["name"],
	)

	return [config["name"] for config in affected_configs]


def sync_configuration_fields(config, registry):
	"""
	Sincronizar campos de configuración con template actualizado.

	Args:
	    config (Document): Entity Configuration a sincronizar
	    registry (Document): Master Template Registry con templates actualizados

	Returns:
	    bool: True si se realizaron cambios, False en caso contrario
	"""

	template = registry.get_template_by_code(config.applied_template)
	if not template:
		return False

	template_fields = {f["field_name"]: f for f in template.get("template_fields", [])}
	changes_made = False

	# Actualizar campos existentes
	for config_field in config.configuration_fields:
		field_name = config_field.field_name

		if field_name in template_fields:
			template_field = template_fields[field_name]

			# Actualizar metadatos del campo
			if config_field.field_label != template_field.get("field_label"):
				config_field.field_label = template_field.get("field_label")
				changes_made = True

			if config_field.field_type != template_field.get("field_type"):
				config_field.field_type = template_field.get("field_type")
				changes_made = True

			if config_field.is_required != template_field.get("is_required", 0):
				config_field.is_required = template_field.get("is_required", 0)
				changes_made = True

		else:
			# Campo ya no existe en template - marcar para eliminación
			config_field.is_active = 0
			changes_made = True

	# Agregar nuevos campos del template
	existing_fields = [f.field_name for f in config.configuration_fields]

	for field_name, field_def in template_fields.items():
		if field_name not in existing_fields:
			config.append(
				"configuration_fields",
				{
					"field_name": field_name,
					"field_label": field_def.get("field_label"),
					"field_type": field_def.get("field_type"),
					"field_value": field_def.get("default_value", ""),
					"is_required": field_def.get("is_required", 0),
					"is_active": 1,
					"created_by": frappe.session.user,
					"last_updated": frappe.utils.now(),
				},
			)
			changes_made = True

	return changes_made


def update_global_template_version(doc):
	"""
	Actualizar versión global de templates en el sistema.

	Args:
	    doc (Document): Master Template Registry
	"""

	# Guardar versión global para referencia
	frappe.db.set_global("document_generation_template_version", doc.template_version)
	frappe.db.set_global("document_generation_last_update", frappe.utils.now())


def create_update_notifications(doc, stats):
	"""
	Crear notificaciones sobre actualización de templates.

	Args:
	    doc (Document): Master Template Registry
	    stats (dict): Estadísticas de configuraciones afectadas
	"""

	# Notificar a administradores del sistema
	admin_users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name"])

	notification_content = _("""
        Los templates maestros han sido actualizados a la versión {0}.

        Configuraciones afectadas: {1}
        - Aprobadas: {2}
        - Pendientes: {3}
        - Borradores: {4}

        La propagación está en progreso. Las configuraciones aprobadas
        requerirán nueva aprobación después de la sincronización.
    """).format(
		doc.template_version,
		stats["total_configurations"],
		stats.get("approved", 0),
		stats.get("pending", 0),
		stats.get("draft", 0),
	)

	for user in admin_users:
		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"subject": _("Templates actualizados - Propagación iniciada"),
				"email_content": notification_content,
				"for_user": user["name"],
				"type": "Alert",
				"document_type": "Master Template Registry",
				"document_name": doc.name,
			}
		).insert(ignore_permissions=True)


def get_affected_configurations_stats(doc):
	"""
	Obtener estadísticas de configuraciones afectadas por cambios.

	Args:
	    doc (Document): Master Template Registry

	Returns:
	    dict: Estadísticas de configuraciones afectadas
	"""

	template_codes = [t.template_code for t in doc.infrastructure_templates]

	if not template_codes:
		return {"total_configurations": 0}

	# Contar configuraciones por estado
	stats = frappe.db.sql(
		"""
        SELECT
            configuration_status,
            COUNT(*) as count
        FROM `tabEntity Configuration`
        WHERE applied_template IN %(template_codes)s
        AND configuration_status IN ('Borrador', 'Pendiente Aprobación', 'Aprobado')
        GROUP BY configuration_status
    """,
		{"template_codes": template_codes},
		as_dict=True,
	)

	result = {"total_configurations": 0}

	for stat in stats:
		status = stat["configuration_status"]
		count = stat["count"]
		result["total_configurations"] += count

		if status == "Aprobado":
			result["approved"] = count
		elif status == "Pendiente Aprobación":
			result["pending"] = count
		elif status == "Borrador":
			result["draft"] = count

	return result
