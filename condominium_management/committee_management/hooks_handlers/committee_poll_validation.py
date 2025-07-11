# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Committee Poll validation hook"""
	if doc.doctype != "Committee Poll":
		return

	# Validate poll dates
	if doc.poll_start_date and doc.poll_end_date:
		if getdate(doc.poll_start_date) > getdate(doc.poll_end_date):
			frappe.throw(_("La fecha de inicio de la encuesta debe ser anterior a la fecha de fin"))

	# Validate poll has options
	if not doc.poll_options:
		frappe.throw(_("La encuesta debe tener al menos una opción"))

	# Validate poll status
	if doc.poll_status == "Cerrada" and doc.poll_end_date and getdate(doc.poll_end_date) > getdate():
		frappe.throw(_("No se puede cerrar una encuesta antes de su fecha de fin"))

	# Auto-close poll if end date has passed
	if doc.poll_status == "Activa" and doc.poll_end_date and getdate(doc.poll_end_date) < getdate():
		doc.poll_status = "Cerrada"
