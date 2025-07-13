# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class DashboardConfiguration(Document):
	"""Gestión de configuraciones de dashboard multi-nivel"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.set_creation_info()
		self.validate_dashboard_name()
		self.validate_role_permissions()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.set_modification_info()
		self.validate_refresh_interval()
		self.validate_widget_configuration()

	def set_creation_info(self):
		"""Establece información de creación"""
		if not self.created_by:
			self.created_by = frappe.session.user
		if not self.creation_date:
			self.creation_date = now()

	def set_modification_info(self):
		"""Actualiza información de modificación"""
		self.last_modified_by = frappe.session.user
		self.last_modified_date = now()

	def validate_dashboard_name(self):
		"""Valida unicidad del nombre del dashboard"""
		if not self.dashboard_name:
			frappe.throw("El nombre del dashboard es obligatorio")

		# Verificar unicidad considerando company_filter si existe
		filters = {"dashboard_name": self.dashboard_name}
		if self.company_filter:
			filters["company_filter"] = self.company_filter

		existing = frappe.db.get_value("Dashboard Configuration", filters, "name")
		if existing and existing != self.name:
			frappe.throw(f"Ya existe un dashboard con el nombre '{self.dashboard_name}' para esta empresa")

	def validate_role_permissions(self):
		"""Valida que el rol especificado tenga permisos adecuados"""
		if self.user_role:
			# Verificar que el rol existe
			if not frappe.db.exists("Role", self.user_role):
				frappe.throw(f"El rol '{self.user_role}' no existe")

			# Verificar permisos del rol para este DocType
			# Nota: frappe.has_permission no acepta user_role como parámetro
			# En su lugar verificamos que el rol tenga permisos definidos en el DocType
			meta = frappe.get_meta("Dashboard Configuration")
			role_permissions = [p for p in meta.permissions if p.role == self.user_role]
			if not role_permissions:
				frappe.throw(
					f"El rol '{self.user_role}' no tiene permisos configurados para Dashboard Configuration"
				)

	def validate_refresh_interval(self):
		"""Valida intervalo de actualización"""
		if self.refresh_interval:
			if self.refresh_interval < 10:
				frappe.throw("El intervalo de actualización mínimo es 10 segundos")
			if self.refresh_interval > 3600:
				frappe.throw("El intervalo de actualización máximo es 3600 segundos (1 hora)")

	def validate_widget_configuration(self):
		"""Valida configuración de widgets"""
		if self.dashboard_widgets:
			for widget in self.dashboard_widgets:
				self.validate_widget_data_source(widget)
				self.validate_widget_position(widget)

	def validate_widget_data_source(self, widget):
		"""Valida fuente de datos del widget"""
		if widget.data_source:
			# Verificar que la fuente de datos es válida
			valid_sources = ["Companies", "Committee Management", "Physical Spaces", "Document Generation"]
			if widget.data_source not in valid_sources:
				frappe.throw(
					f"Fuente de datos '{widget.data_source}' no es válida. Opciones: {', '.join(valid_sources)}"
				)

	def validate_widget_position(self, widget):
		"""Valida posición y tamaño del widget"""
		if hasattr(widget, "position_x") and widget.position_x < 0:
			frappe.throw("La posición X del widget no puede ser negativa")
		if hasattr(widget, "position_y") and widget.position_y < 0:
			frappe.throw("La posición Y del widget no puede ser negativa")
		if hasattr(widget, "width") and widget.width and widget.width < 1:
			frappe.throw("El ancho del widget debe ser al menos 1")
		if hasattr(widget, "height") and widget.height and widget.height < 1:
			frappe.throw("La altura del widget debe ser al menos 1")

	def get_dashboard_data(self):
		"""Obtiene datos del dashboard para renderizado"""
		from condominium_management.dashboard_consolidado.api import get_dashboard_data

		return get_dashboard_data(self.name)

	def get_widgets_configuration(self):
		"""Obtiene configuración completa de widgets"""
		widgets = []

		if self.dashboard_widgets:
			for widget in self.dashboard_widgets:
				widget_config = {
					"type": widget.widget_type,
					"name": widget.widget_name,
					"data_source": widget.data_source,
					"position": {
						"x": getattr(widget, "position_x", 0),
						"y": getattr(widget, "position_y", 0),
					},
					"size": {"width": getattr(widget, "width", 3), "height": getattr(widget, "height", 2)},
				}
				widgets.append(widget_config)

		return widgets

	@frappe.whitelist()
	def create_snapshot(self, snapshot_type="Manual"):
		"""Crea snapshot del dashboard actual"""
		snapshot_data = {
			"dashboard_data": self.get_dashboard_data(),
			"widgets_config": self.get_widgets_configuration(),
			"creation_info": {
				"created_by": frappe.session.user,
				"creation_date": now(),
				"dashboard_name": self.dashboard_name,
				"company_filter": self.company_filter,
			},
		}

		snapshot = frappe.get_doc(
			{
				"doctype": "Dashboard Snapshot",
				"snapshot_date": now(),
				"dashboard_config": self.name,
				"snapshot_type": snapshot_type,
				"triggered_by": frappe.session.user,
				"snapshot_data": frappe.as_json(snapshot_data),
			}
		)
		snapshot.insert(ignore_permissions=True)

		return snapshot.name
