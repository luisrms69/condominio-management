# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Voting System validation hook"""
	if doc.doctype != "Voting System":
		return

	# Validate voting dates - check field names with hasattr()
	if (
		hasattr(doc, "voting_start_date")
		and hasattr(doc, "voting_end_date")
		and doc.voting_start_date
		and doc.voting_end_date
	):
		if getdate(doc.voting_start_date) > getdate(doc.voting_end_date):
			frappe.throw(_("La fecha de inicio de votación debe ser anterior a la fecha de fin"))
	elif (
		hasattr(doc, "voting_start_time")
		and hasattr(doc, "voting_end_time")
		and doc.voting_start_time
		and doc.voting_end_time
	):
		# Alternative field names - validate time fields
		if doc.voting_start_time > doc.voting_end_time:
			frappe.throw(_("La hora de inicio de votación debe ser anterior a la hora de fin"))

	# Validate required percentage
	if doc.required_percentage and (doc.required_percentage < 0 or doc.required_percentage > 100):
		frappe.throw(_("El porcentaje requerido debe estar entre 0 y 100"))

	# Validate voter eligibility - check field names with hasattr()
	vote_records_field = None
	if hasattr(doc, "vote_records") and doc.vote_records:
		vote_records_field = doc.vote_records
	elif hasattr(doc, "votes") and doc.votes:
		vote_records_field = doc.votes

	if vote_records_field:
		for vote in vote_records_field:
			if hasattr(vote, "voter_eligibility") and not vote.voter_eligibility:
				frappe.throw(_("Todos los votantes deben tener elegibilidad validada"))

	# Validate voting is not closed if still active - check field names with hasattr()
	end_date_field = None
	if hasattr(doc, "voting_end_date") and doc.voting_end_date:
		end_date_field = doc.voting_end_date
	elif hasattr(doc, "voting_end_time") and doc.voting_end_time:
		end_date_field = doc.voting_end_time

	if doc.status == "Activa" and end_date_field and getdate(end_date_field) < getdate():
		frappe.msgprint(_("La votación debería estar cerrada ya que la fecha de fin ha pasado"), alert=True)
