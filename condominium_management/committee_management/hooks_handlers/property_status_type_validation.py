# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def validate(doc, method):
	"""Property Status Type validation hook"""
	if doc.status_name and not doc.status_name.strip():
		frappe.throw("El nombre del estado de propiedad es obligatorio")
