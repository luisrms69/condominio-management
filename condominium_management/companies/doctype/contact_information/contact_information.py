# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address


class ContactInformation(Document):
	"""
	Información de contacto para personas relacionadas con el condominio.

	Funcionalidades principales:
	- Almacenamiento de datos de contacto básicos (nombre, email, teléfono)
	- Validación automática de formato de email según estándares RFC
	- Verificación de longitud mínima de números telefónicos
	- Gestión de tipos de contacto (Administrador, Portero, Emergencias, etc.)
	- Control de preferencias de comunicación por persona
	- Validación de consistencia en información proporcionada

	Parámetros importantes:
	    contact_name (Data): Nombre completo de la persona de contacto
	    contact_type (Select): Tipo de contacto (Administrador, Portero, Emergencias)
	    email (Data): Dirección de correo electrónico válida
	    phone_number (Data): Número telefónico con al menos 10 dígitos
	    position (Data): Cargo o posición dentro del condominio
	    is_primary (Check): Indica si es el contacto principal para su tipo
	    availability_hours (Data): Horarios de disponibilidad del contacto

	Errores comunes:
	    ValidationError: Cuando el formato de email no cumple estándares RFC
	    Warning: Cuando el número telefónico tiene menos de 10 dígitos

	Ejemplo de uso:
	    contacto = frappe.new_doc("Contact Information")
	    contacto.contact_name = "Juan Pérez"
	    contacto.contact_type = "Administrador"
	    contacto.email = "juan.perez@condominio.com"
	    contacto.phone_number = "5551234567"
	    contacto.save()
	"""

	def validate(self):
		"""
		Ejecuta todas las validaciones de información de contacto.

		Valida formato de email y longitud de número telefónico.
		"""
		self.validate_email()
		self.validate_phone()

	def validate_email(self):
		"""
		Valida el formato del email según estándares RFC.

		Utiliza la función validate_email_address de Frappe para verificar
		que el email proporcionado cumple con el formato estándar.

		Raises:
		    ValidationError: Si el formato del email no es válido
		"""
		if self.email:
			if not validate_email_address(self.email):
				frappe.throw(_("Formato de email inválido: {0}").format(self.email))

	def validate_phone(self):
		"""
		Valida que el número telefónico tenga al menos 10 dígitos.

		Muestra una advertencia si el número es menor a 10 dígitos,
		que es el mínimo estándar para números telefónicos mexicanos.
		"""
		if self.phone_number and len(self.phone_number) < 10:
			frappe.msgprint("El número telefónico debe tener al menos 10 dígitos.", indicator="orange")
