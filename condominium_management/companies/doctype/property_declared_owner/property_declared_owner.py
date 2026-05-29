# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document


class PropertyDeclaredOwner(Document):
	def validate(self):
		self.validate_percentage()
		self.validate_owner_info()

	def validate_percentage(self):
		if self.ownership_percentage <= 0:
			frappe.throw(_("El porcentaje de titularidad debe ser mayor a 0"))
		if self.ownership_percentage > 100:
			frappe.throw(_("El porcentaje de titularidad no puede exceder 100%"))

	def validate_owner_info(self):
		if not self.owner_name or not self.owner_name.strip():
			frappe.throw(_("El nombre del propietario es requerido"))
		# owner_id es opcional — validar formato solo si tiene valor
		if self.owner_id and self.owner_id.strip():
			self.validate_owner_id_format()

	def validate_owner_id_format(self):
		"""Validar formato RFC/CURP mexicano — advertencia no bloqueante"""
		owner_id_clean = self.owner_id.strip().upper()
		rfc_moral = re.compile(r"^[A-ZÑ&]{3}\d{6}[A-Z\d]{3}$")
		rfc_fisica = re.compile(r"^[A-ZÑ&]{4}\d{6}[A-Z\d]{3}$")
		curp = re.compile(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$")
		if self.owner_type == "Persona Moral":
			valid = bool(rfc_moral.match(owner_id_clean))
		else:
			valid = bool(rfc_fisica.match(owner_id_clean)) or bool(curp.match(owner_id_clean))
		if not valid:
			frappe.msgprint(
				_("El identificador '{0}' no tiene el formato esperado de RFC o CURP mexicano").format(
					self.owner_id
				),
				indicator="orange",
				alert=True,
			)

	def get_owner_display_name(self):
		if self.owner_id:
			return f"{self.owner_name} ({self.owner_id})"
		return self.owner_name

	def get_ownership_display(self):
		return f"{self.get_owner_display_name()} - {self.ownership_percentage}%"
