# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, nowdate


@frappe.whitelist()
def get_committee_dashboard_data():
	"""Get comprehensive data for the committee executive dashboard"""

	dashboard_data = {
		"overview_metrics": get_overview_metrics(),
		"recent_meetings": get_recent_meetings(),
		"pending_agreements": get_pending_agreements(),
		"active_polls": get_active_polls(),
		"upcoming_events": get_upcoming_events(),
		"committee_performance": get_committee_performance(),
		"assembly_insights": get_assembly_insights(),
		"quick_actions": get_quick_actions(),
		"alerts_notifications": get_alerts_and_notifications(),
	}

	return dashboard_data


def get_overview_metrics():
	"""Get overview metrics for the dashboard"""
	try:
		return {
			"active_members": frappe.db.count("Committee Member", {"is_active": 1}),
			"scheduled_meetings": frappe.db.count("Committee Meeting", {"meeting_status": "Programada"}),
			"overdue_agreements": frappe.db.count("Agreement Tracking", {"status": "Vencido"}),
			"active_polls": frappe.db.count("Committee Poll", {"poll_status": "Activa"}),
			"planned_events": frappe.db.count("Community Event", {"event_status": "Planificado"}),
			"pending_agreements": frappe.db.count(
				"Agreement Tracking", {"status": ["in", ["Pendiente", "En Progreso"]]}
			),
			"completed_agreements_this_month": get_completed_agreements_this_month(),
			"average_meeting_attendance": get_average_meeting_attendance(),
		}
	except Exception as e:
		frappe.log_error(f"Error getting overview metrics: {e!s}")
		return {}


def get_completed_agreements_this_month():
	"""Get count of agreements completed this month"""
	try:
		from frappe.utils import get_first_day, get_last_day

		first_day = get_first_day(nowdate())
		last_day = get_last_day(nowdate())

		return frappe.db.count(
			"Agreement Tracking",
			{"status": "Completado", "completion_date": ["between", [first_day, last_day]]},
		)
	except Exception:
		return 0


def get_average_meeting_attendance():
	"""Calculate average meeting attendance rate"""
	try:
		meetings = frappe.get_all(
			"Committee Meeting", filters={"meeting_status": "Completada"}, fields=["name"]
		)

		if not meetings:
			return 0

		total_attendance = 0
		meeting_count = 0

		for meeting in meetings:
			meeting_doc = frappe.get_doc("Committee Meeting", meeting.name)
			if hasattr(meeting_doc, "get_attendance_summary"):
				summary = meeting_doc.get_attendance_summary()
				total_attendance += summary.get("attendance_rate", 0)
				meeting_count += 1

		return round(total_attendance / meeting_count, 1) if meeting_count > 0 else 0
	except Exception:
		return 0


def get_recent_meetings():
	"""Get recent and upcoming meetings"""
	try:
		# Get recent completed meetings
		recent_completed = frappe.get_all(
			"Committee Meeting",
			filters={"meeting_status": "Completada", "meeting_date": [">=", add_days(nowdate(), -30)]},
			fields=["name", "meeting_title", "meeting_date", "completion_rate"],
			order_by="meeting_date desc",
			limit=5,
		)

		# Get upcoming meetings
		upcoming = frappe.get_all(
			"Committee Meeting",
			filters={
				"meeting_status": ["in", ["Programada", "En Progreso"]],
				"meeting_date": [">=", nowdate()],
			},
			fields=["name", "meeting_title", "meeting_date", "meeting_format", "physical_space"],
			order_by="meeting_date asc",
			limit=5,
		)

		return {"recent_completed": recent_completed, "upcoming": upcoming}
	except Exception as e:
		frappe.log_error(f"Error getting recent meetings: {e!s}")
		return {"recent_completed": [], "upcoming": []}


def get_pending_agreements():
	"""Get pending and overdue agreements"""
	try:
		pending = frappe.get_all(
			"Agreement Tracking",
			filters={"status": ["in", ["Pendiente", "En Progreso"]]},
			fields=[
				"name",
				"agreement_title",
				"due_date",
				"responsible_person",
				"priority",
				"completion_percentage",
			],
			order_by="due_date asc",
			limit=10,
		)

		# Add days remaining calculation
		for agreement in pending:
			if agreement.due_date:
				days_remaining = (getdate(agreement.due_date) - getdate(nowdate())).days
				agreement["days_remaining"] = days_remaining
				agreement["is_overdue"] = days_remaining < 0

		return pending
	except Exception as e:
		frappe.log_error(f"Error getting pending agreements: {e!s}")
		return []


def get_active_polls():
	"""Get currently active polls"""
	try:
		return frappe.get_all(
			"Committee Poll",
			filters={"poll_status": "Activa"},
			fields=["name", "poll_title", "poll_end_date", "total_responses", "total_eligible_voters"],
			order_by="poll_end_date asc",
			limit=5,
		)
	except Exception as e:
		frappe.log_error(f"Error getting active polls: {e!s}")
		return []


