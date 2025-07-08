# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class PhysicalSpace(Document):
	def before_naming(self):
		"""Hook antes de establecer nombre - generar código"""
		self.generate_space_code()

	def before_save(self):
		"""Hook antes de guardar - validar jerarquía"""
		self.validate_hierarchy()
		self.update_hierarchy_info()

	def generate_space_code(self):
		"""Generar código único del espacio si no existe"""
		if not self.space_code:
			# Generar código basado en nombre y timestamp
			import re
			import unicodedata

			# Normalizar texto removiendo acentos
			normalized = unicodedata.normalize("NFD", self.space_name)
			ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

			# Crear código base
			base_code = re.sub(r"[^A-Za-z0-9]", "", ascii_text)[:10].upper()
			timestamp = frappe.utils.cstr(frappe.utils.now_datetime().strftime("%m%d%H%M"))
			self.space_code = f"{base_code}-{timestamp}"

	def validate_hierarchy(self):
		"""Validaciones críticas para jerarquía híbrida"""
		# 1. Un espacio no puede ser su propio padre
		if self.parent_space and self.name and self.parent_space == self.name:
			frappe.throw("Un espacio no puede ser su propio padre")

		# 2. Validar ciclos en la jerarquía - solo si el documento ya existe
		if self.parent_space and self.name and frappe.db.exists("Physical Space", self.name):
			if self.has_circular_reference():
				frappe.throw("Se detectó una referencia circular en la jerarquía")

	def has_circular_reference(self):
		"""Detectar referencias circulares en jerarquía"""
		visited = set()
		current = self.parent_space

		while current:
			if current in visited:
				return True
			visited.add(current)

			parent_doc = frappe.get_doc("Physical Space", current)
			current = parent_doc.parent_space

			# Límite de seguridad
			if len(visited) > 100:
				frappe.throw("Jerarquía demasiado profunda")

		return False

	def update_hierarchy_info(self):
		"""Actualizar información jerárquica automáticamente"""
		if self.parent_space:
			try:
				if frappe.db.exists("Physical Space", self.parent_space):
					parent = frappe.get_doc("Physical Space", self.parent_space)
					self.space_level = parent.space_level + 1
					self.space_path = f"{parent.space_path}/{self.space_name}"
				else:
					# Parent no existe aún, usar valores por defecto
					self.space_level = 1
					self.space_path = f"/PENDING/{self.space_name}"
			except Exception:
				# Fallback si hay cualquier error
				self.space_level = 1
				self.space_path = f"/ERROR/{self.space_name}"
		else:
			self.space_level = 0
			self.space_path = f"/{self.space_name}"

	def get_all_children(self, include_self=False):
		"""Obtener todos los hijos recursivamente - SIN limitaciones nested set"""
		children = []
		if include_self:
			children.append(self.name)

		direct_children = frappe.get_all(
			"Physical Space", filters={"parent_space": self.name}, fields=["name"]
		)

		for child in direct_children:
			child_doc = frappe.get_doc("Physical Space", child.name)
			children.extend(child_doc.get_all_children(include_self=True))

		return children

	def load_template_fields(self):
		"""Cargar campos dinámicos basados en space_category"""
		if self.space_category:
			category = frappe.get_doc("Space Category", self.space_category)
			if category.ps_template_code:
				# TODO: Implementar get_template cuando exista templates system
				# template = get_template(category.ps_template_code)
				# return template.get("fields", [])
				pass
		return []

	def after_insert(self):
		"""Hook para Document Generation automático"""
		if self.space_category:
			# TODO: Integrar con Document Generation cuando esté disponible
			# frappe.enqueue(
			#     "condominium_management.document_generation.api.template_propagation.trigger_template_update",
			#     entity_type="Physical Space",
			#     entity_name=self.name,
			#     queue="default"
			# )
			pass

	def on_update(self):
		"""Hook después de actualizar"""
		self.update_children_hierarchy()

	def update_children_hierarchy(self):
		"""Actualizar jerarquía de espacios hijos cuando cambie el padre"""
		children = frappe.get_all("Physical Space", filters={"parent_space": self.name}, fields=["name"])

		for child in children:
			child_doc = frappe.get_doc("Physical Space", child.name)
			child_doc.update_hierarchy_info()
			child_doc.save()
