# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_insert(doc, method):
	"""Committee Member after insert hook"""
	if doc.doctype != "Committee Member":
		return

	# Assign user permissions based on role
	if doc.user and doc.role:
		assign_role_permissions(doc)

	# Create initial KPI records
	create_initial_kpis(doc)


def on_update(doc, method):
	"""Committee Member on update hook"""
	if doc.doctype != "Committee Member":
		return

	# Update permissions if role changed
	if doc.has_value_changed("role") and doc.user:
		assign_role_permissions(doc)

	# Update KPI records if status changed
	if doc.has_value_changed("is_active"):
		update_kpi_status(doc)


def assign_role_permissions(doc):
	"""Assign frappe user permissions based on committee role"""
	try:
		role_mapping = {
			"Presidente": "Committee President",
			"Secretario": "Committee Secretary",
			"Tesorero": "Committee Treasurer",
			"Vocal": "Committee Member",
		}

		frappe_role = role_mapping.get(doc.role)
		if frappe_role:
			# Add role to user if not already present
			if not frappe.db.exists("Has Role", {"parent": doc.user, "role": frappe_role}):
				user_doc = frappe.get_doc("User", doc.user)
				user_doc.append("roles", {"role": frappe_role})
				user_doc.save()

	except Exception as e:
		frappe.log_error(f"Error assigning role permissions: {e!s}")


def create_initial_kpis(doc):
	"""Create initial KPI records for new committee member"""
	try:
		if not frappe.db.exists("Committee KPI", {"committee_member": doc.name}):
			kpi_doc = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": doc.name,
					"kpi_period": "Mensual",
					"kpi_year": frappe.utils.nowdate()[:4],
					"kpi_month": frappe.utils.nowdate()[5:7],
					"meetings_attended": 0,
					"meetings_organized": 0,
					"agreements_created": 0,
					"agreements_completed": 0,
					"polls_created": 0,
					"events_organized": 0,
				}
			)
			kpi_doc.insert()

	except Exception as e:
		frappe.log_error(f"Error creating initial KPIs: {e!s}")


def update_kpi_status(doc):
	"""Update KPI status when committee member status changes"""
	try:
		kpi_records = frappe.get_all("Committee KPI", filters={"committee_member": doc.name}, fields=["name"])

		for kpi in kpi_records:
			kpi_doc = frappe.get_doc("Committee KPI", kpi.name)
			kpi_doc.is_active = doc.is_active
			kpi_doc.save()

	except Exception as e:
		frappe.log_error(f"Error updating KPI status: {e!s}")
