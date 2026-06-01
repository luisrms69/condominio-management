# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def after_insert(doc, method):
	"""Committee Member after insert hook — asignar permisos de rol al usuario."""
	if doc.doctype != "Committee Member":
		return

	if doc.user and doc.committee_position:
		assign_role_permissions(doc)


def on_update(doc, method):
	"""Committee Member on update hook."""
	if doc.doctype != "Committee Member":
		return

	if doc.has_value_changed("committee_position") and doc.user:
		assign_role_permissions(doc)


def assign_role_permissions(doc):
	"""Asigna rol de Frappe al usuario según el cargo del comité.

	El cargo expone atribuciones (can_call_assembly, can_sign_documents, etc.)
	pero el rol de Frappe se deriva del nivel jerárquico del Committee Position.
	Por ahora se asigna Committee Member genérico a todos.
	"""
	try:
		frappe_role = "Committee Member"

		if doc.committee_position:
			hierarchy = frappe.db.get_value("Committee Position", doc.committee_position, "hierarchy_level")
			if hierarchy and hierarchy >= 4:
				frappe_role = "Committee President"
			elif hierarchy and hierarchy == 3:
				frappe_role = "Committee Secretary"

		if not frappe.db.exists("Has Role", {"parent": doc.user, "role": frappe_role}):
			user_doc = frappe.get_doc("User", doc.user)
			user_doc.append("roles", {"role": frappe_role})
			user_doc.save()

	except Exception as e:
		frappe.log_error(f"Error assigning role permissions to committee member: {e!s}")
