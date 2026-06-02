# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Custom fields on Frappe Event DocType for condominium event management.

Called from after_migrate hook — idempotent, safe to run multiple times.
Creates new fields, and syncs insert_after + label on existing ones.
"""

import frappe

MEETING_DEPENDS = "eval:doc.event_category=='Meeting'"
COMMITTEE_DEPENDS = "eval:doc.condominium_meeting_type=='Committee Meeting'"
ASSEMBLY_DEPENDS = "eval:doc.condominium_meeting_type=='Assembly'"
PUBLISHED_DEPENDS = "eval:doc.asm_convocation_published"
CE_DEPENDS = "eval:doc.condominium_meeting_type=='Community Event'"
CE_REG_DEPENDS = "eval:doc.condominium_meeting_type=='Community Event' && doc.ce_registration_required"
CE_APPROVAL_DEPENDS = "eval:doc.condominium_meeting_type=='Community Event' && doc.ce_requires_approval"

CUSTOM_FIELDS = [
	# ── Meeting type selector (visible when event_category == Meeting) ─────────
	{
		"dt": "Event",
		"fieldname": "condominium_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Reunión",
		"options": "Committee Meeting\nAssembly\nCommunity Event\nWork Meeting",
		"insert_after": "event_category",
		"depends_on": MEETING_DEPENDS,
		"read_only_depends_on": "eval:!doc.__islocal",
	},
	# ── Committee Meeting tab ─────────────────────────────────────────────────
	# depends_on intentionally empty — visibility via JS toggle_meeting_tabs().
	# committee_header_section ensures all sections have depends_on so Tab.refresh()
	# auto-hides the tab when no section is visible (fixes "tab always visible" bug).
	{
		"dt": "Event",
		"fieldname": "committee_tab",
		"fieldtype": "Tab Break",
		"label": "Comité",
		"insert_after": "links",
		"depends_on": "",
	},
	{
		"dt": "Event",
		"fieldname": "committee_header_section",
		"fieldtype": "Section Break",
		"insert_after": "committee_tab",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Sesión",
		"options": "Ordinaria\nExtraordinaria\nEmergencia\nTrabajo",
		"insert_after": "committee_header_section",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_agenda_section",
		"fieldtype": "Section Break",
		"label": "Agenda",
		"insert_after": "committee_meeting_type",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_agenda_items",
		"fieldtype": "Table",
		"label": "Puntos de Agenda",
		"options": "Event Committee Agenda Item",
		"insert_after": "committee_agenda_section",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_agreements_section",
		"fieldtype": "Section Break",
		"label": "Acuerdos",
		"insert_after": "committee_agenda_items",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_agreements_widget",
		"fieldtype": "HTML",
		"label": "Acuerdos",
		"insert_after": "committee_agreements_section",
		"depends_on": COMMITTEE_DEPENDS,
	},
	# ── Assembly tab ───────────────────────────────────────────────────────────
	# depends_on intentionally empty — same reasoning as committee_tab above.
	{
		"dt": "Event",
		"fieldname": "assembly_tab",
		"fieldtype": "Tab Break",
		"label": "Asamblea",
		"insert_after": "committee_agreements_widget",
		"depends_on": "",
	},
	# ── 1. Tipo de Asamblea ────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_type",
		"fieldtype": "Select",
		"label": "Tipo de Asamblea",
		"options": "Ordinaria\nExtraordinaria",
		"insert_after": "assembly_tab",
		"depends_on": ASSEMBLY_DEPENDS,
		"mandatory_depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": "eval:!doc.__islocal",
		"reqd": 0,
	},
	# ── 2. Convocatoria ────────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_quorum_section",
		"fieldtype": "Section Break",
		"label": "Convocatoria",
		"insert_after": "asm_type",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_date",
		"fieldtype": "Date",
		"label": "Fecha de Convocatoria",
		"insert_after": "asm_quorum_section",
		"depends_on": ASSEMBLY_DEPENDS,
		"mandatory_depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
		"reqd": 0,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convener",
		"fieldtype": "Link",
		"label": "Convocante",
		"options": "Committee Member",
		"insert_after": "asm_convocation_date",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_col_break",
		"fieldtype": "Column Break",
		"insert_after": "asm_convener",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_first_call",
		"fieldtype": "Time",
		"label": "Hora Primera Convocatoria",
		"insert_after": "asm_col_break",
		"depends_on": ASSEMBLY_DEPENDS,
		"mandatory_depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
		"reqd": 0,
	},
	{
		"dt": "Event",
		"fieldname": "asm_second_call",
		"fieldtype": "Time",
		"label": "Hora Segunda Convocatoria",
		"insert_after": "asm_first_call",
		"depends_on": ASSEMBLY_DEPENDS,
		"mandatory_depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
		"reqd": 0,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_first",
		"fieldtype": "Percent",
		"label": "Quórum Mínimo Primera Convocatoria",
		"insert_after": "asm_second_call",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_second",
		"fieldtype": "Percent",
		"label": "Quórum Mínimo Segunda Convocatoria",
		"insert_after": "asm_quorum_first",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	# ── 3. Medios de Notificación ──────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_formal_section",
		"fieldtype": "Section Break",
		"label": "Medios de Notificación",
		"insert_after": "asm_quorum_second",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notif_email",
		"fieldtype": "Check",
		"label": "Email",
		"insert_after": "asm_formal_section",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notif_fisico",
		"fieldtype": "Check",
		"label": "Aviso físico",
		"insert_after": "asm_notif_email",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notif_portal",
		"fieldtype": "Check",
		"label": "Portal digital",
		"insert_after": "asm_notif_fisico",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notif_publicacion",
		"fieldtype": "Check",
		"label": "Publicación",
		"insert_after": "asm_notif_portal",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notif_otro",
		"fieldtype": "Check",
		"label": "Otro",
		"insert_after": "asm_notif_publicacion",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_formal_col",
		"fieldtype": "Column Break",
		"insert_after": "asm_notif_otro",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_document",
		"fieldtype": "Attach",
		"label": "Documento de Convocatoria",
		"insert_after": "asm_formal_col",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only_depends_on": PUBLISHED_DEPENDS,
	},
	# ── 4. Agenda ─────────────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_agenda_section",
		"fieldtype": "Section Break",
		"label": "Agenda Formal",
		"insert_after": "asm_convocation_document",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_formal_agenda",
		"fieldtype": "Table",
		"label": "Agenda Formal",
		"options": "Assembly Agenda",
		"insert_after": "asm_agenda_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── 5. Registro de Quórum ─────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_quorum_reg_section",
		"fieldtype": "Section Break",
		"label": "Registro de Asistencia",
		"insert_after": "asm_formal_agenda",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_registration",
		"fieldtype": "Table",
		"label": "Registro de Quórum",
		"options": "Quorum Record",
		"insert_after": "asm_quorum_reg_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_col",
		"fieldtype": "Column Break",
		"insert_after": "asm_quorum_registration",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_opened_in_call",
		"fieldtype": "Select",
		"label": "Abierta en Convocatoria",
		"options": "Primera Convocatoria\nSegunda Convocatoria",
		"insert_after": "asm_quorum_col",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_current",
		"fieldtype": "Percent",
		"label": "Quórum Actual (%)",
		"insert_after": "asm_opened_in_call",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only": 1,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_reached",
		"fieldtype": "Check",
		"label": "Quórum Alcanzado",
		"insert_after": "asm_quorum_current",
		"depends_on": ASSEMBLY_DEPENDS,
		"read_only": 1,
	},
	# ── 6. Cierre de Asamblea ─────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_execution_section",
		"fieldtype": "Section Break",
		"label": "Cierre de Asamblea",
		"insert_after": "asm_quorum_reached",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_actual_start",
		"fieldtype": "Datetime",
		"label": "Hora Real de Inicio",
		"insert_after": "asm_execution_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_actual_end",
		"fieldtype": "Datetime",
		"label": "Hora Real de Cierre",
		"insert_after": "asm_actual_start",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_status",
		"fieldtype": "Select",
		"label": "Estado de Asamblea",
		"options": "Planificada\nConvocada\nEn Progreso\nCerrada\nCancelada",
		"insert_after": "asm_actual_end",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_number",
		"fieldtype": "Data",
		"label": "Número / Folio de Asamblea",
		"insert_after": "asm_status",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_agreements_tasks_created",
		"fieldtype": "Check",
		"label": "Acuerdos convertidos en tareas",
		"insert_after": "asm_number",
		"depends_on": ASSEMBLY_DEPENDS,
		"default": "0",
	},
	# ── 7. Mesa de Asamblea ───────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_assembly_officers_section",
		"fieldtype": "Section Break",
		"label": "Mesa de Asamblea",
		"insert_after": "asm_agreements_tasks_created",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_presiding_officer",
		"fieldtype": "Data",
		"label": "Presidente de Asamblea",
		"insert_after": "asm_assembly_officers_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_secretary",
		"fieldtype": "Data",
		"label": "Secretario de Actas",
		"insert_after": "asm_presiding_officer",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_col3",
		"fieldtype": "Column Break",
		"insert_after": "asm_secretary",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_declared_on",
		"fieldtype": "Datetime",
		"label": "Hora de Declaración de Quórum",
		"insert_after": "asm_col3",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── 8. Asuntos Generales ──────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_notes_section",
		"fieldtype": "Section Break",
		"label": "Asuntos Generales",
		"insert_after": "asm_quorum_declared_on",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notes",
		"fieldtype": "Text Editor",
		"label": "Asuntos Generales",
		"insert_after": "asm_notes_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── 9. Formalización del Acta ─────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_formalization_section",
		"fieldtype": "Section Break",
		"label": "Formalización del Acta",
		"insert_after": "asm_notes",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_minutes_status",
		"fieldtype": "Select",
		"label": "Estado del Acta",
		"options": "Borrador\nGenerada\nFirmada\nCancelada",
		"insert_after": "asm_formalization_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_minutes_document",
		"fieldtype": "Attach",
		"label": "Documento del Acta",
		"insert_after": "asm_minutes_status",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_formal_col2",
		"fieldtype": "Column Break",
		"insert_after": "asm_minutes_document",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_requires_protocolization",
		"fieldtype": "Check",
		"label": "Requiere Protocolización",
		"insert_after": "asm_formal_col2",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_protocolization_notes",
		"fieldtype": "Small Text",
		"label": "Notas de Protocolización",
		"insert_after": "asm_requires_protocolization",
		"depends_on": "eval:doc.condominium_meeting_type=='Assembly' && doc.asm_requires_protocolization",
	},
	# ── Banderas internas (hidden) ────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_convocation_published",
		"fieldtype": "Check",
		"label": "Convocatoria Publicada",
		"insert_after": "asm_protocolization_notes",
		"depends_on": ASSEMBLY_DEPENDS,
		"hidden": 1,
		"default": "0",
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_published_on",
		"fieldtype": "Datetime",
		"label": "Fecha de Publicación de Convocatoria",
		"insert_after": "asm_convocation_published",
		"depends_on": ASSEMBLY_DEPENDS,
		"hidden": 1,
		"read_only": 1,
	},
	# ── 8. Acuerdos de Seguimiento ────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_agreements_section",
		"fieldtype": "Section Break",
		"label": "Acuerdos de Seguimiento",
		"insert_after": "asm_convocation_published_on",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_agreements_widget",
		"fieldtype": "HTML",
		"label": "Acuerdos de Seguimiento",
		"insert_after": "asm_agreements_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── Community Event tab ────────────────────────────────────────────────────
	# depends_on intentionally empty — visibility controlled 100% via JS toggle_meeting_tabs()
	{
		"dt": "Event",
		"fieldname": "community_event_tab",
		"fieldtype": "Tab Break",
		"label": "Evento Comunitario",
		"insert_after": "asm_agreements_widget",
		"depends_on": "",
	},
	# ── 1. Configuración ──────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "ce_config_section",
		"fieldtype": "Section Break",
		"label": "Configuración del Evento",
		"insert_after": "community_event_tab",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_event_type",
		"fieldtype": "Select",
		"label": "Tipo de Evento",
		"options": "Social\nDeportivo\nCultural\nInfantil\nInformativo\nOtro",
		"insert_after": "ce_config_section",
		"depends_on": CE_DEPENDS,
		"reqd": 1,
	},
	{
		"dt": "Event",
		"fieldname": "ce_target_audience",
		"fieldtype": "Select",
		"label": "Audiencia (informativo)",
		"options": "Todos los Propietarios\nSolo Residentes\nComité\nGrupo específico",
		"insert_after": "ce_event_type",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_status",
		"fieldtype": "Select",
		"label": "Estado del Evento",
		"options": "Planeado\nPublicado\nFinalizado\nCancelado",
		"insert_after": "ce_target_audience",
		"depends_on": CE_DEPENDS,
		"default": "Planeado",
	},
	{
		"dt": "Event",
		"fieldname": "ce_outdoor_event",
		"fieldtype": "Check",
		"label": "Evento al aire libre (verificar clima)",
		"insert_after": "ce_status",
		"depends_on": CE_DEPENDS,
		"default": "0",
	},
	# ── 2. Registro y Capacidad ───────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "ce_registration_section",
		"fieldtype": "Section Break",
		"label": "Registro y Capacidad",
		"insert_after": "ce_outdoor_event",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_registration_required",
		"fieldtype": "Check",
		"label": "Requiere Registro",
		"insert_after": "ce_registration_section",
		"depends_on": CE_DEPENDS,
		"default": "0",
	},
	{
		"dt": "Event",
		"fieldname": "ce_max_capacity",
		"fieldtype": "Int",
		"label": "Capacidad Máxima",
		"insert_after": "ce_registration_required",
		"depends_on": CE_REG_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_rsvp_deadline",
		"fieldtype": "Date",
		"label": "Fecha Límite de Registro",
		"insert_after": "ce_max_capacity",
		"depends_on": CE_REG_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_col1",
		"fieldtype": "Column Break",
		"insert_after": "ce_rsvp_deadline",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_current_count",
		"fieldtype": "Int",
		"label": "Registrados",
		"insert_after": "ce_col1",
		"depends_on": CE_REG_DEPENDS,
		"read_only": 1,
	},
	{
		"dt": "Event",
		"fieldname": "ce_available_capacity",
		"fieldtype": "Int",
		"label": "Capacidad Disponible",
		"insert_after": "ce_current_count",
		"depends_on": CE_REG_DEPENDS,
		"read_only": 1,
	},
	# ── 3. Presupuesto ────────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "ce_budget_section",
		"fieldtype": "Section Break",
		"label": "Presupuesto",
		"insert_after": "ce_available_capacity",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_estimated_budget",
		"fieldtype": "Currency",
		"label": "Presupuesto estimado (informativo)",
		"insert_after": "ce_budget_section",
		"depends_on": CE_DEPENDS,
	},
	# ── Aprobación — campos reemplazados por checklist, ahora ocultos ────────
	{
		"dt": "Event",
		"fieldname": "ce_approval_section",
		"fieldtype": "Section Break",
		"label": "Aprobación",
		"insert_after": "ce_estimated_budget",
		"depends_on": CE_DEPENDS,
		"hidden": 1,
	},
	{
		"dt": "Event",
		"fieldname": "ce_requires_approval",
		"fieldtype": "Check",
		"label": "Requiere Aprobación",
		"insert_after": "ce_approval_section",
		"depends_on": CE_DEPENDS,
		"hidden": 1,
		"default": "0",
	},
	{
		"dt": "Event",
		"fieldname": "ce_approval_reference",
		"fieldtype": "Data",
		"label": "Referencia de Aprobación",
		"insert_after": "ce_requires_approval",
		"depends_on": CE_APPROVAL_DEPENDS,
		"hidden": 1,
	},
	# ── 4. Lista de Verificación ──────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "ce_checklist_section",
		"fieldtype": "Section Break",
		"label": "Lista de Verificación",
		"insert_after": "ce_outdoor_event",
		"depends_on": CE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "ce_checklist",
		"fieldtype": "Table",
		"label": "Checklist",
		"options": "Event Checklist Progress",
		"insert_after": "ce_checklist_section",
		"depends_on": CE_DEPENDS,
	},
]

# Properties synced on existing Custom Fields
_SYNC_PROPS = (
	"insert_after",
	"label",
	"depends_on",
	"mandatory_depends_on",
	"options",
	"read_only_depends_on",
	"reqd",
	"hidden",
	"default",
)


def setup_event_committee_fields():
	"""Create or sync custom fields on Event for committee/assembly support.

	Idempotent: creates missing fields and updates insert_after + label on
	existing ones so reordering is applied without manual DB cleanup.
	"""
	created = []
	for field in CUSTOM_FIELDS:
		name = f"{field['dt']}-{field['fieldname']}"
		if frappe.db.exists("Custom Field", name):
			updates = {}
			for prop in _SYNC_PROPS:
				if prop not in field:
					continue
				current = frappe.db.get_value("Custom Field", name, prop)
				if current != field[prop]:
					updates[prop] = field[prop]
			for k, v in updates.items():
				frappe.db.set_value("Custom Field", name, k, v)
			continue

		doc = frappe.get_doc({"doctype": "Custom Field", **field})
		doc.insert(ignore_permissions=True)
		created.append(field["fieldname"])

	if created:
		frappe.db.commit()

	return created
