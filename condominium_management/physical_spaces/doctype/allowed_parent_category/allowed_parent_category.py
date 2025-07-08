# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AllowedParentCategory(Document):
	def validate(self):
		"""Validar configuración de categoría padre permitida"""
		self.validate_category_exists()
		self.validate_no_self_reference()

	def validate_category_exists(self):
		"""Validar que la categoría padre existe y está activa"""
		if self.parent_category:
			category = frappe.get_doc("Space Category", self.parent_category)
			if not category.is_active:
				frappe.throw(f"La categoría padre '{self.parent_category}' no está activa")

	def validate_no_self_reference(self):
		"""Validar que una categoría no se referencie a sí misma como padre"""
		# Esta validación se hará a nivel de Space Category cuando se asigne
		pass
