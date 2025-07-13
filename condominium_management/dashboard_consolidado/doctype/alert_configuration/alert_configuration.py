# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now


class AlertConfiguration(Document):
	"""Configuración de alertas para el dashboard consolidado"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_alert_configuration()
		self.set_default_values()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_frequency_settings()
		self.validate_channel_configuration()

	def validate_alert_configuration(self):
		"""Valida configuración básica de la alerta"""
		if not self.alert_name:
			frappe.throw("El nombre de la alerta es obligatorio")

		if not self.alert_priority:
			frappe.throw("La prioridad de la alerta es obligatoria")

		valid_priorities = ["Baja", "Media", "Alta", "Crítica"]
		if self.alert_priority not in valid_priorities:
			frappe.throw(f"Prioridad inválida. Opciones: {', '.join(valid_priorities)}")

		if not self.trigger_type:
			frappe.throw("El tipo de disparador es obligatorio")

		valid_trigger_types = ["Umbral", "Cambio", "Tiempo", "Evento", "Personalizado"]
		if self.trigger_type not in valid_trigger_types:
			frappe.throw(f"Tipo de disparador inválido. Opciones: {', '.join(valid_trigger_types)}")

	def validate_frequency_settings(self):
		"""Valida configuración de frecuencia"""
		if not self.check_frequency:
			frappe.throw("La frecuencia de verificación es obligatoria")

		valid_frequencies = [
			"Minuto",
			"5 Minutos",
			"15 Minutos",
			"30 Minutos",
			"Hora",
			"6 Horas",
			"12 Horas",
			"Día",
		]
		if self.check_frequency not in valid_frequencies:
			frappe.throw(f"Frecuencia inválida. Opciones: {', '.join(valid_frequencies)}")

		# Validar configuración específica del trigger
		if self.trigger_type == "Umbral":
			self.validate_threshold_configuration()
		elif self.trigger_type == "Tiempo":
			self.validate_time_configuration()

	def validate_threshold_configuration(self):
		"""Valida configuración de umbrales"""
		if hasattr(self, "threshold_value") and self.threshold_value is not None:
			if hasattr(self, "threshold_operator") and not self.threshold_operator:
				frappe.throw("El operador de umbral es obligatorio cuando se especifica un valor")

			valid_operators = [
				"Mayor que",
				"Menor que",
				"Igual a",
				"Mayor o igual",
				"Menor o igual",
				"Diferente de",
			]
			if hasattr(self, "threshold_operator") and self.threshold_operator not in valid_operators:
				frappe.throw(f"Operador de umbral inválido. Opciones: {', '.join(valid_operators)}")

	def validate_time_configuration(self):
		"""Valida configuración temporal"""
		if self.trigger_type == "Tiempo":
			if hasattr(self, "trigger_time") and not self.trigger_time:
				frappe.throw("La hora de disparador es obligatoria para alertas de tiempo")

	def validate_channel_configuration(self):
		"""Valida configuración de canales de notificación"""
		if hasattr(self, "alert_channels") and self.alert_channels:
			for channel in self.alert_channels:
				if hasattr(channel, "channel_type") and channel.channel_type:
					valid_channel_types = ["Email", "SMS", "Push", "Slack", "Teams", "Webhook"]
					if channel.channel_type not in valid_channel_types:
						frappe.throw(f"Tipo de canal inválido: {channel.channel_type}")

	def set_default_values(self):
		"""Establece valores por defecto"""
		if not hasattr(self, "is_active") or self.is_active is None:
			self.is_active = 1

		if not hasattr(self, "created_by") or not self.created_by:
			self.created_by = frappe.session.user

		if not hasattr(self, "creation_date") or not self.creation_date:
			self.creation_date = now()

	def should_trigger_now(self, current_data):
		"""Determina si la alerta debe dispararse ahora"""
		if not self.is_active:
			return False

		try:
			if self.trigger_type == "Umbral":
				return self.check_threshold_condition(current_data)
			elif self.trigger_type == "Cambio":
				return self.check_change_condition(current_data)
			elif self.trigger_type == "Tiempo":
				return self.check_time_condition()
			elif self.trigger_type == "Evento":
				return self.check_event_condition(current_data)
			elif self.trigger_type == "Personalizado":
				return self.check_custom_condition(current_data)
		except Exception as e:
			frappe.log_error(f"Error checking alert condition for {self.name}: {e!s}")
			return False

		return False

	def check_threshold_condition(self, current_data):
		"""Verifica condición de umbral"""
		if not hasattr(self, "data_source_field") or not self.data_source_field:
			return False

		if not hasattr(self, "threshold_value") or self.threshold_value is None:
			return False

		current_value = current_data.get(self.data_source_field)
		if current_value is None:
			return False

		threshold_value = float(self.threshold_value)
		current_value = float(current_value)

		operator = getattr(self, "threshold_operator", "Mayor que")

		if operator == "Mayor que":
			return current_value > threshold_value
		elif operator == "Menor que":
			return current_value < threshold_value
		elif operator == "Igual a":
			return current_value == threshold_value
		elif operator == "Mayor o igual":
			return current_value >= threshold_value
		elif operator == "Menor o igual":
			return current_value <= threshold_value
		elif operator == "Diferente de":
			return current_value != threshold_value

		return False

	def check_change_condition(self, current_data):
		"""Verifica condición de cambio"""
		# Obtener valor anterior del cache/base de datos
		previous_value = self.get_previous_value()
		current_value = current_data.get(getattr(self, "data_source_field", ""))

		if previous_value is None or current_value is None:
			return False

		# Detectar cambio significativo
		change_threshold = getattr(self, "change_threshold", 0)
		if change_threshold > 0:
			change_percent = abs((current_value - previous_value) / previous_value * 100)
			return change_percent >= change_threshold
		else:
			return current_value != previous_value

	def check_time_condition(self):
		"""Verifica condición temporal"""
		from frappe.utils import get_time, now_datetime

		if not hasattr(self, "trigger_time") or not self.trigger_time:
			return False

		current_time = get_time(now_datetime().time())
		trigger_time = get_time(self.trigger_time)

		# Verificar si es hora de disparar (con tolerancia de 1 minuto)
		time_diff = abs(
			(current_time.hour * 60 + current_time.minute) - (trigger_time.hour * 60 + trigger_time.minute)
		)

		return time_diff <= 1

	def check_event_condition(self, current_data):
		"""Verifica condición de evento"""
		# Implementar lógica específica para eventos
		event_type = getattr(self, "event_type", "")
		return current_data.get("events", {}).get(event_type, False)

	def check_custom_condition(self, current_data):
		"""Verifica condición personalizada"""
		if not hasattr(self, "custom_condition") or not self.custom_condition:
			return False

		try:
			# Evaluar condición personalizada de forma segura
			safe_context = {"data": current_data, "abs": abs, "max": max, "min": min, "sum": sum, "len": len}

			return bool(eval(self.custom_condition, {"__builtins__": {}}, safe_context))
		except Exception as e:
			frappe.log_error(f"Error evaluating custom condition: {e!s}")
			return False

	def get_previous_value(self):
		"""Obtiene valor anterior para comparación"""
		# Implementar cache o consulta a histórico
		return None

	def trigger_alert(self, current_data, triggered_value=None):
		"""Dispara la alerta"""
		alert_data = {
			"alert_config": self.name,
			"alert_name": self.alert_name,
			"priority": self.alert_priority,
			"triggered_at": now(),
			"triggered_by_system": True,
			"trigger_data": current_data,
			"triggered_value": triggered_value,
		}

		# Enviar notificaciones por los canales configurados
		self.send_notifications(alert_data)

		# Registrar en log de alertas
		self.log_alert_trigger(alert_data)

	def send_notifications(self, alert_data):
		"""Envía notificaciones por los canales configurados"""
		if hasattr(self, "alert_channels") and self.alert_channels:
			for channel in self.alert_channels:
				try:
					self.send_channel_notification(channel, alert_data)
				except Exception as e:
					frappe.log_error(f"Error sending notification via {channel.channel_type}: {e!s}")

	def send_channel_notification(self, channel, alert_data):
		"""Envía notificación por un canal específico"""
		if channel.channel_type == "Email":
			self.send_email_notification(channel, alert_data)
		elif channel.channel_type == "SMS":
			self.send_sms_notification(channel, alert_data)
		# Agregar más tipos de canales según sea necesario

	def send_email_notification(self, channel, alert_data):
		"""Envía notificación por email"""
		recipients = getattr(channel, "recipients", "").split(",")
		if not recipients:
			return

		frappe.sendmail(
			recipients=recipients,
			subject=f"Alerta: {self.alert_name}",
			message=f"Se ha disparado la alerta '{self.alert_name}' con prioridad {self.alert_priority}.\n\nValor disparador: {alert_data.get('triggered_value', 'N/A')}",
		)

	def send_sms_notification(self, channel, alert_data):
		"""Envía notificación por SMS"""
		# Implementar integración SMS
		pass

	def log_alert_trigger(self, alert_data):
		"""Registra el disparo de la alerta"""
		frappe.log_error(title=f"Alert Triggered: {self.alert_name}", message=frappe.as_json(alert_data))
