# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TemplateAutoAssignmentRule(Document):
	"""
	Regla para asignación automática de templates.

	Funcionalidades principales:
	- Definir criterios para auto-asignación de templates
	- Configurar prioridad entre reglas
	- Soporte para tipos y subtipos de entidades

	Parámetros importantes:
	    entity_type (Data): Tipo principal de entidad
	    entity_subtype (Data): Subtipo específico (opcional)
	    target_template (Data): Código del template a asignar
	    priority (Int): Prioridad de la regla (mayor número = mayor prioridad)

	Ejemplo de uso:
	    rule = frappe.new_doc("Template Auto Assignment Rule")
	    rule.entity_type = "Amenity"
	    rule.entity_subtype = "piscina"
	    rule.target_template = "POOL_AREA"
	    rule.save()
	"""

	pass
