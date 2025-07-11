# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_insert(doc, method):
	"""Community Event after insert hook"""
	if doc.doctype != "Community Event":
		return

	# Create initial event activities if none exist
	if not doc.event_activities:
		create_default_activities(doc)


def on_update(doc, method):
	"""Community Event on update hook"""
	if doc.doctype != "Community Event":
		return

	# Update budget calculations when expenses change
	if doc.has_value_changed("event_expenses"):
		doc.calculate_budget_utilization()

	# Update KPIs when event is completed
	if doc.has_value_changed("event_status") and doc.event_status == "Completado":
		update_event_kpis(doc)


def create_default_activities(doc):
	"""Create default event activities"""
	try:
		default_activities = [
			{"activity_name": "Preparación del evento", "activity_type": "Preparación"},
			{"activity_name": "Desarrollo del evento", "activity_type": "Ejecución"},
			{"activity_name": "Limpieza y cierre", "activity_type": "Cierre"},
		]

		for activity in default_activities:
			doc.append(
				"event_activities",
				{
					"activity_name": activity["activity_name"],
					"activity_type": activity["activity_type"],
					"is_mandatory": 1,
				},
			)

		doc.save()

	except Exception as e:
		frappe.log_error(f"Error creating default activities: {e!s}")


def update_event_kpis(doc):
	"""Update KPI records when event is completed"""
	try:
		# Update KPIs for all event organizers
		if doc.event_organizers:
			for organizer in doc.event_organizers:
				if organizer.committee_member:
					update_member_kpis(organizer.committee_member, "events_organized", 1)

	except Exception as e:
		frappe.log_error(f"Error updating event KPIs: {e!s}")


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
