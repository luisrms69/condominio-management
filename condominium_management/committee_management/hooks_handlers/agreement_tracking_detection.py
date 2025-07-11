# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_insert(doc, method):
	"""Agreement Tracking after insert hook"""
	if doc.doctype != "Agreement Tracking":
		return

	# Create ToDo for responsible person
	create_todo_for_responsible(doc)

	# Update KPIs
	update_agreement_kpis(doc)


def on_update(doc, method):
	"""Agreement Tracking on update hook"""
	if doc.doctype != "Agreement Tracking":
		return

	# Update ToDo status when agreement status changes
	if doc.has_value_changed("status"):
		update_related_todos(doc)

	# Update KPIs when agreement is completed
	if doc.has_value_changed("status") and doc.status == "Completado":
		update_completion_kpis(doc)


def create_todo_for_responsible(doc):
	"""Create ToDo for responsible person"""
	try:
		if doc.responsible_person:
			user = frappe.db.get_value("Committee Member", doc.responsible_person, "user")
			if user:
				todo_doc = frappe.get_doc(
					{
						"doctype": "ToDo",
						"allocated_to": user,
						"description": f"Acuerdo: {doc.agreement_title}",
						"reference_type": "Agreement Tracking",
						"reference_name": doc.name,
						"date": doc.due_date,
						"priority": doc.priority or "Medium",
					}
				)
				todo_doc.insert()

	except Exception as e:
		frappe.log_error(f"Error creating ToDo for responsible: {e!s}")


def update_related_todos(doc):
	"""Update related ToDos when agreement status changes"""
	try:
		todos = frappe.get_all(
			"ToDo",
			filters={"reference_type": "Agreement Tracking", "reference_name": doc.name},
			fields=["name"],
		)

		for todo in todos:
			todo_doc = frappe.get_doc("ToDo", todo.name)
			if doc.status == "Completado":
				todo_doc.status = "Closed"
			elif doc.status == "Vencido":
				todo_doc.priority = "High"
			todo_doc.save()

	except Exception as e:
		frappe.log_error(f"Error updating related ToDos: {e!s}")


def update_agreement_kpis(doc):
	"""Update KPI records when agreement is created"""
	try:
		if doc.responsible_person:
			update_member_kpis(doc.responsible_person, "agreements_created", 1)

	except Exception as e:
		frappe.log_error(f"Error updating agreement KPIs: {e!s}")


def update_completion_kpis(doc):
	"""Update KPI records when agreement is completed"""
	try:
		if doc.responsible_person:
			update_member_kpis(doc.responsible_person, "agreements_completed", 1)

	except Exception as e:
		frappe.log_error(f"Error updating completion KPIs: {e!s}")


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
