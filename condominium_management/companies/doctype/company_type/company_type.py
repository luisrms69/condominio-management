# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class CompanyType(Document):
	def before_naming(self):
		"""Hook antes de naming - generar código automático"""
		self.generate_type_code()

	def before_save(self):
		"""Hook antes de guardar - validaciones"""
		self.validate_management_type()

	def generate_type_code(self):
		"""Generar código único basado en el nombre"""
		if not self.type_code and self.type_name:
			# Limpiar nombre para código
			clean_name = re.sub(r"[^A-Za-z0-9\s]", "", self.type_name)
			words = clean_name.upper().split()

			if len(words) >= 2:
				# Tomar primeras 2-3 letras de cada palabra
				code = "".join([word[:3] for word in words[:2]])
			else:
				# Una sola palabra, tomar primeras 6 letras
				code = words[0][:6] if words else "TYPE"

			# Verificar unicidad
			counter = 1
			original_code = code
			while frappe.db.exists("Company Type", code):
				code = f"{original_code}{counter}"
				counter += 1

			self.type_code = code

	def validate_management_type(self):
		"""Validar configuración de tipo de administración"""
		if self.is_management_type:
			# Verificar que no hay conflictos con Company existentes
			pass  # Implementar si es necesario

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay Company usando este tipo"""
		if frappe.db.count("Company", filters={"company_type": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay empresas usando este tipo.")

	def on_trash(self):
		"""Prevenir eliminación si hay Company usando este tipo"""
		if frappe.db.count("Company", filters={"company_type": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay empresas usando este tipo.")