def get_upcoming_events():
	"""Get upcoming community events"""
	try:
		return frappe.get_all(
			"Community Event",
			filters={
				"event_start_date": [">=", nowdate()],
				"event_status": ["in", ["Planificado", "En Organización", "Confirmado"]],
			},
			fields=[
				"name",
				"event_name",
				"event_start_date",
				"event_type",
				"registered_attendees_count",
				"capacity_maximum",
			],
			order_by="event_start_date asc",
			limit=5,
		)
	except Exception as e:
		frappe.log_error(f"Error getting upcoming events: {e!s}")
		return []


def get_committee_performance():
	"""Get committee performance metrics"""
	try:
		current_month = nowdate()[5:7]
		current_year = nowdate()[:4]

		# Get current month KPIs for all active members
		kpis = frappe.get_all(
			"Committee KPI",
			filters={"kpi_year": current_year, "kpi_month": current_month, "kpi_period": "Mensual"},
			fields=["committee_member", "performance_score", "attendance_rate", "completion_rate"],
			order_by="performance_score desc",
		)

		# Calculate averages
		if kpis:
			avg_performance = sum(kpi.performance_score or 0 for kpi in kpis) / len(kpis)
			avg_attendance = sum(kpi.attendance_rate or 0 for kpi in kpis) / len(kpis)
			avg_completion = sum(kpi.completion_rate or 0 for kpi in kpis) / len(kpis)
		else:
			avg_performance = avg_attendance = avg_completion = 0

		return {
			"average_performance_score": round(avg_performance, 1),
			"average_attendance_rate": round(avg_attendance, 1),
			"average_completion_rate": round(avg_completion, 1),
			"top_performers": kpis[:3],
			"total_members_evaluated": len(kpis),
		}
	except Exception as e:
		frappe.log_error(f"Error getting committee performance: {e!s}")
		return {}


def get_assembly_insights():
	"""Get assembly management insights"""
	try:
		# Get recent assemblies
		recent_assemblies = frappe.get_all(
			"Assembly Management",
			filters={"assembly_date": [">=", add_days(nowdate(), -90)]},
			fields=["name", "assembly_title", "assembly_date", "actual_quorum_percentage", "assembly_status"],
			order_by="assembly_date desc",
			limit=3,
		)

		# Calculate average quorum
		if recent_assemblies:
			avg_quorum = sum(assembly.actual_quorum_percentage or 0 for assembly in recent_assemblies) / len(
				recent_assemblies
			)
		else:
			avg_quorum = 0

		# Get upcoming assemblies
		upcoming_assemblies = frappe.get_all(
			"Assembly Management",
			filters={
				"assembly_date": [">=", nowdate()],
				"assembly_status": ["in", ["Planificada", "Convocada"]],
			},
			fields=["name", "assembly_title", "assembly_date", "assembly_type"],
			order_by="assembly_date asc",
			limit=2,
		)

		return {
			"recent_assemblies": recent_assemblies,
			"upcoming_assemblies": upcoming_assemblies,
			"average_quorum_percentage": round(avg_quorum, 1),
			"total_assemblies_ytd": frappe.db.count(
				"Assembly Management", {"assembly_date": [">=", f"{nowdate()[:4]}-01-01"]}
			),
		}
	except Exception as e:
		frappe.log_error(f"Error getting assembly insights: {e!s}")
		return {}


def get_quick_actions():
	"""Get available quick actions for the user"""
	try:
		user_roles = frappe.get_roles()
		actions = []

		# Actions for Committee Presidents
		if "Committee President" in user_roles:
			actions.extend(
				[
					{"label": "Convocar Asamblea", "action": "new_assembly", "icon": "users"},
					{"label": "Crear Programa de Reuniones", "action": "new_schedule", "icon": "calendar"},
					{"label": "Revisar KPIs", "action": "view_kpis", "icon": "trending-up"},
				]
			)

		# Actions for Committee Secretaries
		if "Committee Secretary" in user_roles:
			actions.extend(
				[
					{"label": "Programar Reunión", "action": "new_meeting", "icon": "calendar-plus"},
					{"label": "Crear Encuesta", "action": "new_poll", "icon": "help-circle"},
					{
						"label": "Seguimiento de Acuerdos",
						"action": "track_agreements",
						"icon": "check-square",
					},
				]
			)

		# Actions for Committee Treasurers
		if "Committee Treasurer" in user_roles:
			actions.extend(
				[
					{"label": "Planificar Evento", "action": "new_event", "icon": "calendar-check"},
					{"label": "Revisar Presupuestos", "action": "review_budgets", "icon": "dollar-sign"},
				]
			)

		# Common actions for all committee members
		if any(
			role in user_roles
			for role in [
				"Committee President",
				"Committee Secretary",
				"Committee Treasurer",
				"Committee Member",
			]
		):
			actions.extend(
				[
					{"label": "Ver Reuniones Pendientes", "action": "pending_meetings", "icon": "clock"},
					{"label": "Actualizar Progreso", "action": "update_progress", "icon": "edit"},
				]
			)

		return actions[:6]  # Limit to 6 quick actions
	except Exception as e:
		frappe.log_error(f"Error getting quick actions: {e!s}")
		return []


