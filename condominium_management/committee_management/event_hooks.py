# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

# DEPRECATED 2026-06-08 — Event ya no es entidad de asamblea ni de evento comunitario condominial.
# Assembly Management es la entidad canónica de asamblea.
# Community Event es la entidad canónica de eventos comunitarios.
# Este archivo se conserva como referencia histórica. No agregar lógica aquí.
# La entrada doc_events["Event"] fue eliminada de hooks.py en la misma fecha.

"""
Server-side validation for condominium Assembly events.

Registered via doc_events in hooks.py — does NOT modify Event DocType.
Always exits early if the event is not an Assembly.
"""

import frappe

# Valid forward-only status transitions for asm_status
_STATUS_FLOW = {
	"Planificada": {"Convocada", "Cancelada"},
	"Convocada": {"En Progreso", "Cancelada"},
	"En Progreso": {"Cerrada"},
	"Cerrada": set(),
	"Cancelada": set(),
}

# Fields frozen once the convocation is published
_FROZEN_ON_PUBLISH = [
	"asm_type",
	"asm_convocation_date",
	"asm_convener",
	"asm_first_call",
	"asm_second_call",
	"asm_quorum_first",
	"asm_quorum_second",
	"asm_notif_email",
	"asm_notif_fisico",
	"asm_notif_portal",
	"asm_notif_publicacion",
	"asm_notif_otro",
	"asm_convocation_document",
]

# Agenda announcement fields — frozen once convocation is published
_FROZEN_AGENDA_FIELDS = [
	"item_number",
	"agenda_topic",
	"topic_description",
	"presenter",
	"requires_vote",
	"vote_type",
	"required_percentage",
	"supporting_documents",
	# discussion_summary and decisions_taken are intentionally NOT frozen —
	# they are captured during/after the assembly, not announced in the convocation.
]


_CE_STATUS_FLOW = {
	"Planeado": {"Publicado", "Cancelado"},
	"Publicado": {"Finalizado", "Cancelado"},
	"Finalizado": set(),
	"Cancelado": set(),
}


def _validate_community_event(doc):
	if doc.get("ce_registration_required"):
		if not doc.get("ce_max_capacity") or doc.get("ce_max_capacity") <= 0:
			frappe.throw(
				"Se requiere capacidad máxima cuando el registro está activo.",
				title="Configuración de registro",
			)
		if not doc.get("ce_rsvp_deadline"):
			frappe.throw(
				"Se requiere fecha límite de registro.",
				title="Configuración de registro",
			)
		if doc.get("starts_on") and doc.get("ce_rsvp_deadline"):
			from frappe.utils import getdate

			if getdate(doc.ce_rsvp_deadline) >= getdate(doc.starts_on):
				frappe.throw(
					"La fecha límite de registro debe ser anterior a la fecha del evento.",
					title="Configuración de registro",
				)

	if doc.is_new():
		return

	old_status = frappe.db.get_value("Event", doc.name, "ce_status") or "Planeado"
	new_status = doc.get("ce_status") or "Planeado"

	if old_status != new_status:
		allowed = _CE_STATUS_FLOW.get(old_status, set())
		if new_status not in allowed:
			frappe.throw(
				f"Transición de estado no permitida: {old_status} → {new_status}",
				title="Estado del evento",
			)

	if new_status == "Finalizado":
		doc.status = "Closed"
	elif new_status == "Cancelado":
		doc.status = "Cancelled"


def _vals_equal(v1, v2):
	"""Robust comparison that handles Decimal/float/int ORM type variations.

	Frappe returns Percent/Float/Currency from DB as Decimal objects, but stores
	them as Python floats in the doc. str() comparison fails: "75.000000000" != "75.0".
	"""
	if v1 == v2:
		return True
	# Both falsy (None, 0, "") — treat as equivalent
	if not v1 and not v2:
		return True
	if v1 is None or v2 is None:
		return False
	try:
		return float(v1) == float(v2)
	except (TypeError, ValueError):
		return str(v1) == str(v2)


def validate_assembly(doc, method):
	if doc.get("condominium_meeting_type") == "Community Event":
		_validate_community_event(doc)
		return

	if doc.get("condominium_meeting_type") != "Assembly":
		return

	_validate_assembly_required_fields(doc)

	if doc.is_new():
		return

	db_doc = frappe.get_doc("Event", doc.name)

	_validate_asm_type_frozen(doc, db_doc)
	_validate_status_transition(doc, db_doc)
	_validate_closure_agreements(doc, db_doc)
	_sync_event_status(doc)
	_validate_published_fields(doc, db_doc)


