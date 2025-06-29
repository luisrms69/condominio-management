# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ServiceInformation(Document):
	"""
	Información detallada de servicios disponibles en el condominio.

	Funcionalidades principales:
	- Registro de servicios específicos disponibles para residentes
	- Gestión de costos y tarifas de servicios de pago
	- Control de servicios gratuitos incluidos en la administración
	- Validación de consistencia entre servicios gratuitos y tarifas
	- Gestión de proveedores externos y horarios de atención
	- Control de requisitos y restricciones por servicio

	Parámetros importantes:
	    service_name (Data): Nombre del servicio disponible
	    service_description (Text): Descripción detallada del servicio
	    service_category (Select): Categoría del servicio (Técnico, Recreativo, Administrativo)
	    is_free (Check): Indica si el servicio es gratuito para residentes
	    service_cost (Currency): Costo del servicio si no es gratuito
	    service_provider (Data): Proveedor del servicio (interno o externo)
	    availability_schedule (Text): Horarios de disponibilidad del servicio
	    requirements (Text): Requisitos necesarios para acceder al servicio

	Errores comunes:
	    ValidationError: Cuando servicio de pago no tiene costo especificado
	    Warning: Cuando servicio gratuito tiene costo especificado

	Ejemplo de uso:
	    servicio = frappe.new_doc("Service Information")
	    servicio.service_name = "Salón de Eventos"
	    servicio.service_category = "Recreativo"
	    servicio.is_free = 0
	    servicio.service_cost = 2500.00
	    servicio.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de información de servicio.

		Valida consistencia entre servicios gratuitos y tarifas.
		"""
		self.validate_service_cost()

	def validate_service_cost(self):
		"""
		Valida la lógica de costos de servicios según si son gratuitos o de pago.

		Los servicios de pago deben tener un costo especificado, mientras que
		los servicios gratuitos no deberían tener costo asociado.

		Raises:
		    ValidationError: Si servicio de pago no tiene costo especificado
		"""
		if not self.is_free and not self.service_cost:
			frappe.throw(_("El costo del servicio es requerido para servicios de pago."))

		if self.is_free and self.service_cost:
			frappe.msgprint(
				_("El costo del servicio será ignorado para servicios gratuitos."), indicator="orange"
			)
			self.service_cost = 0
