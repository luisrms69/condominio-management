# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NearbyReference(Document):
	"""
	Referencias cercanas al condominio para facilitar la orientación y ubicación.

	Funcionalidades principales:
	- Registro de ubicaciones de referencia próximas al condominio
	- Cálculo y almacenamiento de distancias desde el condominio
	- Categorización de referencias por tipo (comercial, educativo, médico, etc.)
	- Gestión de instrucciones específicas para llegar desde cada referencia
	- Validación de distancias positivas y lógicas
	- Control de relevancia y utilidad de cada referencia

	Parámetros importantes:
	    reference_name (Data): Nombre de la ubicación de referencia
	    reference_type (Select): Tipo de referencia (Centro Comercial, Escuela, Hospital)
	    distance (Select): Distancia aproximada desde el condominio
	    distance_unit (Select): Unidad de medida (metros, kilómetros, minutos)
	    description (Text): Descripción detallada de la referencia
	    is_landmark (Check): Indica si es un punto de referencia principal
	    directions (Text): Instrucciones específicas desde esta referencia

	Errores comunes:
	    ValidationError: Cuando la distancia especificada es negativa

	Ejemplo de uso:
	    referencia = frappe.new_doc("Nearby Reference")
	    referencia.reference_name = "Centro Comercial Plaza Norte"
	    referencia.reference_type = "Centro Comercial"
	    referencia.distance = "500 metros"
	    referencia.is_landmark = 1
	    referencia.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de referencia cercana.

		Valida que la distancia sea un valor lógico y positivo.
		"""
		self.validate_distance()

	def validate_distance(self):
		"""
		Valida que la distancia especificada sea un valor positivo.

		Las distancias negativas no tienen sentido físico, por lo que
		se genera un error de validación si se detecta este caso.

		Raises:
		    ValidationError: Si la distancia es negativa
		"""
		if self.distance and self.distance < 0:
			frappe.throw(_("La distancia no puede ser negativa."))
