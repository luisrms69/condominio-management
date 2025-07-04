# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Entity Detection API para Document Generation Module
===================================================

APIs para detección automática de entidades que requieren configuración
de documentos y asignación automática de templates.
"""

import frappe
from frappe import _


@frappe.whitelist()
def auto_detect_configuration_needed(doc, entity_config):
	"""
	Detectar automáticamente si documento requiere configuración de templates.

	Args:
	    doc (Document): Documento que se insertó/actualizó
	    entity_config (dict): Configuración del tipo de entidad

	Returns:
	    dict: Resultado de la detección y configuración creada
	"""

	try:
		# Detectar subtipo de entidad si está configurado
		entity_subtype = None
		if entity_config.get("detection_field"):
			detection_field = entity_config["detection_field"]
			if hasattr(doc, detection_field):
				entity_subtype = str(getattr(doc, detection_field))

		# Buscar regla de auto-asignación
		registry = frappe.get_single("Master Template Registry")
		assignment_rule = registry.get_assignment_rule_for_entity(doc.doctype, entity_subtype)

		if not assignment_rule:
			# No hay regla automática - crear configuración básica
			return create_basic_configuration(doc, entity_subtype)

		# Crear configuración con template asignado automáticamente
		return create_auto_assigned_configuration(doc, entity_subtype, assignment_rule)

	except Exception as e:
		frappe.log_error(
			f"Error en auto-detección para {doc.doctype} {doc.name}: {e!s}", "Entity Detection API"
		)
		return {"success": False, "error": str(e)}


def create_basic_configuration(doc, entity_subtype=None):
	"""
	Crear configuración básica sin template asignado.

	Args:
	    doc (Document): Documento origen
	    entity_subtype (str): Subtipo detectado

	Returns:
	    dict: Resultado de la creación
	"""

	# Verificar si ya existe configuración
	existing = frappe.db.exists(
		"Entity Configuration", {"source_doctype": doc.doctype, "source_docname": doc.name}
	)

	if existing:
		return {"success": True, "existing": True, "configuration_name": existing}

	# Crear nueva configuración
	config = frappe.get_doc(
		{
			"doctype": "Entity Configuration",
			"configuration_name": f"Config-{doc.doctype}-{doc.name}",
			"source_doctype": doc.doctype,
			"source_docname": doc.name,
			"entity_subtype": entity_subtype or "",
			"configuration_status": "Borrador",
			"auto_assigned": 0,
			"approval_required": 1,
		}
	)

	config.insert(ignore_permissions=True)

	return {
		"success": True,
		"created": True,
		"configuration_name": config.name,
		"needs_manual_template": True,
	}


def create_auto_assigned_configuration(doc, entity_subtype, assignment_rule):
	"""
	Crear configuración con template asignado automáticamente.

	Args:
	    doc (Document): Documento origen
	    entity_subtype (str): Subtipo detectado
	    assignment_rule (dict): Regla de asignación automática

	Returns:
	    dict: Resultado de la creación
	"""

	# Verificar si ya existe configuración
	existing = frappe.db.exists(
		"Entity Configuration", {"source_doctype": doc.doctype, "source_docname": doc.name}
	)

	if existing:
		return {"success": True, "existing": True, "configuration_name": existing}

	# Obtener template asignado
	registry = frappe.get_single("Master Template Registry")
	template = registry.get_template_by_code(assignment_rule["target_template"])

	if not template:
		return create_basic_configuration(doc, entity_subtype)

	# Crear configuración con template
	config = frappe.get_doc(
		{
			"doctype": "Entity Configuration",
			"configuration_name": f"Config-{doc.doctype}-{doc.name}",
			"source_doctype": doc.doctype,
			"source_docname": doc.name,
			"entity_subtype": entity_subtype or "",
			"applied_template": assignment_rule["target_template"],
			"target_document_type": template.get("target_document"),
			"target_section": template.get("target_section"),
			"configuration_status": "Pendiente Aprobación",
			"auto_assigned": 1,
			"approval_required": 1,
		}
	)

	# Crear campos de configuración desde template
	populate_configuration_fields(config, template, doc)

	config.insert(ignore_permissions=True)

	# Notificar auto-asignación exitosa
	frappe.msgprint(
		_("Configuración creada automáticamente con template {0}").format(assignment_rule["target_template"]),
		indicator="green",
	)

	return {
		"success": True,
		"created": True,
		"configuration_name": config.name,
		"template_assigned": assignment_rule["target_template"],
		"auto_assigned": True,
	}


def populate_configuration_fields(config, template, source_doc):
	"""
	Poblar campos de configuración desde template y documento origen.

	Args:
	    config (Document): Entity Configuration a poblar
	    template (dict): Template con definición de campos
	    source_doc (Document): Documento origen para extraer valores
	"""

	template_fields = template.get("template_fields", [])

	for field_def in template_fields:
		field_value = ""

		# Intentar obtener valor del documento origen
		source_field = field_def.get("source_field")
		if source_field and hasattr(source_doc, source_field):
			field_value = str(getattr(source_doc, source_field))

		# Usar valor por defecto si no hay valor del origen
		if not field_value:
			field_value = field_def.get("default_value", "")

		config.append(
			"configuration_fields",
			{
				"field_name": field_def["field_name"],
				"field_label": field_def.get("field_label", field_def["field_name"]),
				"field_type": field_def.get("field_type", "Data"),
				"field_value": field_value,
				"is_required": field_def.get("is_required", 0),
				"is_active": 1,
				"created_by": frappe.session.user,
				"last_updated": frappe.utils.now(),
			},
		)


@frappe.whitelist()
def get_available_templates_for_entity(doctype, entity_subtype=None):
	"""
	Obtener templates disponibles para un tipo de entidad.

	Args:
	    doctype (str): Tipo de documento
	    entity_subtype (str): Subtipo específico (opcional)

	Returns:
	    list: Lista de templates disponibles
	"""

	try:
		registry = frappe.get_single("Master Template Registry")
		available_templates = []

		# Buscar templates que coincidan con el tipo de entidad
		for template in registry.infrastructure_templates:
			if template.infrastructure_type == doctype or not template.infrastructure_type:
				# Verificar si coincide con subtipo
				if entity_subtype and template.infrastructure_subtype:
					if template.infrastructure_subtype.lower() == entity_subtype.lower():
						available_templates.append(template.as_dict())
				else:
					available_templates.append(template.as_dict())

		return available_templates

	except Exception as e:
		frappe.log_error(f"Error obteniendo templates para {doctype}: {e!s}", "Entity Detection API")
		return []


@frappe.whitelist()
def preview_template_content(template_code, sample_data=None):
	"""
	Preview del contenido renderizado de un template.

	Args:
	    template_code (str): Código del template
	    sample_data (dict): Datos de ejemplo para renderizar

	Returns:
	    dict: Contenido renderizado y metadatos
	"""

	try:
		registry = frappe.get_single("Master Template Registry")
		template = registry.get_template_by_code(template_code)

		if not template:
			return {"success": False, "error": "Template no encontrado"}

		# Usar datos de ejemplo si no se proporcionan
		if not sample_data:
			sample_data = generate_sample_data_for_template(template)

		# Renderizar contenido
		rendered_content = ""
		if template.get("template_content"):
			try:
				rendered_content = frappe.render_template(template["template_content"], sample_data)
			except Exception as e:
				return {"success": False, "error": f"Error renderizando template: {e!s}"}

		return {
			"success": True,
			"template_code": template_code,
			"template_name": template.get("template_name"),
			"rendered_content": rendered_content,
			"sample_data": sample_data,
			"template_fields": template.get("template_fields", []),
		}

	except Exception as e:
		frappe.log_error(f"Error en preview de template {template_code}: {e!s}", "Entity Detection API")
		return {"success": False, "error": str(e)}


def generate_sample_data_for_template(template):
	"""
	Generar datos de ejemplo para un template.

	Args:
	    template (dict): Definición del template

	Returns:
	    dict: Datos de ejemplo
	"""

	sample_data = {
		"doc": {"name": "SAMPLE-001", "creation": frappe.utils.now(), "modified": frappe.utils.now()}
	}

	# Generar valores de ejemplo para campos del template
	template_fields = template.get("template_fields", [])
	for field_def in template_fields:
		field_name = field_def["field_name"]
		field_type = field_def.get("field_type", "Data")

		if field_type == "Data":
			sample_data[field_name] = f"Ejemplo {field_name}"
		elif field_type == "Int":
			sample_data[field_name] = 100
		elif field_type == "Float":
			sample_data[field_name] = 99.99
		elif field_type == "Date":
			sample_data[field_name] = frappe.utils.today()
		elif field_type == "Datetime":
			sample_data[field_name] = frappe.utils.now()
		elif field_type == "Select":
			sample_data[field_name] = "Opción 1"
		else:
			sample_data[field_name] = "Valor de ejemplo"

	return sample_data


@frappe.whitelist()
def validate_template_syntax(template_content, field_definitions=None):
	"""
	Validar sintaxis de template Jinja2.

	Args:
	    template_content (str): Contenido del template
	    field_definitions (list): Definiciones de campos para validación

	Returns:
	    dict: Resultado de la validación
	"""

	try:
		# Crear datos de prueba para validación
		test_data = {}
		if field_definitions:
			for field in field_definitions:
				test_data[field["field_name"]] = "test_value"

		# Intentar renderizar template
		frappe.render_template(template_content, test_data)

		return {"success": True, "valid": True, "message": "Sintaxis válida"}

	except Exception as e:
		return {"success": True, "valid": False, "error": str(e), "message": f"Error de sintaxis: {e!s}"}
