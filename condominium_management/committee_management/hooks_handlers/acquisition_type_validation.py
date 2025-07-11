# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def validate(doc, method):
	"""Acquisition Type validation hook"""
	if doc.type_name and not doc.type_name.strip():
		frappe.throw("El nombre del tipo de adquisición es obligatorio")
