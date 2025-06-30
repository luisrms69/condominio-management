# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SyncDataType(Document):
	"""
	Configuración de tipos de datos para sincronización entre empresas.

	Funcionalidades principales:
	- Definición de tipos específicos de datos a sincronizar
	- Control de prioridades y frecuencias de sincronización por tipo
	- Registro de contadores de registros sincronizados exitosamente
	- Gestión de filtros y criterios de selección de datos
	- Validación de contadores de sincronización no negativos
	- Configuración de transformaciones de datos por tipo

	Parámetros importantes:
	    data_type (Data): Tipo de dato a sincronizar (ej: Customer, Item, Price List)
	    is_enabled (Check): Indica si este tipo está habilitado para sincronización
	    sync_priority (Select): Prioridad de sincronización (Alta, Media, Baja)
	    last_sync_count (Int): Contador de registros sincronizados en último proceso
	    sync_frequency (Select): Frecuencia de sincronización (Tiempo real, Diaria, Semanal)
	    filter_conditions (Text): Condiciones de filtro en formato JSON
	    field_mappings (Text): Mapeo de campos entre sistemas

	Errores comunes:
	    ValidationError: Cuando el contador de sincronización es negativo

	Ejemplo de uso:
	    sync_type = frappe.new_doc("Sync Data Type")
	    sync_type.data_type = "Customer"
	    sync_type.is_enabled = 1
	    sync_type.sync_priority = "Alta"
	    sync_type.last_sync_count = 0
	    sync_type.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de tipo de dato de sincronización.

		Valida que los contadores de sincronización sean consistentes.
		"""
		self.validate_sync_count()

	def validate_sync_count(self):
		"""
		Valida que el contador de sincronización no sea negativo.

		Los contadores de registros sincronizados deben ser valores
		positivos o cero, nunca negativos.

		Raises:
		    ValidationError: Si el contador de última sincronización es negativo
		"""
		if self.last_sync_count and self.last_sync_count < 0:
			frappe.throw(_("El contador de última sincronización no puede ser negativo."))
