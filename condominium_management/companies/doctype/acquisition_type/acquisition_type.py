# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AcquisitionType(Document):
	def validate(self):
		"""Validaciones del tipo de adquisición"""
		self.validate_notary_requirements()

	def validate_notary_requirements(self):
		"""Validar requerimientos de notario"""
		if self.requires_notary and not self.required_documents:
			frappe.msgprint("Se recomienda especificar los documentos requeridos cuando se requiere notario.")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Property Registry usando este tipo"""
		if frappe.db.count("Property Registry", filters={"acquisition_type": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay propiedades usando este tipo de adquisición.")

	def on_trash(self):
		"""Prevenir eliminación si hay Property Registry usando este tipo"""
		if frappe.db.count("Property Registry", filters={"acquisition_type": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay propiedades usando este tipo de adquisición.")

	def get_document_checklist(self):
		"""Obtener lista de documentos requeridos"""
		if self.required_documents:
			return [doc.strip() for doc in self.required_documents.split("\n") if doc.strip()]
		return []
