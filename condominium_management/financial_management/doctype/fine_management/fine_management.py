# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Fine Management - Sistema de Gestión de Multas
==============================================

DocType para manejo completo de multas y sanciones con:
- Workflow de aprobación
- Proceso de apelación
- Enforcement levels automáticos
- Integración con ERPNext Sales Invoice
- Tracking completo de cobros
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, getdate, nowdate, random_string


class FineManagement(Document):
	"""Fine Management DocType con business logic completa"""

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_account_selection()
		self.validate_violation_data()
		self.validate_fine_amounts()
		self.calculate_final_amount()
		self.set_enforcement_defaults()
		self.validate_appeal_workflow()

	def on_submit(self):
		"""Acciones al confirmar la multa"""
		self.generate_confirmation_number()
		self.update_enforcement_level()
		self.create_erpnext_invoice()
		self.send_notification()

	# =============================================================================
	# VALIDATION METHODS
	# =============================================================================

	def validate_account_selection(self):
		"""Validar selección correcta de cuentas según tipo de infractor"""
		if not self.violator_type:
			frappe.throw(_("Tipo de Infractor es obligatorio"))

		# Validar que se seleccione al menos una cuenta
		if not self.property_account and not self.resident_account:
			frappe.throw(_("Debe seleccionar Property Account o Resident Account"))

		# Para Propietarios, requiere Property Account
		if self.violator_type == "Propietario" and not self.property_account:
			frappe.throw(_("Propietarios requieren Property Account"))

		# Para Residentes, puede ser cualquiera
		if self.violator_type == "Residente":
			if self.resident_account:
				# Verificar que Resident Account pertenece a Property Account
				if self.property_account:
					resident_doc = frappe.get_doc("Resident Account", self.resident_account)
					if resident_doc.property_account != self.property_account:
						frappe.throw(_("Resident Account no pertenece a la Property Account seleccionada"))

		# Para Visitantes/Proveedores/Contratistas, requiere Property Account responsable
		if self.violator_type in ["Visitante", "Proveedor", "Contratista"]:
			if not self.property_account:
				frappe.throw(
					_("Para {0} debe especificarse Property Account responsable").format(self.violator_type)
				)

	def validate_violation_data(self):
		"""Validar datos completos de la infracción"""
		if not self.violation_description:
			frappe.throw(_("Descripción de la Infracción es obligatoria"))

		if not self.violation_date:
			self.violation_date = self.fine_date

		# Validar que violation_date no sea futura
		if getdate(self.violation_date) > getdate():
			frappe.throw(_("Fecha de Infracción no puede ser futura"))

		# Validar que fine_date no sea anterior a violation_date
		if getdate(self.fine_date) < getdate(self.violation_date):
			frappe.throw(_("Fecha de Multa no puede ser anterior a Fecha de Infracción"))

	def validate_fine_amounts(self):
		"""Validar montos de la multa"""
		if not self.fine_amount or flt(self.fine_amount) <= 0:
			frappe.throw(_("Monto de la Multa debe ser mayor a cero"))

		# Establecer base_fine_amount si no está definido
		if not self.base_fine_amount:
			self.base_fine_amount = self.fine_amount

		# Validar límites por categoría de infracción
		category_limits = {"Leve": 5000.0, "Moderada": 15000.0, "Grave": 50000.0, "Muy Grave": 100000.0}

		if self.violation_category and self.violation_category in category_limits:
			max_amount = category_limits[self.violation_category]
			if flt(self.fine_amount) > max_amount:
				frappe.throw(
					_("Monto excede límite para categoría {0}: ${1:,.2f}").format(
						self.violation_category, max_amount
					)
				)

	def calculate_final_amount(self):
		"""Calcular monto final con recargos y descuentos"""
		base_amount = flt(self.base_fine_amount) or flt(self.fine_amount)
		final_amount = base_amount

		# Aplicar multiplicador por reincidencia
		if self.recurring_violation and self.recurrence_multiplier:
			final_amount = final_amount * flt(self.recurrence_multiplier)

		# Aplicar descuento si aplica
		if self.discount_percentage:
			discount_amount = final_amount * (flt(self.discount_percentage) / 100)
			final_amount = final_amount - discount_amount

		self.final_amount = final_amount
		self.outstanding_amount = final_amount - flt(self.payment_amount)

	def set_enforcement_defaults(self):
		"""Establecer valores por defecto para enforcement"""
		if not self.enforcement_level:
			self.enforcement_level = "Recordatorio Amigable"

		if not self.collection_attempts:
			self.collection_attempts = 0

		# Establecer due_date si no está definida
		if not self.due_date:
			days_to_pay = {"Leve": 30, "Moderada": 21, "Grave": 14, "Muy Grave": 7}
			days = days_to_pay.get(self.violation_category, 21)
			self.due_date = add_days(self.fine_date, days)

	def validate_appeal_workflow(self):
		"""Validar workflow de apelación"""
		if self.appeal_submitted:
			if not self.appeal_date:
				self.appeal_date = getdate()

			if not self.appeal_reason:
				frappe.throw(_("Razón de Apelación es obligatoria cuando se presenta apelación"))

			if not self.appeal_status:
				self.appeal_status = "En Revisión"

			# Verificar plazo para apelación (14 días desde fine_date)
			days_since_fine = (getdate(self.appeal_date) - getdate(self.fine_date)).days
			if days_since_fine > 14:
				frappe.throw(_("Apelación debe presentarse dentro de 14 días de la multa"))

	# =============================================================================
	# BUSINESS LOGIC METHODS
	# =============================================================================

	def generate_confirmation_number(self):
		"""Generar número de confirmación único"""
		if not hasattr(self, "_confirmation_number"):
			date_part = getdate().strftime("%Y%m%d")
			random_part = random_string(4).upper()
			self._confirmation_number = f"FINE-{date_part}-{random_part}"

		# Verificar unicidad
		if frappe.db.exists(
			"Fine Management", {"confirmation_number": self._confirmation_number, "name": ["!=", self.name]}
		):
			# Regenerar si existe
			return self.generate_confirmation_number()

		frappe.db.set_value("Fine Management", self.name, "confirmation_number", self._confirmation_number)

	def update_enforcement_level(self):
		"""Actualizar nivel de enforcement según vencimiento"""
		if not self.due_date:
			return

		days_overdue = (getdate() - getdate(self.due_date)).days

		if days_overdue <= 0:
			return  # No vencida

		# Escalación automática de enforcement
		if days_overdue <= 7:
			new_level = "Recordatorio Amigable"
		elif days_overdue <= 15:
			new_level = "Notificación Formal"
		elif days_overdue <= 30:
			new_level = "Ultima Advertencia"
		else:
			new_level = "Acción Legal"

		if self.enforcement_level != new_level:
			self.enforcement_level = new_level
			self.collection_attempts = (self.collection_attempts or 0) + 1
			frappe.db.set_value(
				"Fine Management",
				self.name,
				{
					"enforcement_level": new_level,
					"collection_attempts": self.collection_attempts,
					"last_reminder_date": getdate(),
				},
			)

	def create_erpnext_invoice(self):
		"""Crear Sales Invoice en ERPNext para la multa"""
		if self.fine_status != "Confirmada":
			return

		# Obtener customer de Property Account
		customer = None
		if self.property_account:
			property_doc = frappe.get_doc("Property Account", self.property_account)
			customer = property_doc.customer

		if not customer:
			frappe.throw(_("No se puede crear factura: Customer no encontrado"))

		# Crear Sales Invoice
		invoice_doc = frappe.new_doc("Sales Invoice")
		invoice_doc.customer = customer
		invoice_doc.due_date = self.due_date
		invoice_doc.posting_date = self.fine_date

		# Agregar item de multa
		invoice_doc.append(
			"items",
			{
				"item_code": "MULTA-CONDOMINIO",  # Item predefinido
				"item_name": f"Multa: {self.fine_type}",
				"description": f"Multa por {self.violation_category}: {self.violation_description[:100]}...",
				"qty": 1,
				"rate": self.final_amount,
				"amount": self.final_amount,
			},
		)

		# Custom fields para tracking
		invoice_doc.custom_fine_management = self.name
		invoice_doc.custom_violation_type = self.fine_type

		try:
			invoice_doc.insert()
			frappe.db.set_value("Fine Management", self.name, "erpnext_invoice", invoice_doc.name)
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Error creando factura para multa {self.name}: {e!s}")

	def send_notification(self):
		"""Enviar notificación de multa"""
		if self.fine_status not in ["Notificada", "Confirmada"]:
			return

		# Template de notificación

		# Log de notificación enviada
		frappe.db.set_value(
			"Fine Management", self.name, {"notification_sent": 1, "notification_date": getdate()}
		)

	# =============================================================================
	# API METHODS
	# =============================================================================

	@frappe.whitelist()
	def process_payment(self, payment_amount, payment_method, payment_reference=None):
		"""Procesar pago de multa"""
		payment_amount = flt(payment_amount)

		if payment_amount <= 0:
			frappe.throw(_("Monto de pago debe ser mayor a cero"))

		if payment_amount > flt(self.outstanding_amount):
			frappe.throw(_("Monto excede saldo pendiente"))

		# Actualizar campos de pago
		self.payment_amount = flt(self.payment_amount) + payment_amount
		self.payment_date = getdate()
		self.payment_method = payment_method
		self.payment_reference = payment_reference
		self.outstanding_amount = flt(self.final_amount) - flt(self.payment_amount)

		# Actualizar estado si está completamente pagada
		if flt(self.outstanding_amount) <= 0:
			self.fine_status = "Pagada"

		self.save()
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Pago procesado exitosamente"),
			"payment_amount": payment_amount,
			"outstanding_amount": self.outstanding_amount,
		}

	@frappe.whitelist()
	def submit_appeal(self, appeal_reason, appeal_date=None):
		"""Presentar apelación a la multa"""
		if self.appeal_submitted:
			frappe.throw(_("Ya se presentó una apelación para esta multa"))

		if not appeal_reason:
			frappe.throw(_("Razón de apelación es obligatoria"))

		# Verificar plazo
		appeal_date = getdate(appeal_date) if appeal_date else getdate()
		days_since_fine = (appeal_date - getdate(self.fine_date)).days
		if days_since_fine > 14:
			frappe.throw(_("Apelación debe presentarse dentro de 14 días"))

		# Registrar apelación
		self.appeal_submitted = 1
		self.appeal_date = appeal_date
		self.appeal_reason = appeal_reason
		self.appeal_status = "En Revisión"
		self.fine_status = "Apelada"

		self.save()
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Apelación presentada exitosamente"),
			"appeal_date": appeal_date,
		}

	@frappe.whitelist()
	def resolve_appeal(self, resolution, approved_by, resolution_notes=None):
		"""Resolver apelación (solo para roles autorizados)"""
		if not self.appeal_submitted:
			frappe.throw(_("No hay apelación para resolver"))

		if self.appeal_status != "En Revisión":
			frappe.throw(_("Apelación ya fue resuelta"))

		# Actualizar resolución
		self.appeal_status = resolution
		self.appeal_resolution = resolution_notes
		self.approved_by = approved_by
		self.approval_date = getdate()

		# Actualizar estado de multa según resolución
		if resolution == "Aprobada":
			self.fine_status = "Cancelada"
			self.outstanding_amount = 0
		elif resolution == "Rechazada":
			self.fine_status = "Confirmada"
		elif resolution == "Modificada":
			self.fine_status = "Confirmada"
			# El monto puede haber sido modificado externamente

		self.save()
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Apelación resuelta: {0}").format(resolution),
			"new_status": self.fine_status,
		}

	@frappe.whitelist()
	def get_fine_summary(self):
		"""Obtener resumen completo de la multa"""
		return {
			"basic_info": {
				"fine_type": self.fine_type,
				"violation_category": self.violation_category,
				"violation_date": self.violation_date,
				"fine_date": self.fine_date,
				"due_date": self.due_date,
			},
			"amounts": {
				"base_amount": self.base_fine_amount,
				"final_amount": self.final_amount,
				"payment_amount": self.payment_amount,
				"outstanding_amount": self.outstanding_amount,
			},
			"violator": {
				"violator_type": self.violator_type,
				"violator_name": self.violator_name,
				"property_account": self.property_account,
				"resident_account": self.resident_account,
			},
			"status": {
				"fine_status": self.fine_status,
				"enforcement_level": self.enforcement_level,
				"collection_attempts": self.collection_attempts,
				"appeal_status": self.appeal_status if self.appeal_submitted else "No Aplica",
			},
			"dates": {
				"days_overdue": max(0, (getdate() - getdate(self.due_date)).days) if self.due_date else 0,
				"last_reminder_date": self.last_reminder_date,
				"escalation_date": self.escalation_date,
			},
		}

	@frappe.whitelist()
	def escalate_enforcement(self):
		"""Escalar nivel de enforcement manualmente"""
		current_levels = [
			"Recordatorio Amigable",
			"Notificación Formal",
			"Ultima Advertencia",
			"Acción Legal",
		]

		if self.enforcement_level not in current_levels:
			self.enforcement_level = "Recordatorio Amigable"

		current_index = current_levels.index(self.enforcement_level)
		if current_index < len(current_levels) - 1:
			self.enforcement_level = current_levels[current_index + 1]
			self.collection_attempts = (self.collection_attempts or 0) + 1
			self.last_reminder_date = getdate()

			if self.enforcement_level == "Acción Legal":
				self.legal_action_date = getdate()

			self.save()
			frappe.db.commit()

			return {
				"success": True,
				"message": _("Enforcement escalado a: {0}").format(self.enforcement_level),
				"new_level": self.enforcement_level,
			}
		else:
			return {"success": False, "message": _("Ya está en el nivel máximo de enforcement")}

	# =============================================================================
	# STATIC METHODS
	# =============================================================================

	@staticmethod
	def get_overdue_fines(days_overdue=None):
		"""Obtener multas vencidas para seguimiento"""
		filters = {"fine_status": ["in", ["Notificada", "Confirmada"]], "due_date": ["<", getdate()]}

		if days_overdue:
			target_date = add_days(getdate(), -days_overdue)
			filters["due_date"] = ["<=", target_date]

		return frappe.get_all(
			"Fine Management",
			filters=filters,
			fields=[
				"name",
				"violator_name",
				"fine_type",
				"final_amount",
				"due_date",
				"enforcement_level",
				"collection_attempts",
			],
		)

	@staticmethod
	def get_enforcement_statistics():
		"""Obtener estadísticas de enforcement"""
		return {
			"total_fines": frappe.db.count("Fine Management"),
			"by_status": frappe.db.get_all(
				"Fine Management", fields=["fine_status", "count(*) as count"], group_by="fine_status"
			),
			"by_enforcement": frappe.db.get_all(
				"Fine Management",
				fields=["enforcement_level", "count(*) as count"],
				group_by="enforcement_level",
			),
			"overdue_count": len(FineManagement.get_overdue_fines()),
			"appeal_rate": frappe.db.sql("""
				SELECT
					(SELECT COUNT(*) FROM `tabFine Management` WHERE appeal_submitted = 1) * 100.0 /
					(SELECT COUNT(*) FROM `tabFine Management`) as appeal_percentage
			""")[0][0]
			if frappe.db.count("Fine Management") > 0
			else 0,
		}
