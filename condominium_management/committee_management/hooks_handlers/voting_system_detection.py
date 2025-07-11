# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_insert(doc, method):
	"""Voting System after insert hook"""
	if doc.doctype != "Voting System":
		return

	# Load eligible voters
	load_eligible_voters(doc)


def on_update(doc, method):
	"""Voting System on update hook"""
	if doc.doctype != "Voting System":
		return

	# Recalculate results when votes change
	if doc.has_value_changed("vote_records"):
		doc.calculate_voting_results()

	# Close voting if end date has passed
	if (
		doc.status == "Activa"
		and doc.voting_end_date
		and frappe.utils.getdate(doc.voting_end_date) < frappe.utils.getdate()
	):
		doc.status = "Cerrada"
		doc.save()


def load_eligible_voters(doc):
	"""Load eligible voters based on assembly or committee context"""
	try:
		eligible_voters = []

		if doc.assembly_management:
			# Load from assembly quorum
			quorum_records = frappe.get_all(
				"Quorum Record",
				filters={"parent": doc.assembly_management},
				fields=["property_registry", "owner_name"],
			)
			eligible_voters = [
				{"voter": q.property_registry, "voter_name": q.owner_name} for q in quorum_records
			]
		else:
			# Load active committee members
			committee_members = frappe.get_all(
				"Committee Member", filters={"is_active": 1}, fields=["name", "member_name"]
			)
			eligible_voters = [{"voter": cm.name, "voter_name": cm.member_name} for cm in committee_members]

		for voter in eligible_voters:
			doc.append(
				"vote_records",
				{
					"voter": voter["voter"],
					"voter_name": voter["voter_name"],
					"voter_eligibility": "Elegible",
					"vote_value": "",
					"vote_timestamp": None,
				},
			)

		doc.save()

	except Exception as e:
		frappe.log_error(f"Error loading eligible voters: {e!s}")
