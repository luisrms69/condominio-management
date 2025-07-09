# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EnforcementLevel(Document):
	def validate(self):
		"""Validaciones del nivel de aplicación"""
		self.validate_severity_order()

	def validate_severity_order(self):
		"""Validar orden de severidad único y válido"""
		if self.severity_order <= 0:
			frappe.throw("El orden de severidad debe ser un número positivo.")

		# Verificar que no existe otro nivel con el mismo orden
		existing = frappe.db.get_value(
			"Enforcement Level", filters={"severity_order": self.severity_order, "name": ["!=", self.name]}
		)
		if existing:
			frappe.throw(f"Ya existe un nivel con orden de severidad {self.severity_order}: {existing}")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Condominium Policy usando este nivel"""
		if frappe.db.count("Condominium Policy", filters={"enforcement_level": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay políticas usando este nivel de aplicación.")

	def on_trash(self):
		"""Prevenir eliminación si hay Condominium Policy usando este nivel"""
		if frappe.db.count("Condominium Policy", filters={"enforcement_level": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay políticas usando este nivel de aplicación.")

	def get_severity_level(self):
		"""Obtener descripción del nivel de severidad"""
		if self.severity_order == 1:
			return "Muy Bajo"
		elif self.severity_order <= 25:
			return "Bajo"
		elif self.severity_order <= 50:
			return "Medio"
		elif self.severity_order <= 75:
			return "Alto"
		else:
			return "Muy Alto"
