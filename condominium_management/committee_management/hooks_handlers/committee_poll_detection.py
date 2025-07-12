# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_update(doc, method):
	"""Committee Poll on update hook"""
	if doc.doctype != "Committee Poll":
		return

	# Recalculate results when poll options change
	if hasattr(doc, "poll_options") and doc.has_value_changed("poll_options"):
		doc.calculate_results()

	# Update KPIs when poll is closed
	if hasattr(doc, "status") and doc.has_value_changed("status") and doc.status == "Cerrada":
		update_poll_kpis(doc)


def update_poll_kpis(doc):
	"""Update KPI records when poll is closed"""
	try:
		if doc.created_by:
			update_member_kpis(doc.created_by, "polls_created", 1)

	except Exception as e:
		frappe.log_error(f"Error updating poll KPIs: {e!s}")


def update_member_kpis(committee_member, field, increment):
	"""Update specific KPI field for committee member"""
	try:
		current_month = frappe.utils.nowdate()[5:7]
		current_year = frappe.utils.nowdate()[:4]

		kpi_record = frappe.db.get_value(
			"Committee KPI",
			{
				"committee_member": committee_member,
				"kpi_period": "Mensual",
				"kpi_year": current_year,
				"kpi_month": current_month,
			},
			"name",
		)

		if kpi_record:
			kpi_doc = frappe.get_doc("Committee KPI", kpi_record)
			current_value = getattr(kpi_doc, field) or 0
			setattr(kpi_doc, field, current_value + increment)
			kpi_doc.save()

	except Exception as e:
		frappe.log_error(f"Error updating member KPIs: {e!s}")
