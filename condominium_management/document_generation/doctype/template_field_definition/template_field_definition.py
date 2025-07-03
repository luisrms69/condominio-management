# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TemplateFieldDefinition(Document):
	"""
	Definición de campo variable para templates.

	Funcionalidades principales:
	- Definir campos dinámicos para templates
	- Configurar validaciones y valores por defecto
	- Mapeo automático desde campos del documento origen

	Parámetros importantes:
	    field_name (Data): Nombre interno del campo
	    field_label (Data): Etiqueta visible del campo
	    field_type (Select): Tipo de dato del campo
	    is_required (Check): Si el campo es obligatorio
	    source_field (Data): Campo origen para auto-completar

	Ejemplo de uso:
	    field = frappe.new_doc("Template Field Definition")
	    field.field_name = "pool_capacity"
	    field.field_label = "Capacidad de la Piscina"
	    field.field_type = "Int"
	    field.save()
	"""

	pass
