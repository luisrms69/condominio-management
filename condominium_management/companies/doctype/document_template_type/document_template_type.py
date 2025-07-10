# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DocumentTemplateType(Document):
	def validate(self):
		"""Validaciones del tipo de plantilla"""
		self.validate_legal_requirements()
		self.validate_retention_period()

	def validate_legal_requirements(self):
		"""Validar requisitos legales"""
		if self.is_legal_document:
			# Documentos legales deben tener firma
			if not self.requires_signature:
				frappe.throw("Los documentos legales deben requerir firma.")

			# Documentos legales deben tener período de retención mayor
			if self.retention_period_days < 1095:  # 3 años
				frappe.throw(
					"Los documentos legales deben tener período de retención mínimo de 3 años (1095 días)."
				)

	def validate_retention_period(self):
		"""Validar período de retención"""
		if self.retention_period_days <= 0:
			frappe.throw("El período de retención debe ser positivo.")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Document Template usando este tipo"""
		if frappe.db.count("Document Template", filters={"template_type": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay plantillas usando este tipo.")

	def on_trash(self):
		"""Prevenir eliminación si hay Document Template usando este tipo"""
		if frappe.db.count("Document Template", filters={"template_type": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay plantillas usando este tipo.")

	def get_requirements_checklist(self):
		"""Obtener lista de requerimientos"""
		requirements = []
		if self.requires_signature:
			requirements.append("Requiere Firma")
		if self.requires_notarization:
			requirements.append("Requiere Notarización")
		if self.is_legal_document:
			requirements.append("Es Documento Legal")
		return requirements

	def get_retention_years(self):
		"""Obtener período de retención en años"""
		return round(self.retention_period_days / 365.25, 1)
