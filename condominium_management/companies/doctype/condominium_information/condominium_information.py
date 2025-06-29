# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CondominiumInformation(Document):
	"""
	Información completa del condominio incluyendo datos físicos, ubicación y accesos.

	Funcionalidades principales:
	- Gestión de información básica del condominio (unidades, áreas, año construcción)
	- Administración de instrucciones de llegada y coordenadas GPS
	- Control de opciones de transporte público disponibles
	- Registro de referencias cercanas para orientación
	- Gestión de puntos de acceso con horarios y restricciones
	- Validación automática de consistencia de datos

	Parámetros importantes:
	    company (Link): Referencia a la empresa/condominio principal
	    total_units (Int): Número total de unidades en el condominio
	    total_area (Float): Superficie total en metros cuadrados
	    common_area (Float): Área común en metros cuadrados
	    private_area (Float): Área privada en metros cuadrados
	    construction_year (Int): Año de construcción del condominio
	    gps_coordinates (Data): Coordenadas GPS (latitud, longitud)
	    how_to_arrive (Text): Instrucciones detalladas de cómo llegar
	    public_transport (Table): Opciones de transporte público disponibles
	    nearby_references (Table): Referencias cercanas para orientación
	    access_points (Table): Puntos de acceso con horarios y restricciones

	Errores comunes:
	    ValidationError: Cuando el número total de unidades es cero o negativo
	    Warning: Cuando las áreas no suman correctamente el total

	Ejemplo de uso:
	    condominio = frappe.new_doc("Condominium Information")
	    condominio.company = "Condominio Las Torres"
	    condominio.total_units = 120
	    condominio.total_area = 8500.50
	    condominio.gps_coordinates = "19.432608, -99.133209"
	    condominio.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de información del condominio.

		Verifica consistencia de áreas y validez del número de unidades.
		"""
		self.validate_areas()
		self.validate_units()

	def validate_areas(self):
		"""
		Valida que los cálculos de área sean consistentes entre sí.

		Compara área total con la suma de área común y privada, mostrando
		advertencia si hay diferencias significativas (>0.01 m²).
		"""
		if self.total_area and self.common_area and self.private_area:
			calculated_total = (self.common_area or 0) + (self.private_area or 0)
			if abs(self.total_area - calculated_total) > 0.01:  # Permite pequeñas diferencias de redondeo
				frappe.msgprint(
					"Advertencia: El área total no coincide con la suma de áreas común y privada.",
					indicator="orange",
				)

	def validate_units(self):
		"""
		Valida que el número total de unidades sea un valor positivo.

		Raises:
		    ValidationError: Si el total de unidades es cero o negativo
		"""
		if self.total_units and self.total_units <= 0:
			frappe.throw(_("El total de unidades debe ser mayor que cero."))

	def before_save(self):
		"""
		Procesos automáticos antes de guardar la información del condominio.

		Reservado para lógica de pre-guardado futura.
		"""
		# Agregar cualquier lógica de pre-guardado aquí
		pass
