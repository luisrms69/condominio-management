# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def validate(doc, method):
	"""Property Usage Type validation hook"""
	if doc.type_name and not doc.type_name.strip():
		frappe.throw("El nombre del tipo de uso es obligatorio")

	if doc.usage_category and not doc.usage_category.strip():
		frappe.throw("La categoría de uso es obligatoria")
