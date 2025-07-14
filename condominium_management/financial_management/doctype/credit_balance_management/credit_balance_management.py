# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Credit Balance Management - Módulo de Gestión de Saldos a Favor
==============================================================

DocType para gestión completa de saldos a favor con aplicación automática,
expiración, transferencias y reconciliación con cuentas de propietarios/residentes.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, flt, getdate, now, nowdate


class CreditBalanceManagement(Document):
	"""Credit Balance Management - Gestión de saldos a favor"""

	def before_insert(self):
		"""Validaciones y configuración antes de insertar"""
		self.validate_account_selection()
		self.validate_credit_amount()
		self.set_default_values()
		self.link_customer_account()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_expiration_date()
		self.calculate_remaining_balance()
		self.calculate_days_until_expiry()
		self.validate_approval_requirements()

	def on_update(self):
		"""Acciones después de actualizar"""
		if self.balance_status == "Activo" and self.auto_apply_enabled:
			self.check_auto_application()

		if self.balance_status in ["Aplicado Total", "Expirado"]:
			self.update_related_accounts()

	def validate_account_selection(self):
		"""Validar selección correcta de cuentas"""
		if self.account_type == "Property Account" and not self.property_account:
			frappe.throw(_("Cuenta de Propiedad es obligatoria para créditos de propietarios"))

		if self.account_type == "Resident Account" and not self.resident_account:
			frappe.throw(_("Cuenta de Residente es obligatoria para créditos de residentes"))

		if self.account_type == "Ambos":
			if not self.property_account or not self.resident_account:
				frappe.throw(_("Ambas cuentas son obligatorias para créditos mixtos"))

		# Verificar que las cuentas estén activas
		if self.property_account:
			prop_account = frappe.get_doc("Property Account", self.property_account)
			if prop_account.account_status != "Activa":
				frappe.throw(_("La cuenta de propiedad no está activa"))

		if self.resident_account:
			res_account = frappe.get_doc("Resident Account", self.resident_account)
			if res_account.account_status != "Activa":
				frappe.throw(_("La cuenta de residente no está activa"))

	def validate_credit_amount(self):
		"""Validar monto del crédito"""
		if flt(self.credit_amount) <= 0:
			frappe.throw(_("El monto del crédito debe ser mayor a cero"))

		# Validar límites según tipo de origen
		if self.origin_type == "Sobrepago" and self.overpayment_amount:
			if flt(self.credit_amount) > flt(self.overpayment_amount):
				frappe.throw(_("El monto del crédito no puede exceder el sobrepago original"))

	def validate_expiration_date(self):
		"""Validar fecha de expiración"""
		if self.expiration_date:
			if getdate(self.expiration_date) <= getdate(self.balance_date):
				frappe.throw(_("La fecha de expiración debe ser posterior a la fecha del saldo"))

	def validate_approval_requirements(self):
		"""Validar requerimientos de aprobación"""
		# Montos altos requieren aprobación
		if flt(self.credit_amount) > 10000.0:
			self.requires_approval = 1

		# Ciertos tipos de origen requieren aprobación
		approval_required_types = ["Ajuste Manual", "Error Corrección", "Transferencia"]
		if self.origin_type in approval_required_types:
			self.requires_approval = 1

		# Si requiere aprobación pero no está aprobado, cambiar estado
		if self.requires_approval and not self.approved_by:
			if self.balance_status == "Activo":
				self.balance_status = "Pendiente Aprobación"

	def set_default_values(self):
		"""Establecer valores por defecto"""
		if not self.balance_status:
			self.balance_status = "Activo"

		if not self.priority_level:
			self.priority_level = "Media"

		if not self.balance_date:
			self.balance_date = nowdate()

		# Valores de tracking
		if not self.total_applied:
			self.total_applied = 0.0

		if not self.usage_count:
			self.usage_count = 0

		# Auditoría
		if not self.created_by:
			self.created_by = frappe.session.user
			self.creation_date = now()

		self.last_modified_by = frappe.session.user
		self.last_modified_date = now()

		# Configurar fecha de expiración por defecto (1 año)
		if not self.expiration_date and self.balance_status == "Activo":
			self.expiration_date = add_days(self.balance_date, 365)

	def link_customer_account(self):
		"""Vincular con Customer de ERPNext"""
		try:
			if self.property_account:
				prop_account = frappe.get_doc("Property Account", self.property_account)
				self.customer = prop_account.customer
			elif self.resident_account:
				res_account = frappe.get_doc("Resident Account", self.resident_account)
				# Obtener customer del Property Account asociado
				if res_account.property_account:
					prop_account = frappe.get_doc("Property Account", res_account.property_account)
					self.customer = prop_account.customer
		except Exception as e:
			frappe.logger().warning(f"Error linking customer for credit balance {self.name}: {e}")

	def calculate_remaining_balance(self):
		"""Calcular saldo restante"""
		self.remaining_balance = flt(self.credit_amount) - flt(self.total_applied)

		# Actualizar estado basado en saldo restante
		if flt(self.remaining_balance) <= 0:
			self.balance_status = "Aplicado Total"
		elif flt(self.total_applied) > 0:
			self.balance_status = "Aplicado Parcial"

	def calculate_days_until_expiry(self):
		"""Calcular días hasta expiración"""
		if self.expiration_date:
			self.days_until_expiry = date_diff(self.expiration_date, nowdate())

			# Marcar como expirado si es necesario
			if self.days_until_expiry <= 0 and self.balance_status in ["Activo", "Aplicado Parcial"]:
				self.balance_status = "Expirado"

	def check_auto_application(self):
		"""Verificar y ejecutar aplicación automática"""
		if not self.auto_apply_enabled or flt(self.remaining_balance) <= 0:
			return

		# Buscar facturas pendientes para aplicar automáticamente
		self.find_and_apply_to_invoices()

	def find_and_apply_to_invoices(self):
		"""Buscar facturas pendientes y aplicar crédito automáticamente"""
		if not self.customer:
			return

		# Obtener facturas pendientes del customer
		pending_invoices = frappe.db.sql(
			"""
			SELECT name, outstanding_amount, due_date
			FROM `tabSales Invoice`
			WHERE customer = %s
			AND docstatus = 1
			AND outstanding_amount > 0
			ORDER BY due_date ASC, creation ASC
			LIMIT 5
		""",
			self.customer,
			as_dict=True,
		)

		total_applied_now = 0.0
		remaining_credit = flt(self.remaining_balance)

		for invoice in pending_invoices:
			if remaining_credit <= 0:
				break

			# Aplicar lo que se pueda a esta factura
			applicable_amount = min(remaining_credit, flt(invoice.outstanding_amount))

			if applicable_amount > 0:
				self.apply_credit_to_invoice(invoice.name, applicable_amount)
				total_applied_now += applicable_amount
				remaining_credit -= applicable_amount

		if total_applied_now > 0:
			frappe.logger().info(f"Auto-applied {total_applied_now} from credit balance {self.name}")

	def apply_credit_to_invoice(self, invoice_name, amount):
		"""Aplicar crédito a una factura específica"""
		try:
			# Crear Payment Entry para aplicar el crédito
			payment_entry = frappe.get_doc(
				{
					"doctype": "Payment Entry",
					"payment_type": "Receive",
					"party_type": "Customer",
					"party": self.customer,
					"paid_amount": amount,
					"received_amount": amount,
					"reference_no": f"CREDIT-{self.name}",
					"reference_date": nowdate(),
					"remarks": f"Aplicación automática de saldo a favor desde {self.name}",
					"references": [
						{
							"reference_doctype": "Sales Invoice",
							"reference_name": invoice_name,
							"allocated_amount": amount,
						}
					],
				}
			)

			payment_entry.insert(ignore_permissions=True)
			payment_entry.submit()

			# Actualizar tracking del crédito
			self.total_applied = flt(self.total_applied) + amount
			self.usage_count += 1
			self.last_used_date = nowdate()

			frappe.logger().info(f"Applied {amount} from credit {self.name} to invoice {invoice_name}")

		except Exception as e:
			frappe.logger().error(f"Error applying credit {self.name} to invoice {invoice_name}: {e}")

	def update_related_accounts(self):
		"""Actualizar cuentas relacionadas cuando el crédito se completa"""
		try:
			# Actualizar Property Account
			if self.property_account:
				prop_account = frappe.get_doc("Property Account", self.property_account)
				prop_account.credit_balance = flt(prop_account.credit_balance) - flt(self.credit_amount)
				prop_account.save(ignore_permissions=True)

			# Actualizar Resident Account
			if self.resident_account:
				res_account = frappe.get_doc("Resident Account", self.resident_account)
				res_account.current_balance = flt(res_account.current_balance) - flt(self.credit_amount)
				res_account.save(ignore_permissions=True)

		except Exception as e:
			frappe.logger().error(f"Error updating related accounts for credit {self.name}: {e}")

	@frappe.whitelist()
	def apply_credit_manual(self, invoice_name, amount, notes=None):
		"""Aplicar crédito manualmente a una factura específica"""
		amount = flt(amount)

		if amount <= 0:
			return {"success": False, "message": _("El monto debe ser mayor a cero")}

		if amount > flt(self.remaining_balance):
			return {"success": False, "message": _("El monto excede el saldo disponible")}

		if self.balance_status not in ["Activo", "Aplicado Parcial"]:
			return {"success": False, "message": _("El saldo no está disponible para aplicación")}

		try:
			# Verificar que la factura existe y tiene saldo pendiente
			invoice = frappe.get_doc("Sales Invoice", invoice_name)
			if flt(invoice.outstanding_amount) < amount:
				return {"success": False, "message": _("El monto excede el saldo pendiente de la factura")}

			# Aplicar el crédito
			self.apply_credit_to_invoice(invoice_name, amount)

			# Actualizar este documento
			self.calculate_remaining_balance()
			self.save(ignore_permissions=True)

			# Registrar en notas si se proporciona
			if notes:
				self.notes = f"{self.notes or ''}\n{now()}: Aplicación manual - {notes}"
				self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Crédito aplicado exitosamente"),
				"applied_amount": amount,
				"remaining_balance": self.remaining_balance,
			}

		except Exception as e:
			frappe.logger().error(f"Error in manual credit application {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def transfer_credit(self, target_account_type, target_account, amount, reason=None):
		"""Transferir crédito a otra cuenta"""
		amount = flt(amount)

		if amount <= 0:
			return {"success": False, "message": _("El monto debe ser mayor a cero")}

		if amount > flt(self.remaining_balance):
			return {"success": False, "message": _("El monto excede el saldo disponible")}

		try:
			# Crear nuevo crédito en la cuenta destino
			new_credit = frappe.get_doc(
				{
					"doctype": "Credit Balance Management",
					"balance_date": nowdate(),
					"account_type": target_account_type,
					"property_account": target_account if target_account_type == "Property Account" else None,
					"resident_account": target_account if target_account_type == "Resident Account" else None,
					"credit_amount": amount,
					"origin_type": "Transferencia",
					"origin_reference": self.name,
					"source_type": "Transferencia entre Cuentas",
					"source_description": f"Transferencia desde {self.name}. Razón: {reason or 'No especificada'}",
					"balance_status": "Activo",
					"requires_approval": 1,  # Las transferencias requieren aprobación
				}
			)

			new_credit.insert(ignore_permissions=True)

			# Actualizar este crédito
			self.total_applied = flt(self.total_applied) + amount
			self.calculate_remaining_balance()
			self.usage_count += 1
			self.last_used_date = nowdate()

			# Registrar transferencia en notas
			transfer_note = f"{now()}: Transferencia de {amount} a {target_account_type} {target_account}"
			if reason:
				transfer_note += f" - Razón: {reason}"
			self.notes = f"{self.notes or ''}\n{transfer_note}"

			self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Transferencia exitosa"),
				"new_credit_id": new_credit.name,
				"transferred_amount": amount,
				"remaining_balance": self.remaining_balance,
			}

		except Exception as e:
			frappe.logger().error(f"Error transferring credit {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def request_refund(self, refund_amount, reason, bank_details=None):
		"""Solicitar reembolso del saldo a favor"""
		refund_amount = flt(refund_amount)

		if not self.refund_eligible:
			return {"success": False, "message": _("Este saldo no es elegible para reembolso")}

		if refund_amount <= 0:
			return {"success": False, "message": _("El monto debe ser mayor a cero")}

		if refund_amount > flt(self.remaining_balance):
			return {"success": False, "message": _("El monto excede el saldo disponible")}

		try:
			# Marcar como solicitado para reembolso
			self.refund_requested = 1
			self.requires_approval = 1

			# Registrar solicitud en notas
			refund_note = f"{now()}: Solicitud de reembolso por {refund_amount}"
			refund_note += f"\nRazón: {reason}"
			if bank_details:
				refund_note += f"\nDetalles bancarios: {bank_details}"

			self.notes = f"{self.notes or ''}\n{refund_note}"
			self.save(ignore_permissions=True)

			# Crear tarea o notificación para administración
			# (esto se podría integrar con un sistema de tareas)

			return {
				"success": True,
				"message": _("Solicitud de reembolso registrada exitosamente"),
				"refund_amount": refund_amount,
				"status": "Pendiente Aprobación",
			}

		except Exception as e:
			frappe.logger().error(f"Error requesting refund for credit {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def approve_credit(self, approval_notes=None):
		"""Aprobar el saldo a favor"""
		if not self.requires_approval:
			return {"success": False, "message": _("Este saldo no requiere aprobación")}

		try:
			self.approved_by = frappe.session.user
			self.approval_date = now()
			self.requires_approval = 0

			# Cambiar estado a activo si estaba pendiente
			if self.balance_status == "Pendiente Aprobación":
				self.balance_status = "Activo"

			# Registrar aprobación en notas
			approval_note = f"{now()}: Aprobado por {frappe.session.user}"
			if approval_notes:
				approval_note += f" - Notas: {approval_notes}"

			self.notes = f"{self.notes or ''}\n{approval_note}"
			self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Saldo aprobado exitosamente"),
				"approved_by": self.approved_by,
				"approval_date": self.approval_date,
			}

		except Exception as e:
			frappe.logger().error(f"Error approving credit {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def extend_expiration(self, days_extension, reason=None):
		"""Extender fecha de expiración"""
		if not self.expiration_date:
			return {"success": False, "message": _("Este saldo no tiene fecha de expiración configurada")}

		if self.balance_status == "Expirado":
			return {"success": False, "message": _("No se puede extender un saldo ya expirado")}

		try:
			old_expiration = self.expiration_date
			self.expiration_date = add_days(self.expiration_date, days_extension)
			self.calculate_days_until_expiry()

			# Registrar extensión en notas
			extension_note = f"{now()}: Expiración extendida {days_extension} días"
			extension_note += f"\nDe: {old_expiration} A: {self.expiration_date}"
			if reason:
				extension_note += f"\nRazón: {reason}"

			self.notes = f"{self.notes or ''}\n{extension_note}"
			self.save(ignore_permissions=True)

			return {
				"success": True,
				"message": _("Expiración extendida exitosamente"),
				"new_expiration_date": self.expiration_date,
				"days_until_expiry": self.days_until_expiry,
			}

		except Exception as e:
			frappe.logger().error(f"Error extending expiration for credit {self.name}: {e}")
			return {"success": False, "message": str(e)}

	@frappe.whitelist()
	def get_credit_summary(self):
		"""Obtener resumen del saldo a favor"""
		return {
			"credit_info": {
				"credit_amount": self.credit_amount,
				"remaining_balance": self.remaining_balance,
				"total_applied": self.total_applied,
				"balance_status": self.balance_status,
				"priority_level": self.priority_level,
			},
			"account_info": {
				"account_type": self.account_type,
				"property_account": self.property_account,
				"resident_account": self.resident_account,
				"customer": self.customer,
			},
			"usage_info": {
				"usage_count": self.usage_count,
				"last_used_date": self.last_used_date,
				"auto_apply_enabled": self.auto_apply_enabled,
			},
			"expiration_info": {
				"expiration_date": self.expiration_date,
				"days_until_expiry": self.days_until_expiry,
				"auto_extend_enabled": self.auto_extend_enabled,
			},
			"approval_info": {
				"requires_approval": self.requires_approval,
				"approved_by": self.approved_by,
				"approval_date": self.approval_date,
			},
		}
