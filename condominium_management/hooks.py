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
# doctype_js = {"doctype" : "public/js/doctype.js"}
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
	"Property Usage Type": {
		"validate": "condominium_management.committee_management.hooks_handlers.property_usage_type_validation.validate",
	},
	"Acquisition Type": {
		"validate": "condominium_management.committee_management.hooks_handlers.acquisition_type_validation.validate",
	},
	"Property Status Type": {
		"validate": "condominium_management.committee_management.hooks_handlers.property_status_type_validation.validate",
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
fixtures = [
	"Master Template Registry",
	"Entity Type Configuration",
	{
		"doctype": "Contribution Category",
		"filters": {"module_name": ["in", ["Document Generation", "Maintenance", "Contracts"]]},
	},
	# Companies Module Masters
	"Company Type",
	"Property Usage Type",
	"Acquisition Type",
	"Property Status Type",
	"Policy Category",
	"Enforcement Level",
	"User Type",
	"Document Template Type",
	"Jurisdiction Level",
	"Compliance Requirement Type",
]

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
