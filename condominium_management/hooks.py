app_name = "condominium_management"
app_title = "Condominium Management"
app_publisher = "Buzola"
app_description = "Sistema Integral de administración de condominios"
app_email = "it@buzola.mx"
app_license = "gpl-3.0"

# Apps
# ------------------

required_apps = ["erpnext"]

# Modules
# ------------------

modules = {
	"companies": {
		"color": "blue",
		"icon": "octicon octicon-organization",
		"type": "module",
		"label": "Companies",
	},
	"document_generation": {
		"color": "green",
		"icon": "octicon octicon-file-text",
		"type": "module",
		"label": "Document Generation",
	},
	"community_contributions": {
		"color": "purple",
		"icon": "octicon octicon-git-pull-request",
		"type": "module",
		"label": "Community Contributions",
	},
	"physical_spaces": {
		"color": "orange",
		"icon": "octicon octicon-home",
		"type": "module",
		"label": "Physical Spaces",
	},
	"committee_management": {
		"color": "red",
		"icon": "octicon octicon-gavel",
		"type": "module",
		"label": "Committee Management",
	},
	"dashboard_consolidado": {
		"color": "teal",
		"icon": "octicon octicon-dashboard",
		"type": "module",
		"label": "Dashboard Consolidado",
	},
}

# Translations
# ------------
# translations are available in the app
app_include_locale = "translations"

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "condominium_management",
# 		"logo": "/assets/condominium_management/logo.png",
# 		"title": "Condominium Management",
# 		"route": "/condominium_management",
# 		"has_permission": "condominium_management.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/condominium_management/css/condominium_management.css"
# app_include_js = "/assets/condominium_management/js/condominium_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/condominium_management/css/condominium_management.css"
# web_include_js = "/assets/condominium_management/js/condominium_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "condominium_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Event": "public/js/event_committee.js",
	"Committee Poll": "committee_management/doctype/committee_poll/committee_poll.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "condominium_management/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "condominium_management.utils.jinja_methods",
# 	"filters": "condominium_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "condominium_management.install.before_install"
after_install = "condominium_management.install.after_install"
after_migrate = [
	"condominium_management.committee_management.default_positions.setup_positions_for_all_condo_companies",
	"condominium_management.committee_management.event_custom_fields.setup_event_committee_fields",
	"condominium_management.committee_management.community_event_checklist.setup_event_checklist_items",
]

# Uninstallation
# ------------

