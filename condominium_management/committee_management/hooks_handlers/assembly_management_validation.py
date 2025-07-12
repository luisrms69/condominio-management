# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Assembly Management validation hook"""
	if doc.doctype != "Assembly Management":
		return

	# Validate convocation dates
	if doc.convocation_date and doc.assembly_date:
		if getdate(doc.convocation_date) >= getdate(doc.assembly_date):
			frappe.throw(_("La fecha de convocatoria debe ser anterior a la fecha de la asamblea"))

	# Validate quorum percentages
	if doc.minimum_quorum_first and doc.minimum_quorum_second:
		if doc.minimum_quorum_first <= doc.minimum_quorum_second:
			frappe.throw(_("El quórum de primera convocatoria debe ser mayor al de segunda convocatoria"))

	# Validate minimum quorum for submission
	if doc.docstatus == 1:  # On submit
		if not doc.quorum_registration:
			frappe.throw(_("Debe registrar al menos un participante en el quórum para enviar la asamblea"))

		# Calculate actual quorum
		total_properties = frappe.db.count("Property Registry", {"property_status_type": "Activo"})
		present_count = len([q for q in doc.quorum_registration if q.attendance_status == "Presente"])

		if total_properties > 0:
			actual_quorum = (present_count / total_properties) * 100
			required_quorum = (
				doc.minimum_quorum_second if doc.call_type == "Segunda" else doc.minimum_quorum_first
			)

			if actual_quorum < required_quorum:
				frappe.throw(
					_("El quórum actual ({:.1f}%) es menor al requerido ({:.1f}%)").format(
						actual_quorum, required_quorum
					)
				)

	# Validate agenda items with voting requirements
	if doc.formal_agenda:
		for item in doc.formal_agenda:
			if item.requires_voting and not item.voting_type:
				frappe.throw(
					_(
						"Los elementos de la agenda que requieren votación deben especificar el tipo de votación"
					)
				)

	# TODO: Validate assembly type consistency - extraordinary_reason field not implemented yet
	# if doc.assembly_type == "Extraordinaria" and not doc.extraordinary_reason:
	# frappe.throw(_("Las asambleas extraordinarias deben especificar la razón"))
	# TEMPORARY: Removed validation until extraordinary_reason field is added to DocType JSON
