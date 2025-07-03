# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Template Propagation API para Document Generation Module
=======================================================

APIs para propagación de cambios en templates y gestión de configuraciones
distribuidas entre múltiples condominios.
"""

import frappe
from frappe import _


@frappe.whitelist()
def propagate_template_changes(registry_name, template_version, affected_stats):
	"""
	Propagar cambios de templates a configuraciones existentes.

	Esta función se ejecuta como job asíncrono desde el hook de template update.

	Args:
	    registry_name (str): Nombre del Master Template Registry
	    template_version (str): Nueva versión de templates
	    affected_stats (dict): Estadísticas de configuraciones afectadas
	"""

	try:
		registry = frappe.get_single("Master Template Registry")
		propagation_results = {
			"total_processed": 0,
			"successful_updates": 0,
			"failed_updates": 0,
			"skipped_updates": 0,
			"errors": [],
		}

		# Obtener configuraciones afectadas por template codes
		template_codes = [t.template_code for t in registry.infrastructure_templates]

		if not template_codes:
			complete_propagation(registry, "Completado", propagation_results)
			return propagation_results

		affected_configs = frappe.get_all(
			"Entity Configuration",
			filters={
				"applied_template": ["in", template_codes],
				"configuration_status": ["in", ["Borrador", "Pendiente Aprobación", "Aprobado"]],
			},
			fields=["name", "applied_template", "configuration_status", "configuration_name"],
		)

		propagation_results["total_processed"] = len(affected_configs)

		# Procesar cada configuración
		for config_data in affected_configs:
			try:
				result = update_single_configuration(config_data, registry)

				if result["success"]:
					propagation_results["successful_updates"] += 1
				else:
					propagation_results["failed_updates"] += 1
					propagation_results["errors"].append(
						{"config": config_data["name"], "error": result["error"]}
					)

			except Exception as e:
				propagation_results["failed_updates"] += 1
				propagation_results["errors"].append({"config": config_data["name"], "error": str(e)})

				frappe.log_error(
					f"Error propagando a configuración {config_data['name']}: {e!s}",
					"Template Propagation",
				)

		# Completar propagación
		status = "Completado" if propagation_results["failed_updates"] == 0 else "Completado con Errores"
		complete_propagation(registry, status, propagation_results)

		return propagation_results

	except Exception as e:
		frappe.log_error(f"Error crítico en propagación de templates: {e!s}", "Template Propagation Critical")

		# Marcar como fallido
		try:
			registry = frappe.get_single("Master Template Registry")
			registry.db_set("update_propagation_status", "Fallido", update_modified=False)
			frappe.db.commit()
		except:
			pass

		raise


def update_single_configuration(config_data, registry):
	"""
	Actualizar una configuración individual con cambios de template.

	Args:
	    config_data (dict): Datos de la configuración a actualizar
	    registry (Document): Master Template Registry con templates actualizados

	Returns:
	    dict: Resultado de la actualización
	"""

	try:
		config = frappe.get_doc("Entity Configuration", config_data["name"])
		template = registry.get_template_by_code(config.applied_template)

		if not template:
			return {"success": False, "error": f"Template {config.applied_template} no encontrado"}

		# Sincronizar campos con template actualizado
		changes_made = sync_configuration_with_template(config, template)

		if changes_made:
			# Marcar como requiere re-aprobación si estaba aprobado
			original_status = config.configuration_status
			if original_status == "Aprobado":
				config.configuration_status = "Pendiente Aprobación"

			config.save()

			return {
				"success": True,
				"changes_made": True,
				"status_changed": original_status != config.configuration_status,
			}
		else:
			return {"success": True, "changes_made": False}

	except Exception as e:
		return {"success": False, "error": str(e)}


def sync_configuration_with_template(config, template):
	"""
	Sincronizar configuración con template actualizado.

	Args:
	    config (Document): Entity Configuration a sincronizar
	    template (dict): Template con cambios

	Returns:
	    bool: True si se realizaron cambios, False en caso contrario
	"""

	template_fields = {f["field_name"]: f for f in template.get("template_fields", [])}
	changes_made = False

	# Actualizar metadatos del documento
	if config.target_document_type != template.get("target_document"):
		config.target_document_type = template.get("target_document")
		changes_made = True

	if config.target_section != template.get("target_section"):
		config.target_section = template.get("target_section")
		changes_made = True

	# Procesar campos existentes
	for config_field in config.configuration_fields:
		field_name = config_field.field_name

		if field_name in template_fields:
			# Campo existe en template - actualizar metadatos
			template_field = template_fields[field_name]

			if config_field.field_label != template_field.get("field_label"):
				config_field.field_label = template_field.get("field_label")
				changes_made = True

			if config_field.field_type != template_field.get("field_type"):
				config_field.field_type = template_field.get("field_type")
				changes_made = True

			if config_field.is_required != template_field.get("is_required", 0):
				config_field.is_required = template_field.get("is_required", 0)
				changes_made = True

			# Actualizar valor por defecto solo si el campo está vacío
			default_value = template_field.get("default_value", "")
			if not config_field.field_value and default_value:
				config_field.field_value = default_value
				changes_made = True

		else:
			# Campo ya no existe en template - desactivar
			if config_field.is_active:
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
					"field_label": field_def.get("field_label", field_name),
					"field_type": field_def.get("field_type", "Data"),
					"field_value": field_def.get("default_value", ""),
					"is_required": field_def.get("is_required", 0),
					"is_active": 1,
					"created_by": "System",
					"last_updated": frappe.utils.now(),
					"updated_by": "System",
				},
			)
			changes_made = True

	# Actualizar timestamp de última sincronización
	if changes_made:
		config.last_template_sync = frappe.utils.now()

	return changes_made


def complete_propagation(registry, status, results):
	"""
	Completar proceso de propagación y notificar resultados.

	Args:
	    registry (Document): Master Template Registry
	    status (str): Estado final de la propagación
	    results (dict): Resultados de la propagación
	"""

	# Actualizar estado en registry
	registry.db_set("update_propagation_status", status, update_modified=False)
	registry.db_set("last_propagation_result", frappe.as_json(results), update_modified=False)

	# Notificar resultados
	frappe.publish_realtime(
		event="template_propagation_completed",
		message={"registry": registry.name, "status": status, "results": results},
	)

	# Crear log de propagación
	create_propagation_log(registry, status, results)

	frappe.db.commit()


def create_propagation_log(registry, status, results):
	"""
	Crear log detallado de la propagación.

	Args:
	    registry (Document): Master Template Registry
	    status (str): Estado de la propagación
	    results (dict): Resultados detallados
	"""

	try:
		log_content = f"""
        Propagación de Templates - {registry.template_version}
        =====================================================

        Estado: {status}
        Fecha: {frappe.utils.now()}

        Estadísticas:
        - Total procesadas: {results['total_processed']}
        - Actualizaciones exitosas: {results['successful_updates']}
        - Actualizaciones fallidas: {results['failed_updates']}
        - Omitidas: {results['skipped_updates']}

        """

		if results.get("errors"):
			log_content += "\nErrores encontrados:\n"
			for error in results["errors"]:
				log_content += f"- {error['config']}: {error['error']}\n"

		# Guardar en log del sistema
		frappe.log_error(log_content, f"Template Propagation - {registry.template_version}")

	except Exception as e:
		frappe.log_error(f"Error creando log de propagación: {e!s}")


@frappe.whitelist()
def get_propagation_status(registry_name=None):
	"""
	Obtener estado actual de propagación de templates.

	Args:
	    registry_name (str): Nombre específico del registry (opcional)

	Returns:
	    dict: Estado de propagación y estadísticas
	"""

	try:
		if registry_name:
			registry = frappe.get_doc("Master Template Registry", registry_name)
		else:
			registry = frappe.get_single("Master Template Registry")

		# Estadísticas básicas
		stats = {
			"registry_name": registry.name,
			"template_version": registry.template_version,
			"propagation_status": registry.update_propagation_status,
			"last_update": registry.last_update,
		}

		# Resultados de última propagación si existen
		last_result = registry.get("last_propagation_result")
		if last_result:
			try:
				stats["last_propagation"] = frappe.parse_json(last_result)
			except:
				pass

		# Configuraciones pendientes de sincronización
		template_codes = [t.template_code for t in registry.infrastructure_templates]
		if template_codes:
			pending_sync = frappe.db.count(
				"Entity Configuration",
				filters={
					"applied_template": ["in", template_codes],
					"configuration_status": ["in", ["Aprobado", "Pendiente Aprobación"]],
					"last_template_sync": ["<", registry.last_update],
				},
			)
			stats["pending_sync_count"] = pending_sync

		return stats

	except Exception as e:
		frappe.log_error(f"Error obteniendo estado de propagación: {e!s}", "Template Propagation API")
		return {}


@frappe.whitelist()
def force_template_resync(config_names=None, template_codes=None):
	"""
	Forzar re-sincronización de configuraciones específicas.

	Args:
	    config_names (list): Nombres de configuraciones específicas
	    template_codes (list): Códigos de templates a re-sincronizar

	Returns:
	    dict: Resultado de la re-sincronización
	"""

	try:
		registry = frappe.get_single("Master Template Registry")

		# Determinar configuraciones a procesar
		if config_names:
			filters = {"name": ["in", config_names]}
		elif template_codes:
			filters = {"applied_template": ["in", template_codes]}
		else:
			frappe.throw(_("Debe especificar config_names o template_codes"))

		# Agregar filtros adicionales
		filters.update({"configuration_status": ["in", ["Borrador", "Pendiente Aprobación", "Aprobado"]]})

		configurations = frappe.get_all(
			"Entity Configuration", filters=filters, fields=["name", "applied_template", "configuration_name"]
		)

		results = {"total_processed": len(configurations), "successful": 0, "failed": 0, "errors": []}

		for config_data in configurations:
			try:
				result = update_single_configuration(config_data, registry)

				if result["success"]:
					results["successful"] += 1
				else:
					results["failed"] += 1
					results["errors"].append({"config": config_data["name"], "error": result["error"]})

			except Exception as e:
				results["failed"] += 1
				results["errors"].append({"config": config_data["name"], "error": str(e)})

		frappe.db.commit()

		return results

	except Exception as e:
		frappe.log_error(f"Error en re-sincronización forzada: {e!s}", "Template Propagation API")
		frappe.throw(_("Error en re-sincronización: {0}").format(str(e)))
