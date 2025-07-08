# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class SpaceCategory(Document):
	def before_save(self):
		"""Hook antes de guardar"""
		self.set_defaults()
		self.generate_category_code()
		self.validate_template_configuration()

	def set_defaults(self):
		"""Establecer valores por defecto"""
		if not self.template_version:
			self.template_version = "1.0"

	def generate_category_code(self):
		"""Generar código único de categoría si no existe"""
		if not self.category_code:
			# Generar código basado en nombre
			base_code = cstr(self.category_name)[:15].upper().replace(" ", "_")
			self.category_code = base_code

	def validate_template_configuration(self):
		"""Validar configuración del template"""
		if self.ps_template_code and not self.template_version:
			self.template_version = "1.0"

		# Validar que el template existe si está configurado
		if self.ps_template_code and self.auto_load_template:
			# TODO: Validar que el template existe cuando se implemente el template system
			pass

	def get_template_fields(self):
		"""Obtener campos del template asociado"""
		if self.ps_template_code:
			# TODO: Implementar cuando exista el template system
			# return get_template_fields(self.ps_template_code)
			pass
		return []

	def validate_parent_child_relationship(self, parent_category, child_category):
		"""Validar si una categoría puede ser padre/hijo de otra"""
		# Validar categorías padre permitidas
		if parent_category and self.allowed_parent_categories:
			allowed_parents = [row.parent_category for row in self.allowed_parent_categories]
			if parent_category not in allowed_parents:
				frappe.throw(
					f"La categoría {parent_category} no está permitida como padre de {self.category_name}"
				)

		# Validar categorías hijo permitidas
		if child_category and self.allowed_child_categories:
			allowed_children = [row.child_category for row in self.allowed_child_categories]
			if child_category not in allowed_children:
				frappe.throw(
					f"La categoría {child_category} no está permitida como hijo de {self.category_name}"
				)

	def get_validation_rules(self):
		"""Obtener reglas de validación para espacios de esta categoría"""
		rules = {
			"requires_components": self.requires_components,
			"requires_dimensions": self.requires_dimensions,
			"requires_capacity": self.requires_capacity,
		}

		# Agregar validaciones específicas del template
		if self.template_fields_config:
			# TODO: Procesar configuración de campos del template
			pass

		return rules

	def get_ui_configuration(self):
		"""Obtener configuración de UI para la categoría"""
		return {
			"icon_class": self.icon_class or "fa fa-building",
			"color_code": self.color_code or "#808080",
			"display_order": self.display_order or 0,
		}

	def after_insert(self):
		"""Hook después de insertar"""
		# Crear configuración por defecto si no existe
		if not self.template_fields_config:
			self.template_fields_config = {}

		# Registrar en el sistema de templates si está configurado
		if self.ps_template_code:
			# TODO: Registrar en template system cuando esté disponible
			pass

	def on_update(self):
		"""Hook después de actualizar"""
		# Actualizar espacios existentes que usen esta categoría
		if self.has_value_changed("ps_template_code") or self.has_value_changed("template_version"):
			self.update_existing_spaces()

	def update_existing_spaces(self):
		"""Actualizar espacios existentes que usen esta categoría"""
		spaces = frappe.get_all("Physical Space", filters={"space_category": self.name}, fields=["name"])

		for _space in spaces:
			# Actualizar campos del template en los espacios existentes
			# space_doc = frappe.get_doc("Physical Space", space.name)
			# TODO: Actualizar template_fields cuando esté implementado
			# space_doc.template_fields = self.get_template_fields()
			# space_doc.save()
			pass
