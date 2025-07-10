# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ComplianceRequirementType(Document):
	def validate(self):
		"""Validaciones del tipo de requerimiento de cumplimiento"""
		self.validate_completion_days()
		self.validate_penalty_requirements()

	def validate_completion_days(self):
		"""Validar días estimados de cumplimiento"""
		if self.estimated_completion_days <= 0:
			frappe.throw("Los días estimados de cumplimiento deben ser positivos.")

	def validate_penalty_requirements(self):
		"""Validar requisitos de penalización"""
		if self.priority_level == "Crítica" and not self.penalty_type:
			frappe.throw("Los requerimientos críticos deben tener tipo de penalización definido.")

		if self.penalty_type in ["Suspensión", "Revocación", "Proceso Legal"]:
			if not self.requires_approval:
				frappe.throw("Las penalizaciones severas requieren aprobación.")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Compliance Rule usando este tipo"""
		if frappe.db.count("Compliance Rule", filters={"requirement_type": olddn}) > 0:
			frappe.throw(
				"No se puede renombrar. Hay reglas de cumplimiento usando este tipo de requerimiento."
			)

	def on_trash(self):
		"""Prevenir eliminación si hay Compliance Rule usando este tipo"""
		if frappe.db.count("Compliance Rule", filters={"requirement_type": self.name}) > 0:
			frappe.throw(
				"No se puede eliminar. Hay reglas de cumplimiento usando este tipo de requerimiento."
			)

	def get_priority_score(self):
		"""Obtener puntaje numérico de prioridad"""
		priority_scores = {"Baja": 1, "Media": 2, "Alta": 3, "Crítica": 4}
		return priority_scores.get(self.priority_level, 0)

	def get_completion_urgency(self):
		"""Obtener urgencia de cumplimiento"""
		if self.estimated_completion_days <= 7:
			return "Inmediata"
		elif self.estimated_completion_days <= 30:
			return "Urgente"
		elif self.estimated_completion_days <= 90:
			return "Normal"
		else:
			return "Planificada"

	def get_requirements_summary(self):
		"""Obtener resumen de requerimientos"""
		summary = []
		if self.requires_documentation:
			summary.append("Documentación")
		if self.requires_approval:
			summary.append("Aprobación")
		if self.penalty_type:
			summary.append(f"Penalización: {self.penalty_type}")

		return summary if summary else ["Sin requerimientos especiales"]
