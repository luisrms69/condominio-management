# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, get_datetime, now_datetime


class CommitteeMeeting(Document):
	def validate(self):
		self.validate_meeting_date()
		self.validate_physical_space()
		self.validate_virtual_meeting_link()
		self.calculate_pending_items()
		self.calculate_completion_rate()

	def validate_meeting_date(self):
		"""Validate meeting date is not in the past"""
		if self.meeting_date:
			meeting_datetime = get_datetime(self.meeting_date)
			if meeting_datetime < now_datetime() and self.status == "Planificada":
				frappe.throw("No se puede planificar una reunión en una fecha pasada")

	def validate_physical_space(self):
		"""Validate physical space is required for non-virtual meetings"""
		if self.meeting_format in ["Presencial", "Híbrida"] and not self.physical_space:
			frappe.throw(
				f"Se requiere especificar un espacio físico para reuniones {self.meeting_format.lower()}s"
			)

	def validate_virtual_meeting_link(self):
		"""Validate virtual meeting link is required for virtual meetings"""
		if self.meeting_format in ["Virtual", "Híbrida"] and not self.virtual_meeting_link:
			frappe.throw(
				f"Se requiere especificar un enlace de reunión virtual para reuniones {self.meeting_format.lower()}s"
			)

	def calculate_pending_items(self):
		"""Calculate number of pending agenda items"""
		pending_count = 0
		for item in self.agenda_items:
			if not item.decisions_taken and not item.action_items:
				pending_count += 1
		self.pending_items_count = pending_count

	def calculate_completion_rate(self):
		"""Calculate completion rate based on agenda items with decisions/actions"""
		if not self.agenda_items:
			self.completion_rate = 0
			return

		completed_items = 0
		for item in self.agenda_items:
			if item.decisions_taken or item.action_items:
				completed_items += 1

		self.completion_rate = (completed_items / len(self.agenda_items)) * 100

	def on_update(self):
		"""Actions after meeting is updated"""
		if self.status == "Completada":
			self.create_follow_up_items()
			self.update_meeting_series()

	def create_follow_up_items(self):
		"""Create follow-up items for actions with due dates"""
		for item in self.agenda_items:
			if item.action_items and item.due_date and item.responsible_member:
				# Create ToDo for follow-up
				todo = frappe.get_doc(
					{
						"doctype": "ToDo",
						"description": f"Acción de reunión: {item.topic_title}\n\n{item.action_items}",
						"owner": frappe.get_value("Committee Member", item.responsible_member, "user"),
						"reference_type": "Committee Meeting",
						"reference_name": self.name,
						"date": item.due_date,
						"priority": self.get_todo_priority(item.priority),
						"status": "Open",
					}
				)
				todo.insert()

	def get_todo_priority(self, priority):
		"""Convert agenda item priority to ToDo priority"""
		priority_map = {"Crítica": "High", "Alta": "High", "Media": "Medium", "Baja": "Low"}
		return priority_map.get(priority, "Medium")

	def update_meeting_series(self):
		"""Update meeting series if this is a scheduled meeting"""
		if self.is_scheduled_meeting and self.meeting_series:
			# Mark this meeting as created in the series
			series_doc = frappe.get_doc("Meeting Schedule", self.meeting_series)
			for scheduled_meeting in series_doc.scheduled_meetings:
				if (
					scheduled_meeting.meeting_date == self.meeting_date.date()
					and not scheduled_meeting.meeting_created
				):
					scheduled_meeting.meeting_created = 1
					scheduled_meeting.linked_meeting = self.name
					break
			series_doc.save()

	def before_submit(self):
		"""Validation before submitting the meeting"""
		if self.status != "Completada":
			frappe.throw("Solo se pueden enviar reuniones completadas")

		if not self.attendees:
			frappe.throw("Debe registrar al menos un asistente antes de enviar la reunión")

		# Validate that all critical agenda items have decisions
		critical_items_without_decisions = []
		for item in self.agenda_items:
			if item.priority == "Crítica" and not item.decisions_taken:
				critical_items_without_decisions.append(item.topic_title)

		if critical_items_without_decisions:
			frappe.throw(
				f"Los siguientes temas críticos no tienen decisiones registradas: "
				f"{', '.join(critical_items_without_decisions)}"
			)

	def load_committee_members_as_attendees(self):
		"""Load all active committee members as attendees"""
		active_members = frappe.get_all(
			"Committee Member", filters={"is_active": 1}, fields=["name", "full_name", "role_in_committee"]
		)

		# Clear existing attendees
		self.attendees = []

		# Add all active committee members
		for member in active_members:
			self.append(
				"attendees",
				{
					"committee_member": member.name,
					"attendance_status": "Presente",  # Default to present
				},
			)

		self.save()

	def get_attendance_summary(self):
		"""Get attendance summary statistics"""
		if not self.attendees:
			return {}

		total_attendees = len(self.attendees)
		present_count = len([a for a in self.attendees if a.attendance_status == "Presente"])
		virtual_count = len([a for a in self.attendees if a.attendance_status == "Virtual"])
		absent_count = len([a for a in self.attendees if a.attendance_status == "Ausente"])
		excused_count = len([a for a in self.attendees if a.attendance_status == "Excusado"])

		return {
			"total_attendees": total_attendees,
			"present_count": present_count,
			"virtual_count": virtual_count,
			"absent_count": absent_count,
			"excused_count": excused_count,
			"attendance_rate": ((present_count + virtual_count) / total_attendees) * 100,
		}

	def get_agenda_summary(self):
		"""Get agenda summary statistics"""
		if not self.agenda_items:
			return {}

		total_items = len(self.agenda_items)
		completed_items = len([item for item in self.agenda_items if item.decisions_taken])
		pending_items = total_items - completed_items

		# Calculate total time spent
		total_minutes = 0
		for item in self.agenda_items:
			if item.time_spent:
				# Convert duration to minutes
				time_parts = str(item.time_spent).split(":")
				if len(time_parts) >= 2:
					total_minutes += int(time_parts[0]) * 60 + int(time_parts[1])

		return {
			"total_items": total_items,
			"completed_items": completed_items,
			"pending_items": pending_items,
			"completion_rate": (completed_items / total_items) * 100 if total_items > 0 else 0,
			"total_time_minutes": total_minutes,
		}

	@staticmethod
	def get_upcoming_meetings(limit=10):
		"""Get upcoming committee meetings"""
		return frappe.get_all(
			"Committee Meeting",
			filters={
				"meeting_date": [">=", now_datetime()],
				"status": ["in", ["Planificada", "En Progreso"]],
			},
			fields=["name", "meeting_title", "meeting_date", "meeting_type", "status"],
			order_by="meeting_date asc",
			limit=limit,
		)

	@staticmethod
	def get_meetings_by_date_range(start_date, end_date):
		"""Get meetings within a date range"""
		return frappe.get_all(
			"Committee Meeting",
			filters={"meeting_date": ["between", [start_date, end_date]]},
			fields=["name", "meeting_title", "meeting_date", "meeting_type", "status", "completion_rate"],
			order_by="meeting_date desc",
		)

	def create_agreement_tracking_items(self):
		"""Create agreement tracking items for decisions taken"""
		for item in self.agenda_items:
			if item.decisions_taken and item.responsible_member:
				# Create Agreement Tracking item
				agreement = frappe.get_doc(
					{
						"doctype": "Agreement Tracking",
						"source_type": "Reunión Comité",
						"source_reference": self.name,
						"agreement_text": f"Decisión tomada en reunión sobre: {item.topic_title}\n\n{item.decisions_taken}",
						"agreement_category": self.get_agreement_category(item.topic_category),
						"responsible_party": item.responsible_member,
						"due_date": item.due_date,
						"priority": item.priority or "Media",
						"status": "Pendiente",
					}
				)
				agreement.insert()

	def get_agreement_category(self, topic_category):
		"""Map topic category to agreement category"""
		category_map = {
			"Financiero": "Financiero",
			"Operativo": "Operativo",
			"Legal": "Legal",
			"Social": "Social",
			"Mantenimiento": "Operativo",
			"Seguridad": "Operativo",
			"Otro": "Operativo",
		}
		return category_map.get(topic_category, "Operativo")
