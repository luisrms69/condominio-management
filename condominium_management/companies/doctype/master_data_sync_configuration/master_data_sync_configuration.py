# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class MasterDataSyncConfiguration(Document):
	"""
	Configuración principal para sincronización de datos maestros entre empresas.

	Funcionalidades principales:
	- Configuración completa de sincronización de datos entre empresas
	- Definición de empresa origen y múltiples empresas destino
	- Control de tipos de datos a sincronizar con configuraciones específicas
	- Gestión de estados de sincronización y seguimiento de errores
	- Validación de configuraciones para evitar conflictos
	- Ejecución automática de procesos de sincronización programados

	Parámetros importantes:
	    sync_name (Data): Nombre único de la configuración de sincronización
	    source_company (Link): Empresa origen de los datos a sincronizar
	    target_companies (Table): Lista de empresas destino para la sincronización
	    sync_data_types (Table): Tipos de datos específicos a sincronizar
	    is_active (Check): Indica si la configuración está activa
	    sync_frequency (Select): Frecuencia de sincronización automática
	    sync_status (Select): Estado actual (Pendiente, En Progreso, Completado, Error)
	    last_sync (Datetime): Timestamp de la última sincronización exitosa
	    error_log (Text): Registro de errores de la última sincronización

	Errores comunes:
	    ValidationError: Cuando empresa origen coincide con alguna empresa destino
	    ValidationError: Cuando no se especifica al menos una empresa destino
	    ValidationError: Cuando hay empresas destino duplicadas

	Ejemplo de uso:
	    config = frappe.new_doc("Master Data Sync Configuration")
	    config.sync_name = "Sync Condominio ABC"
	    config.source_company = "Administradora XYZ"
	    config.is_active = 1
	    config.sync_frequency = "Diaria"
	    config.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de configuración de sincronización.

		Valida empresa origen, empresas destino y previene conflictos.
		"""
		self.validate_source_company()
		self.validate_target_companies()

	def validate_source_company(self):
		"""
		Valida que la empresa origen exista y sea diferente de las empresas destino.

		La empresa origen no puede aparecer también como empresa destino ya que
		esto crearía un bucle de sincronización sin sentido.

		Raises:
		    ValidationError: Si no se especifica empresa origen
		    ValidationError: Si empresa origen coincide con alguna empresa destino
		"""
		if not self.source_company:
			frappe.throw("La empresa origen es requerida.")

		# Verificar que empresa origen no aparece en empresas destino
		if hasattr(self, "target_companies"):
			for target in self.target_companies:
				if target.target_company == self.source_company:
					frappe.throw("La empresa origen no puede ser la misma que una empresa destino.")

	def validate_target_companies(self):
		"""
		Valida la lista de empresas destino para la sincronización.

		Debe haber al menos una empresa destino y no debe haber duplicados
		en la lista de empresas objetivo.

		Raises:
		    ValidationError: Si no se especifica al menos una empresa destino
		    ValidationError: Si hay empresas destino duplicadas
		"""
		if not self.target_companies:
			frappe.throw("Debe especificarse al menos una empresa destino.")

		# Verificar empresas destino duplicadas
		company_list = [target.target_company for target in self.target_companies]
		if len(company_list) != len(set(company_list)):
			frappe.throw("No se permiten empresas destino duplicadas.")

	def before_save(self):
		"""
		Procesos automáticos antes de guardar la configuración.

		Establece estado inicial si la configuración está activa.
		"""
		if self.is_active and not self.last_sync:
			self.sync_status = "Pendiente"

	def on_submit(self):
		"""
		Procesos automáticos al someter la configuración para aprobación.

		Activa automáticamente la configuración al ser sometida.
		"""
		self.is_active = 1

	def execute_sync(self):
		"""
		Ejecuta el proceso de sincronización de datos maestros.

		Cambia el estado a 'En Progreso', ejecuta la sincronización y
		actualiza el estado final según el resultado.

		Raises:
		    ValidationError: Si la configuración no está activa
		"""
		if not self.is_active:
			frappe.throw("La configuración de sincronización no está activa.")

		self.sync_status = "En Progreso"
		self.save()

		try:
			# La lógica de sincronización se implementaría aquí
			self.last_sync = now()
			self.sync_status = "Completado"
			self.error_log = ""
		except Exception as e:
			self.sync_status = "Error"
			self.error_log = str(e)
			frappe.log_error(f"Error en Sincronización de Datos Maestros: {e!s}")

		self.save()
