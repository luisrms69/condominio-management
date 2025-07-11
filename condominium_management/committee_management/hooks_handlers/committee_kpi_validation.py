# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate(doc, method):
	"""Committee KPI validation hook"""
	if doc.doctype != "Committee KPI":
		return

	# Validate KPI values are not negative
	numeric_fields = [
		"meetings_attended",
		"meetings_organized",
		"agreements_created",
		"agreements_completed",
		"polls_created",
		"events_organized",
		"assemblies_attended",
		"assemblies_organized",
	]

	for field in numeric_fields:
		if hasattr(doc, field) and getattr(doc, field) and getattr(doc, field) < 0:
			frappe.throw(_("El valor de {} no puede ser negativo").format(field))

	# Validate percentage fields
	percentage_fields = ["attendance_rate", "completion_rate", "performance_score"]
	for field in percentage_fields:
		if hasattr(doc, field) and getattr(doc, field):
			value = getattr(doc, field)
			if value < 0 or value > 100:
				frappe.throw(_("El valor de {} debe estar entre 0 y 100").format(field))

	# Validate period consistency
	if doc.kpi_period == "Mensual" and not doc.kpi_month:
		frappe.throw(_("Los KPIs mensuales deben especificar el mes"))

	# Auto-calculate rates and scores
	doc.calculate_performance_metrics()
