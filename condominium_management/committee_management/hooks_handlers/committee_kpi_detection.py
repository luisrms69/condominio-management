# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_update(doc, method):
	"""Committee KPI on update hook"""
	if doc.doctype != "Committee KPI":
		return

	# Recalculate performance metrics when values change
	if doc.has_value_changed(
		[
			"meetings_attended",
			"meetings_organized",
			"agreements_created",
			"agreements_completed",
			"polls_created",
			"events_organized",
		]
	):
		doc.calculate_performance_metrics()

	# Generate alerts for low performance
	if doc.performance_score and doc.performance_score < 50:
		# create_performance_alert(doc)  # TODO: Implement alert function
		pass
