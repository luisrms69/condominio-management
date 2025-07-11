# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate(doc, method):
	"""Committee Member validation hook"""
	if doc.doctype != "Committee Member":
		return

	# Validate unique roles per company
	if doc.role == "Presidente" and doc.is_active:
		existing_president = frappe.db.exists(
			"Committee Member",
			{"role": "Presidente", "is_active": 1, "company": doc.company, "name": ["!=", doc.name]},
		)
		if existing_president:
			frappe.throw(_("Ya existe un Presidente activo para esta empresa"))

	# Validate property registry is active
	if hasattr(doc, "property_registry") and doc.property_registry:
		property_status = frappe.db.get_value("Property Registry", doc.property_registry, "status")
		if property_status != "Activo":
			frappe.throw(_("El registro de propiedad debe estar activo para asignar un miembro del comité"))

	# Validate date consistency
	if doc.start_date and doc.end_date:
		if doc.start_date >= doc.end_date:
			frappe.throw(_("La fecha de inicio debe ser anterior a la fecha de fin"))
