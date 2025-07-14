# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, flt, get_datetime, getdate, now, nowdate


class BillingCycle(Document):
	"""Ciclo de facturación con auto-generación y seguimiento de cobranza"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_date_configuration()
		self.validate_fee_structure()
		self.set_default_values()
		self.calculate_cycle_totals()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_cycle_status()
		self.validate_late_fee_configuration()
		self.update_collection_metrics()
		self.calculate_next_cycle_date()
		self.update_audit_information()

	def validate_date_configuration(self):
		"""Valida la configuración de fechas"""
		if not self.start_date or not self.end_date:
			frappe.throw(_("Las fechas de inicio y fin son obligatorias"))

		if self.start_date >= self.end_date:
			frappe.throw(_("La fecha de inicio debe ser anterior a la fecha de fin"))

		if not self.due_date:
			frappe.throw(_("La fecha de vencimiento es obligatoria"))

		if self.due_date < self.end_date:
			frappe.throw(_("La fecha de vencimiento debe ser posterior a la fecha de fin"))

		# Validar que no se traslapen con otros ciclos activos
		existing_cycles = frappe.db.sql(
			"""
			SELECT name FROM `tabBilling Cycle`
			WHERE company = %s
				AND name != %s
				AND cycle_status IN ('Programado', 'Activo', 'Facturado')
				AND (
					(start_date <= %s AND end_date >= %s) OR
					(start_date <= %s AND end_date >= %s) OR
					(start_date >= %s AND end_date <= %s)
				)
		""",
			[
				self.company,
				self.name or "",
				self.start_date,
				self.start_date,
				self.end_date,
				self.end_date,
				self.start_date,
				self.end_date,
			],
		)

		if existing_cycles:
			frappe.throw(
				_("Ya existe un ciclo activo que se traslapa con las fechas especificadas: {0}").format(
					existing_cycles[0][0]
				)
			)

	def validate_fee_structure(self):
		"""Valida la estructura de cuotas vinculada"""
		if not self.fee_structure:
			frappe.throw(_("La estructura de cuotas es obligatoria"))

		fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)
		if fee_structure_doc.company != self.company:
			frappe.throw(_("La estructura de cuotas debe pertenecer al mismo condominio"))

		if fee_structure_doc.docstatus != 1:
			frappe.throw(_("La estructura de cuotas debe estar aprobada"))

	def validate_cycle_status(self):
		"""Valida las transiciones de estado del ciclo"""
		valid_transitions = {
			"Borrador": ["Programado", "Cancelado"],
			"Programado": ["Activo", "Cancelado"],
			"Activo": ["Facturado", "Cancelado"],
			"Facturado": ["Completado"],
			"Completado": [],
			"Cancelado": [],
		}

		if self.is_new():
			if not self.cycle_status:
				self.cycle_status = "Borrador"
			return

		old_status = frappe.db.get_value("Billing Cycle", self.name, "cycle_status")
		if old_status and self.cycle_status != old_status:
			if self.cycle_status not in valid_transitions.get(old_status, []):
				frappe.throw(
					_("Transición de estado inválida: de {0} a {1}").format(old_status, self.cycle_status)
				)

	def validate_late_fee_configuration(self):
		"""Valida la configuración de recargos por mora"""
		if self.apply_late_fees:
			if not self.late_fee_percentage and not self.late_fee_flat_amount:
				frappe.throw(_("Debe especificar un porcentaje o monto fijo para recargos por mora"))

			if self.late_fee_percentage and (self.late_fee_percentage < 0 or self.late_fee_percentage > 100):
				frappe.throw(_("El porcentaje de recargo debe estar entre 0 y 100"))

			if self.late_fee_flat_amount and self.late_fee_flat_amount < 0:
				frappe.throw(_("El monto fijo de recargo no puede ser negativo"))

			if not self.late_fee_after_days or self.late_fee_after_days < 1:
				frappe.throw(_("Los días para aplicar recargo deben ser mayor a 0"))

	def set_default_values(self):
		"""Establece valores por defecto"""
		if not self.cycle_status:
			self.cycle_status = "Borrador"

		if not self.cycle_type:
			self.cycle_type = "Regular"

		if not self.billing_frequency:
			self.billing_frequency = "Mensual"

		if not self.generation_status:
			self.generation_status = "Pendiente"

		if self.auto_generate_invoices is None:
			self.auto_generate_invoices = 1

		if self.send_notifications is None:
			self.send_notifications = 1

		if not self.grace_period_days:
			self.grace_period_days = 5

	def calculate_cycle_totals(self):
		"""Calcula los totales del ciclo basado en las propiedades"""
		if not self.fee_structure:
			return

		# Obtener propiedades activas del condominio
		properties = frappe.db.sql(
			"""
			SELECT COUNT(*) as total_count,
				   SUM(ownership_percentage) as total_percentage
			FROM `tabProperty Account`
			WHERE company = %s
				AND account_status = 'Activa'
		""",
			[self.company],
			as_dict=True,
		)

		if properties and properties[0]:
			self.total_properties = properties[0].total_count or 0

			# Calcular monto total basado en la estructura de cuotas
			fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)
			total_amount = 0

			# Aquí se calcularía el monto total según el método de cálculo
			# Por ahora, cálculo simplificado
			if fee_structure_doc.calculation_method == "Monto Fijo":
				total_amount = flt(fee_structure_doc.base_amount) * self.total_properties
			else:
				# Para otros métodos, se requeriría lógica más compleja
				total_amount = flt(fee_structure_doc.base_amount) * self.total_properties

			self.total_amount = flt(total_amount, 2)

	def calculate_next_cycle_date(self):
		"""Calcula la fecha del próximo ciclo"""
		if not self.end_date or not self.billing_frequency:
			return

		frequency_map = {"Mensual": 1, "Bimestral": 2, "Trimestral": 3, "Semestral": 6, "Anual": 12}

		months_to_add = frequency_map.get(self.billing_frequency, 1)
		self.next_cycle_date = add_months(self.end_date, months_to_add)

	def update_collection_metrics(self):
		"""Actualiza métricas de cobranza"""
		if self.cycle_status not in ["Facturado", "Completado"]:
			return

		# Obtener datos de cobranza desde las facturas generadas
		collection_data = frappe.db.sql(
			"""
			SELECT
				SUM(total) as total_invoiced,
				SUM(outstanding_amount) as pending_amount,
				SUM(paid_amount) as paid_amount,
				COUNT(*) as invoice_count
			FROM `tabSales Invoice`
			WHERE company = %s
				AND posting_date BETWEEN %s AND %s
				AND custom_billing_cycle = %s
		""",
			[self.company, self.start_date, self.end_date, self.name],
			as_dict=True,
		)

		if collection_data and collection_data[0]:
			data = collection_data[0]
			self.total_invoiced = flt(data.total_invoiced or 0, 2)
			self.paid_amount = flt(data.paid_amount or 0, 2)
			self.pending_amount = flt(data.pending_amount or 0, 2)

			# Calcular tasa de cobranza
			if self.total_invoiced > 0:
				self.collection_rate = flt((self.paid_amount / self.total_invoiced) * 100, 2)

			# Calcular monto vencido
			overdue_data = frappe.db.sql(
				"""
				SELECT SUM(outstanding_amount) as overdue
				FROM `tabSales Invoice`
				WHERE company = %s
					AND due_date < %s
					AND outstanding_amount > 0
					AND custom_billing_cycle = %s
			""",
				[self.company, nowdate(), self.name],
				as_dict=True,
			)

			if overdue_data and overdue_data[0]:
				self.overdue_amount = flt(overdue_data[0].overdue or 0, 2)

	def update_audit_information(self):
		"""Actualiza información de auditoría"""
		if self.is_new():
			self.created_by = frappe.session.user
			self.creation_date = now()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = now()

	@frappe.whitelist()
	def generate_invoices(self):
		"""
		Genera facturas automáticamente para todas las propiedades del ciclo

		Returns:
			dict: Resultado de la generación
		"""
		if self.cycle_status != "Activo":
			frappe.throw(_("Solo se pueden generar facturas para ciclos activos"))

		if self.generation_status == "Completado":
			frappe.throw(_("Las facturas ya han sido generadas para este ciclo"))

		# Actualizar estado de generación
		self.generation_status = "En Proceso"
		self.save()

		generated_count = 0
		failed_count = 0
		errors = []

		try:
			# Obtener todas las propiedades activas
			properties = frappe.db.sql(
				"""
				SELECT name, property_registry, account_name, customer
				FROM `tabProperty Account`
				WHERE company = %s
					AND account_status = 'Activa'
			""",
				[self.company],
				as_dict=True,
			)

			fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)

			for prop in properties:
				try:
					# Crear factura para la propiedad
					invoice = self.create_invoice_for_property(prop, fee_structure_doc)
					if invoice:
						generated_count += 1
				except Exception as e:
					failed_count += 1
					errors.append(f"Propiedad {prop.account_name}: {e!s}")

			# Actualizar contadores
			self.generated_count = generated_count
			self.failed_count = failed_count
			self.generation_status = "Completado" if failed_count == 0 else "Error"

			# Cambiar estado del ciclo
			if self.generation_status == "Completado":
				self.cycle_status = "Facturado"

			self.save()

			return {
				"success": True,
				"generated_count": generated_count,
				"failed_count": failed_count,
				"errors": errors,
			}

		except Exception as e:
			self.generation_status = "Error"
			self.save()
			frappe.throw(_("Error en la generación de facturas: {0}").format(str(e)))

	def create_invoice_for_property(self, property_account, fee_structure):
		"""
		Crea una factura individual para una propiedad

		Args:
			property_account: Datos de la cuenta de propiedad
			fee_structure: Documento de estructura de cuotas

		Returns:
			Sales Invoice: Factura creada
		"""
		if not property_account.customer:
			raise frappe.ValidationError(
				f"La propiedad {property_account.account_name} no tiene cliente asignado"
			)

		# Calcular monto para la propiedad
		property_registry = frappe.get_doc("Property Registry", property_account.property_registry)
		amount = self.calculate_property_amount(property_registry, fee_structure)

		# Crear factura
		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": property_account.customer,
				"company": self.company,
				"posting_date": self.start_date,
				"due_date": self.due_date,
				"custom_billing_cycle": self.name,
				"custom_property_account": property_account.name,
				"items": [
					{
						"item_code": "CUOTA-MANTENIMIENTO",  # Item por defecto
						"item_name": f"Cuota de Mantenimiento - {self.cycle_name}",
						"qty": 1,
						"rate": amount,
						"amount": amount,
					}
				],
			}
		)

		invoice.insert(ignore_permissions=True)
		invoice.submit()

		return invoice

	def calculate_property_amount(self, property_registry, fee_structure):
		"""
		Calcula el monto correspondiente a una propiedad específica

		Args:
			property_registry: Registro de la propiedad
			fee_structure: Estructura de cuotas

		Returns:
			float: Monto calculado
		"""
		if fee_structure.calculation_method == "Monto Fijo":
			return flt(fee_structure.base_amount, 2)

		elif fee_structure.calculation_method == "Por Indiviso":
			return flt((fee_structure.base_amount * property_registry.ownership_percentage) / 100, 2)

		elif fee_structure.calculation_method == "Por M2":
			return flt(fee_structure.base_amount * property_registry.area_sqm, 2)

		else:
			# Método mixto o personalizado
			return flt(fee_structure.base_amount, 2)

	@frappe.whitelist()
	def send_reminders(self):
		"""
		Envía recordatorios de pago para facturas vencidas

		Returns:
			dict: Resultado del envío
		"""
		if not self.send_notifications:
			return {"success": False, "message": "Las notificaciones están deshabilitadas"}

		# Obtener facturas vencidas del ciclo
		overdue_invoices = frappe.db.sql(
			"""
			SELECT name, customer, outstanding_amount, due_date
			FROM `tabSales Invoice`
			WHERE custom_billing_cycle = %s
				AND due_date < %s
				AND outstanding_amount > 0
		""",
			[self.name, nowdate()],
			as_dict=True,
		)

		sent_count = 0
		for invoice in overdue_invoices:
			try:
				# Aquí se implementaría el envío real de notificaciones
				# Por ahora, solo simulamos
				sent_count += 1
			except Exception as e:
				frappe.log_error(f"Error enviando recordatorio para factura {invoice.name}: {e!s}")

		# Actualizar última fecha de recordatorio
		self.last_reminder_sent = now()
		self.save()

		return {"success": True, "sent_count": sent_count, "total_overdue": len(overdue_invoices)}

	@frappe.whitelist()
	def get_cycle_summary(self):
		"""
		Obtiene resumen completo del ciclo

		Returns:
			dict: Resumen del ciclo
		"""
		return {
			"cycle_info": {
				"name": self.name,
				"cycle_name": self.cycle_name,
				"status": self.cycle_status,
				"type": self.cycle_type,
				"frequency": self.billing_frequency,
			},
			"dates": {
				"start_date": self.start_date,
				"end_date": self.end_date,
				"due_date": self.due_date,
				"next_cycle": self.next_cycle_date,
			},
			"financial": {
				"total_amount": self.total_amount,
				"total_invoiced": self.total_invoiced,
				"paid_amount": self.paid_amount,
				"pending_amount": self.pending_amount,
				"overdue_amount": self.overdue_amount,
				"collection_rate": self.collection_rate,
			},
			"properties": {
				"total_properties": self.total_properties,
				"generated_invoices": self.generated_count,
				"failed_invoices": self.failed_count,
			},
			"late_fees": {
				"apply_late_fees": self.apply_late_fees,
				"percentage": self.late_fee_percentage,
				"flat_amount": self.late_fee_flat_amount,
				"after_days": self.late_fee_after_days,
			},
		}

	def on_update(self):
		"""Acciones al actualizar el documento"""
		# Actualizar métricas de cobranza si está facturado
		if self.cycle_status in ["Facturado", "Completado"]:
			self.update_collection_metrics()

	def on_cancel(self):
		"""Acciones al cancelar el documento"""
		# Cancelar facturas asociadas si las hay
		associated_invoices = frappe.db.get_list(
			"Sales Invoice", filters={"custom_billing_cycle": self.name, "docstatus": 1}, fields=["name"]
		)

		for invoice in associated_invoices:
			invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
			if invoice_doc.outstanding_amount == invoice_doc.total:
				# Solo cancelar si no tiene pagos
				invoice_doc.cancel()

		self.cycle_status = "Cancelado"
