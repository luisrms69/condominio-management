# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PropertyUsageType(Document):
	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Property Registry usando este tipo"""
		if frappe.db.count("Property Registry", filters={"space_usage": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay propiedades usando este tipo de uso.")

	def on_trash(self):
		"""Prevenir eliminación si hay Property Registry usando este tipo"""
		if frappe.db.count("Property Registry", filters={"space_usage": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay propiedades usando este tipo de uso.")
