# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FeeComponent(Document):
	"""Componente individual de una estructura de cuotas"""

	def validate(self):
		"""Validaciones del componente"""
		self.validate_amount_fields()
		self.validate_component_name()

	def validate_amount_fields(self):
		"""Validar que se especifique monto o porcentaje según el tipo"""
		if self.amount_type == "Fijo" and not self.amount:
			frappe.throw("El monto es obligatorio para componentes de tipo Fijo")

		if self.amount_type == "Porcentaje" and not self.percentage:
			frappe.throw("El porcentaje es obligatorio para componentes de tipo Porcentaje")

		if self.amount_type == "Fijo" and self.amount <= 0:
			frappe.throw("El monto debe ser mayor a 0")

		if self.amount_type == "Porcentaje" and (self.percentage <= 0 or self.percentage > 100):
			frappe.throw("El porcentaje debe estar entre 0 y 100")

	def validate_component_name(self):
		"""Validar nombre del componente"""
		if not self.component_name or len(self.component_name.strip()) < 3:
			frappe.throw("El nombre del componente debe tener al menos 3 caracteres")
