# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TargetCompanySync(Document):
	"""
	Configuración de empresa destino para procesos de sincronización de datos.

	Funcionalidades principales:
	- Definición de empresas destino en configuraciones de sincronización
	- Control de estado de sincronización por empresa individual
	- Registro de contadores de errores y éxitos por empresa destino
	- Gestión de configuraciones específicas de conexión por empresa
	- Validación de contadores de errores no negativos
	- Seguimiento de última sincronización exitosa por empresa

	Parámetros importantes:
	    target_company (Link): Empresa destino para la sincronización
	    is_enabled (Check): Indica si la sincronización está habilitada para esta empresa
	    sync_status (Select): Estado actual de sincronización para esta empresa
	    last_sync_date (Datetime): Fecha y hora de última sincronización exitosa
	    sync_errors (Int): Contador de errores de sincronización acumulados
	    connection_settings (Text): Configuraciones específicas de conexión en JSON
	    priority (Select): Prioridad de sincronización para esta empresa

	Errores comunes:
	    ValidationError: Cuando contador de errores de sincronización es negativo

	Ejemplo de uso:
	    target = frappe.new_doc("Target Company Sync")
	    target.target_company = "Condominio ABC"
	    target.is_enabled = 1
	    target.sync_errors = 0
	    target.priority = "Alta"
	    target.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de configuración de empresa destino.

		Valida que los contadores de errores sean valores lógicos.
		"""
		self.validate_sync_errors()

	def validate_sync_errors(self):
		"""
		Valida que el contador de errores de sincronización no sea negativo.

		Los contadores de errores deben ser valores positivos o cero,
		nunca negativos ya que representan cantidad de errores ocurridos.

		Raises:
		    ValidationError: Si el contador de errores de sincronización es negativo
		"""
		if self.sync_errors and self.sync_errors < 0:
			frappe.throw("El contador de errores de sincronización no puede ser negativo.")
