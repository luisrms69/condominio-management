# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate(doc, method):
	"""Committee Member validation hook — complementa la lógica del controller."""
	if doc.doctype != "Committee Member":
		return

	# Validar que property_registry pertenezca al condominio declarado
	if doc.property_registry and doc.company:
		pr_company = frappe.db.get_value("Property Registry", doc.property_registry, "company")
		if pr_company and pr_company != doc.company:
			frappe.throw(
				_("La propiedad '{0}' no pertenece al condominio '{1}'.").format(
					doc.property_registry, doc.company
				)
			)

	# Validar que committee_position pertenezca al condominio declarado
	if doc.committee_position and doc.company:
		pos_company = frappe.db.get_value("Committee Position", doc.committee_position, "company")
		if pos_company and pos_company != doc.company:
			frappe.throw(
				_("El cargo '{0}' no pertenece al condominio '{1}'.").format(
					doc.committee_position, doc.company
				)
			)