def get_alerts_and_notifications():
	"""Get important alerts and notifications"""
	try:
		alerts = []

		# Check for overdue agreements
		overdue_count = frappe.db.count("Agreement Tracking", {"status": "Vencido"})
		if overdue_count > 0:
			alerts.append(
				{
					"type": "danger",
					"title": "Acuerdos Vencidos",
					"message": f"Hay {overdue_count} acuerdo(s) vencido(s) que requieren atención",
					"action": "view_overdue_agreements",
				}
			)

		# Check for meetings without quorum
		upcoming_meetings = frappe.get_all(
			"Committee Meeting",
			filters={
				"meeting_date": ["between", [nowdate(), add_days(nowdate(), 7)]],
				"meeting_status": "Programada",
			},
		)
		if upcoming_meetings:
			alerts.append(
				{
					"type": "warning",
					"title": "Reuniones Próximas",
					"message": f"Hay {len(upcoming_meetings)} reunión(es) programada(s) para esta semana",
					"action": "view_upcoming_meetings",
				}
			)

		# Check for active polls ending soon
		ending_polls = frappe.get_all(
			"Committee Poll",
			filters={
				"poll_status": "Activa",
				"poll_end_date": ["between", [nowdate(), add_days(nowdate(), 3)]],
			},
		)
		if ending_polls:
			alerts.append(
				{
					"type": "info",
					"title": "Encuestas por Cerrar",
					"message": f"Hay {len(ending_polls)} encuesta(s) que terminan en los próximos 3 días",
					"action": "view_ending_polls",
				}
			)

		# Check for events needing attention
		events_needing_attention = frappe.get_all(
			"Community Event",
			filters={
				"event_start_date": ["between", [nowdate(), add_days(nowdate(), 14)]],
				"event_status": ["in", ["Planificado", "En Organización"]],
			},
		)
		if events_needing_attention:
			alerts.append(
				{
					"type": "success",
					"title": "Eventos Próximos",
					"message": f"Hay {len(events_needing_attention)} evento(s) en las próximas 2 semanas",
					"action": "view_upcoming_events",
				}
			)

		return alerts[:5]  # Limit to 5 alerts
	except Exception as e:
		frappe.log_error(f"Error getting alerts and notifications: {e!s}")
		return []


@frappe.whitelist()
def get_committee_member_profile():
	"""Get current user's committee member profile"""
	try:
		current_user = frappe.session.user
		member = frappe.db.get_value(
			"Committee Member",
			{"user": current_user, "is_active": 1},
			["name", "member_name", "role", "start_date", "can_approve_expenses", "expense_approval_limit"],
			as_dict=True,
		)

		if member:
			# Get recent activity
			recent_activity = get_member_recent_activity(member.name)
			member["recent_activity"] = recent_activity

			# Get current month KPIs
			current_month = nowdate()[5:7]
			current_year = nowdate()[:4]

			kpis = frappe.db.get_value(
				"Committee KPI",
				{"committee_member": member.name, "kpi_year": current_year, "kpi_month": current_month},
				["performance_score", "attendance_rate", "completion_rate"],
				as_dict=True,
			)

			member["current_kpis"] = kpis or {}

		return member
	except Exception as e:
		frappe.log_error(f"Error getting committee member profile: {e!s}")
		return None


def get_member_recent_activity(member_name):
	"""Get recent activity for a committee member"""
	try:
		activities = []

		# Recent meetings attended
		recent_meetings = frappe.get_all(
			"Meeting Attendee",
			filters={"committee_member": member_name, "parenttype": "Committee Meeting"},
			fields=["parent", "attendance_status"],
			limit=5,
		)

		for meeting in recent_meetings:
			meeting_info = frappe.db.get_value(
				"Committee Meeting", meeting.parent, ["meeting_title", "meeting_date"], as_dict=True
			)
			if meeting_info:
				activities.append(
					{
						"type": "meeting",
						"title": f"Reunión: {meeting_info.meeting_title}",
						"date": meeting_info.meeting_date,
						"status": meeting.attendance_status,
					}
				)

		# Recent agreements
		recent_agreements = frappe.get_all(
			"Agreement Tracking",
			filters={"responsible_person": member_name},
			fields=["name", "agreement_title", "status", "due_date"],
			order_by="creation desc",
			limit=3,
		)

		for agreement in recent_agreements:
			activities.append(
				{
					"type": "agreement",
					"title": f"Acuerdo: {agreement.agreement_title}",
					"date": agreement.due_date,
					"status": agreement.status,
				}
			)

		# Sort by date
		activities.sort(key=lambda x: x.get("date", ""), reverse=True)

		return activities[:10]
	except Exception as e:
		frappe.log_error(f"Error getting member recent activity: {e!s}")
		return []
