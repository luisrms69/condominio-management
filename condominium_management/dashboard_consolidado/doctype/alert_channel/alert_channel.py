# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AlertChannel(Document):
	"""Canal de notificación para alertas - Child table de Alert Configuration"""

	def validate(self):
		"""Validaciones del canal de alerta"""
		self.validate_channel_type()
		self.validate_channel_configuration()

	def validate_channel_type(self):
		"""Valida el tipo de canal"""
		if not self.channel_type:
			frappe.throw("El tipo de canal es obligatorio")

		valid_channel_types = ["Email", "SMS", "Push", "Slack", "Teams", "Webhook", "Sistema"]
		if self.channel_type not in valid_channel_types:
			frappe.throw(f"Tipo de canal inválido. Opciones: {', '.join(valid_channel_types)}")

	def validate_channel_configuration(self):
		"""Valida configuración específica del canal"""
		if self.channel_type == "Email":
			self.validate_email_configuration()
		elif self.channel_type == "SMS":
			self.validate_sms_configuration()
		elif self.channel_type == "Webhook":
			self.validate_webhook_configuration()

	def validate_email_configuration(self):
		"""Valida configuración de email"""
		if not hasattr(self, "recipients") or not self.recipients:
			frappe.throw("Los destinatarios son obligatorios para canales de email")

		# Validar formato de emails
		import re

		email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

		recipients = self.recipients.split(",")
		for recipient in recipients:
			recipient = recipient.strip()
			if not re.match(email_pattern, recipient):
				frappe.throw(f"Formato de email inválido: {recipient}")

	def validate_sms_configuration(self):
		"""Valida configuración de SMS"""
		if not hasattr(self, "phone_numbers") or not self.phone_numbers:
			frappe.throw("Los números de teléfono son obligatorios para canales SMS")

	def validate_webhook_configuration(self):
		"""Valida configuración de webhook"""
		if not hasattr(self, "webhook_url") or not self.webhook_url:
			frappe.throw("La URL del webhook es obligatoria")

		# Validar formato de URL
		import re

		url_pattern = r"^https?://.+"
		if not re.match(url_pattern, self.webhook_url):
			frappe.throw("Formato de URL inválido para webhook")
