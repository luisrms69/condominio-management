# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Committee Poll validation hook"""
	if doc.doctype != "Committee Poll":
		return

	# Validate poll dates - check field names with hasattr()
	if hasattr(doc, "start_date") and hasattr(doc, "end_date") and doc.start_date and doc.end_date:
		if getdate(doc.start_date) > getdate(doc.end_date):
			frappe.throw(_("La fecha de inicio de la encuesta debe ser anterior a la fecha de fin"))

	# Validate poll has options (handled by DocType validation)
	# if not doc.poll_options:
	#     frappe.throw(_("La encuesta debe tener al menos una opción"))

	# Validate poll status - check field names with hasattr()
	if (
		hasattr(doc, "status")
		and doc.status == "Cerrada"
		and hasattr(doc, "end_date")
		and doc.end_date
		and getdate(doc.end_date) > getdate()
	):
		frappe.throw(_("No se puede cerrar una encuesta antes de su fecha de fin"))

	# Auto-close poll if end date has passed - check field names with hasattr()
	if (
		hasattr(doc, "status")
		and doc.status == "Abierta"
		and hasattr(doc, "end_date")
		and doc.end_date
		and getdate(doc.end_date) < getdate()
	):
		doc.status = "Cerrada"
