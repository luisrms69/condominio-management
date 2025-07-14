# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Payment Collection - Módulo de Recaudación de Pagos
==================================================

DocType para gestión completa de pagos con integración ERPNext Payment Entry
y reconciliación automática con facturas y cuentas de propietarios/residentes.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now, nowdate


class PaymentCollection(Document):
	"""Payment Collection - Gestión de recaudación de pagos"""

	def before_insert(self):
		"""Validaciones y configuración antes de insertar"""
		self.validate_account_selection()
		self.validate_payment_method()
		self.set_default_values()
		self.generate_confirmation_number()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_payment_amount()
		self.validate_reference_uniqueness()
		self.calculate_financial_details()

	def on_update(self):
		"""Acciones después de actualizar"""
		if self.payment_status == "Procesado":
			self.process_payment()
			self.update_account_balances()
			self.create_payment_entry()

	def validate_account_selection(self):
		"""Validar selección correcta de cuentas"""
		if self.account_type == "Propietario" and not self.property_account:
			frappe.throw(_("Cuenta de Propiedad es obligatoria para pagos de propietarios"))

		if self.account_type == "Residente" and not self.resident_account:
			frappe.throw(_("Cuenta de Residente es obligatoria para pagos de residentes"))

		if self.account_type == "Ambos":
			if not self.property_account or not self.resident_account:
				frappe.throw(_("Ambas cuentas son obligatorias para pagos mixtos"))

		# Verificar que las cuentas estén activas
		if self.property_account:
			prop_account = frappe.get_doc("Property Account", self.property_account)
			if prop_account.account_status != "Activa":
				frappe.throw(_("La cuenta de propiedad no está activa"))

		if self.resident_account:
			res_account = frappe.get_doc("Resident Account", self.resident_account)
			if res_account.account_status != "Activa":
				frappe.throw(_("La cuenta de residente no está activa"))

	def validate_payment_method(self):
		"""Validar método de pago y campos requeridos"""
		bank_methods = ["Transferencia Bancaria", "Depósito", "Cheque"]

		if self.payment_method in bank_methods:
			if not self.bank_name or not self.transaction_reference:
				frappe.throw(_("Banco y referencia son obligatorios para {0}").format(self.payment_method))

		if self.payment_method == "Cheque" and not self.reference_number:
			frappe.throw(_("Número de cheque es obligatorio"))

		if self.payment_method in ["Tarjeta de Crédito", "Tarjeta de Débito", "Pago en Línea"]:
			if not self.transaction_reference:
				frappe.throw(_("Referencia de transacción es obligatoria"))

	def validate_payment_amount(self):
		"""Validar monto del pago"""
		if flt(self.payment_amount) <= 0:
			frappe.throw(_("El monto del pago debe ser mayor a cero"))

		# Validar límites según tipo de cuenta
		if self.resident_account:
			res_account = frappe.get_doc("Resident Account", self.resident_account)
			if flt(self.payment_amount) > flt(res_account.spending_limits):
				if not res_account.approval_required_amount or flt(self.payment_amount) > flt(
					res_account.approval_required_amount
				):
					self.requires_verification = 1

	def validate_reference_uniqueness(self):
		"""Validar unicidad de número de referencia"""
		if self.reference_number:
			existing = frappe.db.exists(
				"Payment Collection", {"reference_number": self.reference_number, "name": ["!=", self.name]}
			)
			if existing:
				frappe.throw(_("El número de referencia {0} ya existe").format(self.reference_number))

	def set_default_values(self):
		"""Establecer valores por defecto"""
		if not self.payment_status:
			self.payment_status = "Pendiente"

		if not self.reconciliation_status:
			self.reconciliation_status = "Pendiente"

		if not self.original_amount:
			self.original_amount = self.payment_amount

		if not self.payment_date:
			self.payment_date = nowdate()

		# Auditoría
		if not self.created_by:
			self.created_by = frappe.session.user
			self.creation_date = now()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = now()

	def generate_confirmation_number(self):
		"""Generar número de confirmación único"""
		if not self.confirmation_number:
			prefix = "CONF"
			date_part = getdate().strftime("%Y%m%d")
			sequence = frappe.db.count("Payment Collection", {"payment_date": self.payment_date}) + 1
			self.confirmation_number = f"{prefix}{date_part}{sequence:04d}"

	def calculate_financial_details(self):
		"""Calcular detalles financieros del pago"""
		self.applied_amount = flt(self.payment_amount)

		# Aplicar descuentos
		if flt(self.discount_amount) > 0:
			self.applied_amount -= flt(self.discount_amount)

		# Aplicar recargos por mora
		if flt(self.late_fee_amount) > 0:
			self.applied_amount += flt(self.late_fee_amount)

		# Aplicar créditos
		if flt(self.credit_applied) > 0:
			self.applied_amount -= flt(self.credit_applied)

		# Validar que el monto aplicado sea positivo
		if flt(self.applied_amount) < 0:
			frappe.throw(_("El monto aplicado no puede ser negativo"))

	@frappe.whitelist()
	def process_payment(self):
		"""Procesar el pago y actualizar estados"""
		if self.payment_status != "Procesado":
			frappe.throw(_("El pago debe estar en estado 'Procesado'"))

		try:
			# Actualizar información de procesamiento
			self.processed_date = now()
			self.processed_by = frappe.session.user

			# Reconciliar con factura si existe
			if self.invoice_reference:
				self.reconcile_with_invoice()

			# Marcar como conciliado
			self.reconciliation_status = "Conciliado"

			# Log del procesamiento
			frappe.logger().info(f"Pago {self.name} procesado exitosamente por {frappe.session.user}")

			return {"success": True, "message": _("Pago procesado exitosamente")}

		except Exception as e:
			frappe.logger().error(f"Error procesando pago {self.name}: {e}")
			self.payment_status = "Rechazado"
			self.reconciliation_status = "Discrepancia"
			return {"success": False, "message": str(e)}

	def reconcile_with_invoice(self):
		"""Reconciliar pago con factura de ERPNext"""
		if not self.invoice_reference:
			return

		try:
			invoice = frappe.get_doc("Sales Invoice", self.invoice_reference)

			# Verificar que la factura esté pendiente
			if invoice.status != "Unpaid":
				frappe.logger().warning(f"Factura {self.invoice_reference} no está pendiente de pago")
				return

			# Crear Payment Entry en ERPNext
			payment_entry = frappe.get_doc(
				{
					"doctype": "Payment Entry",
					"payment_type": "Receive",
					"party_type": "Customer",
					"party": invoice.customer,
					"paid_amount": self.applied_amount,
					"received_amount": self.applied_amount,
					"target_exchange_rate": 1,
					"reference_no": self.reference_number or self.confirmation_number,
					"reference_date": self.payment_date,
					"references": [
						{
							"reference_doctype": "Sales Invoice",
							"reference_name": self.invoice_reference,
							"allocated_amount": self.applied_amount,
						}
					],
				}
			)

			payment_entry.insert(ignore_permissions=True)
			payment_entry.submit()

			frappe.logger().info(f"Payment Entry {payment_entry.name} creado para pago {self.name}")

		except Exception as e:
			frappe.logger().error(
				f"Error reconciliando pago {self.name} con factura {self.invoice_reference}: {e}"
			)
			raise

	def update_account_balances(self):
		"""Actualizar balances de las cuentas"""
		try:
			# Actualizar Property Account
			if self.property_account:
				prop_account = frappe.get_doc("Property Account", self.property_account)
				prop_account.current_balance = flt(prop_account.current_balance) + flt(self.applied_amount)
				prop_account.save(ignore_permissions=True)

			# Actualizar Resident Account
			if self.resident_account:
				res_account = frappe.get_doc("Resident Account", self.resident_account)
				res_account.current_balance = flt(res_account.current_balance) + flt(self.applied_amount)
				res_account.save(ignore_permissions=True)

			frappe.db.commit()

		except Exception as e:
			frappe.logger().error(f"Error actualizando balances para pago {self.name}: {e}")
			raise

	def create_payment_entry(self):
		"""Crear Payment Entry en ERPNext si no existe"""
		if not self.invoice_reference:
			return

		# Verificar si ya existe un Payment Entry
		existing_pe = frappe.db.exists("Payment Entry", {"reference_no": self.confirmation_number})
		if existing_pe:
			return

		try:
			# Obtener información del customer
			customer = None
			if self.property_account:
				prop_account = frappe.get_doc("Property Account", self.property_account)
				customer = prop_account.customer

			if not customer:
				frappe.logger().warning(f"No se encontró customer para pago {self.name}")
				return

			# Crear Payment Entry
			payment_entry = frappe.get_doc(
				{
					"doctype": "Payment Entry",
					"payment_type": "Receive",
					"party_type": "Customer",
					"party": customer,
					"paid_amount": self.applied_amount,
					"received_amount": self.applied_amount,
					"reference_no": self.confirmation_number,
					"reference_date": self.payment_date,
					"remarks": f"Pago procesado desde Payment Collection {self.name}",
				}
			)

			payment_entry.insert(ignore_permissions=True)
			frappe.logger().info(f"Payment Entry {payment_entry.name} creado para pago {self.name}")

		except Exception as e:
			frappe.logger().error(f"Error creando Payment Entry para pago {self.name}: {e}")

	@frappe.whitelist()
	def get_payment_summary(self):
		"""Obtener resumen del pago"""
		return {
			"payment_info": {
				"confirmation_number": self.confirmation_number,
				"payment_date": self.payment_date,
				"payment_amount": self.payment_amount,
				"applied_amount": self.applied_amount,
				"payment_method": self.payment_method,
				"payment_status": self.payment_status,
			},
			"account_info": {
				"account_type": self.account_type,
				"property_account": self.property_account,
				"resident_account": self.resident_account,
			},
			"reconciliation_info": {
				"reconciliation_status": self.reconciliation_status,
				"invoice_reference": self.invoice_reference,
				"billing_cycle": self.billing_cycle,
			},
			"processing_info": {
				"processed_date": self.processed_date,
				"processed_by": self.processed_by,
				"verification_required": self.requires_verification,
			},
		}

	@frappe.whitelist()
	def verify_payment(self, verification_notes=None):
		"""Verificar el pago manualmente"""
		if not self.requires_verification:
			return {"success": False, "message": _("Este pago no requiere verificación")}

		try:
			self.verified_by = frappe.session.user
			self.verification_date = now()
			self.verification_notes = verification_notes or ""
			self.requires_verification = 0

			if self.payment_status == "Pendiente":
				self.payment_status = "Procesado"

			self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Pago verificado exitosamente"),
				"verified_by": self.verified_by,
				"verification_date": self.verification_date,
			}

		except Exception as e:
			frappe.logger().error(f"Error verificando pago {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def cancel_payment(self, reason=None):
		"""Cancelar el pago"""
		if self.payment_status == "Procesado":
			frappe.throw(_("No se puede cancelar un pago ya procesado"))

		try:
			self.payment_status = "Cancelado"
			self.reconciliation_status = "Cancelado"

			if reason:
				self.payment_notes = f"{self.payment_notes or ''}\nCancelación: {reason}"

			self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Pago cancelado exitosamente"),
				"cancelled_by": frappe.session.user,
				"cancellation_date": now(),
			}

		except Exception as e:
			frappe.logger().error(f"Error cancelando pago {self.name}: {e}")
			return {"success": False, "message": str(e)}
