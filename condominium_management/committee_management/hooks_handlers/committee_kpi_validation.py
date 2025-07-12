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

	# Validate period consistency - FIXED: use period_year instead of kpi_period
	# NOTE: DocType JSON has 'period_year' field, not 'kpi_period'
	if hasattr(doc, "period_year") and doc.period_year and hasattr(doc, "kpi_month"):
		# Logic needs to be updated based on actual field structure
		pass  # TODO: Implement period validation using correct field names

	# Auto-calculate rates and scores - TEMP: Method not implemented yet
	if hasattr(doc, "calculate_performance_metrics"):
		doc.calculate_performance_metrics()
	# TODO: Implement calculate_performance_metrics method in CommitteeKPI DocType
