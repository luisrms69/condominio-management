# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


def check_pending_meetings():
	"""Daily task to check for pending meetings that need to be created"""
	try:
		# Get active meeting schedules with auto-creation enabled
		schedules = frappe.get_all(
			"Meeting Schedule", filters={"docstatus": 1, "auto_create_meetings": 1}, fields=["name"]
		)

		for schedule in schedules:
			schedule_doc = frappe.get_doc("Meeting Schedule", schedule.name)
			schedule_doc.create_upcoming_meetings()

		frappe.log_error(f"Processed {len(schedules)} meeting schedules", "Check Pending Meetings")

	except Exception as e:
		frappe.log_error(f"Error in check_pending_meetings: {e!s}")


def check_overdue_agreements():
	"""Daily task to check for overdue agreements"""
	try:
		today = getdate(nowdate())

		# Find agreements that are overdue
		overdue_agreements = frappe.get_all(
			"Agreement Tracking",
			filters={"status": ["not in", ["Completado", "Cancelado"]], "due_date": ["<", today]},
			fields=["name", "agreement_title", "responsible_person", "due_date"],
		)

		for agreement in overdue_agreements:
			# Update status to overdue
			agreement_doc = frappe.get_doc("Agreement Tracking", agreement.name)
			if agreement_doc.status != "Vencido":
				agreement_doc.status = "Vencido"
				agreement_doc.save()

				# Create escalation notification
				create_overdue_notification(agreement_doc)

		frappe.log_error(
			f"Processed {len(overdue_agreements)} overdue agreements", "Check Overdue Agreements"
		)

	except Exception as e:
		frappe.log_error(f"Error in check_overdue_agreements: {e!s}")


def calculate_daily_kpis():
	"""Daily task to calculate and update KPIs"""
	try:
		# Get all active committee members
		committee_members = frappe.get_all("Committee Member", filters={"is_active": 1}, fields=["name"])

		current_month = nowdate()[5:7]
		current_year = nowdate()[:4]

		for member in committee_members:
			# Find or create current month KPI record
			kpi_record = frappe.db.get_value(
				"Committee KPI",
				{
					"committee_member": member.name,
					"kpi_period": "Mensual",
					"kpi_year": current_year,
					"kpi_month": current_month,
				},
				"name",
			)

			if not kpi_record:
				# Create new KPI record for current month
				kpi_doc = frappe.get_doc(
					{
						"doctype": "Committee KPI",
						"committee_member": member.name,
						"kpi_period": "Mensual",
						"kpi_year": current_year,
						"kpi_month": current_month,
					}
				)
				kpi_doc.insert()
			else:
				# Update existing KPI record
				kpi_doc = frappe.get_doc("Committee KPI", kpi_record)
				kpi_doc.calculate_performance_metrics()
				kpi_doc.save()

		frappe.log_error(
			f"Updated KPIs for {len(committee_members)} committee members", "Calculate Daily KPIs"
		)

	except Exception as e:
		frappe.log_error(f"Error in calculate_daily_kpis: {e!s}")


def send_meeting_reminders():
	"""Weekly task to send meeting reminders"""
	try:
		# Get upcoming meetings in the next 7 days
		next_week = add_days(nowdate(), 7)

		upcoming_meetings = frappe.get_all(
			"Committee Meeting",
			filters={
				"meeting_date": ["between", [nowdate(), next_week]],
				"meeting_status": ["in", ["Programada", "En Curso"]],
			},
			fields=["name", "meeting_title", "meeting_date", "meeting_time"],
		)

		for meeting in upcoming_meetings:
			send_meeting_reminder_notifications(meeting)

		frappe.log_error(
			f"Sent reminders for {len(upcoming_meetings)} upcoming meetings", "Send Meeting Reminders"
		)

	except Exception as e:
		frappe.log_error(f"Error in send_meeting_reminders: {e!s}")


def generate_weekly_reports():
	"""Weekly task to generate committee reports"""
	try:
		# Generate weekly summary reports for active committee members
		committee_members = frappe.get_all(
			"Committee Member",
			filters={"is_active": 1, "role": ["in", ["Presidente", "Secretario"]]},
			fields=["name", "member_name", "role", "user"],
		)

		for member in committee_members:
			generate_weekly_summary(member)

		frappe.log_error(
			f"Generated weekly reports for {len(committee_members)} committee leaders",
			"Generate Weekly Reports",
		)

	except Exception as e:
		frappe.log_error(f"Error in generate_weekly_reports: {e!s}")


def create_overdue_notification(agreement_doc):
	"""Create notification for overdue agreement"""
	try:
		if agreement_doc.responsible_person:
			user = frappe.db.get_value("Committee Member", agreement_doc.responsible_person, "user")
			if user:
				# Create high priority ToDo
				todo_doc = frappe.get_doc(
					{
						"doctype": "ToDo",
						"allocated_to": user,
						"description": f"VENCIDO: {agreement_doc.agreement_title} (vencido el {agreement_doc.due_date})",
						"reference_type": "Agreement Tracking",
						"reference_name": agreement_doc.name,
						"date": nowdate(),
						"priority": "High",
					}
				)
				todo_doc.insert()

	except Exception as e:
		frappe.log_error(f"Error creating overdue notification: {e!s}")


def send_meeting_reminder_notifications(meeting):
	"""Send reminder notifications for meeting"""
	try:
		meeting_doc = frappe.get_doc("Committee Meeting", meeting.name)

		for attendee in meeting_doc.attendees:
			if attendee.committee_member:
				user = frappe.db.get_value("Committee Member", attendee.committee_member, "user")
				if user:
					# Create reminder ToDo
					todo_doc = frappe.get_doc(
						{
							"doctype": "ToDo",
							"allocated_to": user,
							"description": f"Recordatorio: {meeting.meeting_title} el {meeting.meeting_date} a las {meeting.meeting_time}",
							"reference_type": "Committee Meeting",
							"reference_name": meeting.name,
							"date": meeting.meeting_date,
							"priority": "Medium",
						}
					)
					todo_doc.insert()

	except Exception as e:
		frappe.log_error(f"Error sending meeting reminder: {e!s}")


def generate_weekly_summary(member):
	"""Generate weekly summary for committee member"""
	try:
		# This is a placeholder for weekly summary generation
		# In a real implementation, this would create a comprehensive report
		# covering meetings, agreements, KPIs, etc.

		summary = {
			"member": member.name,
			"period": f"Semana del {add_days(nowdate(), -7)} al {nowdate()}",
			"meetings_attended": 0,  # Would be calculated from actual data
			"agreements_progress": 0,  # Would be calculated from actual data
			"pending_tasks": 0,  # Would be calculated from actual data
		}

		# For now, just log the summary
		frappe.log_error(f"Weekly summary for {member.member_name}: {summary}", "Weekly Summary")

	except Exception as e:
		frappe.log_error(f"Error generating weekly summary: {e!s}")
