# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_submit(doc, method):
	"""Meeting Schedule on submit hook"""
	if doc.doctype != "Meeting Schedule":
		return

	# Auto-create meetings if enabled
	if doc.auto_create_meetings:
		doc.create_upcoming_meetings()


def on_update(doc, method):
	"""Meeting Schedule on update hook"""
	if doc.doctype != "Meeting Schedule":
		return

	# Recalculate meeting counts when scheduled meetings change
	if doc.has_value_changed("scheduled_meetings"):
		doc.calculate_meeting_counts()

	# Update sync date when meetings are created
	if doc.has_value_changed("meetings_created_count"):
		doc.last_sync_date = frappe.utils.now_datetime()
