# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe.model.document import Document


class ContributionRequest(Document):
	"""
	Framework genérico para contribuciones de cualquier módulo.

	Funcionalidades principales:
	- Gestión universal de contribuciones
	- Workflow de aprobación configurable por módulo
	- Export/import automático de fixtures
	- Versionado y tracking de cambios

	Extensible para:
	- Templates de infraestructura (Document Generation)
	- Rutinas de mantenimiento (Maintenance)
	- Templates de contratos (Contracts)
	- Configuraciones de espacios (Physical Spaces)
	- Y cualquier módulo futuro

	Estados: Draft → Submitted → Under Review → Approved/Rejected → Integrated
	"""

	def validate(self):
		"""
		Validar datos de la contribución según su categoría.
		"""
		self.validate_contribution_data()
		self.validate_status_transitions()
		self.update_audit_fields()

	def before_submit(self):
		"""
		Ejecutar antes de enviar la contribución.
		"""
		self.status = "Submitted"
		self.submitted_by = frappe.session.user
		self.submission_date = frappe.utils.now()

	def validate_contribution_data(self):
		"""
		Validar datos específicos según la categoría de contribución.

		Utiliza el handler específico del módulo para validación.
		"""
		if not self.contribution_category:
			return

		category = frappe.get_doc("Contribution Category", self.contribution_category)

		# Validar campos requeridos por categoría
		if self.contribution_data:
			try:
				contribution_data = (
					json.loads(self.contribution_data)
					if isinstance(self.contribution_data, str)
					else self.contribution_data
				)
				category.validate_contribution_data(contribution_data)
			except json.JSONDecodeError:
				frappe.throw(frappe._("Datos de contribución debe ser un JSON válido"))
		else:
			frappe.throw(frappe._("Datos de contribución son requeridos"))

		# Validar usando handler específico del módulo
		handler = self.get_module_handler()
		if handler:
			handler.validate_contribution(contribution_data)

	def validate_status_transitions(self):
		"""
		Validar que las transiciones de estado sean válidas.
		"""
		if self.is_new():
			return

		old_status = self.get_db_value("status")
		new_status = self.status

		valid_transitions = {
			"Draft": ["Submitted"],
			"Submitted": ["Under Review", "Draft"],
			"Under Review": ["Approved", "Rejected", "Submitted"],
			"Approved": ["Integrated"],
			"Rejected": ["Draft", "Submitted"],
			"Integrated": [],  # Estado final
		}

		if old_status != new_status:
			if new_status not in valid_transitions.get(old_status, []):
				frappe.throw(
					frappe._("Transición de estado inválida: {0} → {1}").format(old_status, new_status)
				)

	def update_audit_fields(self):
		"""
		Actualizar campos de auditoría según el estado.
		"""
		if self.has_value_changed("status"):
			current_time = frappe.utils.now()
			current_user = frappe.session.user

			if self.status == "Under Review":
				self.reviewed_by = current_user
				self.review_date = current_time
			elif self.status == "Approved":
				self.approved_by = current_user
				self.approval_date = current_time
			elif self.status == "Integrated":
				self.integration_date = current_time

	def get_module_handler(self):
		"""
		Obtener handler específico del módulo para procesamiento.

		Returns:
		    object: Handler específico del módulo o None
		"""
		if not self.contribution_category:
			return None

		category = frappe.get_doc("Contribution Category", self.contribution_category)
		handler_path = category.get_module_handler_path()

		if handler_path:
			try:
				return frappe.get_attr(handler_path + ".ContributionHandler")()
			except (ImportError, AttributeError):
				frappe.log_error(f"Handler no encontrado: {handler_path}")
				return None

		return None

	def export_to_fixtures(self):
		"""
		Exportar contribución a formato de fixtures.

		Returns:
		    dict: Datos listos para integración como fixture
		"""
		if self.status != "Approved":
			frappe.throw(frappe._("Solo se pueden exportar contribuciones aprobadas"))

		handler = self.get_module_handler()
		if not handler:
			frappe.throw(frappe._("Handler del módulo no disponible"))

		contribution_data = (
			json.loads(self.contribution_data)
			if isinstance(self.contribution_data, str)
			else self.contribution_data
		)

		# Agregar metadata de contribución
		contribution_data["contribution_metadata"] = {
			"contributed_by": self.company,
			"contribution_request": self.name,
			"submission_date": self.submission_date,
			"approved_by": self.approved_by,
			"approval_date": self.approval_date,
			"business_case": self.business_justification,
		}

		exported_data = handler.export_to_fixtures(contribution_data)

		# Guardar JSON exportado
		self.exported_json = json.dumps(exported_data, indent=2)
		self.save()

		return exported_data

	def preview_contribution(self):
		"""
		Generar preview de cómo se vería la contribución.

		Returns:
		    dict: Preview de la contribución
		"""
		handler = self.get_module_handler()
		if not handler:
			return {"error": "Handler del módulo no disponible"}

		contribution_data = (
			json.loads(self.contribution_data)
			if isinstance(self.contribution_data, str)
			else self.contribution_data
		)

		try:
			return handler.preview_contribution(contribution_data)
		except Exception as e:
			return {"error": str(e)}

	@frappe.whitelist()
	def approve_contribution(self):
		"""
		Aprobar la contribución (método para botón en interfaz).
		"""
		if self.status != "Under Review":
			frappe.throw(frappe._("Solo se pueden aprobar contribuciones en revisión"))

		self.status = "Approved"
		self.save()

		frappe.msgprint(frappe._("Contribución aprobada exitosamente"))

	@frappe.whitelist()
	def reject_contribution(self):
		"""
		Rechazar la contribución (método para botón en interfaz).
		"""
		if self.status != "Under Review":
			frappe.throw(frappe._("Solo se pueden rechazar contribuciones en revisión"))

		self.status = "Rejected"
		self.save()

		frappe.msgprint(frappe._("Contribución rechazada"))

	@frappe.whitelist()
	def integrate_contribution(self):
		"""
		Integrar contribución aprobada a fixtures.
		"""
		if self.status != "Approved":
			frappe.throw(frappe._("Solo se pueden integrar contribuciones aprobadas"))

		try:
			exported_data = self.export_to_fixtures()

			# TODO: Aquí se implementaría la lógica para escribir el fixture
			# Por ahora solo marcamos como integrado
			self.status = "Integrated"
			self.save()

			frappe.msgprint(frappe._("Contribución integrada exitosamente"))

			return exported_data

		except Exception as e:
			frappe.log_error(f"Error integrando contribución {self.name}: {e!s}")
			frappe.throw(frappe._("Error al integrar contribución: {0}").format(str(e)))
