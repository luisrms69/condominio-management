# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class ComponentType(Document):
	def before_save(self):
		"""Hook antes de guardar"""
		self.validate_code_prefix()
		self.validate_template_configuration()

	def validate_code_prefix(self):
		"""Validar que el prefijo de código es único y válido"""
		if self.code_prefix:
			# Normalizar prefijo (mayúsculas, sin espacios)
			self.code_prefix = cstr(self.code_prefix).upper().replace(" ", "")

			# Validar que no existe otro tipo con el mismo prefijo
			existing = frappe.db.get_value(
				"Component Type", filters={"code_prefix": self.code_prefix, "name": ["!=", self.name]}
			)
			if existing:
				frappe.throw(f"Ya existe un tipo de componente con el prefijo '{self.code_prefix}'")

	def validate_template_configuration(self):
		"""Validar configuración del template"""
		if self.component_template_code and not self.template_version:
			self.template_version = "1.0"

		# Validar que el template existe si está configurado
		if self.component_template_code and self.auto_load_template:
			# TODO: Validar que el template existe cuando se implemente el template system
			pass

	def get_validation_rules(self):
		"""Obtener reglas de validación para componentes de este tipo"""
		rules = {
			"requires_brand": self.requires_brand,
			"requires_model": self.requires_model,
			"requires_installation_date": self.requires_installation_date,
			"requires_warranty": self.requires_warranty,
			"requires_specifications": self.requires_specifications,
		}

		# Agregar validaciones específicas del template
		if self.template_fields_config:
			# TODO: Procesar configuración de campos del template
			pass

		return rules

	def get_maintenance_configuration(self):
		"""Obtener configuración de mantenimiento para este tipo"""
		return {
			"default_frequency": self.default_maintenance_frequency,
			"maintenance_type": self.maintenance_type,
			"estimated_lifespan_years": self.estimated_lifespan_years,
			"critical_component": self.critical_component,
			"requires_certification": self.requires_certification,
		}

	def get_ui_configuration(self):
		"""Obtener configuración de UI para el tipo de componente"""
		return {
			"icon_class": self.icon_class or "fa fa-cog",
			"color_code": self.color_code or "#606060",
			"display_order": self.display_order or 0,
		}

	def get_template_fields(self):
		"""Obtener campos del template asociado"""
		if self.component_template_code:
			# TODO: Implementar cuando exista el template system
			# return get_component_template_fields(self.component_template_code)
			pass
		return []

	def validate_component_data(self, component_data):
		"""Validar datos de un componente según las reglas de este tipo"""
		errors = []

		# Validar campos obligatorios
		if self.requires_brand and not component_data.get("brand"):
			errors.append("La marca es obligatoria para este tipo de componente")

		if self.requires_model and not component_data.get("model"):
			errors.append("El modelo es obligatorio para este tipo de componente")

		if self.requires_installation_date and not component_data.get("installation_date"):
			errors.append("La fecha de instalación es obligatoria para este tipo de componente")

		if self.requires_warranty and not component_data.get("warranty_expiry_date"):
			errors.append("La información de garantía es obligatoria para este tipo de componente")

		if self.requires_specifications and not component_data.get("technical_specifications"):
			errors.append("Las especificaciones técnicas son obligatorias para este tipo de componente")

		return errors

	def after_insert(self):
		"""Hook después de insertar"""
		# Crear configuración por defecto si no existe
		if not self.template_fields_config:
			self.template_fields_config = {}

		# Registrar en el sistema de templates si está configurado
		if self.component_template_code:
			# TODO: Registrar en template system cuando esté disponible
			pass

	def on_update(self):
		"""Hook después de actualizar"""
		# Actualizar componentes existentes que usen este tipo
		if self.has_value_changed("component_template_code") or self.has_value_changed("template_version"):
			self.update_existing_components()

	def update_existing_components(self):
		"""Actualizar componentes existentes que usen este tipo"""
		components = frappe.get_all("Space Component", filters={"component_type": self.name}, fields=["name"])

		for _component in components:
			# Actualizar campos del template en los componentes existentes
			# component_doc = frappe.get_doc("Space Component", component.name)
			# TODO: Actualizar template_fields cuando esté implementado
			pass

	def get_next_inventory_code(self):
		"""Obtener el siguiente código de inventario para este tipo"""
		# Buscar el último código usado
		last_code = frappe.db.sql(
			"""
            SELECT inventory_code
            FROM `tabSpace Component`
            WHERE component_type = %s
            AND inventory_code LIKE %s
            ORDER BY inventory_code DESC
            LIMIT 1
        """,
			(self.name, f"{self.code_prefix}%"),
		)

		if last_code:
			# Extraer número y incrementar
			last_num = last_code[0][0].replace(self.code_prefix, "").replace("-", "")
			try:
				next_num = int(last_num) + 1
				return f"{self.code_prefix}-{next_num:04d}"
			except ValueError:
				# Si no se puede convertir, usar timestamp
				return f"{self.code_prefix}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
		else:
			# Primer código
			return f"{self.code_prefix}-0001"
