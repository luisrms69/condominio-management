# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, add_months, getdate, now_datetime, nowdate


class MeetingSchedule(Document):
	def validate(self):
		self.validate_schedule_period()
		self.validate_meeting_dates()
		self.set_created_by()
		self.calculate_meeting_counts()

	def validate_schedule_period(self):
		"""Validate schedule period"""
		current_year = datetime.now().year

		if self.schedule_year < current_year:
			frappe.msgprint(
				f"Está creando un programa para el año {self.schedule_year} que ya pasó", alert=True
			)

		if self.schedule_year > current_year + 2:
			frappe.throw("No se pueden crear programas para más de 2 años en el futuro")

	def validate_meeting_dates(self):
		"""Validate meeting dates"""
		if not self.scheduled_meetings:
			frappe.throw("Debe programar al menos una reunión")

		# Check for duplicate dates
		dates = [getdate(meeting.meeting_date) for meeting in self.scheduled_meetings]
		if len(dates) != len(set(dates)):
			frappe.throw("No puede haber fechas de reunión duplicadas")

		# Validate dates are within the scheduled year
		for meeting in self.scheduled_meetings:
			meeting_date = getdate(meeting.meeting_date)
			if meeting_date.year != self.schedule_year:
				frappe.throw(
					f"La fecha de reunión {meeting.meeting_date} no corresponde al año del programa {self.schedule_year}"
				)

	def set_created_by(self):
		"""Set created_by field to current committee member if applicable"""
		if not self.created_by:
			current_user = frappe.session.user
			committee_member = frappe.db.get_value(
				"Committee Member", {"user": current_user, "is_active": 1}, "name"
			)
			if committee_member:
				self.created_by = committee_member

	def calculate_meeting_counts(self):
		"""Calculate meeting counts"""
		if not self.scheduled_meetings:
			self.meetings_created_count = 0
			self.pending_meetings_count = 0
			return

		created_count = len([m for m in self.scheduled_meetings if m.meeting_created])
		self.meetings_created_count = created_count
		self.pending_meetings_count = len(self.scheduled_meetings) - created_count

	def on_submit(self):
		"""Actions when schedule is submitted"""
		self.approval_status = "Aprobado"
		self.approved_by = self.get_current_committee_member()

		if self.auto_create_meetings:
			self.create_upcoming_meetings()

	def get_current_committee_member(self):
		"""Get current user's committee member record"""
		current_user = frappe.session.user
		return frappe.db.get_value("Committee Member", {"user": current_user, "is_active": 1}, "name")

	def create_upcoming_meetings(self):
		"""Create meetings for upcoming dates"""
		today = getdate(nowdate())

		for scheduled_meeting in self.scheduled_meetings:
			meeting_date = getdate(scheduled_meeting.meeting_date)

			# Only create meetings for future dates or dates within the next 30 days
			if meeting_date >= today and not scheduled_meeting.meeting_created:
				meeting_doc = self.create_committee_meeting(scheduled_meeting)
				if meeting_doc:
					scheduled_meeting.meeting_created = 1
					scheduled_meeting.linked_meeting = meeting_doc.name

		self.calculate_meeting_counts()
		self.last_sync_date = now_datetime()
		self.save()

	def create_committee_meeting(self, scheduled_meeting):
		"""Create a committee meeting from scheduled meeting"""
		try:
			meeting_doc = frappe.get_doc(
				{
					"doctype": "Committee Meeting",
					"meeting_title": f"Reunión {scheduled_meeting.meeting_type} - {self.schedule_period} {self.schedule_year}",
					"meeting_date": scheduled_meeting.meeting_date,
					"meeting_type": scheduled_meeting.meeting_type,
					"meeting_format": "Presencial",  # Default, can be changed later
					"physical_space": scheduled_meeting.tentative_location,
					"is_scheduled_meeting": 1,
					"meeting_series": self.name,
				}
			)

			# Add suggested topics as agenda items
			if scheduled_meeting.suggested_topics:
				topics = scheduled_meeting.suggested_topics.split("\n")
				for _i, topic in enumerate(topics):
					if topic.strip():
						meeting_doc.append(
							"agenda_items",
							{
								"topic_title": topic.strip(),
								"topic_category": "Operativo",
								"priority": "Media",
							},
						)

			meeting_doc.insert()
			return meeting_doc

		except Exception as e:
			frappe.log_error(f"Error creating committee meeting: {e!s}")
			return None

	def sync_scheduled_meetings(self):
		"""Sync and create any pending meetings"""
		if self.docstatus != 1:
			frappe.throw("Solo se pueden sincronizar programas aprobados")

		self.create_upcoming_meetings()

		return {
			"meetings_created": self.meetings_created_count,
			"meetings_pending": self.pending_meetings_count,
		}

	def generate_standard_schedule(self):
		"""Generate a standard meeting schedule based on period"""
		if self.scheduled_meetings:
			frappe.throw(
				"Ya existen reuniones programadas. Elimínelas primero si desea generar un programa estándar"
			)

		# Clear existing meetings
		self.scheduled_meetings = []

		if self.schedule_period == "Anual":
			self.generate_annual_schedule()
		elif self.schedule_period == "Semestral":
			self.generate_semestral_schedule()
		elif self.schedule_period == "Trimestral":
			self.generate_trimestral_schedule()

		self.save()

	def generate_annual_schedule(self):
		"""Generate annual meeting schedule"""
		# Monthly meetings + quarterly reviews + annual planning
		months = [
			(1, "Ordinaria", "Revisión de metas anuales"),
			(2, "Ordinaria", "Seguimiento enero"),
			(3, "Revisión Financiera", "Revisión trimestre 1"),
			(4, "Ordinaria", "Seguimiento marzo"),
			(5, "Ordinaria", "Seguimiento abril"),
			(6, "Revisión Financiera", "Revisión trimestre 2"),
			(7, "Ordinaria", "Seguimiento junio"),
			(8, "Ordinaria", "Seguimiento julio"),
			(9, "Revisión Financiera", "Revisión trimestre 3"),
			(10, "Ordinaria", "Seguimiento septiembre"),
			(11, "Planeación", "Planeación año siguiente"),
			(12, "Evaluación", "Evaluación anual"),
		]

		for month, meeting_type, topics in months:
			# Schedule for the 15th of each month
			meeting_date = datetime(self.schedule_year, month, 15).date()

			self.append(
				"scheduled_meetings",
				{
					"meeting_date": meeting_date,
					"meeting_type": meeting_type,
					"tentative_time": "18:00:00",
					"is_mandatory": 1,
					"suggested_topics": topics,
				},
			)

	def generate_semestral_schedule(self):
		"""Generate semestral meeting schedule"""
		# Bi-monthly meetings + mid-term and final reviews
		meetings = [
			(1, "Planeación", "Planeación semestral"),
			(2, "Ordinaria", "Seguimiento enero"),
			(3, "Revisión Financiera", "Revisión primer trimestre"),
			(4, "Ordinaria", "Seguimiento marzo"),
			(5, "Ordinaria", "Seguimiento abril"),
			(6, "Evaluación", "Evaluación semestral"),
		]

		for month, meeting_type, topics in meetings:
			meeting_date = datetime(self.schedule_year, month, 15).date()

			self.append(
				"scheduled_meetings",
				{
					"meeting_date": meeting_date,
					"meeting_type": meeting_type,
					"tentative_time": "18:00:00",
					"is_mandatory": 1,
					"suggested_topics": topics,
				},
			)

	def generate_trimestral_schedule(self):
		"""Generate trimestral meeting schedule"""
		# Monthly meetings for three months
		for month in [1, 2, 3]:
			meeting_type = "Planeación" if month == 1 else "Ordinaria" if month == 2 else "Evaluación"
			topics = f"Reunión {meeting_type.lower()} del trimestre"

			meeting_date = datetime(self.schedule_year, month, 15).date()

			self.append(
				"scheduled_meetings",
				{
					"meeting_date": meeting_date,
					"meeting_type": meeting_type,
					"tentative_time": "18:00:00",
					"is_mandatory": 1,
					"suggested_topics": topics,
				},
			)

	def get_schedule_summary(self):
		"""Get schedule summary statistics"""
		if not self.scheduled_meetings:
			return {}

		total_meetings = len(self.scheduled_meetings)
		mandatory_meetings = len([m for m in self.scheduled_meetings if m.is_mandatory])
		created_meetings = len([m for m in self.scheduled_meetings if m.meeting_created])

		# Upcoming meetings
		today = getdate(nowdate())
		upcoming_meetings = [
			m for m in self.scheduled_meetings if getdate(m.meeting_date) >= today and not m.meeting_created
		]

		# Past meetings
		past_meetings = [m for m in self.scheduled_meetings if getdate(m.meeting_date) < today]

		return {
			"total_meetings": total_meetings,
			"mandatory_meetings": mandatory_meetings,
			"created_meetings": created_meetings,
			"pending_meetings": total_meetings - created_meetings,
			"upcoming_meetings": len(upcoming_meetings),
			"past_meetings": len(past_meetings),
			"completion_rate": (created_meetings / total_meetings * 100) if total_meetings > 0 else 0,
		}

	def get_next_scheduled_meeting(self):
		"""Get the next scheduled meeting"""
		today = getdate(nowdate())

		upcoming_meetings = [m for m in self.scheduled_meetings if getdate(m.meeting_date) >= today]

		if upcoming_meetings:
			# Sort by date and return the earliest
			upcoming_meetings.sort(key=lambda x: getdate(x.meeting_date))
			return upcoming_meetings[0]

		return None

	@staticmethod
	def get_active_schedules():
		"""Get active meeting schedules"""
		current_year = datetime.now().year

		return frappe.get_all(
			"Meeting Schedule",
			filters={"schedule_year": ["in", [current_year, current_year + 1]], "docstatus": 1},
			fields=[
				"name",
				"schedule_year",
				"schedule_period",
				"approval_status",
				"meetings_created_count",
				"pending_meetings_count",
			],
			order_by="schedule_year desc, creation desc",
		)

	@staticmethod
	def check_pending_meetings():
		"""Check for pending meetings that need to be created (scheduled task)"""
		active_schedules = frappe.get_all(
			"Meeting Schedule", filters={"docstatus": 1, "auto_create_meetings": 1}, fields=["name"]
		)

		for schedule in active_schedules:
			schedule_doc = frappe.get_doc("Meeting Schedule", schedule.name)
			schedule_doc.create_upcoming_meetings()

	@staticmethod
	def send_meeting_reminders():
		"""Send reminders for upcoming scheduled meetings (scheduled task)"""
		# This would integrate with Communication System
		# For now, create a placeholder method
		pass
