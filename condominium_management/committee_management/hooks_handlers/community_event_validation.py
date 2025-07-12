# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Community Event validation hook"""
	if doc.doctype != "Community Event":
		return

	# Validate event dates
	if doc.event_start_date and doc.event_end_date:
		if getdate(doc.event_start_date) > getdate(doc.event_end_date):
			frappe.throw(_("La fecha de inicio del evento debe ser anterior a la fecha de fin"))

	# Validate budget
	if doc.approved_budget and doc.approved_budget < 0:
		frappe.throw(_("El presupuesto aprobado no puede ser negativo"))

	# Validate expenses don't exceed budget
	if doc.event_expenses and doc.approved_budget:
		total_expenses = sum(expense.amount for expense in doc.event_expenses)
		if total_expenses > doc.approved_budget:
			frappe.throw(
				_("Los gastos del evento ({}) exceden el presupuesto aprobado ({})").format(
					total_expenses, doc.approved_budget
				)
			)

	# Validate registration limit
	if doc.registration_limit and doc.registration_limit < 0:
		frappe.throw(_("El límite de registro no puede ser negativo"))

	# Validate event capacity
	if doc.event_location and doc.registration_limit:
		# Check if physical space has capacity info
		space_capacity = frappe.db.get_value("Physical Space", doc.event_location, "capacity")
		if space_capacity and doc.registration_limit > space_capacity:
			frappe.msgprint(_("El límite de registro excede la capacidad del espacio físico"), alert=True)
