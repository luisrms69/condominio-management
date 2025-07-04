# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Conflict Detection API para Document Generation Module
=====================================================

APIs para detección de conflictos entre configuraciones de documentos
y validación de consistencia entre condominios.
"""

import frappe
from frappe import _


@frappe.whitelist()
def detect_configuration_conflicts(config_name):
	"""
	Detectar conflictos en configuración específica.

	Args:
	    config_name (str): Nombre de la Entity Configuration

	Returns:
	    list: Lista de conflictos detectados
	"""

	try:
		config = frappe.get_doc("Entity Configuration", config_name)
		conflicts = []

		# Detectar conflictos de horarios
		conflicts.extend(detect_schedule_conflicts(config))

		# Detectar conflictos de capacidad
		conflicts.extend(detect_capacity_conflicts(config))

		# Detectar conflictos de ubicación
		conflicts.extend(detect_location_conflicts(config))

		# Detectar conflictos de recursos
		conflicts.extend(detect_resource_conflicts(config))

		# Detectar inconsistencias con templates
		conflicts.extend(detect_template_inconsistencies(config))

		return conflicts

	except Exception as e:
		frappe.log_error(f"Error detectando conflictos para {config_name}: {e!s}", "Conflict Detection API")
		return []


def detect_schedule_conflicts(config):
	"""
	Detectar conflictos de horarios en configuración.

	Args:
	    config (Document): Entity Configuration

	Returns:
	    list: Conflictos de horarios encontrados
	"""

	conflicts = []

	# Obtener campos relacionados con horarios
	schedule_fields = get_configuration_fields_by_type(config, ["time", "datetime"])

	if not schedule_fields:
		return conflicts

	# Buscar configuraciones similares con horarios conflictivos
	similar_configs = frappe.get_all(
		"Entity Configuration",
		filters={
			"source_doctype": config.source_doctype,
			"entity_subtype": config.entity_subtype,
			"configuration_status": ["in", ["Aprobado", "Pendiente Aprobación"]],
			"name": ["!=", config.name],
		},
		fields=["name", "configuration_name"],
	)

	for similar_config in similar_configs:
		try:
			other_config = frappe.get_doc("Entity Configuration", similar_config["name"])

			# Comparar horarios
			schedule_conflict = compare_schedule_fields(config, other_config, schedule_fields)
			if schedule_conflict:
				conflicts.append(
					{
						"type": "schedule_conflict",
						"severity": "Media",
						"description": f"Conflicto de horarios con {other_config.configuration_name}",
						"conflicting_config": other_config.name,
						"details": schedule_conflict,
					}
				)

		except Exception as e:
			frappe.log_error(f"Error comparando horarios con {similar_config['name']}: {e!s}")

	return conflicts


def detect_capacity_conflicts(config):
	"""
	Detectar conflictos de capacidad en configuración.

	Args:
	    config (Document): Entity Configuration

	Returns:
	    list: Conflictos de capacidad encontrados
	"""

	conflicts = []

	# Obtener campos relacionados con capacidad
	capacity_fields = get_configuration_fields_by_name_pattern(config, ["capacity", "limite", "maximo"])

	if not capacity_fields:
		return conflicts

	# Validar capacidades lógicas
	for field in capacity_fields:
		try:
			capacity_value = int(field.field_value) if field.field_value.isdigit() else 0

			# Detectar capacidades ilógicas
			if capacity_value <= 0:
				conflicts.append(
					{
						"type": "invalid_capacity",
						"severity": "Alta",
						"description": f"Capacidad inválida en campo {field.field_label}",
						"field_name": field.field_name,
						"current_value": field.field_value,
					}
				)

			elif capacity_value > 10000:  # Capacidad excesivamente alta
				conflicts.append(
					{
						"type": "excessive_capacity",
						"severity": "Baja",
						"description": f"Capacidad muy alta en campo {field.field_label}",
						"field_name": field.field_name,
						"current_value": field.field_value,
					}
				)

		except ValueError:
			conflicts.append(
				{
					"type": "non_numeric_capacity",
					"severity": "Media",
					"description": f"Valor no numérico en campo de capacidad {field.field_label}",
					"field_name": field.field_name,
					"current_value": field.field_value,
				}
			)

	return conflicts


def detect_location_conflicts(config):
	"""
	Detectar conflictos de ubicación en configuración.

	Args:
	    config (Document): Entity Configuration

	Returns:
	    list: Conflictos de ubicación encontrados
	"""

	conflicts = []

	# Obtener campos relacionados con ubicación
	location_fields = get_configuration_fields_by_name_pattern(
		config, ["ubicacion", "location", "area", "zona", "sector"]
	)

	if not location_fields:
		return conflicts

	# Buscar duplicación de ubicaciones
	for field in location_fields:
		if not field.field_value:
			continue

		# Buscar otras configuraciones con la misma ubicación
		duplicate_locations = frappe.db.sql(
			"""
            SELECT DISTINCT ec.name, ec.configuration_name
            FROM `tabEntity Configuration` ec
            JOIN `tabConfiguration Field` cf ON cf.parent = ec.name
            WHERE cf.field_name = %(field_name)s
            AND cf.field_value = %(field_value)s
            AND ec.name != %(config_name)s
            AND ec.configuration_status IN ('Aprobado', 'Pendiente Aprobación')
        """,
			{"field_name": field.field_name, "field_value": field.field_value, "config_name": config.name},
			as_dict=True,
		)

		if duplicate_locations:
			conflicts.append(
				{
					"type": "location_duplicate",
					"severity": "Alta",
					"description": f"Ubicación duplicada: {field.field_value}",
					"field_name": field.field_name,
					"conflicting_configs": [loc["name"] for loc in duplicate_locations],
				}
			)

	return conflicts


def detect_resource_conflicts(config):
	"""
	Detectar conflictos de recursos en configuración.

	Args:
	    config (Document): Entity Configuration

	Returns:
	    list: Conflictos de recursos encontrados
	"""

	conflicts = []

	# Obtener campos relacionados con recursos
	resource_fields = get_configuration_fields_by_name_pattern(
		config, ["equipo", "equipment", "recurso", "resource"]
	)

	if not resource_fields:
		return conflicts

	# Detectar asignación múltiple de recursos únicos
	for field in resource_fields:
		if not field.field_value:
			continue

		# Buscar el mismo recurso asignado a otras configuraciones
		resource_conflicts = frappe.db.sql(
			"""
            SELECT DISTINCT ec.name, ec.configuration_name
            FROM `tabEntity Configuration` ec
            JOIN `tabConfiguration Field` cf ON cf.parent = ec.name
            WHERE cf.field_name LIKE %(field_pattern)s
            AND cf.field_value = %(field_value)s
            AND ec.name != %(config_name)s
            AND ec.configuration_status IN ('Aprobado', 'Pendiente Aprobación')
        """,
			{
				"field_pattern": f"%{field.field_name.split('_')[-1]}%",
				"field_value": field.field_value,
				"config_name": config.name,
			},
			as_dict=True,
		)

		if resource_conflicts:
			conflicts.append(
				{
					"type": "resource_conflict",
					"severity": "Media",
					"description": f"Recurso {field.field_value} asignado múltiples veces",
					"field_name": field.field_name,
					"conflicting_configs": [res["name"] for res in resource_conflicts],
				}
			)

	return conflicts


def detect_template_inconsistencies(config):
	"""
	Detectar inconsistencias con template asignado.

	Args:
	    config (Document): Entity Configuration

	Returns:
	    list: Inconsistencias encontradas
	"""

	conflicts = []

	if not config.applied_template:
		return conflicts

	try:
		# Obtener template actual
		registry = frappe.get_single("Master Template Registry")
		template = registry.get_template_by_code(config.applied_template)

		if not template:
			conflicts.append(
				{
					"type": "missing_template",
					"severity": "Alta",
					"description": f"Template {config.applied_template} no existe",
					"template_code": config.applied_template,
				}
			)
			return conflicts

		# Verificar campos requeridos
		template_fields = {f["field_name"]: f for f in template.get("template_fields", [])}
		config_fields = {f.field_name: f for f in config.configuration_fields}

		# Campos faltantes
		for field_name, field_def in template_fields.items():
			if field_name not in config_fields:
				conflicts.append(
					{
						"type": "missing_field",
						"severity": "Media",
						"description": f"Campo requerido {field_def.get('field_label', field_name)} no configurado",
						"field_name": field_name,
					}
				)

			elif field_def.get("is_required") and not config_fields[field_name].field_value:
				conflicts.append(
					{
						"type": "empty_required_field",
						"severity": "Alta",
						"description": f"Campo requerido {field_def.get('field_label', field_name)} está vacío",
						"field_name": field_name,
					}
				)

		# Campos obsoletos
		for field_name in config_fields:
			if field_name not in template_fields:
				conflicts.append(
					{
						"type": "obsolete_field",
						"severity": "Baja",
						"description": f"Campo {field_name} ya no existe en template",
						"field_name": field_name,
					}
				)

	except Exception as e:
		conflicts.append(
			{
				"type": "template_validation_error",
				"severity": "Media",
				"description": f"Error validando template: {e!s}",
			}
		)

	return conflicts


def get_configuration_fields_by_type(config, field_types):
	"""
	Obtener campos de configuración por tipo.

	Args:
	    config (Document): Entity Configuration
	    field_types (list): Lista de tipos de campo a buscar

	Returns:
	    list: Campos que coinciden con los tipos
	"""

	return [
		field
		for field in config.configuration_fields
		if field.field_type.lower() in [t.lower() for t in field_types]
	]


def get_configuration_fields_by_name_pattern(config, patterns):
	"""
	Obtener campos de configuración por patrón en el nombre.

	Args:
	    config (Document): Entity Configuration
	    patterns (list): Lista de patrones a buscar en nombres de campo

	Returns:
	    list: Campos que coinciden con algún patrón
	"""

	matching_fields = []

	for field in config.configuration_fields:
		field_name_lower = field.field_name.lower()
		field_label_lower = (field.field_label or "").lower()

		for pattern in patterns:
			pattern_lower = pattern.lower()
			if pattern_lower in field_name_lower or pattern_lower in field_label_lower:
				matching_fields.append(field)
				break

	return matching_fields


def compare_schedule_fields(config1, config2, schedule_fields):
	"""
	Comparar campos de horarios entre dos configuraciones.

	Args:
	    config1 (Document): Primera configuración
	    config2 (Document): Segunda configuración
	    schedule_fields (list): Campos de horarios a comparar

	Returns:
	    dict: Detalles del conflicto si existe, None en caso contrario
	"""

	config2_fields = {f.field_name: f.field_value for f in config2.configuration_fields}

	conflicts = []

	for field in schedule_fields:
		field_name = field.field_name
		field_value1 = field.field_value
		field_value2 = config2_fields.get(field_name)

		if field_value1 and field_value2 and field_value1 == field_value2:
			conflicts.append(
				{
					"field_name": field_name,
					"field_label": field.field_label,
					"conflicting_value": field_value1,
				}
			)

	return conflicts if conflicts else None


@frappe.whitelist()
def get_conflict_summary(filters=None):
	"""
	Obtener resumen de conflictos en el sistema.

	Args:
	    filters (dict): Filtros opcionales para configuraciones

	Returns:
	    dict: Resumen de conflictos por tipo y severidad
	"""

	try:
		# Obtener configuraciones activas
		config_filters = {"configuration_status": ["in", ["Pendiente Aprobación", "Aprobado"]]}

		if filters:
			config_filters.update(filters)

		configurations = frappe.get_all("Entity Configuration", filters=config_filters, fields=["name"])

		summary = {
			"total_configurations": len(configurations),
			"configurations_with_conflicts": 0,
			"conflicts_by_type": {},
			"conflicts_by_severity": {"Alta": 0, "Media": 0, "Baja": 0},
		}

		for config in configurations:
			conflicts = detect_configuration_conflicts(config["name"])

			if conflicts:
				summary["configurations_with_conflicts"] += 1

				for conflict in conflicts:
					conflict_type = conflict.get("type", "unknown")
					severity = conflict.get("severity", "Baja")

					# Contar por tipo
					if conflict_type not in summary["conflicts_by_type"]:
						summary["conflicts_by_type"][conflict_type] = 0
					summary["conflicts_by_type"][conflict_type] += 1

					# Contar por severidad
					summary["conflicts_by_severity"][severity] += 1

		return summary

	except Exception as e:
		frappe.log_error(f"Error generando resumen de conflictos: {e!s}", "Conflict Detection API")
		return {}
