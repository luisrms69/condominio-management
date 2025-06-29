# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractServiceItem(Document):
	"""
	Elemento de servicio dentro de un contrato de gestión de servicios.

	Funcionalidades principales:
	- Definición de servicios específicos incluidos en contratos de gestión
	- Gestión de tarifas mensuales por servicio individual
	- Control de descripciones detalladas y especificaciones de servicios
	- Validación de tarifas no negativas para servicios de pago
	- Categorización de servicios por tipo y frecuencia
	- Gestión de términos y condiciones específicos por servicio

	Parámetros importantes:
	    service_name (Data): Nombre del servicio específico incluido
	    service_description (Text): Descripción detallada del servicio
	    service_category (Select): Categoría del servicio (Administrativo, Técnico, Limpieza)
	    monthly_rate (Currency): Tarifa mensual del servicio en MXN
	    frequency (Select): Frecuencia del servicio (Diario, Semanal, Mensual)
	    is_included (Check): Indica si el servicio está incluido en la tarifa base
	    service_provider (Data): Proveedor específico del servicio si es subcontratado

	Errores comunes:
	    ValidationError: Cuando la tarifa mensual es negativa

	Ejemplo de uso:
	    servicio = frappe.new_doc("Contract Service Item")
	    servicio.service_name = "Limpieza de Áreas Comunes"
	    servicio.service_category = "Limpieza"
	    servicio.monthly_rate = 5000.00
	    servicio.frequency = "Diario"
	    servicio.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones del elemento de servicio de contrato.

		Valida que las tarifas mensuales sean valores positivos.
		"""
		self.validate_monthly_rate()

	def validate_monthly_rate(self):
		"""
		Valida que la tarifa mensual sea un valor positivo.

		Las tarifas de servicios no pueden ser negativas ya que representan
		un costo que debe ser pagado por el servicio prestado.

		Raises:
		    ValidationError: Si la tarifa mensual es negativa
		"""
		if self.monthly_rate and self.monthly_rate < 0:
			frappe.throw("La tarifa mensual no puede ser negativa.")
