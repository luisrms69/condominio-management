# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PolicyCategory(Document):
	def validate(self):
		"""Validaciones de la categoría de política"""
		self.validate_chapter_mapping()

	def validate_chapter_mapping(self):
		"""Validar formato del mapeo de capítulos"""
		if self.chapter_mapping:
			# Validar formato básico (ej: XVIII-XX)
			if not self.chapter_mapping.replace("-", "").replace(",", "").replace(" ", "").isalnum():
				frappe.msgprint(
					"El formato de capítulos relacionados debe usar números romanos o arábigos separados por guiones."
				)

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Condominium Policy usando esta categoría"""
		if frappe.db.count("Condominium Policy", filters={"policy_category": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay políticas usando esta categoría.")

	def on_trash(self):
		"""Prevenir eliminación si hay Condominium Policy usando esta categoría"""
		if frappe.db.count("Condominium Policy", filters={"policy_category": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay políticas usando esta categoría.")

	def get_related_chapters(self):
		"""Obtener lista de capítulos relacionados"""
		if self.chapter_mapping:
			return [chapter.strip() for chapter in self.chapter_mapping.split(",") if chapter.strip()]
		return []
