# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours


class OperatingHours(Document):
	"""
	Horarios de operación para servicios y puntos de acceso del condominio.

	Funcionalidades principales:
	- Definición de horarios específicos de operación por día de la semana
	- Gestión de horarios de apertura y cierre para diferentes servicios
	- Validación de consistencia lógica en rangos de tiempo
	- Control de horarios especiales y excepciones
	- Soporte para servicios 24/7 o con horarios restringidos
	- Gestión de horarios de mantenimiento y cierre temporal

	Parámetros importantes:
	    day_of_week (Select): Día de la semana (Lunes, Martes, etc.)
	    open_time (Time): Hora de apertura del servicio
	    close_time (Time): Hora de cierre del servicio
	    is_24_hours (Check): Indica si el servicio opera 24 horas
	    is_closed (Check): Indica si el servicio está cerrado este día
	    special_notes (Text): Notas especiales sobre horarios o restricciones
	    maintenance_hours (Data): Horarios de mantenimiento si aplican

	Errores comunes:
	    ValidationError: Cuando hora de cierre es anterior o igual a hora de apertura

	Ejemplo de uso:
	    horario = frappe.new_doc("Operating Hours")
	    horario.day_of_week = "Lunes"
	    horario.open_time = "08:00:00"
	    horario.close_time = "18:00:00"
	    horario.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de horarios de operación.

		Valida que los rangos de tiempo sean lógicamente consistentes.
		"""
		self.validate_time_range()

	def validate_time_range(self):
		"""
		Valida que la hora de cierre sea posterior a la hora de apertura.

		Para horarios normales (no 24 horas), la hora de cierre debe ser
		posterior a la hora de apertura para que el rango tenga sentido.

		Raises:
		    ValidationError: Si hora de cierre es anterior o igual a hora de apertura
		"""
		if self.open_time and self.close_time:
			if self.close_time <= self.open_time:
				frappe.throw(_("La hora de cierre debe ser posterior a la hora de apertura."))
