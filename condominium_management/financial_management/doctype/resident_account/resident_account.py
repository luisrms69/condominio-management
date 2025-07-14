# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, get_datetime, getdate, now, nowdate


class ResidentAccount(Document):
	"""Cuenta de residente con gestión de saldos a favor y servicios premium"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_property_account()
		self.validate_resident_data()
		self.set_default_values()
		self.generate_account_code()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_financial_limits()
		self.validate_credit_configuration()
		self.calculate_credit_metrics()
		self.update_transaction_summary()
		self.update_audit_information()

	def validate_property_account(self):
		"""Valida la cuenta de propiedad vinculada"""
		if not self.property_account:
			frappe.throw(_("La cuenta de propiedad es obligatoria"))

		# Verificar que la Property Account existe y está activa
		property_account_doc = frappe.get_doc("Property Account", self.property_account)
		if property_account_doc.account_status != "Activa":
			frappe.throw(_("Solo se pueden crear cuentas para propiedades activas"))

		# Establecer company desde la Property Account
		if not self.company:
			self.company = property_account_doc.company

	def validate_resident_data(self):
		"""Valida los datos del residente"""
		if not self.resident_name or len(self.resident_name.strip()) < 2:
			frappe.throw(_("El nombre del residente debe tener al menos 2 caracteres"))

		# Verificar unicidad de residente por propiedad
		existing = frappe.db.get_value(
			"Resident Account",
			{
				"resident_name": self.resident_name,
				"property_account": self.property_account,
				"name": ["!=", self.name],
			},
			"name",
		)
		if existing:
			frappe.throw(
				_("Ya existe una cuenta para este residente en esta propiedad: {0}").format(existing)
			)

		# Validar tipo de residente
		valid_types = ["Propietario", "Inquilino", "Familiar", "Huésped", "Empleado Doméstico"]
		if self.resident_type not in valid_types:
			frappe.throw(_("Tipo de residente inválido. Tipos válidos: {0}").format(", ".join(valid_types)))

	def validate_financial_limits(self):
		"""Valida límites financieros"""
		if self.current_balance is None:
			self.current_balance = 0.0

		if self.credit_limit and self.credit_limit < 0:
			frappe.throw(_("El límite de crédito no puede ser negativo"))

		if self.deposit_amount and self.deposit_amount < 0:
			frappe.throw(_("El monto de depósito no puede ser negativo"))

		if self.spending_limits and self.spending_limits <= 0:
			frappe.throw(_("El límite de gastos diarios debe ser mayor a 0"))

		if self.approval_required_amount and self.approval_required_amount <= 0:
			frappe.throw(_("El monto que requiere aprobación debe ser mayor a 0"))

	def validate_credit_configuration(self):
		"""Valida la configuración de crédito"""
		if self.credit_limit and self.credit_limit > 0:
			# Si hay límite de crédito, validar configuración
			if not self.credit_payment_due_date:
				# Establecer fecha de vencimiento por defecto (30 días)
				self.credit_payment_due_date = add_days(getdate(), 30)

			if not self.credit_payment_status:
				self.credit_payment_status = "Al Día"

		# Validar que la fecha de vencimiento no sea pasada
		if self.credit_payment_due_date and self.credit_payment_due_date < getdate():
			if self.credit_payment_status == "Al Día":
				self.credit_payment_status = "Vencido"

	def calculate_credit_metrics(self):
		"""Calcula métricas de crédito"""
		if self.credit_limit and self.credit_limit > 0:
			# Calcular crédito disponible
			used_credit = abs(self.current_balance) if self.current_balance < 0 else 0
			self.available_credit = flt(self.credit_limit - used_credit, 2)

			# Calcular porcentaje de utilización
			if used_credit > 0:
				self.credit_utilization_percentage = flt((used_credit / self.credit_limit) * 100, 2)
			else:
				self.credit_utilization_percentage = 0
		else:
			self.available_credit = 0
			self.credit_utilization_percentage = 0

		# Calcular cargos pendientes (saldo negativo)
		self.pending_charges = flt(abs(self.current_balance) if self.current_balance < 0 else 0, 2)

	def update_transaction_summary(self):
		"""Actualiza el resumen de transacciones"""
		if not self.account_code:
			self.transaction_summary = "Cuenta nueva - Sin transacciones"
			return

		# Aquí se podría integrar con un DocType de transacciones
		# Por ahora, crear un resumen básico
		summary_lines = [
			f"Cuenta: {self.account_code}",
			f"Residente: {self.resident_name}",
			f"Saldo Actual: ${self.current_balance:,.2f}",
		]

		if self.credit_limit:
			summary_lines.append(f"Límite Crédito: ${self.credit_limit:,.2f}")
			summary_lines.append(f"Crédito Disponible: ${self.available_credit:,.2f}")

		if self.last_transaction_date:
			summary_lines.append(f"Última Transacción: {self.last_transaction_date}")
			if self.last_transaction_amount:
				summary_lines.append(f"Monto: ${self.last_transaction_amount:,.2f}")

		self.transaction_summary = "\n".join(summary_lines)

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

		if not self.resident_type:
			self.resident_type = "Familiar"

		if self.current_balance is None:
			self.current_balance = 0.0

		if self.auto_charge_enabled is None:
			self.auto_charge_enabled = 1

		if self.notifications_enabled is None:
			self.notifications_enabled = 1

		# Límites por defecto según el tipo de residente
		if not self.spending_limits:
			limits_by_type = {
				"Propietario": 5000.0,
				"Inquilino": 3000.0,
				"Familiar": 1500.0,
				"Huésped": 500.0,
				"Empleado Doméstico": 200.0,
			}
			self.spending_limits = limits_by_type.get(self.resident_type, 1000.0)

		if not self.approval_required_amount:
			approval_limits = {
				"Propietario": 10000.0,
				"Inquilino": 5000.0,
				"Familiar": 2000.0,
				"Huésped": 1000.0,
				"Empleado Doméstico": 500.0,
			}
			self.approval_required_amount = approval_limits.get(self.resident_type, 2000.0)

	def generate_account_code(self):
		"""Genera el código de cuenta si no está especificado"""
		if not self.account_code and self.property_account and self.resident_name:
			# Obtener código de Property Account
			property_account_doc = frappe.get_doc("Property Account", self.property_account)

			# Generar código: PROP-CODE + RES + número secuencial
			existing_count = frappe.db.count("Resident Account", {"property_account": self.property_account})

			sequence_number = existing_count + 1
			resident_initials = "".join([name[0].upper() for name in self.resident_name.split()[:2]])

			self.account_code = (
				f"{property_account_doc.account_name}-RES{sequence_number:02d}-{resident_initials}"
			)

	@frappe.whitelist()
	def add_transaction(self, amount, transaction_type, description="", reference_doc=None):
		"""
		Añade una transacción a la cuenta del residente

		Args:
			amount: Monto de la transacción (positivo = crédito, negativo = cargo)
			transaction_type: Tipo de transacción (Pago, Cargo, Transferencia, etc.)
			description: Descripción de la transacción
			reference_doc: Documento de referencia

		Returns:
			dict: Resultado de la transacción
		"""
		amount = flt(amount, 2)

		# Validar que la cuenta esté activa
		if self.account_status != "Activa":
			frappe.throw(_("No se pueden procesar transacciones en cuentas inactivas"))

		# Validar límites para cargos
		if amount < 0:  # Es un cargo
			charge_amount = abs(amount)

			# Verificar límite diario
			if self.spending_limits and charge_amount > self.spending_limits:
				frappe.throw(
					_("El cargo excede el límite diario permitido de ${0:,.2f}").format(self.spending_limits)
				)

			# Verificar si requiere aprobación
			if self.approval_required_amount and charge_amount > self.approval_required_amount:
				frappe.throw(
					_("Cargos superiores a ${0:,.2f} requieren aprobación").format(
						self.approval_required_amount
					)
				)

			# Verificar límite de crédito
			new_balance = self.current_balance + amount
			if self.credit_limit and abs(new_balance) > self.credit_limit and new_balance < 0:
				frappe.throw(_("El cargo excede el límite de crédito disponible"))

		# Procesar la transacción
		old_balance = self.current_balance
		self.current_balance = flt(old_balance + amount, 2)
		self.last_transaction_date = getdate()
		self.last_transaction_amount = amount

		# Actualizar métricas
		self.calculate_credit_metrics()
		self.update_transaction_summary()

		# Guardar cambios
		self.save()

		# Log de la transacción
		self.add_comment(
			"Info",
			_(
				"Transacción procesada: {0} ${1:,.2f}. Saldo anterior: ${2:,.2f}, Nuevo saldo: ${3:,.2f}"
			).format(transaction_type, amount, old_balance, self.current_balance),
		)

		return {
			"success": True,
			"old_balance": old_balance,
			"new_balance": self.current_balance,
			"transaction_amount": amount,
			"available_credit": self.available_credit,
		}

	@frappe.whitelist()
	def transfer_to_property_account(self, amount, description="Transferencia a cuenta principal"):
		"""
		Transfiere saldo a la cuenta de propiedad principal

		Args:
			amount: Monto a transferir
			description: Descripción de la transferencia

		Returns:
			dict: Resultado de la transferencia
		"""
		amount = flt(amount, 2)

		if amount <= 0:
			frappe.throw(_("El monto de transferencia debe ser mayor a 0"))

		if amount > self.current_balance:
			frappe.throw(_("Saldo insuficiente para la transferencia"))

		# Procesar transferencia
		old_balance = self.current_balance
		self.current_balance = flt(old_balance - amount, 2)
		self.last_transaction_date = getdate()
		self.last_transaction_amount = -amount

		# Actualizar métricas
		self.calculate_credit_metrics()
		self.update_transaction_summary()

		# Guardar cambios
		self.save()

		# Log de la transferencia
		self.add_comment("Info", _("Transferencia realizada: ${0:,.2f} a cuenta principal").format(amount))

		return {
			"success": True,
			"transferred_amount": amount,
			"remaining_balance": self.current_balance,
			"property_account": self.property_account,
		}

	@frappe.whitelist()
	def get_spending_summary(self, period_days=30):
		"""
		Obtiene resumen de gastos para un período

		Args:
			period_days: Días hacia atrás para el resumen

		Returns:
			dict: Resumen de gastos
		"""
		# Por ahora, retornar datos básicos
		# En implementación completa, esto consultaría transacciones reales

		return {
			"period_days": period_days,
			"current_balance": self.current_balance,
			"available_credit": self.available_credit,
			"spending_limit": self.spending_limits,
			"utilization_percentage": self.credit_utilization_percentage,
			"account_status": self.account_status,
			"last_transaction": {"date": self.last_transaction_date, "amount": self.last_transaction_amount},
		}

	@frappe.whitelist()
	def request_credit_increase(self, requested_amount, justification):
		"""
		Solicita aumento de límite de crédito

		Args:
			requested_amount: Nuevo límite solicitado
			justification: Justificación de la solicitud

		Returns:
			dict: Resultado de la solicitud
		"""
		requested_amount = flt(requested_amount, 2)

		if requested_amount <= self.credit_limit:
			frappe.throw(_("El nuevo límite debe ser mayor al actual"))

		# Crear comentario con la solicitud
		self.add_comment(
			"Workflow",
			_("Solicitud de aumento de crédito: ${0:,.2f} (actual: ${1:,.2f}). Justificación: {2}").format(
				requested_amount, self.credit_limit or 0, justification
			),
		)

		return {
			"success": True,
			"current_limit": self.credit_limit or 0,
			"requested_limit": requested_amount,
			"status": "Pendiente aprobación",
		}

	def on_update(self):
		"""Acciones al actualizar el documento"""
		# Actualizar loyalty points basado en transacciones
		self.calculate_loyalty_points()

	def calculate_loyalty_points(self):
		"""Calcula puntos de lealtad basado en actividad"""
		# Lógica simple: 1 punto por cada $100 de saldo positivo
		if self.current_balance > 0:
			self.loyalty_points = int(self.current_balance / 100)
		else:
			self.loyalty_points = 0
