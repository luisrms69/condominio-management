# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Custom fields on Frappe Event DocType for condominium event management.

Called from after_migrate hook — idempotent, safe to run multiple times.
Only creates fields that don't exist yet; never modifies or deletes existing ones.
"""

import frappe

MEETING_DEPENDS = "eval:doc.event_category=='Meeting'"
COMMITTEE_DEPENDS = "eval:doc.condominium_meeting_type=='Committee Meeting'"
ASSEMBLY_DEPENDS = "eval:doc.condominium_meeting_type=='Assembly'"

CUSTOM_FIELDS = [
	# ── Meeting type selector (visible when event_category == Meeting) ─────────
	{
		"dt": "Event",
		"fieldname": "condominium_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Reunión",
		"options": "Committee Meeting\nAssembly\nWork Meeting",
		"insert_after": "event_participants",
		"depends_on": MEETING_DEPENDS,
		"read_only_depends_on": "eval:!doc.__islocal",
	},
	# ── Committee Meeting specific ─────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "committee_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Sesión",
		"options": "Ordinaria\nExtraordinaria\nEmergencia\nTrabajo",
		"insert_after": "committee_tab",
		"depends_on": COMMITTEE_DEPENDS,
	},
	# ── Agenda child table ─────────────────────────────────────────────────────
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
	# ── Assembly ───────────────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "assembly_tab",
		"fieldtype": "Tab Break",
		"label": "Asamblea",
		"insert_after": "committee_agreements_widget",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_type",
		"fieldtype": "Select",
		"label": "Tipo de Asamblea",
		"options": "Ordinaria\nExtraordinaria",
		"insert_after": "assembly_tab",
		"depends_on": ASSEMBLY_DEPENDS,
		"reqd": 1,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_date",
		"fieldtype": "Date",
		"label": "Fecha de Convocatoria",
		"insert_after": "asm_type",
		"depends_on": ASSEMBLY_DEPENDS,
		"reqd": 1,
	},
	{
		"dt": "Event",
		"fieldname": "asm_col_break",
		"fieldtype": "Column Break",
		"insert_after": "asm_convocation_date",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_first_call",
		"fieldtype": "Time",
		"label": "Hora Primera Convocatoria",
		"insert_after": "asm_col_break",
		"depends_on": ASSEMBLY_DEPENDS,
		"reqd": 1,
	},
	{
		"dt": "Event",
		"fieldname": "asm_second_call",
		"fieldtype": "Time",
		"label": "Hora Segunda Convocatoria",
		"insert_after": "asm_first_call",
		"depends_on": ASSEMBLY_DEPENDS,
		"reqd": 1,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_section",
		"fieldtype": "Section Break",
		"label": "Quórum",
		"insert_after": "asm_second_call",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_first",
		"fieldtype": "Percent",
		"label": "Quórum Mínimo Primera Convocatoria",
		"insert_after": "asm_quorum_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_second",
		"fieldtype": "Percent",
		"label": "Quórum Mínimo Segunda Convocatoria",
		"insert_after": "asm_quorum_first",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_col",
		"fieldtype": "Column Break",
		"insert_after": "asm_quorum_second",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_quorum_current",
		"fieldtype": "Percent",
		"label": "Quórum Actual (%)",
		"insert_after": "asm_quorum_col",
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
	{
		"dt": "Event",
		"fieldname": "asm_agenda_section",
		"fieldtype": "Section Break",
		"label": "Agenda Formal",
		"insert_after": "asm_quorum_reached",
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
	{
		"dt": "Event",
		"fieldname": "asm_quorum_reg_section",
		"fieldtype": "Section Break",
		"label": "Control de Quórum",
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
		"fieldname": "asm_notes_section",
		"fieldtype": "Section Break",
		"label": "Notas",
		"insert_after": "asm_quorum_registration",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_notes",
		"fieldtype": "Text Editor",
		"label": "Notas de la Asamblea",
		"insert_after": "asm_notes_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── Datos formales — convocatoria ──────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_formal_section",
		"fieldtype": "Section Break",
		"label": "Datos Formales",
		"insert_after": "asm_notes",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_number",
		"fieldtype": "Data",
		"label": "Número / Folio de Asamblea",
		"insert_after": "asm_formal_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_status",
		"fieldtype": "Select",
		"label": "Estado de Asamblea",
		"options": "Planificada\nConvocada\nEn Progreso\nCerrada\nCancelada",
		"insert_after": "asm_number",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convener",
		"fieldtype": "Link",
		"label": "Convocante",
		"options": "Committee Member",
		"insert_after": "asm_status",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_formal_col",
		"fieldtype": "Column Break",
		"insert_after": "asm_convener",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_method",
		"fieldtype": "Select",
		"label": "Medio de Convocatoria",
		"options": "Email\nFísico\nPortal\nPublicación\nOtro",
		"insert_after": "asm_formal_col",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_convocation_document",
		"fieldtype": "Attach",
		"label": "Documento de Convocatoria",
		"insert_after": "asm_convocation_method",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	# ── Datos formales — ejecución / cierre ────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "asm_execution_section",
		"fieldtype": "Section Break",
		"label": "Ejecución y Cierre",
		"insert_after": "asm_convocation_document",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_opened_in_call",
		"fieldtype": "Select",
		"label": "Abierta en Convocatoria",
		"options": "Primera Convocatoria\nSegunda Convocatoria",
		"insert_after": "asm_execution_section",
		"depends_on": ASSEMBLY_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "asm_actual_start",
		"fieldtype": "Datetime",
		"label": "Hora Real de Inicio",
		"insert_after": "asm_opened_in_call",
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
]


def setup_event_committee_fields():
	"""Create custom fields on Event for committee meeting support.

	Idempotent: skips fields that already exist.
	"""
	created = []
	for field in CUSTOM_FIELDS:
		name = f"{field['dt']}-{field['fieldname']}"
		if frappe.db.exists("Custom Field", name):
			# Update read_only_depends_on if specified and changed
			if "read_only_depends_on" in field:
				current = frappe.db.get_value("Custom Field", name, "read_only_depends_on")
				if current != field["read_only_depends_on"]:
					frappe.db.set_value(
						"Custom Field", name, "read_only_depends_on", field["read_only_depends_on"]
					)
			continue
		doc = frappe.get_doc({"doctype": "Custom Field", **field})
		doc.insert(ignore_permissions=True)
		created.append(field["fieldname"])

	if created:
		frappe.db.commit()

	return created
