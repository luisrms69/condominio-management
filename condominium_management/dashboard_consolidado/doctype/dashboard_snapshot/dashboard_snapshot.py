# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import now


class DashboardSnapshot(Document):
	"""Snapshots de dashboards para auditoría y análisis histórico"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_snapshot_configuration()
		self.set_snapshot_metadata()

	def validate_snapshot_configuration(self):
		"""Valida la configuración del snapshot"""
		if not self.dashboard_config:
			frappe.throw("La configuración del dashboard es obligatoria")

		if not frappe.db.exists("Dashboard Configuration", self.dashboard_config):
			frappe.throw(f"La configuración del dashboard '{self.dashboard_config}' no existe")

		if not self.snapshot_type:
			self.snapshot_type = "Manual"

		valid_snapshot_types = ["Manual", "Automático", "Programado"]
		if self.snapshot_type not in valid_snapshot_types:
			frappe.throw(f"Tipo de snapshot inválido. Opciones: {', '.join(valid_snapshot_types)}")

	def set_snapshot_metadata(self):
		"""Establece metadatos del snapshot"""
		if not self.snapshot_date:
			self.snapshot_date = now()

		if not self.triggered_by:
			self.triggered_by = frappe.session.user

		# Establecer tamaño de datos si hay snapshot_data
		if self.snapshot_data:
			try:
				data_size = len(str(self.snapshot_data))
				self.data_size_bytes = data_size
			except Exception:
				self.data_size_bytes = 0

	def get_snapshot_summary(self):
		"""Obtiene resumen del snapshot"""
		summary = {
			"snapshot_name": self.name,
			"dashboard_config": self.dashboard_config,
			"snapshot_date": self.snapshot_date,
			"snapshot_type": self.snapshot_type,
			"triggered_by": self.triggered_by,
			"data_size_bytes": getattr(self, "data_size_bytes", 0),
		}

		if self.snapshot_data:
			try:
				data = (
					json.loads(self.snapshot_data)
					if isinstance(self.snapshot_data, str)
					else self.snapshot_data
				)
				summary["widgets_count"] = len(data.get("widgets_config", []))
				summary["kpis_count"] = len(data.get("dashboard_data", {}).get("kpis", {}))
			except Exception:
				summary["widgets_count"] = 0
				summary["kpis_count"] = 0

		return summary

	def get_dashboard_data(self):
		"""Obtiene datos del dashboard del snapshot"""
		if not self.snapshot_data:
			return {}

		try:
			data = (
				json.loads(self.snapshot_data) if isinstance(self.snapshot_data, str) else self.snapshot_data
			)
			return data.get("dashboard_data", {})
		except Exception as e:
			frappe.log_error(f"Error parsing snapshot data: {e!s}")
			return {}

	def get_widgets_configuration(self):
		"""Obtiene configuración de widgets del snapshot"""
		if not self.snapshot_data:
			return []

		try:
			data = (
				json.loads(self.snapshot_data) if isinstance(self.snapshot_data, str) else self.snapshot_data
			)
			return data.get("widgets_config", [])
		except Exception as e:
			frappe.log_error(f"Error parsing widgets config: {e!s}")
			return []

	@frappe.whitelist()
	def restore_dashboard_configuration(self):
		"""Restaura configuración del dashboard desde este snapshot"""
		if not self.snapshot_data:
			frappe.throw("No hay datos de snapshot para restaurar")

		try:
			data = (
				json.loads(self.snapshot_data) if isinstance(self.snapshot_data, str) else self.snapshot_data
			)
			widgets_config = data.get("widgets_config", [])

			# Obtener dashboard configuration actual
			dashboard_config = frappe.get_doc("Dashboard Configuration", self.dashboard_config)

			# Limpiar widgets actuales
			dashboard_config.dashboard_widgets = []

			# Restaurar widgets desde snapshot
			for widget in widgets_config:
				dashboard_config.append(
					"dashboard_widgets",
					{
						"widget_type": widget.get("type"),
						"widget_name": widget.get("name"),
						"data_source": widget.get("data_source"),
						"position_x": widget.get("position", {}).get("x", 0),
						"position_y": widget.get("position", {}).get("y", 0),
						"width": widget.get("size", {}).get("width", 3),
						"height": widget.get("size", {}).get("height", 2),
					},
				)

			dashboard_config.save()

			return {
				"status": "success",
				"message": f"Configuración restaurada desde snapshot {self.name}",
				"widgets_restored": len(widgets_config),
			}

		except Exception as e:
			frappe.log_error(f"Error restoring dashboard configuration: {e!s}")
			frappe.throw(f"Error restaurando configuración: {e!s}")

	@frappe.whitelist()
	def compare_with_current(self):
		"""Compara este snapshot con la configuración actual del dashboard"""
		try:
			# Obtener configuración actual
			current_dashboard = frappe.get_doc("Dashboard Configuration", self.dashboard_config)
			current_widgets = current_dashboard.get_widgets_configuration()

			# Obtener configuración del snapshot
			snapshot_widgets = self.get_widgets_configuration()

			comparison = {
				"snapshot_date": self.snapshot_date,
				"current_widgets_count": len(current_widgets),
				"snapshot_widgets_count": len(snapshot_widgets),
				"widgets_added": [],
				"widgets_removed": [],
				"widgets_modified": [],
			}

			# Comparar widgets por nombre
			current_widget_names = {w.get("name") for w in current_widgets}
			snapshot_widget_names = {w.get("name") for w in snapshot_widgets}

			comparison["widgets_added"] = list(current_widget_names - snapshot_widget_names)
			comparison["widgets_removed"] = list(snapshot_widget_names - current_widget_names)

			# Comparar widgets modificados
			for current_widget in current_widgets:
				widget_name = current_widget.get("name")
				snapshot_widget = next((w for w in snapshot_widgets if w.get("name") == widget_name), None)

				if snapshot_widget:
					# Comparar propiedades
					if (
						current_widget.get("position") != snapshot_widget.get("position")
						or current_widget.get("size") != snapshot_widget.get("size")
						or current_widget.get("data_source") != snapshot_widget.get("data_source")
					):
						comparison["widgets_modified"].append(
							{
								"widget_name": widget_name,
								"changes": self._get_widget_changes(current_widget, snapshot_widget),
							}
						)

			return comparison

		except Exception as e:
			frappe.log_error(f"Error comparing with current configuration: {e!s}")
			return {"error": str(e)}

	def _get_widget_changes(self, current, snapshot):
		"""Obtiene cambios específicos entre widgets"""
		changes = {}

		if current.get("position") != snapshot.get("position"):
			changes["position"] = {"current": current.get("position"), "snapshot": snapshot.get("position")}

		if current.get("size") != snapshot.get("size"):
			changes["size"] = {"current": current.get("size"), "snapshot": snapshot.get("size")}

		if current.get("data_source") != snapshot.get("data_source"):
			changes["data_source"] = {
				"current": current.get("data_source"),
				"snapshot": snapshot.get("data_source"),
			}

		return changes
