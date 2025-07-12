# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_update(doc, method):
	"""Committee KPI on update hook"""
	if doc.doctype != "Committee KPI":
		return

	# Recalculate performance metrics when values change
	# Check individual fields - has_value_changed() doesn't accept lists
	metrics_fields_changed = any(
		[
			hasattr(doc, field) and doc.has_value_changed(field)
			for field in [
				"meetings_attended",
				"meetings_organized",
				"agreements_created",
				"agreements_completed",
				"polls_created",
				"events_organized",
			]
			if hasattr(doc, field)
		]
	)

	if metrics_fields_changed:
		# TEMP: Method not implemented yet
		if hasattr(doc, "calculate_performance_metrics"):
			doc.calculate_performance_metrics()

	# Generate alerts for low performance - TEMP: Field not implemented yet
	if hasattr(doc, "performance_score") and doc.performance_score and doc.performance_score < 50:
		# create_performance_alert(doc)  # TODO: Implement alert function
		pass
