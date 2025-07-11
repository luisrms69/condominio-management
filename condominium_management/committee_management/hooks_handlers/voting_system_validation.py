# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Voting System validation hook"""
	if doc.doctype != "Voting System":
		return

	# Validate voting dates
	if doc.voting_start_date and doc.voting_end_date:
		if getdate(doc.voting_start_date) > getdate(doc.voting_end_date):
			frappe.throw(_("La fecha de inicio de votación debe ser anterior a la fecha de fin"))

	# Validate required percentage
	if doc.required_percentage and (doc.required_percentage < 0 or doc.required_percentage > 100):
		frappe.throw(_("El porcentaje requerido debe estar entre 0 y 100"))

	# Validate voter eligibility
	if doc.vote_records:
		for vote in doc.vote_records:
			if not vote.voter_eligibility:
				frappe.throw(_("Todos los votantes deben tener elegibilidad validada"))

	# Validate voting is not closed if still active
	if doc.status == "Activa" and doc.voting_end_date and getdate(doc.voting_end_date) < getdate():
		frappe.msgprint(_("La votación debería estar cerrada ya que la fecha de fin ha pasado"), alert=True)
