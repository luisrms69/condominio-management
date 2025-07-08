# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, today


class SpaceComponent(Document):
	def before_save(self):
		"""Hook antes de guardar"""
		self.validate_component_hierarchy()
		self.set_default_values()

	def validate_component_hierarchy(self):
		"""Validar jerarquía de componentes"""
		# 1. Un componente no puede ser su propio padre
		if self.parent_component == self.name:
			frappe.throw("Un componente no puede ser su propio padre")

		# 2. Validar referencias circulares
		if self.parent_component and self.has_circular_reference():
			frappe.throw("Se detectó una referencia circular en la jerarquía de componentes")

	def has_circular_reference(self):
		"""Detectar referencias circulares en jerarquía de componentes"""
		visited = set()
		current = self.parent_component

		while current:
			if current in visited:
				return True
			visited.add(current)

			# Obtener componente padre
			parent_component = frappe.db.get_value("Space Component", current, "parent_component")
			current = parent_component

			# Límite de seguridad
			if len(visited) > 50:
				frappe.throw("Jerarquía de componentes demasiado profunda")

		return False

	def set_default_values(self):
		"""Establecer valores por defecto"""
		# Establecer fecha de inventario por defecto
		if not self.inventory_date:
			self.inventory_date = today()

		# Generar código de inventario automático si no existe
		if not self.inventory_code:
			self.generate_inventory_code()

	def generate_inventory_code(self):
		"""Generar código de inventario automático"""
		if self.component_type:
			# Obtener prefijo del tipo de componente
			component_type_doc = frappe.get_doc("Component Type", self.component_type)
			prefix = component_type_doc.get("code_prefix", "COMP")
		else:
			prefix = "COMP"

		# Generar código secuencial
		last_code = frappe.db.sql(
			"""
            SELECT inventory_code
            FROM `tabSpace Component`
            WHERE inventory_code LIKE %s
            ORDER BY inventory_code DESC
            LIMIT 1
        """,
			f"{prefix}%",
		)

		if last_code:
			# Extraer número y incrementar
			last_num = last_code[0][0].replace(prefix, "").replace("-", "")
			try:
				next_num = int(last_num) + 1
				self.inventory_code = f"{prefix}-{next_num:04d}"
			except ValueError:
				# Si no se puede convertir, usar timestamp
				self.inventory_code = f"{prefix}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
		else:
			# Primer código
			self.inventory_code = f"{prefix}-0001"

	def get_all_subcomponents(self, include_self=False):
		"""Obtener todos los subcomponentes recursivamente"""
		components = []
		if include_self:
			components.append(self.name)

		# Buscar componentes hijos directos
		direct_children = frappe.get_all(
			"Space Component", filters={"parent_component": self.name}, fields=["name"]
		)

		for child in direct_children:
			child_doc = frappe.get_doc("Space Component", child.name)
			components.extend(child_doc.get_all_subcomponents(include_self=True))

		return components

	def get_maintenance_schedule(self):
		"""Obtener programación de mantenimiento para este componente"""
		# TODO: Integrar con módulo de mantenimiento cuando esté disponible
		return []

	def get_component_hierarchy_path(self):
		"""Obtener la ruta completa de la jerarquía del componente"""
		path = [self.component_name]
		current = self.parent_component

		while current:
			parent_doc = frappe.get_doc("Space Component", current)
			path.insert(0, parent_doc.component_name)
			current = parent_doc.parent_component

		return " → ".join(path)

	def is_warranty_expired(self):
		"""Verificar si la garantía ha expirado"""
		if self.warranty_expiry_date:
			return frappe.utils.getdate(self.warranty_expiry_date) < frappe.utils.getdate()
		return False

	def get_component_age_days(self):
		"""Obtener la edad del componente en días"""
		if self.installation_date:
			return frappe.utils.date_diff(frappe.utils.getdate(), self.installation_date)
		elif self.inventory_date:
			return frappe.utils.date_diff(frappe.utils.getdate(), self.inventory_date)
		return 0

	def validate_component_type_requirements(self):
		"""Validar requisitos específicos del tipo de componente"""
		if self.component_type:
			# TODO: Implementar validaciones específicas por tipo cuando esté disponible
			# el sistema de templates
			pass
