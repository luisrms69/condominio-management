# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PropertyCopropiedad(Document):
	def validate(self):
		"""Validaciones de la copropiedad"""
		self.validate_percentage()
		self.validate_owner_info()

	def validate_percentage(self):
		"""Validar porcentaje de copropiedad"""
		if self.copropiedad_percentage <= 0:
			frappe.throw(_("El porcentaje de copropiedad debe ser mayor a 0"))

		if self.copropiedad_percentage > 100:
			frappe.throw(_("El porcentaje de copropiedad no puede exceder 100%"))

	def validate_owner_info(self):
		"""Validar información del propietario"""
		if not self.owner_name or not self.owner_name.strip():
			frappe.throw(_("El nombre del propietario es requerido"))

		if not self.owner_id or not self.owner_id.strip():
			frappe.throw(_("La identificación del propietario es requerida"))

		# Validar formato de identificación según tipo
		if not self.validate_owner_id_format():
			frappe.throw(_("Formato de identificación inválido para {0}").format(self.owner_name))

	def validate_owner_id_format(self):
		"""Validar formato de identificación según tipo"""
		if self.owner_type == "Persona Natural":
			# Validar cédula colombiana (básico)
			return self.owner_id.isdigit() and len(self.owner_id) >= 6 and len(self.owner_id) <= 11
		elif self.owner_type == "Persona Jurídica":
			# Validar NIT colombiano (básico)
			return len(self.owner_id) >= 9 and len(self.owner_id) <= 11
		return False

	def get_owner_display_name(self):
		"""Obtener nombre de display del propietario"""
		if self.owner_type == "Persona Natural":
			return f"{self.owner_name} (C.C. {self.owner_id})"
		else:
			return f"{self.owner_name} (NIT {self.owner_id})"

	def get_ownership_display(self):
		"""Obtener display de la propiedad"""
		return f"{self.get_owner_display_name()} - {self.copropiedad_percentage}%"
