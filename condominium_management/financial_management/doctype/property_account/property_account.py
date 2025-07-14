# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, get_datetime, getdate, now, nowdate


class PropertyAccount(Document):
	"""Cuenta de propiedad con integración ERPNext Customer"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_property_registry()
		self.validate_customer_link()
		self.set_default_values()
		self.generate_account_name()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_billing_configuration()
		self.validate_financial_data()
		self.calculate_pending_amount()
		self.update_payment_summary()
		self.update_audit_information()

	def validate_property_registry(self):
		"""Valida el registro de propiedad vinculado"""
		if not self.property_registry:
			frappe.throw(_("El registro de propiedad es obligatorio"))

		# Verificar que la propiedad existe y está activa
		property_doc = frappe.get_doc("Property Registry", self.property_registry)
		if property_doc.status != "Activa":
			frappe.throw(_("Solo se pueden crear cuentas para propiedades activas"))

		# Verificar unicidad por propiedad
		existing = frappe.db.get_value(
			"Property Account",
			{"property_registry": self.property_registry, "name": ["!=", self.name]},
			"name",
		)
		if existing:
			frappe.throw(_("Ya existe una cuenta para esta propiedad: {0}").format(existing))

	def validate_customer_link(self):
		"""Valida la vinculación con Customer de ERPNext"""
		if not self.customer:
			frappe.throw(_("El cliente de ERPNext es obligatorio"))

		# Verificar que el Customer existe
		if not frappe.db.exists("Customer", self.customer):
			frappe.throw(_("El cliente {0} no existe en ERPNext").format(self.customer))

		# Verificar que el Customer pertenece al Customer Group correcto
		customer_doc = frappe.get_doc("Customer", self.customer)
		valid_groups = ["Condóminos", "Residentes"]
		if customer_doc.customer_group not in valid_groups:
			frappe.throw(_("El cliente debe pertenecer a los grupos: {0}").format(", ".join(valid_groups)))

	def validate_billing_configuration(self):
		"""Valida la configuración de facturación"""
		if not self.billing_frequency:
			frappe.throw(_("La frecuencia de facturación es obligatoria"))

		if not self.billing_start_date:
			frappe.throw(_("La fecha de inicio de facturación es obligatoria"))

		if self.billing_start_date > getdate():
			frappe.throw(_("La fecha de inicio no puede ser futura"))

		# Validar día de facturación
		if not self.billing_day or self.billing_day < 1 or self.billing_day > 31:
			frappe.throw(_("El día de facturación debe estar entre 1 y 31"))

		# Validar estructura de cuotas si está especificada
		if self.fee_structure:
			fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)
			if not fee_structure_doc.is_active:
				frappe.throw(_("La estructura de cuotas debe estar activa"))

	def validate_financial_data(self):
		"""Valida los datos financieros"""
		if self.current_balance is None:
			self.current_balance = 0.0

		if self.credit_balance and self.credit_balance < 0:
			frappe.throw(_("El saldo a favor no puede ser negativo"))

		# Validar montos de último pago
		if self.last_payment_amount and self.last_payment_amount < 0:
			frappe.throw(_("El monto del último pago no puede ser negativo"))

		if self.last_payment_amount and not self.last_payment_date:
			frappe.throw(_("Si hay monto de último pago, debe especificar la fecha"))

	def calculate_pending_amount(self):
		"""Calcula el monto pendiente basado en facturas"""
		if not self.customer:
			self.pending_amount = 0
			return

		# Obtener facturas pendientes del Customer
		pending_invoices = frappe.db.sql(
			"""
			SELECT SUM(outstanding_amount)
			FROM `tabSales Invoice`
			WHERE customer = %s
				AND docstatus = 1
				AND outstanding_amount > 0
		""",
			(self.customer,),
		)

		self.pending_amount = flt(pending_invoices[0][0] if pending_invoices[0][0] else 0, 2)

	def update_payment_summary(self):
		"""Actualiza los resúmenes de pagos"""
		if not self.customer:
			return

		# Calcular montos YTD
		current_year = getdate().year

		# Total pagado este año
		ytd_payments = frappe.db.sql(
			"""
			SELECT SUM(paid_amount)
			FROM `tabPayment Entry`
			WHERE party = %s
				AND party_type = 'Customer'
				AND docstatus = 1
				AND YEAR(posting_date) = %s
		""",
			(self.customer, current_year),
		)

		self.ytd_paid_amount = flt(ytd_payments[0][0] if ytd_payments[0][0] else 0, 2)

		# Total facturado este año
		ytd_invoiced = frappe.db.sql(
			"""
			SELECT SUM(grand_total)
			FROM `tabSales Invoice`
			WHERE customer = %s
				AND docstatus = 1
				AND YEAR(posting_date) = %s
		""",
			(self.customer, current_year),
		)

		self.total_invoiced_ytd = flt(ytd_invoiced[0][0] if ytd_invoiced[0][0] else 0, 2)

		# Calcular tasa de éxito de pagos
		if self.total_invoiced_ytd > 0:
			self.payment_success_rate = flt((self.ytd_paid_amount / self.total_invoiced_ytd) * 100, 2)
		else:
			self.payment_success_rate = 0

		# Calcular cuota mensual actual
		self.calculate_monthly_fee()

		# Calcular retraso promedio de pagos
		self.calculate_average_payment_delay()

	def calculate_monthly_fee(self):
		"""Calcula la cuota mensual basada en la estructura activa"""
		if not self.fee_structure or not self.property_registry:
			self.monthly_fee_amount = 0
			return

		try:
			fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)
			fee_calculation = fee_structure_doc.calculate_fee_for_property(self.property_registry)
			self.monthly_fee_amount = flt(fee_calculation.get("total_fee", 0), 2)
		except Exception:
			self.monthly_fee_amount = 0

	def calculate_average_payment_delay(self):
		"""Calcula el retraso promedio de pagos"""
		if not self.customer:
			self.average_payment_delay = 0
			return

		# Obtener pagos de los últimos 12 meses
		twelve_months_ago = add_days(getdate(), -365)

		delays = frappe.db.sql(
			"""
			SELECT DATEDIFF(pe.posting_date, si.due_date) as delay
			FROM `tabPayment Entry` pe
			INNER JOIN `tabPayment Entry Reference` per ON pe.name = per.parent
			INNER JOIN `tabSales Invoice` si ON per.reference_name = si.name
			WHERE pe.party = %s
				AND pe.party_type = 'Customer'
				AND pe.docstatus = 1
				AND pe.posting_date >= %s
				AND si.due_date IS NOT NULL
				AND DATEDIFF(pe.posting_date, si.due_date) >= 0
		""",
			(self.customer, twelve_months_ago),
		)

		if delays:
			total_delay = sum([d[0] for d in delays if d[0] > 0])
			count_delayed = len([d for d in delays if d[0] > 0])
			self.average_payment_delay = flt(total_delay / count_delayed if count_delayed > 0 else 0, 0)
		else:
			self.average_payment_delay = 0

	def update_audit_information(self):
		"""Actualiza información de auditoría"""
		if self.is_new():
			self.created_by = frappe.session.user
			self.creation_date = now()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = now()

	def set_default_values(self):
		"""Establece valores por defecto"""
		if not self.account_status:
			self.account_status = "Activa"

		if not self.billing_frequency:
			self.billing_frequency = "Mensual"

		if not self.billing_day:
			self.billing_day = 1

		if not self.billing_start_date:
			self.billing_start_date = getdate()

		if self.current_balance is None:
			self.current_balance = 0.0

		# Auto-generar facturas por defecto
		if self.auto_generate_invoices is None:
			self.auto_generate_invoices = 1

		# Elegible para descuentos por defecto
		if self.discount_eligibility is None:
			self.discount_eligibility = 1

	def generate_account_name(self):
		"""Genera el nombre de cuenta si no está especificado"""
		if not self.account_name and self.property_registry:
			property_doc = frappe.get_doc("Property Registry", self.property_registry)
			self.account_name = f"CUENTA-{property_doc.property_number or property_doc.name}"

	@frappe.whitelist()
	def create_customer_if_not_exists(self, customer_name, customer_group="Condóminos"):
		"""
		Crea un Customer en ERPNext si no existe

		Args:
			customer_name: Nombre del cliente
			customer_group: Grupo del cliente (Condóminos/Residentes)

		Returns:
			str: Nombre del Customer creado
		"""
		if frappe.db.exists("Customer", customer_name):
			return customer_name

		# Crear Customer
		customer_doc = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_group": customer_group,
				"territory": "Mexico",  # Default territory
				"customer_type": "Individual",
			}
		)
		customer_doc.insert()

		return customer_doc.name

	@frappe.whitelist()
	def get_outstanding_invoices(self):
		"""
		Obtiene las facturas pendientes de esta cuenta

		Returns:
			list: Lista de facturas pendientes
		"""
		if not self.customer:
			return []

		invoices = frappe.db.sql(
			"""
			SELECT
				name,
				posting_date,
				due_date,
				grand_total,
				outstanding_amount,
				DATEDIFF(CURDATE(), due_date) as days_overdue
			FROM `tabSales Invoice`
			WHERE customer = %s
				AND docstatus = 1
				AND outstanding_amount > 0
			ORDER BY due_date ASC
		""",
			(self.customer,),
			as_dict=True,
		)

		return invoices

	@frappe.whitelist()
	def get_payment_history(self, limit=10):
		"""
		Obtiene el historial de pagos de esta cuenta

		Args:
			limit: Número máximo de registros

		Returns:
			list: Lista de pagos
		"""
		if not self.customer:
			return []

		payments = frappe.db.sql(
			"""
			SELECT
				pe.name,
				pe.posting_date,
				pe.paid_amount,
				pe.mode_of_payment,
				pe.reference_no,
				pe.reference_date
			FROM `tabPayment Entry` pe
			WHERE pe.party = %s
				AND pe.party_type = 'Customer'
				AND pe.docstatus = 1
			ORDER BY pe.posting_date DESC
			LIMIT %s
		""",
			(self.customer, limit),
			as_dict=True,
		)

		return payments

	@frappe.whitelist()
	def generate_monthly_invoice(self, posting_date=None):
		"""
		Genera factura mensual para esta cuenta

		Args:
			posting_date: Fecha de la factura (opcional)

		Returns:
			str: Nombre de la factura creada
		"""
		if not self.fee_structure or not self.customer:
			frappe.throw(_("Se requiere estructura de cuotas y cliente para generar factura"))

		if not posting_date:
			posting_date = getdate()

		# Calcular cuota
		fee_structure_doc = frappe.get_doc("Fee Structure", self.fee_structure)
		fee_calculation = fee_structure_doc.calculate_fee_for_property(self.property_registry)

		# Crear Sales Invoice
		invoice_doc = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": self.customer,
				"posting_date": posting_date,
				"due_date": add_days(posting_date, 30),  # 30 días para pagar
				"company": self.company,
				"items": [
					{
						"item_code": "CUOTA_MANTENIMIENTO",  # Item debe existir
						"qty": 1,
						"rate": fee_calculation["total_fee"],
						"description": f"Cuota mensual - {self.property_registry}",
					}
				],
			}
		)

		invoice_doc.insert()
		invoice_doc.submit()

		# Actualizar última factura generada
		self.add_comment("Info", _("Factura generada: {0}").format(invoice_doc.name))

		return invoice_doc.name

	def on_update(self):
		"""Acciones al actualizar el documento"""
		# Actualizar resumen de historial de pagos
		self.update_payment_history_summary()

	def update_payment_history_summary(self):
		"""Actualiza el resumen textual del historial de pagos"""
		if not self.customer:
			self.payment_history_summary = "No hay cliente vinculado"
			return

		recent_payments = self.get_payment_history(5)
		if not recent_payments:
			self.payment_history_summary = "No hay pagos registrados"
			return

		summary_lines = ["Últimos 5 pagos:"]
		for payment in recent_payments:
			summary_lines.append(
				f"• {payment.posting_date}: ${payment.paid_amount:,.2f} ({payment.mode_of_payment or 'N/A'})"
			)

		self.payment_history_summary = "\n".join(summary_lines)
