# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class ServiceManagementContract(Document):
	"""
	Gestión de contratos de servicio entre empresas administradoras y condominios.

	Funcionalidades principales:
	- Administración completa de contratos de gestión de servicios
	- Validación de fechas y términos financieros
	- Control de empresas proveedoras y clientes
	- Gestión de sincronización de datos entre empresas
	- Configuración de ciclos de facturación y términos de pago
	- Seguimiento de estados de contrato (Activo, Suspendido, Terminado)

	Parámetros importantes:
	    contract_name (str): Nombre único del contrato de gestión
	    service_provider (Link): Empresa administradora que brinda el servicio
	    client_condominium (Link): Condominio cliente que recibe el servicio
	    contract_start (Date): Fecha de inicio del contrato
	    contract_end (Date): Fecha de finalización del contrato
	    monthly_fee (Currency): Tarifa mensual del servicio en MXN
	    billing_cycle (Select): Frecuencia de facturación (Mensual, Trimestral, etc.)
	    contract_status (Select): Estado actual (Activo, Suspendido, Terminado)
	    data_sharing_level (Select): Nivel de compartición de datos (Completo, Limitado, Solo Lectura)

	Errores comunes:
	    ValidationError: Cuando fechas de contrato son inconsistentes
	    ValidationError: Cuando proveedor y cliente son la misma empresa
	    ValidationError: Cuando tarifa mensual es negativa

	Ejemplo de uso:
	    contrato = frappe.new_doc("Service Management Contract")
	    contrato.contract_name = "Gestión Condominio ABC"
	    contrato.service_provider = "Administradora XYZ"
	    contrato.client_condominium = "Condominio ABC"
	    contrato.contract_start = "2025-01-01"
	    contrato.monthly_fee = 15000.00
	    contrato.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones del contrato de gestión de servicios.

		Valida fechas, empresas involucradas y términos financieros antes de guardar.
		"""
		self.validate_contract_dates()
		self.validate_companies()
		self.validate_financial_terms()

	def validate_contract_dates(self):
		"""
		Valida que las fechas del contrato sean lógicamente consistentes.

		Raises:
		    ValidationError: Si fecha de fin es anterior o igual a fecha de inicio
		"""
		if self.contract_start and self.contract_end:
			if getdate(self.contract_end) <= getdate(self.contract_start):
				frappe.throw(_("La fecha de fin del contrato debe ser posterior a la fecha de inicio."))

		if self.contract_start and getdate(self.contract_start) < getdate(today()):
			frappe.msgprint(_("La fecha de inicio del contrato está en el pasado."), indicator="orange")

	def validate_companies(self):
		"""
		Valida que la empresa proveedora y el condominio cliente sean diferentes.

		Raises:
		    ValidationError: Si proveedor y cliente son la misma empresa
		"""
		if self.service_provider == self.client_condominium:
			frappe.throw(
				_("La empresa administradora y el condominio cliente no pueden ser la misma entidad.")
			)

	def validate_financial_terms(self):
		"""
		Valida que los términos financieros del contrato sean válidos.

		Raises:
		    ValidationError: Si la tarifa mensual es negativa
		"""
		if self.monthly_fee and self.monthly_fee < 0:
			frappe.throw(_("La tarifa mensual no puede ser negativa."))

	def before_save(self):
		"""
		Procesos automáticos antes de guardar el documento.

		Establece moneda por defecto si no está especificada.
		"""
		# Auto-establecer moneda MXN si no está proporcionada
		if not self.currency:
			self.currency = "MXN"

	def on_submit(self):
		"""
		Procesos automáticos al someter el contrato para aprobación.

		Cambia el estado del contrato a 'Activo' automáticamente.
		"""
		self.contract_status = "Activo"
		self.save()

	def on_cancel(self):
		"""
		Procesos automáticos al cancelar el contrato.

		Cambia el estado del contrato a 'Terminado' automáticamente.
		"""
		self.contract_status = "Terminado"
		self.save()
