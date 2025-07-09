# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyStatusType(Document):
	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Property Registry usando este estado"""
		if frappe.db.count("Property Registry", filters={"property_status": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay propiedades usando este estado.")

	def on_trash(self):
		"""Prevenir eliminación si hay Property Registry usando este estado"""
		if frappe.db.count("Property Registry", filters={"property_status": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay propiedades usando este estado.")
