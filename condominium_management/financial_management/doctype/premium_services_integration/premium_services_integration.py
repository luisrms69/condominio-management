# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Premium Services Integration - Sistema de Integración de Servicios Premium
==========================================================================

DocType para integración completa de servicios premium con:
- Gestión de servicios de resort/luxury living
- Integración financiera con Property/Resident Accounts
- Sistema de reservas y programación
- Seguimiento financiero y rentabilidad
- APIs externas y sincronización
"""

import json

import frappe
import requests
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, getdate, nowdate


class PremiumServicesIntegration(Document):
	"""Premium Services Integration DocType con business logic completa"""

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_service_configuration()
		self.validate_pricing_structure()
		self.validate_access_requirements()
		self.validate_integration_settings()
		self.set_defaults()

	def on_submit(self):
		"""Acciones al activar el servicio"""
		self.activate_service()
		self.setup_financial_integration()
		self.initialize_external_integrations()
		self.create_cost_center_if_needed()

	# =============================================================================
	# VALIDATION METHODS
	# =============================================================================

	def validate_service_configuration(self):
		"""Validar configuración básica del servicio"""
		if not self.service_name:
			frappe.throw(_("Nombre del Servicio es obligatorio"))

		if not self.service_category:
			frappe.throw(_("Categoría del Servicio es obligatoria"))

		if not self.company:
			frappe.throw(_("Condominio es obligatorio"))

		# Validar que no exista otro servicio con el mismo nombre en la company
		existing_service = frappe.db.exists(
			"Premium Services Integration",
			{
				"company": self.company,
				"service_name": self.service_name,
				"service_status": ["in", ["Activo", "En Prueba"]],
				"name": ["!=", self.name],
			},
		)

		if existing_service:
			frappe.throw(
				_("Ya existe un servicio activo con el nombre '{0}' en {1}").format(
					self.service_name, self.company
				)
			)

	def validate_pricing_structure(self):
		"""Validar estructura de precios"""
		if not self.pricing_model:
			frappe.throw(_("Modelo de Precios es obligatorio"))

		if not self.base_price or flt(self.base_price) <= 0:
			if self.pricing_model != "Paquete Anual":  # Algunos modelos pueden tener precio 0
				frappe.throw(_("Precio Base debe ser mayor a cero"))

		# Validar descuentos
		if self.member_discount_percentage and flt(self.member_discount_percentage) > 50:
			frappe.throw(_("Descuento para miembros no puede exceder 50%"))

		# Validar precios estacionales y dinámicos
		if self.seasonal_pricing_enabled and self.dynamic_pricing_enabled:
			frappe.msgprint(
				_("Advertencia: Precios estacionales y dinámicos habilitados simultáneamente"), alert=True
			)

	def validate_access_requirements(self):
		"""Validar requerimientos de acceso"""
		if self.advance_booking_required and not self.booking_window_days:
			frappe.throw(_("Reserva anticipada requiere especificar ventana de reserva"))

		if self.booking_window_days and self.booking_window_days > 365:
			frappe.throw(_("Ventana de reserva no puede exceder 365 días"))

		if self.capacity_limits and self.capacity_limits <= 0:
			frappe.throw(_("Límites de capacidad deben ser mayor a cero"))

		# Validar nivel de membresía vs acceso
		if (
			self.membership_tier_required
			and self.membership_tier_required != "No Aplica"
			and self.access_level_required == "Todos los Residentes"
		):
			frappe.msgprint(_("Advertencia: Nivel de membresía específico con acceso para todos"), alert=True)

	def validate_integration_settings(self):
		"""Validar configuraciones de integración"""
		# Validar integración financiera
		if not self.integrate_with_property_account and not self.integrate_with_resident_account:
			frappe.throw(_("Debe integrar con Property Account o Resident Account"))

		# Validar configuración de APIs externas
		if self.external_system_integration:
			if not self.api_endpoint_url:
				frappe.throw(_("Integración externa requiere URL de endpoint"))

			if not self.authentication_method:
				frappe.throw(_("Integración externa requiere método de autenticación"))

		# Validar espacio físico si es requerido
		if self.location_based_service and not self.physical_space_required:
			frappe.msgprint(_("Servicio basado en ubicación debería especificar espacio físico"), alert=True)

	def set_defaults(self):
		"""Establecer valores por defecto"""
		if not self.integration_date:
			self.integration_date = getdate()

		if not self.currency:
			self.currency = frappe.db.get_value("Company", self.company, "default_currency") or "MXN"

		# Establecer defaults según categoría de servicio
		if self.service_category == "Spa y Bienestar":
			self.set_spa_defaults()
		elif self.service_category == "Gastronomía":
			self.set_restaurant_defaults()
		elif self.service_category == "Deportes y Recreación":
			self.set_recreation_defaults()

	def set_spa_defaults(self):
		"""Configurar defaults para servicios de spa"""
		if not self.advance_booking_required:
			self.advance_booking_required = 1
		if not self.booking_window_days:
			self.booking_window_days = 7
		if not self.cancellation_policy:
			self.cancellation_policy = "24 horas"

	def set_restaurant_defaults(self):
		"""Configurar defaults para servicios gastronómicos"""
		if not self.billing_frequency:
			self.billing_frequency = "Inmediato"
		if not self.payment_collection_method:
			self.payment_collection_method = "Cargo a Cuenta"

	def set_recreation_defaults(self):
		"""Configurar defaults para servicios recreativos"""
		if not self.capacity_limits:
			self.capacity_limits = 50
		if not self.advance_booking_required:
			self.advance_booking_required = 1

	# =============================================================================
	# BUSINESS LOGIC METHODS
	# =============================================================================

	def activate_service(self):
		"""Activar servicio premium"""
		if self.service_status == "En Prueba":
			# Verificar que todas las configuraciones estén completas
			if self.validate_activation_requirements():
				self.service_status = "Activo"
				frappe.db.set_value("Premium Services Integration", self.name, "service_status", "Activo")

	def validate_activation_requirements(self):
		"""Validar requerimientos para activación"""
		required_configs = []

		if not self.base_price:
			required_configs.append("Precio Base")

		if not self.billing_frequency:
			required_configs.append("Frecuencia de Facturación")

		if self.external_system_integration and not self.api_endpoint_url:
			required_configs.append("URL de API Externa")

		if required_configs:
			frappe.throw(_("Configuraciones faltantes para activar: {0}").format(", ".join(required_configs)))

		return True

	def setup_financial_integration(self):
		"""Configurar integración financiera"""
		if self.revenue_tracking_enabled:
			self.create_revenue_tracking_setup()

		if self.auto_billing_enabled:
			self.setup_automatic_billing()

	def create_revenue_tracking_setup(self):
		"""Crear configuración de seguimiento de ingresos"""
		# Crear o actualizar Cost Center si es necesario
		if not self.cost_center_allocation:
			cost_center_name = f"Premium Services - {self.service_name}"

			if not frappe.db.exists("Cost Center", cost_center_name):
				cost_center = frappe.get_doc(
					{
						"doctype": "Cost Center",
						"cost_center_name": cost_center_name,
						"parent_cost_center": frappe.db.get_value("Company", self.company, "cost_center"),
						"company": self.company,
						"is_group": 0,
					}
				)
				cost_center.insert(ignore_permissions=True)
				self.cost_center_allocation = cost_center.name

	def setup_automatic_billing(self):
		"""Configurar facturación automática"""
		# Esta función se puede expandir para configurar trabajos cron
		frappe.logger().info(f"Configurando facturación automática para {self.service_name}")

	def initialize_external_integrations(self):
		"""Inicializar integraciones externas"""
		if self.external_system_integration and self.api_endpoint_url:
			try:
				self.test_external_api_connection()
				self.setup_webhook_notifications()
			except Exception as e:
				frappe.log_error(f"Error inicializando integración externa: {e!s}")

	def test_external_api_connection(self):
		"""Probar conexión con API externa"""
		headers = self.get_api_headers()

		try:
			response = requests.get(f"{self.api_endpoint_url}/health", headers=headers, timeout=10)
			if response.status_code == 200:
				frappe.logger().info(f"Conexión API exitosa para {self.service_name}")
			else:
				frappe.log_error(f"Error conexión API: {response.status_code}")
		except requests.RequestException as e:
			frappe.log_error(f"Error conexión API: {e!s}")

	def get_api_headers(self):
		"""Obtener headers para API externa"""
		headers = {"Content-Type": "application/json"}

		if self.authentication_method == "API Key":
			headers["Authorization"] = f"Bearer {self.get_api_key()}"
		elif self.authentication_method == "Basic Auth":
			# Implementar Basic Auth si es necesario
			pass

		return headers

	def get_api_key(self):
		"""Obtener API key (implementar según necesidades de seguridad)"""
		# Esta función debería obtener la API key de forma segura
		return "placeholder_api_key"

	def setup_webhook_notifications(self):
		"""Configurar notificaciones webhook"""
		if self.webhook_notifications_enabled:
			frappe.logger().info(f"Configurando webhooks para {self.service_name}")

	def create_cost_center_if_needed(self):
		"""Crear Cost Center si es necesario"""
		if not self.cost_center_allocation and self.revenue_tracking_enabled:
			self.create_revenue_tracking_setup()

	# =============================================================================
	# SERVICE DELIVERY METHODS
	# =============================================================================

	def calculate_service_price(self, resident_account=None, booking_date=None, duration=1):
		"""Calcular precio del servicio para un residente específico"""
		base_price = flt(self.base_price)

		# Aplicar descuento de miembro si aplica
		if resident_account and self.member_discount_percentage:
			member_discount = base_price * (flt(self.member_discount_percentage) / 100)
			base_price -= member_discount

		# Aplicar precios estacionales si están habilitados
		if self.seasonal_pricing_enabled and booking_date:
			seasonal_multiplier = self.get_seasonal_multiplier(booking_date)
			base_price *= seasonal_multiplier

		# Aplicar precios dinámicos si están habilitados
		if self.dynamic_pricing_enabled:
			dynamic_multiplier = self.get_dynamic_pricing_multiplier()
			base_price *= dynamic_multiplier

		# Aplicar duración
		total_price = base_price * duration

		return total_price

	def get_seasonal_multiplier(self, booking_date):
		"""Obtener multiplicador estacional"""
		month = getdate(booking_date).month

		# Temporada alta: Diciembre, Enero, Febrero (vacaciones)
		if month in [12, 1, 2]:
			return 1.3
		# Temporada media: Julio, Agosto (vacaciones verano)
		elif month in [7, 8]:
			return 1.15
		# Temporada baja: resto del año
		else:
			return 1.0

	def get_dynamic_pricing_multiplier(self):
		"""Obtener multiplicador de precios dinámicos basado en demanda"""
		# Esta función se puede expandir para considerar:
		# - Ocupación actual
		# - Historial de demanda
		# - Eventos especiales
		# Por ahora retorna 1.0 (sin cambio)
		return 1.0

	def check_availability(self, booking_date, duration=1):
		"""Verificar disponibilidad del servicio"""
		if not self.capacity_limits:
			return True

		# Query para verificar reservas existentes
		existing_bookings = frappe.db.sql(
			"""
			SELECT COUNT(*) as count
			FROM `tabService Booking`
			WHERE service_name = %s
			AND booking_date = %s
			AND booking_status NOT IN ('Cancelada', 'No Show')
		""",
			[self.service_name, booking_date],
		)

		current_bookings = existing_bookings[0][0] if existing_bookings else 0

		return current_bookings < self.capacity_limits

	def validate_access_permissions(self, user, resident_account=None):
		"""Validar permisos de acceso del usuario"""
		user_roles = frappe.get_roles(user)

		# Verificar nivel de acceso requerido
		if self.access_level_required == "Solo Propietarios":
			if "Residente Propietario" not in user_roles:
				return False, _("Servicio disponible solo para propietarios")

		# Verificar nivel de membresía si se requiere
		if (
			self.membership_tier_required
			and self.membership_tier_required != "No Aplica"
			and resident_account
		):
			user_tier = self.get_user_membership_tier(resident_account)
			if not self.validate_membership_tier(user_tier):
				return False, _("Nivel de membresía insuficiente")

		return True, _("Acceso autorizado")

	def get_user_membership_tier(self, resident_account):
		"""Obtener nivel de membresía del usuario"""
		# Esta función se puede expandir para obtener el tier real
		# Por ahora retorna "Básico" como default
		return "Básico"

	def validate_membership_tier(self, user_tier):
		"""Validar si el tier del usuario es suficiente"""
		tier_hierarchy = ["Básico", "Plata", "Oro", "Platino", "Diamante"]

		required_index = tier_hierarchy.index(self.membership_tier_required)
		user_index = tier_hierarchy.index(user_tier) if user_tier in tier_hierarchy else 0

		return user_index >= required_index

	# =============================================================================
	# API METHODS
	# =============================================================================

	@frappe.whitelist()
	def create_service_booking(self, resident_account, booking_date, duration=1, notes=None):
		"""Crear reserva de servicio"""
		# Validar disponibilidad
		if not self.check_availability(booking_date, duration):
			frappe.throw(_("Servicio no disponible para la fecha solicitada"))

		# Validar permisos de acceso
		access_valid, message = self.validate_access_permissions(frappe.session.user, resident_account)
		if not access_valid:
			frappe.throw(message)

		# Calcular precio
		service_price = self.calculate_service_price(resident_account, booking_date, duration)

		# Crear registro de reserva (esto requeriría un DocType adicional)
		booking_data = {
			"doctype": "Service Booking",
			"service_name": self.service_name,
			"resident_account": resident_account,
			"booking_date": booking_date,
			"duration": duration,
			"service_price": service_price,
			"booking_status": "Confirmada",
			"notes": notes,
		}

		# En un sistema real, esto crearía la reserva
		frappe.logger().info(f"Reserva creada: {booking_data}")

		return {
			"success": True,
			"message": _("Reserva creada exitosamente"),
			"booking_price": service_price,
			"booking_date": booking_date,
		}

	@frappe.whitelist()
	def get_service_performance(self, period_days=30):
		"""Obtener métricas de rendimiento del servicio"""
		if not self.performance_metrics_tracking:
			frappe.throw(_("Seguimiento de métricas no está habilitado"))

		from_date = add_days(getdate(), -period_days)

		# Obtener métricas de rendimiento
		performance_data = {
			"service_name": self.service_name,
			"period": f"Últimos {period_days} días",
			"revenue": self.get_revenue_for_period(from_date, getdate()),
			"bookings": self.get_bookings_for_period(from_date, getdate()),
			"utilization_rate": self.calculate_utilization_rate(from_date, getdate()),
			"customer_satisfaction": self.get_average_rating(from_date, getdate()),
		}

		return performance_data

	def get_revenue_for_period(self, from_date, to_date):
		"""Obtener ingresos para un período"""
		# Esta función se puede expandir para consultar datos reales
		return {"total": 50000.0, "target": flt(self.monthly_revenue_target) or 45000.0, "variance": 5000.0}

	def get_bookings_for_period(self, from_date, to_date):
		"""Obtener reservas para un período"""
		# Función placeholder - expandir con datos reales
		return {"total": 45, "completed": 42, "cancelled": 2, "no_show": 1}

	def calculate_utilization_rate(self, from_date, to_date):
		"""Calcular tasa de utilización"""
		if not self.capacity_limits:
			return 0.0

		# Cálculo placeholder
		days_in_period = (getdate(to_date) - getdate(from_date)).days
		total_capacity = self.capacity_limits * days_in_period
		utilized_capacity = 42  # De get_bookings_for_period

		return (utilized_capacity / total_capacity) * 100 if total_capacity > 0 else 0.0

	def get_average_rating(self, from_date, to_date):
		"""Obtener calificación promedio"""
		# Función placeholder - expandir con sistema de ratings real
		return 4.5

	@frappe.whitelist()
	def sync_with_external_system(self):
		"""Sincronizar con sistema externo"""
		if not self.external_system_integration:
			frappe.throw(_("Integración externa no está habilitada"))

		try:
			# Obtener datos del sistema externo
			external_data = self.fetch_external_data()

			# Procesar y actualizar datos locales
			self.process_external_data(external_data)

			return {
				"success": True,
				"message": _("Sincronización completada exitosamente"),
				"last_sync": nowdate(),
			}
		except Exception as e:
			frappe.log_error(f"Error en sincronización: {e!s}")
			return {"success": False, "message": _("Error en sincronización: {0}").format(str(e))}

	def fetch_external_data(self):
		"""Obtener datos del sistema externo"""
		headers = self.get_api_headers()

		response = requests.get(f"{self.api_endpoint_url}/bookings", headers=headers, timeout=30)

		if response.status_code == 200:
			return response.json()
		else:
			raise Exception(f"Error API: {response.status_code}")

	def process_external_data(self, data):
		"""Procesar datos del sistema externo"""
		# Implementar lógica de procesamiento según el sistema externo
		frappe.logger().info(f"Procesando {len(data.get('bookings', []))} reservas del sistema externo")

	# =============================================================================
	# STATIC METHODS
	# =============================================================================

	@staticmethod
	def get_active_services(company=None):
		"""Obtener servicios activos"""
		filters = {"service_status": "Activo"}
		if company:
			filters["company"] = company

		return frappe.get_all(
			"Premium Services Integration",
			filters=filters,
			fields=["name", "service_name", "service_category", "base_price", "pricing_model"],
		)

	@staticmethod
	def get_services_by_category(category, company=None):
		"""Obtener servicios por categoría"""
		filters = {"service_category": category, "service_status": "Activo"}
		if company:
			filters["company"] = company

		return frappe.get_all(
			"Premium Services Integration",
			filters=filters,
			fields=["name", "service_name", "base_price", "advance_booking_required", "capacity_limits"],
		)