_ASM_REQUIRED_FIELDS = {
	"asm_type": "Tipo de Asamblea",
	"asm_convocation_date": "Fecha de Convocatoria",
	"asm_first_call": "Hora Primera Convocatoria",
	"asm_second_call": "Hora Segunda Convocatoria",
}


def _validate_assembly_required_fields(doc):
	"""Server-side mandatory check for Assembly minimum fields.
	Complements mandatory_depends_on in custom field meta for defense-in-depth.
	"""
	missing = [label for field, label in _ASM_REQUIRED_FIELDS.items() if not doc.get(field)]
	if missing:
		frappe.throw(
			"Campos obligatorios para la asamblea: " + ", ".join(missing),
			title="Campos obligatorios",
		)


def _validate_asm_type_frozen(doc, db_doc):
	db_type = db_doc.get("asm_type") or ""
	if doc.get("asm_type") != db_type and db_type:
		frappe.throw(
			"El tipo de asamblea no puede modificarse una vez guardado.",
			title="Campo protegido",
		)


def _validate_status_transition(doc, db_doc):
	old_status = db_doc.get("asm_status") or "Planificada"
	new_status = doc.get("asm_status") or "Planificada"

	if old_status == new_status:
		return

	allowed = _STATUS_FLOW.get(old_status, set())
	if new_status not in allowed:
		frappe.throw(
			f"Transición de estado no permitida: {old_status} → {new_status}",
			title="Flujo de asamblea",
		)


def _validate_closure_agreements(doc, db_doc):
	"""Require explicit confirmation before closing an assembly."""
	old_status = db_doc.get("asm_status") or "Planificada"
	new_status = doc.get("asm_status") or "Planificada"

	if old_status == new_status or new_status != "Cerrada":
		return  # Only fires on transition TO Cerrada

	if not doc.get("asm_agreements_tasks_created"):
		frappe.throw(
			"No se puede cerrar la asamblea: marca 'Acuerdos convertidos en tareas' para confirmar.",
			title="Confirmación requerida",
		)


def _sync_event_status(doc):
	asm_status = doc.get("asm_status")
	if asm_status == "Cerrada":
		doc.status = "Closed"
	elif asm_status == "Cancelada":
		doc.status = "Cancelled"


def _validate_published_fields(doc, db_doc):
	was_published = db_doc.get("asm_convocation_published")
	is_published_now = doc.get("asm_convocation_published")

	# Prevent revoking a published convocation
	if was_published and not is_published_now:
		frappe.throw(
			"No se puede revocar la publicación de convocatoria.",
			title="Acción irreversible",
		)

	# Only freeze fields if it WAS already published before this save
	if not was_published:
		return

	meta = frappe.get_meta("Event")

	for field in _FROZEN_ON_PUBLISH:
		if not _vals_equal(db_doc.get(field), doc.get(field)):
			label = (meta.get_field(field) and meta.get_field(field).label) or field
			frappe.throw(
				f"El campo '{label}' no puede modificarse: la convocatoria ya fue publicada.",
				title="Campo protegido",
			)

	_validate_frozen_agenda(doc, db_doc)


def _validate_frozen_agenda(doc, db_doc):
	db_rows = {row.name: row for row in (db_doc.get("asm_formal_agenda") or [])}
	current_names = set()

	for row in doc.get("asm_formal_agenda") or []:
		# Prevent adding new rows after publication
		if not row.name or row.name not in db_rows:
			frappe.throw(
				"No se pueden agregar nuevos puntos de agenda: la convocatoria ya fue publicada.",
				title="Agenda protegida",
			)
		current_names.add(row.name)
		db_row = db_rows[row.name]

		for field in _FROZEN_AGENDA_FIELDS:
			if not _vals_equal(getattr(row, field, None), getattr(db_row, field, None)):
				frappe.throw(
					f"Punto '{row.agenda_topic}': el campo '{field.replace('_', ' ').title()}' "
					"no puede modificarse después de publicar la convocatoria.",
					title="Agenda protegida",
				)

	# Prevent deleting rows after publication
	for db_name in db_rows:
		if db_name not in current_names:
			frappe.throw(
				"No se pueden eliminar puntos de agenda: la convocatoria ya fue publicada.",
				title="Agenda protegida",
			)
