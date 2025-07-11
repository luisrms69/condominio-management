# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Agreement Tracking validation hook"""
	if doc.doctype != "Agreement Tracking":
		return

	# Validate dates
	if doc.agreement_date and doc.due_date:
		if getdate(doc.agreement_date) > getdate(doc.due_date):
			frappe.throw(_("La fecha del acuerdo debe ser anterior a la fecha de vencimiento"))

	# Validate completion percentage
	if doc.completion_percentage and (doc.completion_percentage < 0 or doc.completion_percentage > 100):
		frappe.throw(_("El porcentaje de completitud debe estar entre 0 y 100"))

	# Auto-update status based on completion and dates
	if doc.completion_percentage == 100:
		doc.status = "Completado"
	elif doc.due_date and getdate(doc.due_date) < getdate() and doc.status != "Completado":
		doc.status = "Vencido"

	# Validate responsible party exists
	if doc.responsible_party:
		if not frappe.db.exists("Committee Member", doc.responsible_party):
			frappe.throw(_("La persona responsable debe ser un miembro del comité válido"))
