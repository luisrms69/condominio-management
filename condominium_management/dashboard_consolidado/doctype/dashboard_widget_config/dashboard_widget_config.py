# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DashboardWidgetConfig(Document):
	"""Configuración individual de widgets de dashboard"""

	def validate(self):
		"""Validaciones del widget"""
		self.validate_widget_type()
		self.validate_position_and_size()
		self.validate_data_source()

	def validate_widget_type(self):
		"""Valida el tipo de widget"""
		if not self.widget_type:
			frappe.throw("El tipo de widget es obligatorio")

		valid_widget_types = [
			"Tarjeta KPI",
			"Gráfico de Barras",
			"Gráfico de Líneas",
			"Gráfico de Pastel",
			"Tabla de Datos",
			"Mapa de Calor",
			"Indicador de Progreso",
			"Lista de Alertas",
			"Widget Personalizado",
		]

		if self.widget_type not in valid_widget_types:
			frappe.throw(f"Tipo de widget inválido. Opciones: {', '.join(valid_widget_types)}")

	def validate_position_and_size(self):
		"""Valida posición y tamaño del widget"""
		# Validar posición
		if hasattr(self, "position_x") and self.position_x is not None and self.position_x < 0:
			frappe.throw("La posición X no puede ser negativa")

		if hasattr(self, "position_y") and self.position_y is not None and self.position_y < 0:
			frappe.throw("La posición Y no puede ser negativa")

		# Validar tamaño
		if hasattr(self, "width") and self.width is not None:
			if self.width < 1 or self.width > 12:
				frappe.throw("El ancho debe estar entre 1 y 12")

		if hasattr(self, "height") and self.height is not None:
			if self.height < 1 or self.height > 8:
				frappe.throw("La altura debe estar entre 1 y 8")

	def validate_data_source(self):
		"""Valida la fuente de datos del widget"""
		if self.data_source:
			valid_data_sources = [
				"Companies",
				"Committee Management",
				"Physical Spaces",
				"Document Generation",
				"API Documentation System",
				"Dashboard Consolidado",
				"Sistema Global",
			]

			if self.data_source not in valid_data_sources:
				frappe.throw(f"Fuente de datos inválida. Opciones: {', '.join(valid_data_sources)}")

	def get_widget_configuration(self):
		"""Obtiene configuración completa del widget"""
		config = {
			"type": self.widget_type,
			"name": self.widget_name,
			"data_source": self.data_source,
			"position": {"x": getattr(self, "position_x", 0), "y": getattr(self, "position_y", 0)},
			"size": {"width": getattr(self, "width", 3), "height": getattr(self, "height", 2)},
		}

		# Agregar configuración específica del tipo de widget
		if hasattr(self, "widget_config") and self.widget_config:
			try:
				import json

				widget_specific_config = (
					json.loads(self.widget_config)
					if isinstance(self.widget_config, str)
					else self.widget_config
				)
				config.update(widget_specific_config)
			except Exception:
				pass

		return config

	def get_default_size_for_type(self):
		"""Obtiene tamaño por defecto basado en el tipo de widget"""
		default_sizes = {
			"Tarjeta KPI": {"width": 3, "height": 2},
			"Gráfico de Barras": {"width": 6, "height": 4},
			"Gráfico de Líneas": {"width": 8, "height": 4},
			"Gráfico de Pastel": {"width": 4, "height": 4},
			"Tabla de Datos": {"width": 8, "height": 6},
			"Mapa de Calor": {"width": 6, "height": 4},
			"Indicador de Progreso": {"width": 4, "height": 2},
			"Lista de Alertas": {"width": 6, "height": 5},
			"Widget Personalizado": {"width": 4, "height": 3},
		}

		return default_sizes.get(self.widget_type, {"width": 4, "height": 3})

	def auto_set_default_size(self):
		"""Establece tamaño por defecto si no está especificado"""
		if not hasattr(self, "width") or not self.width:
			default_size = self.get_default_size_for_type()
			self.width = default_size["width"]
			self.height = default_size["height"]
