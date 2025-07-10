# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JurisdictionLevel(Document):
	def validate(self):
		"""Validaciones del nivel de jurisdicción"""
		self.validate_hierarchy_order()
		self.validate_geographic_scope()

	def validate_hierarchy_order(self):
		"""Validar orden jerárquico único y válido"""
		if self.hierarchy_order <= 0:
			frappe.throw("El orden jerárquico debe ser un número positivo.")

		# Verificar que no existe otro nivel con el mismo orden
		existing = frappe.db.get_value(
			"Jurisdiction Level", filters={"hierarchy_order": self.hierarchy_order, "name": ["!=", self.name]}
		)
		if existing:
			frappe.throw(f"Ya existe un nivel con orden jerárquico {self.hierarchy_order}: {existing}")

	def validate_geographic_scope(self):
		"""Validar ámbito geográfico según orden jerárquico"""
		# Validaciones básicas de coherencia
		if self.geographic_scope == "Nacional" and self.hierarchy_order > 1:
			frappe.throw("El ámbito Nacional debe tener orden jerárquico 1.")

		if self.geographic_scope == "Local" and self.hierarchy_order < 3:
			frappe.throw("El ámbito Local debe tener orden jerárquico 3 o mayor.")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Compliance Rule usando este nivel"""
		if frappe.db.count("Compliance Rule", filters={"jurisdiction_level": olddn}) > 0:
			frappe.throw(
				"No se puede renombrar. Hay reglas de cumplimiento usando este nivel de jurisdicción."
			)

	def on_trash(self):
		"""Prevenir eliminación si hay Compliance Rule usando este nivel"""
		if frappe.db.count("Compliance Rule", filters={"jurisdiction_level": self.name}) > 0:
			frappe.throw(
				"No se puede eliminar. Hay reglas de cumplimiento usando este nivel de jurisdicción."
			)

	def get_authority_description(self):
		"""Obtener descripción de autoridad"""
		authorities = []
		if self.can_issue_permits:
			authorities.append("Emisión de Permisos")
		if self.can_enforce_laws:
			authorities.append("Aplicación de Leyes")

		if authorities:
			return ", ".join(authorities)
		else:
			return "Sin autoridades específicas"

	def get_jurisdiction_hierarchy(self):
		"""Obtener jerarquía de jurisdicciones"""
		hierarchy_map = {1: "Primer Nivel", 2: "Segundo Nivel", 3: "Tercer Nivel", 4: "Cuarto Nivel"}
		return hierarchy_map.get(self.hierarchy_order, f"Nivel {self.hierarchy_order}")
