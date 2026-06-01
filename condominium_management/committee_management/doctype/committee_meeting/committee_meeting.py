# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, get_datetime, now_datetime


class CommitteeMeeting(Document):
	def validate(self):
		self.validate_meeting_date()
		self.validate_physical_space()

	def validate_meeting_date(self):
		if self.meeting_date and self.status == "Planificada":
			if get_datetime(self.meeting_date) < now_datetime():
				frappe.throw(_("No se puede planificar una reunión en una fecha pasada."))

	def validate_physical_space(self):
		if self.meeting_format in ["Presencial", "Híbrida"] and not self.physical_space:
			frappe.throw(
				_("Se requiere espacio físico para reuniones {0}.").format(self.meeting_format.lower())
			)

	def on_update(self):
		if self.status == "Terminada":
			self.create_follow_up_tasks()
			self.update_meeting_series()

	def create_follow_up_tasks(self):
		"""Crea ToDos en ERPNext para action_items con responsable y fecha."""
		for item in self.agenda_items:
			if not item.action_items or not item.responsible_member:
				continue
			user = frappe.db.get_value("Committee Member", item.responsible_member, "user")
			if not user:
				continue
			frappe.get_doc(
				{
					"doctype": "ToDo",
					"description": f"[{self.meeting_title}] {item.topic_title}\n\n{item.action_items}",
					"owner": user,
					"reference_type": "Committee Meeting",
					"reference_name": self.name,
					"date": item.due_date,
					"status": "Open",
				}
			).insert(ignore_permissions=True)

	def update_meeting_series(self):
		if not self.is_scheduled_meeting or not self.meeting_series:
			return
		try:
			series_doc = frappe.get_doc("Meeting Schedule", self.meeting_series)
			for sm in series_doc.scheduled_meetings:
				if sm.meeting_date == get_datetime(self.meeting_date).date() and not sm.meeting_created:
					sm.meeting_created = 1
					sm.linked_meeting = self.name
					break
			series_doc.save(ignore_permissions=True)
		except Exception:
			pass

	@frappe.whitelist()
	def create_event(self):
		"""Crea un Event de Frappe para esta reunión con recordatorio 24h antes."""
		if not self.meeting_date:
			frappe.throw(_("La reunión debe tener fecha y hora antes de agendarla."))

		event = frappe.get_doc(
			{
				"doctype": "Event",
				"subject": self.meeting_title,
				"starts_on": self.meeting_date,
				"event_type": "Private",
				"send_reminder": 1,
				"reminder_date_time": add_to_date(self.meeting_date, hours=-24),
				"description": self.meeting_notes or f"Reunión de comité: {self.meeting_title}",
				"status": "Open",
			}
		)

		for attendee in self.attendees:
			user = frappe.db.get_value("Committee Member", attendee.committee_member, "user")
			if user:
				event.append(
					"event_participants",
					{
						"reference_doctype": "User",
						"reference_docname": user,
						"role": "Attendee",
					},
				)

		event.insert(ignore_permissions=True)
		return event.name

	@frappe.whitelist()
	def create_task(self, subject, assigned_to=None, due_date=None, description=None):
		"""Crea un ToDo/Task ligado a esta reunión."""
		todo = frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": f"[{self.meeting_title}]\n{subject}"
				+ (f"\n\n{description}" if description else ""),
				"owner": assigned_to or frappe.session.user,
				"reference_type": "Committee Meeting",
				"reference_name": self.name,
				"date": due_date,
				"status": "Open",
			}
		)
		todo.insert(ignore_permissions=True)
		return todo.name

	@staticmethod
	def get_upcoming_meetings(company=None, limit=10):
		filters = {
			"meeting_date": [">=", now_datetime()],
			"status": "Planificada",
		}
		if company:
			filters["company"] = company
		return frappe.get_all(
			"Committee Meeting",
			filters=filters,
			fields=["name", "meeting_title", "meeting_date", "meeting_type", "status"],
			order_by="meeting_date asc",
			limit=limit,
		)
