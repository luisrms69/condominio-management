# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Financial Transparency Config - Sistema de Configuración de Transparencia
========================================================================

DocType para configuración granular de transparencia financiera con:
- Control de acceso por rol
- Configuración portal residentes
- Transparencia comité y decisiones
- Cumplimiento regulatorio
- Reglas personalizadas
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class FinancialTransparencyConfig(Document):
	"""Financial Transparency Config DocType con business logic completa"""

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_transparency_configuration()
		self.validate_access_consistency()
		self.validate_compliance_requirements()
		self.set_effective_defaults()
		self.validate_custom_rules()

	def on_submit(self):
		"""Acciones al activar la configuración"""
		self.activate_transparency_config()
		self.update_role_permissions()
		self.create_audit_trail()

	# =============================================================================
	# VALIDATION METHODS
	# =============================================================================

	def validate_transparency_configuration(self):
		"""Validar configuración básica de transparencia"""
		if not self.config_name:
			frappe.throw(_("Nombre de Configuración es obligatorio"))

		if not self.company:
			frappe.throw(_("Condominio es obligatorio"))

		if not self.transparency_level:
			frappe.throw(_("Nivel de Transparencia es obligatorio"))

		# Validar que no exista otra configuración activa para la misma company
		existing_config = frappe.db.exists(
			"Financial Transparency Config",
			{"company": self.company, "config_status": "Activo", "name": ["!=", self.name]},
		)

		if existing_config:
			frappe.throw(_("Ya existe una configuración activa para {0}").format(self.company))

	def validate_access_consistency(self):
		"""Validar consistencia en niveles de acceso"""
		# Validar que niveles de transparencia sean consistentes
		transparency_levels = [
			self.income_transparency_level,
			self.expense_transparency_level,
			self.budget_transparency_level,
			self.balance_transparency_level,
			self.reserve_transparency_level,
		]

		# Si transparency_level es "Básico", no debe haber niveles "Completo"
		if self.transparency_level == "Básico":
			for level in transparency_levels:
				if level == "Completo":
					frappe.throw(_("Nivel 'Básico' no permite transparencia 'Completa' en datos financieros"))

		# Si transparency_level es "Completo", todos deben ser al menos "Detallado"
		if self.transparency_level == "Completo":
			for level in transparency_levels:
				if level in ["Oculto", "Resumen"]:
					frappe.throw(
						_("Nivel 'Completo' requiere al menos transparencia 'Detallada' en todos los datos")
					)

	def validate_compliance_requirements(self):
		"""Validar requerimientos de cumplimiento"""
		# Validar período de retención de datos
		if self.data_retention_period and self.data_retention_period < 3:
			frappe.throw(_("Período de retención mínimo es 3 años por regulaciones"))

		if self.data_retention_period and self.data_retention_period > 10:
			frappe.throw(_("Período de retención máximo es 10 años"))

		# Si cumplimiento regulatorio es "Máximo", ciertos campos son obligatorios
		if self.regulatory_compliance_level == "Máximo":
			if not self.audit_trail_required:
				frappe.throw(_("Cumplimiento 'Máximo' requiere auditoría obligatoria"))

			if not self.data_retention_period:
				self.data_retention_period = 7  # Default para cumplimiento máximo

	def set_effective_defaults(self):
		"""Establecer valores por defecto según nivel de transparencia"""
		if not self.effective_from:
			self.effective_from = getdate()

		# Configurar defaults según transparency_level
		if self.transparency_level == "Básico":
			self.set_basic_transparency_defaults()
		elif self.transparency_level == "Estándar":
			self.set_standard_transparency_defaults()
		elif self.transparency_level == "Avanzado":
			self.set_advanced_transparency_defaults()
		elif self.transparency_level == "Completo":
			self.set_complete_transparency_defaults()

	def set_basic_transparency_defaults(self):
		"""Configurar defaults para transparencia básica"""
		if not self.income_transparency_level:
			self.income_transparency_level = "Resumen"
		if not self.expense_transparency_level:
			self.expense_transparency_level = "Resumen"
		if not self.budget_transparency_level:
			self.budget_transparency_level = "Oculto"
		if not self.portal_access_level:
			self.portal_access_level = "Básico"

	def set_standard_transparency_defaults(self):
		"""Configurar defaults para transparencia estándar"""
		if not self.income_transparency_level:
			self.income_transparency_level = "Detallado"
		if not self.expense_transparency_level:
			self.expense_transparency_level = "Detallado"
		if not self.budget_transparency_level:
			self.budget_transparency_level = "Resumen"
		if not self.portal_access_level:
			self.portal_access_level = "Estándar"

	def set_advanced_transparency_defaults(self):
		"""Configurar defaults para transparencia avanzada"""
		if not self.income_transparency_level:
			self.income_transparency_level = "Completo"
		if not self.expense_transparency_level:
			self.expense_transparency_level = "Detallado"
		if not self.budget_transparency_level:
			self.budget_transparency_level = "Detallado"
		if not self.portal_access_level:
			self.portal_access_level = "Avanzado"

	def set_complete_transparency_defaults(self):
		"""Configurar defaults para transparencia completa"""
		transparency_fields = [
			"income_transparency_level",
			"expense_transparency_level",
			"budget_transparency_level",
			"balance_transparency_level",
			"reserve_transparency_level",
		]

		for field in transparency_fields:
			if not self.get(field):
				setattr(self, field, "Completo")

		if not self.portal_access_level:
			self.portal_access_level = "Completo"

	def validate_custom_rules(self):
		"""Validar reglas personalizadas"""
		if self.enable_custom_rules:
			if not any(
				[
					self.property_type_restrictions,
					self.ownership_percentage_rules,
					self.payment_status_restrictions,
				]
			):
				frappe.throw(_("Reglas personalizadas habilitadas requieren al menos una regla definida"))

	# =============================================================================
	# BUSINESS LOGIC METHODS
	# =============================================================================

	def activate_transparency_config(self):
		"""Activar configuración de transparencia"""
		if self.config_status == "Aprobado":
			# Desactivar otras configuraciones activas
			frappe.db.sql(
				"""
				UPDATE `tabFinancial Transparency Config`
				SET config_status = 'Inactivo'
				WHERE company = %s
				AND config_status = 'Activo'
				AND name != %s
			""",
				(self.company, self.name),
			)

			# Activar esta configuración
			self.config_status = "Activo"
			frappe.db.set_value("Financial Transparency Config", self.name, "config_status", "Activo")

	def update_role_permissions(self):
		"""Actualizar permisos de roles según configuración"""
		if not self.enable_role_based_access:
			return

		# Mapeo de niveles de acceso a permisos
		access_mapping = {
			"Sin Acceso": {"read": 0, "write": 0, "create": 0},
			"Solo Lectura": {"read": 1, "write": 0, "create": 0},
			"Lectura Limitada": {"read": 1, "write": 0, "create": 0},
			"Lectura Completa": {"read": 1, "write": 0, "create": 0},
		}

		# Aplicar configuración de acceso a DocTypes financieros
		financial_doctypes = [
			"Fee Structure",
			"Property Account",
			"Resident Account",
			"Billing Cycle",
			"Payment Collection",
			"Credit Balance Management",
			"Fine Management",
			"Budget Planning",
		]

		default_permissions = access_mapping.get(self.default_access_level, {})

		for doctype in financial_doctypes:
			self.apply_transparency_permissions(doctype, default_permissions)

	def apply_transparency_permissions(self, doctype, permissions):
		"""Aplicar permisos de transparencia a un DocType específico"""
		# Esta función se puede expandir para modificar permisos dinámicamente
		frappe.logger().info(f"Aplicando permisos de transparencia a {doctype}")

	def create_audit_trail(self):
		"""Crear registro de auditoría"""
		if self.audit_trail_required:
			audit_entry = {
				"doctype": "Comment",
				"comment_type": "Info",
				"reference_doctype": "Financial Transparency Config",
				"reference_name": self.name,
				"content": f"Configuración de transparencia activada: {self.config_name}",
				"comment_email": frappe.session.user,
			}

			frappe.get_doc(audit_entry).insert(ignore_permissions=True)

	# =============================================================================
	# ACCESS CONTROL METHODS
	# =============================================================================

	def check_financial_data_access(self, user, data_type):
		"""Verificar acceso a datos financieros para un usuario"""
		user_roles = frappe.get_roles(user)

		# Mapeo de tipos de datos a niveles de transparencia
		transparency_mapping = {
			"income": self.income_transparency_level,
			"expense": self.expense_transparency_level,
			"budget": self.budget_transparency_level,
			"balance": self.balance_transparency_level,
			"reserve": self.reserve_transparency_level,
		}

		transparency_level = transparency_mapping.get(data_type, "Oculto")

		# Determinar acceso basado en roles y nivel de transparencia
		if "Administrador Financiero" in user_roles:
			return "Completo"
		elif "Comité Administración" in user_roles:
			return transparency_level if transparency_level != "Oculto" else "Resumen"
		elif "Contador Condominio" in user_roles:
			return transparency_level if transparency_level in ["Detallado", "Completo"] else "Resumen"
		elif "Residente Propietario" in user_roles:
			return transparency_level if transparency_level != "Oculto" else "Sin Acceso"
		else:
			return "Sin Acceso"

	def check_document_access(self, user, document_type):
		"""Verificar acceso a documentos específicos"""
		frappe.get_roles(user)

		# Mapeo de tipos de documentos a niveles de acceso
		access_mapping = {
			"invoices": self.invoices_access_level,
			"payments": self.payments_access_level,
			"contracts": self.contracts_access_level,
			"reports": self.reports_access_level,
			"committee_decisions": self.committee_decisions_access,
		}

		access_level = access_mapping.get(document_type, "Sin Acceso")

		# Aplicar reglas personalizadas si están habilitadas
		if self.enable_custom_rules:
			access_level = self.apply_custom_access_rules(user, document_type, access_level)

		return access_level

	def apply_custom_access_rules(self, user, document_type, current_access):
		"""Aplicar reglas de acceso personalizadas"""
		# Obtener información del usuario/residente
		user_info = self.get_user_property_info(user)

		# Aplicar restricciones por tipo de propiedad
		if self.property_type_restrictions and user_info.get("property_type"):
			if user_info["property_type"] in self.property_type_restrictions:
				return "Sin Acceso"

		# Aplicar reglas por porcentaje de propiedad
		if self.ownership_percentage_rules and user_info.get("ownership_percentage"):
			ownership_pct = user_info["ownership_percentage"]
			# Ejemplo: Si ownership < 5%, acceso limitado
			if ownership_pct < 5 and current_access == "Todos Detallados":
				return "Todos Resumen"

		# Aplicar restricciones por estado de pago
		if self.payment_status_restrictions and user_info.get("payment_status"):
			if user_info["payment_status"] == "Moroso":
				return "Sin Acceso" if document_type == "reports" else current_access

		return current_access

	def get_user_property_info(self, user):
		"""Obtener información de propiedad del usuario"""
		# Query para obtener información del usuario desde Property Account
		user_info = frappe.db.sql(
			"""
			SELECT
				pa.property_type,
				pa.ownership_percentage,
				CASE
					WHEN pa.current_balance < 0 THEN 'Moroso'
					WHEN pa.current_balance = 0 THEN 'Al Corriente'
					ELSE 'Con Saldo a Favor'
				END as payment_status
			FROM `tabProperty Account` pa
			INNER JOIN `tabCustomer` c ON pa.customer = c.name
			WHERE c.owner = %s
			LIMIT 1
		""",
			[user],
			as_dict=True,
		)

		return user_info[0] if user_info else {}

	# =============================================================================
	# API METHODS
	# =============================================================================

	@frappe.whitelist()
	def get_transparency_summary(self):
		"""Obtener resumen de configuración de transparencia"""
		return {
			"basic_info": {
				"config_name": self.config_name,
				"transparency_level": self.transparency_level,
				"config_status": self.config_status,
				"effective_from": self.effective_from,
			},
			"financial_transparency": {
				"income_level": self.income_transparency_level,
				"expense_level": self.expense_transparency_level,
				"budget_level": self.budget_transparency_level,
				"balance_level": self.balance_transparency_level,
				"reserve_level": self.reserve_transparency_level,
			},
			"access_control": {
				"role_based_access": self.enable_role_based_access,
				"default_access": self.default_access_level,
				"resident_portal": self.enable_resident_portal,
				"portal_level": self.portal_access_level,
			},
			"compliance": {
				"regulatory_level": self.regulatory_compliance_level,
				"audit_required": self.audit_trail_required,
				"data_retention": self.data_retention_period,
				"privacy_level": self.privacy_protection_level,
			},
		}

	@frappe.whitelist()
	def check_user_access(self, user, resource_type, resource_name=None):
		"""Verificar acceso de usuario a recurso específico"""
		if resource_type == "financial_data":
			return self.check_financial_data_access(user, resource_name)
		elif resource_type == "document":
			return self.check_document_access(user, resource_name)
		else:
			return "Sin Acceso"

	@frappe.whitelist()
	def generate_transparency_report(self):
		"""Generar reporte de transparencia"""
		if not self.monthly_transparency_report:
			frappe.throw(_("Reportes de transparencia no están habilitados"))

		report_data = {
			"period": getdate().strftime("%B %Y"),
			"config_summary": self.get_transparency_summary(),
			"access_statistics": self.get_access_statistics(),
			"compliance_status": self.get_compliance_status(),
		}

		return report_data

	def get_access_statistics(self):
		"""Obtener estadísticas de acceso"""
		# Esta función se puede expandir para obtener estadísticas reales
		return {
			"total_users": frappe.db.count("User"),
			"active_residents": frappe.db.count("Property Account", {"account_status": "Activa"}),
			"portal_enabled": self.enable_resident_portal,
			"transparency_level": self.transparency_level,
		}

	def get_compliance_status(self):
		"""Obtener estado de cumplimiento"""
		return {
			"regulatory_compliance": self.regulatory_compliance_level,
			"audit_trail_active": self.audit_trail_required,
			"data_retention_configured": bool(self.data_retention_period),
			"privacy_protection": self.privacy_protection_level,
			"external_audit_ready": self.external_audit_access,
		}

	@frappe.whitelist()
	def update_transparency_level(self, new_level, reason=None):
		"""Actualizar nivel de transparencia"""
		old_level = self.transparency_level
		self.transparency_level = new_level

		# Reconfigurar defaults según nuevo nivel
		if new_level == "Básico":
			self.set_basic_transparency_defaults()
		elif new_level == "Estándar":
			self.set_standard_transparency_defaults()
		elif new_level == "Avanzado":
			self.set_advanced_transparency_defaults()
		elif new_level == "Completo":
			self.set_complete_transparency_defaults()

		self.save()

		# Crear registro de auditoría
		if self.audit_trail_required:
			audit_message = f"Nivel de transparencia cambiado de '{old_level}' a '{new_level}'"
			if reason:
				audit_message += f". Razón: {reason}"

			frappe.get_doc(
				{
					"doctype": "Comment",
					"comment_type": "Info",
					"reference_doctype": "Financial Transparency Config",
					"reference_name": self.name,
					"content": audit_message,
					"comment_email": frappe.session.user,
				}
			).insert(ignore_permissions=True)

		return {
			"success": True,
			"message": _("Nivel de transparencia actualizado a {0}").format(new_level),
			"old_level": old_level,
			"new_level": new_level,
		}

	# =============================================================================
	# STATIC METHODS
	# =============================================================================

	@staticmethod
	def get_active_config(company):
		"""Obtener configuración activa para una company"""
		config = frappe.db.get_value(
			"Financial Transparency Config",
			{"company": company, "config_status": "Activo"},
			["name", "transparency_level", "enable_role_based_access"],
		)

		if config:
			return frappe.get_doc("Financial Transparency Config", config[0])
		else:
			return None

	@staticmethod
	def get_default_transparency_config():
		"""Obtener configuración de transparencia por defecto"""
		return {
			"transparency_level": "Estándar",
			"income_transparency_level": "Detallado",
			"expense_transparency_level": "Detallado",
			"budget_transparency_level": "Resumen",
			"balance_transparency_level": "Resumen",
			"reserve_transparency_level": "Resumen",
			"enable_resident_portal": True,
			"portal_access_level": "Estándar",
			"regulatory_compliance_level": "Estándar",
			"data_retention_period": 5,
		}
