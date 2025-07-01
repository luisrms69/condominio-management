# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AccessPointDetail(Document):
	"""
	Detalle de punto de acceso para control de entrada y salida del condominio.

	Funcionalidades principales:
	- Configuración de métodos de control de acceso (tarjeta, código, huella, etc.)
	- Definición de tipos de acceso permitidos (peatonal, vehicular, mixto)
	- Gestión de horarios de operación por días de la semana
	- Control de quiénes pueden acceder (residentes, visitas, proveedores)
	- Configuración de niveles de seguridad por punto de acceso
	- Validación de consistencia en configuración de accesos

	Parámetros importantes:
	    access_point_name (Data): Nombre identificativo del punto de acceso
	    access_point_type (Select): Tipo de acceso (Peatonal, Vehicular, Mixto, Emergencia)
	    security_level (Select): Nivel de seguridad (Bajo, Medio, Alto, Restringido)
	    access_control_method (Select): Método de control (Tarjeta, Código, Huella, etc.)
	    who_can_access (MultiSelectPills): Quiénes pueden acceder
	    access_vehicle_type (Select): Tipo de acceso vehicular permitido
	    opening_time (Time): Hora de apertura del punto de acceso
	    closing_time (Time): Hora de cierre del punto de acceso
	    operating_days (MultiSelectPills): Días de operación del punto

	Errores comunes:
	    ValidationError: Cuando horarios de apertura y cierre son inconsistentes
	    ValidationError: Cuando no se especifica método de control para acceso restringido

	Ejemplo de uso:
	    acceso = frappe.new_doc("Access Point Detail")
	    acceso.access_point_name = "Entrada Principal"
	    acceso.access_point_type = "Mixto"
	    acceso.access_control_method = "Tarjeta"
	    acceso.opening_time = "06:00:00"
	    acceso.closing_time = "22:00:00"
	    acceso.save()
	"""

	def validate(self):
		"""
		Ejecuta validaciones del detalle de punto de acceso.

		Valida horarios de operación y consistencia de configuración.
		"""
		self.validate_operating_hours()
		self.validate_access_configuration()

	def validate_operating_hours(self):
		"""
		Valida que los horarios de operación sean lógicamente consistentes.

		Raises:
		    ValidationError: Si hora de cierre es anterior a hora de apertura
		"""
		if self.opening_time and self.closing_time:
			# Convertir a formato comparable
			from frappe.utils import get_time

			opening = get_time(self.opening_time)
			closing = get_time(self.closing_time)

			if closing <= opening:
				frappe.throw(_("La hora de cierre debe ser posterior a la hora de apertura."))

	def validate_access_configuration(self):
		"""
		Valida la configuración de acceso según el nivel de seguridad.

		Raises:
		    ValidationError: Si configuración de seguridad es inconsistente
		"""
		if self.security_level == "Restringido" and not self.access_control_method:
			frappe.throw(
				_(
					"Los puntos de acceso con nivel de seguridad 'Restringido' deben especificar un método de control de acceso."
				)
			)
