# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def validate(doc, method):
	"""Meeting Schedule validation hook"""
	if doc.doctype != "Meeting Schedule":
		return

	# Validate schedule year
	current_year = frappe.utils.nowdate()[:4]
	if doc.schedule_year and doc.schedule_year < int(current_year) - 1:
		frappe.throw(_("No se pueden crear programas para años muy anteriores"))

	# Validate scheduled meetings
	if not doc.scheduled_meetings:
		frappe.throw(_("Debe programar al menos una reunión"))

	# Validate meeting dates are within schedule year
	for meeting in doc.scheduled_meetings:
		if meeting.meeting_date:
			meeting_year = getdate(meeting.meeting_date).year
			if meeting_year != doc.schedule_year:
				frappe.throw(
					_("Todas las reuniones deben estar en el año del programa ({})").format(doc.schedule_year)
				)

	# Check for duplicate meeting dates
	dates = [meeting.meeting_date for meeting in doc.scheduled_meetings if meeting.meeting_date]
	if len(dates) != len(set(dates)):
		frappe.throw(_("No puede haber fechas de reunión duplicadas"))

	# Validate auto-creation settings
	if doc.auto_create_meetings and not doc.scheduled_meetings:
		frappe.throw(_("Debe tener reuniones programadas para habilitar la creación automática"))
