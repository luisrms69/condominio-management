# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class InfrastructureTemplateDefinition(Document):
	"""
	Definición individual de template para tipo de infraestructura.

	Funcionalidades principales:
	- Definición de contenido usando sintaxis Jinja2
	- Campos variables configurables por template
	- Asignación a documentos y secciones específicas
	- Validación de sintaxis de template

	Parámetros importantes:
	    template_code (Data): Código único identificador del template
	    template_name (Data): Nombre descriptivo del template
	    infrastructure_type (Select): Tipo principal de infraestructura
	    infrastructure_subtype (Data): Subtipo específico para detección
	    target_document (Select): Documento donde se aplicará el template
	    template_content (Long Text): Contenido del template en Jinja2

	Errores comunes:
	    ValidationError: Sintaxis Jinja2 inválida o campos requeridos faltantes
	    Warning: Template referencia campos no definidos

	Ejemplo de uso:
	    template = frappe.new_doc("Infrastructure Template Definition")
	    template.template_code = "POOL_AREA"
	    template.template_name = "Área de Piscina"
	    template.save()
	"""

	def validate(self):
		"""
		Validar definición del template.

		Verifica sintaxis Jinja2 y consistencia de campos.
		"""
		self.validate_template_syntax()
		self.validate_field_references()

	def validate_template_syntax(self):
		"""
		Validar sintaxis Jinja2 del contenido del template.

		Raises:
		    ValidationError: Si la sintaxis Jinja2 es inválida
		"""
		if not self.template_content:
			return

		try:
			# Usar el validador nativo de Frappe para templates
			frappe.render_template(self.template_content, {})
		except Exception as e:
			frappe.throw(_("Error en sintaxis del template: {0}").format(str(e)))

	def validate_field_references(self):
		"""
		Validar que campos referenciados en template estén definidos.

		Verifica que variables usadas en template_content tengan
		correspondencia en template_fields.
		"""
		if not self.template_content or not self.template_fields:
			return

		# Extraer variables del template (simplificado)
		import re

		template_vars = re.findall(r"\{\{\s*(\w+)", self.template_content)
		defined_fields = [field.field_name for field in self.template_fields]

		for var in template_vars:
			if var not in defined_fields and var not in ["doc", "frappe"]:
				frappe.msgprint(
					_("Variable '{0}' usada en template pero no definida en campos").format(var),
					indicator="orange",
				)

	def get_rendered_content(self, context=None):
		"""
		Obtener contenido renderizado del template.

		Args:
		    context (dict): Contexto con valores para variables del template

		Returns:
		    str: Contenido renderizado o template original si hay errores
		"""
		if not self.template_content:
			return ""

		if not context:
			context = {}

		try:
			return frappe.render_template(self.template_content, context)
		except Exception as e:
			frappe.log_error(f"Error renderizando template {self.template_code}: {e!s}")
			return self.template_content  # Retornar contenido original en caso de error
