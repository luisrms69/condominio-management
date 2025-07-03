# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConfigurationField(Document):
	"""
	Campo individual de configuración para templates.

	Funcionalidades principales:
	- Almacenar valores específicos para campos de templates
	- Mantener metadata del campo (tipo, etiqueta, requerido)
	- Tracking de cambios y auditoría
	- Validación de tipos de datos

	Parámetros importantes:
	    field_name (Data): Nombre interno del campo
	    field_label (Data): Etiqueta visible del campo
	    field_type (Select): Tipo de dato del campo
	    field_value (Long Text): Valor actual del campo
	    is_required (Check): Si el campo es obligatorio

	Ejemplo de uso:
	    field = frappe.new_doc("Configuration Field")
	    field.field_name = "pool_capacity"
	    field.field_label = "Capacidad de la Piscina"
	    field.field_type = "Int"
	    field.field_value = "50"
	    field.save()
	"""

	def validate(self):
		"""
		Validar campo de configuración.

		Verifica tipo de dato y valores requeridos.
		"""
		self.validate_field_value_type()
		self.validate_required_field()
		self.update_audit_fields()

	def validate_field_value_type(self):
		"""
		Validar que el valor del campo coincida con el tipo especificado.

		Raises:
		    ValidationError: Si el valor no es compatible con el tipo
		"""
		if not self.field_value:
			return

		try:
			if self.field_type == "Int":
				int(self.field_value)
			elif self.field_type == "Float":
				float(self.field_value)
			elif self.field_type == "Date":
				frappe.utils.getdate(self.field_value)
			elif self.field_type == "Datetime":
				frappe.utils.get_datetime(self.field_value)
			elif self.field_type == "Check":
				if self.field_value.lower() not in ["0", "1", "true", "false"]:
					raise ValueError("Invalid boolean value")

		except (ValueError, TypeError):
			frappe.throw(
				frappe._("Valor '{0}' no es válido para tipo de campo '{1}'").format(
					self.field_value, self.field_type
				)
			)

	def validate_required_field(self):
		"""
		Validar que campos requeridos tengan valor.

		Raises:
		    ValidationError: Si campo requerido está vacío
		"""
		if self.is_required and not self.field_value:
			frappe.throw(
				frappe._("Campo requerido '{0}' no puede estar vacío").format(
					self.field_label or self.field_name
				)
			)

	def update_audit_fields(self):
		"""
		Actualizar campos de auditoría automáticamente.

		Registra quién y cuándo se modificó el campo.
		"""
		if self.is_new():
			self.created_by = frappe.session.user

		if self.has_value_changed("field_value"):
			self.last_updated = frappe.utils.now()
			self.updated_by = frappe.session.user

	def get_formatted_value(self):
		"""
		Obtener valor formateado según el tipo de campo.

		Returns:
		    str: Valor formateado para mostrar
		"""
		if not self.field_value:
			return ""

		try:
			if self.field_type == "Date":
				date_val = frappe.utils.getdate(self.field_value)
				return frappe.utils.formatdate(date_val)
			elif self.field_type == "Datetime":
				datetime_val = frappe.utils.get_datetime(self.field_value)
				return frappe.utils.format_datetime(datetime_val)
			elif self.field_type == "Float":
				return frappe.utils.fmt_money(float(self.field_value))
			elif self.field_type == "Check":
				return "Sí" if self.field_value in ["1", "true", "True"] else "No"
			else:
				return str(self.field_value)

		except:
			return str(self.field_value)

	def get_typed_value(self):
		"""
		Obtener valor convertido al tipo apropiado.

		Returns:
		    object: Valor convertido al tipo de Python correspondiente
		"""
		if not self.field_value:
			return None

		try:
			if self.field_type == "Int":
				return int(self.field_value)
			elif self.field_type == "Float":
				return float(self.field_value)
			elif self.field_type == "Date":
				return frappe.utils.getdate(self.field_value)
			elif self.field_type == "Datetime":
				return frappe.utils.get_datetime(self.field_value)
			elif self.field_type == "Check":
				return self.field_value in ["1", "true", "True"]
			else:
				return str(self.field_value)

		except:
			return self.field_value
