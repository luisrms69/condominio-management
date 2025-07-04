# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConflictDetectionField(Document):
	"""
	Campo configurado para detección de conflictos.

	Funcionalidades principales:
	- Definir campos específicos que deben verificarse por conflictos
	- Configurar tipo y severidad de conflictos
	- Establecer reglas de validación personalizadas
	- Habilitar/deshabilitar detección por campo

	Parámetros importantes:
	    field_name (Data): Nombre del campo a verificar
	    conflict_type (Select): Tipo de conflicto (Duplicación, Horario, etc.)
	    severity (Select): Nivel de severidad del conflicto
	    validation_rule (Text): Regla personalizada de validación
	    is_active (Check): Si la detección está habilitada

	Ejemplo de uso:
	    field = frappe.new_doc("Conflict Detection Field")
	    field.field_name = "operating_hours"
	    field.conflict_type = "Horario"
	    field.severity = "Alta"
	    field.save()
	"""

	def validate(self):
		"""
		Validar configuración del campo de detección de conflictos.

		Verifica que la configuración sea consistente y válida.
		"""
		self.validate_conflict_configuration()
		self.validate_custom_rule()

	def validate_conflict_configuration(self):
		"""
		Validar configuración básica del conflicto.

		Verifica que los valores seleccionados sean consistentes.
		"""
		# Validar que campos requeridos estén completos
		if not self.field_name:
			frappe.throw(frappe._("Nombre del campo es requerido"))

		if not self.field_label:
			self.field_label = self.field_name.replace("_", " ").title()

	def validate_custom_rule(self):
		"""
		Validar regla de validación personalizada.

		Verifica que la regla personalizada tenga sintaxis válida si está presente.
		"""
		if self.conflict_type == "Personalizado" and not self.validation_rule:
			frappe.throw(frappe._("Regla de validación es requerida para conflictos personalizados"))

		# TODO: Implementar validación de sintaxis de reglas personalizadas
		# Esto podría incluir validación de expresiones Python seguras

	def get_conflict_description(self):
		"""
		Obtener descripción del tipo de conflicto.

		Returns:
		    str: Descripción del conflicto configurado
		"""
		descriptions = {
			"Duplicación": "Verifica valores duplicados entre configuraciones",
			"Horario": "Detecta conflictos de horarios superpuestos",
			"Capacidad": "Valida límites de capacidad lógicos",
			"Ubicación": "Detecta conflictos de ubicación física",
			"Recurso": "Verifica asignación múltiple de recursos únicos",
			"Personalizado": "Aplica regla de validación personalizada",
		}

		return descriptions.get(self.conflict_type, "Tipo de conflicto no definido")

	def should_check_conflict(self):
		"""
		Determinar si se debe verificar este campo por conflictos.

		Returns:
		    bool: True si la detección está habilitada y configurada
		"""
		return self.is_active and self.field_name and self.conflict_type

	def get_severity_level(self):
		"""
		Obtener nivel numérico de severidad.

		Returns:
		    int: Nivel de severidad (1=Baja, 2=Media, 3=Alta)
		"""
		severity_levels = {"Baja": 1, "Media": 2, "Alta": 3}
		return severity_levels.get(self.severity, 2)
