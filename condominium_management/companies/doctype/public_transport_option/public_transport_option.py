# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PublicTransportOption(Document):
	"""
	Opciones de transporte público disponibles para llegar al condominio.

	Funcionalidades principales:
	- Registro de medios de transporte público disponibles
	- Gestión de distancias caminando desde estaciones/paradas
	- Control de líneas, rutas y horarios de operación
	- Almacenamiento de tarifas y frecuencias de servicio
	- Validación de distancias de caminata realistas
	- Gestión de instrucciones específicas para cada transporte

	Parámetros importantes:
	    transport_type (Select): Tipo de transporte (Metro, Autobús, Metrobús)
	    line_route (Data): Línea o ruta específica del transporte
	    station_stop_name (Data): Nombre de la estación o parada más cercana
	    walking_distance (Int): Distancia caminando en metros
	    estimated_fare (Currency): Tarifa estimada del viaje
	    frequency (Data): Frecuencia de paso del transporte
	    operating_hours (Data): Horarios de operación del servicio
	    special_instructions (Text): Instrucciones adicionales para el usuario

	Errores comunes:
	    ValidationError: Cuando la distancia caminando es negativa

	Ejemplo de uso:
	    transporte = frappe.new_doc("Public Transport Option")
	    transporte.transport_type = "Metro"
	    transporte.line_route = "Línea 1"
	    transporte.station_stop_name = "Estación Insurgentes"
	    transporte.walking_distance = 800
	    transporte.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de opción de transporte público.

		Valida que la distancia caminando sea un valor realista.
		"""
		self.validate_walking_distance()

	def validate_walking_distance(self):
		"""
		Valida que la distancia caminando sea un valor positivo.

		Las distancias negativas no son físicamente posibles, por lo que
		se genera un error si se detecta este caso.

		Raises:
		    ValidationError: Si la distancia caminando es negativa
		"""
		if self.walking_distance and self.walking_distance < 0:
			frappe.throw("La distancia caminando no puede ser negativa.")
