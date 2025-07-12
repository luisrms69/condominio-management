# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Committee Meeting validation hook"""
	if doc.doctype != "Committee Meeting":
		return

	# Validate meeting dates - FIXED: meeting_date is Datetime, no separate meeting_time field
	if doc.meeting_date:
		# Check if meeting date is not in the past (except for rescheduled meetings)
		if (
			hasattr(doc, "is_rescheduled")
			and not doc.is_rescheduled
			and getdate(doc.meeting_date) < getdate()
		):
			frappe.msgprint(_("La fecha de la reunión es en el pasado"), alert=True)

	# Validate physical space requirements
	if doc.meeting_format in ["Presencial", "Híbrida"] and not doc.physical_space:
		frappe.throw(_("Debe especificar un espacio físico para reuniones presenciales o híbridas"))

	# Validate virtual meeting requirements
	if doc.meeting_format in ["Virtual", "Híbrida"] and not doc.virtual_meeting_link:
		frappe.throw(_("Debe especificar un enlace de reunión virtual para reuniones virtuales o híbridas"))

	# Validate agenda items
	if doc.agenda_items:
		for item in doc.agenda_items:
			if not item.topic_title:
				frappe.throw(_("Todos los elementos de la agenda deben tener un título"))

	# Validate attendees
	if doc.attendees:
		committee_members = [att.committee_member for att in doc.attendees if att.committee_member]
		if len(committee_members) != len(set(committee_members)):
			frappe.throw(_("No puede haber miembros del comité duplicados en la lista de asistentes"))

	# Validate meeting completion - TEMP: meeting_status field not implemented yet
	if hasattr(doc, "meeting_status") and doc.meeting_status == "Completada":
		if hasattr(doc, "meeting_summary") and not doc.meeting_summary:
			frappe.throw(_("Debe proporcionar un resumen de la reunión para marcarla como completada"))

		# Check if all agenda items have decisions
		if hasattr(doc, "agenda_items") and doc.agenda_items:
			incomplete_items = [
				item for item in doc.agenda_items if hasattr(item, "decision_made") and not item.decision_made
			]
			if incomplete_items:
				frappe.msgprint(_("Hay elementos de la agenda sin decisión registrada"), alert=True)