# before_uninstall = "condominium_management.uninstall.before_uninstall"
# after_uninstall = "condominium_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "condominium_management.utils.before_app_install"
# after_app_install = "condominium_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "condominium_management.utils.before_app_uninstall"
# after_app_uninstall = "condominium_management.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "condominium_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# Document Generation Events
# ---------------------------
# Universal hooks for auto-detection of entities requiring document configuration
# TEMPORALMENTE DESACTIVADOS: Los hooks universales ("*") interfieren con el setup wizard de ERPNext
# causando errores de validación de enlaces durante CI. Se reactivarán después del merge.
# ISSUE #7: Reactivar hooks universales con verificaciones de contexto
# PRIORIDAD: CRÍTICA - Debe resolverse inmediatamente después del merge
doc_events = {
	# "*": {
	# 	"after_insert": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_insert",
	# 	"on_update": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_update",
	# },
	# Committee Management — Assembly validation on native Event
	"Event": {
		"validate": "condominium_management.committee_management.event_hooks.validate_assembly",
	},
	"Master Template Registry": {
		"on_update": "condominium_management.document_generation.hooks_handlers.template_propagation.on_template_update"
	},
	"Entity Configuration": {
		"validate": "condominium_management.document_generation.hooks_handlers.auto_detection.validate_entity_configuration",
		"on_update": "condominium_management.document_generation.hooks_handlers.auto_detection.check_configuration_conflicts",
	},
	# Companies Module Hooks
	# ----------------------
	# Hooks específicos para módulo Companies - auto-detección de configuraciones
	"Company": {
		"validate": "condominium_management.companies.hooks.company_hooks.validate_company_fields",
		"after_insert": "condominium_management.companies.hooks_handlers.company_detection.after_insert",
		"on_update": "condominium_management.companies.hooks_handlers.company_detection.on_update",
		"on_save": "condominium_management.companies.hooks.company_hooks.on_company_save",
		"on_trash": "condominium_management.companies.hooks.company_hooks.on_company_trash",
	},
	"Service Management Contract": {
		"validate": "condominium_management.companies.hooks_handlers.contract_detection.validate",
		"on_update": "condominium_management.companies.hooks_handlers.contract_detection.on_update",
	},
	"Company Account": {
		"after_insert": "condominium_management.companies.hooks_handlers.account_detection.after_insert",
	},
	# Physical Spaces Module Hooks
	# -----------------------------
	# Hooks específicos para módulo Physical Spaces - validaciones y actualizaciones
	"Physical Space": {
		"after_insert": "condominium_management.physical_spaces.hooks_handlers.space_detection.after_insert",
		"on_update": "condominium_management.physical_spaces.hooks_handlers.space_detection.on_update",
	},
	"Space Category": {
		"validate": "condominium_management.physical_spaces.hooks_handlers.category_validation.validate",
		"on_update": "condominium_management.physical_spaces.hooks_handlers.category_detection.on_update",
	},
	"Space Component": {
		"validate": "condominium_management.physical_spaces.hooks_handlers.component_validation.validate",
		"after_insert": "condominium_management.physical_spaces.hooks_handlers.component_detection.after_insert",
	},
	"Component Type": {
		"validate": "condominium_management.physical_spaces.hooks_handlers.component_type_validation.validate",
		"on_update": "condominium_management.physical_spaces.hooks_handlers.component_type_detection.on_update",
	},
	# Committee Management Module Hooks
	# ---------------------------------
	# Hooks específicos para módulo Committee Management - validaciones y automatizaciones
	"Committee Member": {
		"validate": "condominium_management.committee_management.hooks_handlers.committee_member_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.committee_member_detection.on_update",
		"after_insert": "condominium_management.committee_management.hooks_handlers.committee_member_detection.after_insert",
	},
	"Committee Meeting": {
		"validate": "condominium_management.committee_management.hooks_handlers.committee_meeting_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.committee_meeting_detection.on_update",
		"after_insert": "condominium_management.committee_management.hooks_handlers.committee_meeting_detection.after_insert",
	},
	"Assembly Management": {
		"validate": "condominium_management.committee_management.hooks_handlers.assembly_management_validation.validate",
		"on_submit": "condominium_management.committee_management.hooks_handlers.assembly_management_detection.on_submit",
		"on_update": "condominium_management.committee_management.hooks_handlers.assembly_management_detection.on_update",
	},
	"Voting System": {
		"validate": "condominium_management.committee_management.hooks_handlers.voting_system_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.voting_system_detection.on_update",
		"after_insert": "condominium_management.committee_management.hooks_handlers.voting_system_detection.after_insert",
	},
	"Agreement Tracking": {
		"validate": "condominium_management.committee_management.hooks_handlers.agreement_tracking_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.agreement_tracking_detection.on_update",
		"after_insert": "condominium_management.committee_management.hooks_handlers.agreement_tracking_detection.after_insert",
	},
	"Committee Poll": {
		"validate": "condominium_management.committee_management.hooks_handlers.committee_poll_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.committee_poll_detection.on_update",
	},
	"Community Event": {
		"validate": "condominium_management.committee_management.hooks_handlers.community_event_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.community_event_detection.on_update",
		"after_insert": "condominium_management.committee_management.hooks_handlers.community_event_detection.after_insert",
	},
	"Committee KPI": {
		"validate": "condominium_management.committee_management.hooks_handlers.committee_kpi_validation.validate",
		"on_update": "condominium_management.committee_management.hooks_handlers.committee_kpi_detection.on_update",
	},
	"Meeting Schedule": {
		"validate": "condominium_management.committee_management.hooks_handlers.meeting_schedule_validation.validate",
		"on_submit": "condominium_management.committee_management.hooks_handlers.meeting_schedule_detection.on_submit",
		"on_update": "condominium_management.committee_management.hooks_handlers.meeting_schedule_detection.on_update",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"monthly": ["condominium_management.document_generation.scheduled.performance_monitoring"],
	"daily": [
		"condominium_management.committee_management.scheduled.check_pending_meetings",
		"condominium_management.committee_management.scheduled.check_overdue_agreements",
		"condominium_management.committee_management.scheduled.calculate_daily_kpis",
	],
	"weekly": [
		"condominium_management.committee_management.scheduled.send_meeting_reminders",
		"condominium_management.committee_management.scheduled.generate_weekly_reports",
	],
}

# Testing
# -------

before_tests = "condominium_management.utils.before_tests"

# Fixtures
# --------
# Global fixtures that will be updated via bench update across all sites
#
# NOTA: Fixtures temporalmente deshabilitados tras audit export-fixtures (2025-10-20)
# Ver: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md
# Ver: docs/development/fixtures_auditoria.md
#
fixtures = [
	# ============================================================================
	# DESHABILITADOS - Requieren corrección antes de migrar (0/14)
	# ============================================================================
	"Master Template Registry",  # ✅ ENABLED - Single DocType. NOTA: campo last_update es volátil
	#                              (se actualiza al usar el sistema). Revertir master_template_registry.json
	#                              después de export-fixtures hasta diseñar solución definitiva.
	{
		"dt": "Entity Type Configuration",
		"filters": [["name", "in", ["Service Management Contract"]]],
	},  # ✅ ENABLED (2026-05-21) - Filtro explícito. Registro 'User' excluido hasta decisión humana
	#     sobre si es configuración funcional o artefacto de desarrollo.
	"Company Type",  # ✅ ENABLED - Autoname normalizado (name == type_code)
	"Acquisition Type",  # ✅ ENABLED - required_documents poblado via one-off script
	"Policy Category",  # ✅ ENABLED - 15 categorías profesionales completas
	# "User Type",                    # ❌ ELIMINADO (2025-10-26) - DocType legacy que hacía override incorrecto de Frappe core
	#                                   # Sin implementación real (0 referencias código), conflicto arquitectónico (duplica Roles)
	#                                   # DocType nativo Frappe restaurado. Ver commit para detalles completos.
	{
		"dt": "Contribution Category",
		"filters": [
			[
				"name",
				"in",
				[
					"Contracts-Contract Template",
					"Document Generation-Infrastructure Template",
					"Financial Management-Financial Template",
					"Maintenance-Maintenance Template",
					"Physical Spaces-Space Template",
					"Security-Security Template",
				],
			]
		],
	},  # ✅ ENABLED (2026-05-21) - Filtro explícito. 55 registros de test en admin1.dev excluidos.
	# ============================================================================
	# HABILITADOS - Fixtures válidos listos para migrar (13/14)
	# ============================================================================
	# Companies Module Masters - Solo fixtures verificados como válidos
	"Property Usage Type",  # ✅ VÁLIDO - Cosmético (5 registros íntegros: Residencial, Comercial, Mixto, Industrial, Oficinas)
	"Property Status Type",  # ✅ VÁLIDO - Cosmético (6 registros íntegros: Activo, Inactivo, En Venta, En Arriendo, En Construcción, Abandonado)
	"Enforcement Level",  # ✅ VÁLIDO - Cosmético (4 registros íntegros)
	"Document Template Type",  # ✅ VÁLIDO - Cosmético (registros íntegros)
	"Jurisdiction Level",  # ✅ VÁLIDO - Cosmético (4 registros íntegros)
	"Compliance Requirement Type",  # ✅ VÁLIDO - Cosmético (5 registros íntegros)
	# Physical Spaces Module Masters — catálogo controlado del app (no editar manualmente)
	"Space Category",  # ✅ ENABLED - 51 categorías precargadas para condominios residencial y uso mixto
	# Sistema de Roles custom del sistema (22 roles requeridos por DocType permissions)
	{
		"dt": "Role",
		"filters": [
			[
				"name",
				"in",
				[
					"Administrador Financiero",
					"Administrator Condominio",
					"API Manager",
					"API User",
					"Assembly Participant",
					"Comité Administración",
					"Committee Member",
					"Committee President",
					"Committee Secretary",
					"Company Administrator",
					"Condominium Manager",
					"Condómino",
					"Configuration Approver",
					"Configuration Manager",
					"Contador Condominio",
					"Event Organizer",
					"Gestor de Dashboards",
					"Master Template Manager",
					"Property Administrator",
					"Property Manager",
					"Residente Propietario",
					"Usuario de Dashboards",
				],
			]
		],
	},  # ✅ ENABLED (2026-05-21) - Bloqueante para v16 clean install
	# Companies Module Custom Fields (Company DocType)
	# prefix genera archivo separado (companies_custom_field.json) para evitar que
	# la entrada de Event sobreescriba este archivo en export-fixtures.
	{
		"dt": "Custom Field",
		"prefix": "companies",
		"filters": [
			["dt", "=", "Company"],
			[
				"fieldname",
				"in",
				[
					# Sección Información Condominio (10 campos)
					"condominium_section",
					"company_type",
					"property_usage_type",
					"acquisition_type",
					"property_status_type",
					"cb_condominium_1",
					"total_units",
					"total_area_sqm",
					"construction_year",
					"floors_count",
					# Sección Administración (5 campos)
					"management_section",
					"management_company",
					"management_start_date",
					"management_contract_end_date",
					"managed_properties",
					# Sección Legal (6 campos)
					"legal_section",
					"legal_representative",
					"legal_representative_id",
					"cb_legal_1",
					"registration_chamber_commerce",
					"registration_date",
					# Sección Financiera (6 campos)
					"financial_section",
					"monthly_admin_fee",
					"reserve_fund",
					"cb_financial_1",
					"insurance_policy_number",
					"insurance_expiry_date",
				],
			],
		],
	},
	# Event Custom Fields — Committee Meeting POC
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "=", "Event"],
			[
				"fieldname",
				"in",
				[
					"condominium_meeting_type",
					"committee_tab",
					"committee_meeting_type",
					"committee_agenda_section",
					"committee_agenda_items",
					"committee_agreements_section",
					"committee_agreements_widget",
					"assembly_tab",
					"asm_type",
					"asm_convocation_date",
					"asm_col_break",
					"asm_first_call",
					"asm_second_call",
					"asm_quorum_section",
					"asm_quorum_first",
					"asm_quorum_second",
					"asm_quorum_col",
					"asm_quorum_current",
					"asm_quorum_reached",
					"asm_agenda_section",
					"asm_formal_agenda",
					"asm_quorum_reg_section",
					"asm_quorum_registration",
					"asm_notes_section",
					"asm_notes",
					"asm_formal_section",
					"asm_number",
					"asm_status",
					"asm_convener",
					"asm_formal_col",
					"asm_notif_email",
					"asm_notif_fisico",
					"asm_notif_portal",
					"asm_notif_publicacion",
					"asm_notif_otro",
					"asm_convocation_document",
					"asm_execution_section",
					"asm_opened_in_call",
					"asm_actual_start",
					"asm_actual_end",
					"asm_agreements_section",
					"asm_agreements_widget",
					"asm_assembly_officers_section",
					"asm_presiding_officer",
					"asm_secretary",
					"asm_col3",
					"asm_quorum_declared_on",
					"asm_formalization_section",
					"asm_minutes_status",
					"asm_minutes_document",
					"asm_formal_col2",
					"asm_requires_protocolization",
					"asm_protocolization_notes",
					"asm_agreements_tasks_created",
					"asm_convocation_published",
					"asm_convocation_published_on",
					"community_event_tab",
					"committee_header_section",
					"ce_config_section",
					"ce_event_type",
					"ce_target_audience",
					"ce_status",
					"ce_registration_section",
					"ce_registration_required",
					"ce_max_capacity",
					"ce_rsvp_deadline",
					"ce_col1",
					"ce_current_count",
					"ce_available_capacity",
					"ce_budget_section",
					"ce_estimated_budget",
					"ce_outdoor_event",
					"ce_checklist_section",
					"ce_checklist",
				],
			],
		],
	},
	# Convocatoria de Asamblea — Print Format
	{
		"dt": "Print Format",
		"filters": [["name", "=", "Convocatoria Asamblea"]],
	},
]

# NOTA IMPORTANTE: Los archivos .json de fixtures deshabilitados NO se borran
# Se mantienen en fixtures/ como referencia para correcciones futuras
# Ver plan corrección completo en: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "condominium_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "condominium_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["condominium_management.utils.before_request"]
# after_request = ["condominium_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["condominium_management.utils.before_job"]
# after_job = ["condominium_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"condominium_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
