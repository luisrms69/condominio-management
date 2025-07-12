# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cint, flt, getdate, now_datetime, nowdate


class AgreementTracking(Document):
	def validate(self):
		self.set_agreement_number()
		self.validate_dates()
		self.update_completion_percentage()
		self.update_status_based_on_due_date()

	def set_agreement_number(self):
		"""Auto-generate agreement number if not set"""
		if not self.agreement_number:
			year = getdate(self.agreement_date).year if self.agreement_date else getdate(nowdate()).year

			# Get count of agreements for this year
			count = frappe.db.count(
				"Agreement Tracking",
				filters={
					"agreement_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
					"name": ["!=", self.name],
				},
			)

			agreement_number = f"ACU-{year}-{str(count + 1).zfill(4)}"
			self.agreement_number = agreement_number

	def validate_dates(self):
		"""Validate agreement and due dates"""
		if self.due_date and self.agreement_date:
			if getdate(self.due_date) < getdate(self.agreement_date):
				frappe.throw("La fecha límite no puede ser anterior a la fecha del acuerdo")

	def update_completion_percentage(self):
		"""Update completion percentage based on latest progress update"""
		if self.progress_updates:
			# Get the latest progress update
			latest_update = max(self.progress_updates, key=lambda x: x.update_date)
			if latest_update.percentage_complete is not None:
				self.completion_percentage = latest_update.percentage_complete

	def update_status_based_on_due_date(self):
		"""Update status to 'Vencido' if past due date"""
		if self.due_date and self.status not in ["Completado", "Cancelado"]:
			if getdate(self.due_date) < getdate(nowdate()):
				self.status = "Vencido"

	def after_insert(self):
		"""Actions after agreement is created"""
		if self.auto_create_todos:
			self.create_todo_items()

	def on_update(self):
		"""Actions when agreement is updated"""
		self.send_progress_notifications()
		self.update_related_todos()

		# Auto-complete if 100%
		if self.completion_percentage == 100 and self.status != "Completado":
			self.status = "Completado"

	def create_todo_items(self):
		"""Create ToDo items for responsible parties"""
		# Create ToDo for primary responsible
		if self.responsible_party:
			responsible_user = frappe.get_value("Committee Member", self.responsible_party, "user")
			if responsible_user:
				todo = frappe.get_doc(
					{
						"doctype": "ToDo",
						"description": f"Acuerdo: {self.agreement_text[:100]}...",
						"owner": responsible_user,
						"reference_type": "Agreement Tracking",
						"reference_name": self.name,
						"date": self.due_date,
						"priority": self.get_todo_priority(),
						"status": "Open",
					}
				)
				todo.insert()

		# Create ToDo for secondary responsible
		if self.secondary_responsible:
			secondary_user = frappe.get_value("Committee Member", self.secondary_responsible, "user")
			if secondary_user:
				todo = frappe.get_doc(
					{
						"doctype": "ToDo",
						"description": f"Acuerdo (Apoyo): {self.agreement_text[:100]}...",
						"owner": secondary_user,
						"reference_type": "Agreement Tracking",
						"reference_name": self.name,
						"date": self.due_date,
						"priority": self.get_todo_priority(),
						"status": "Open",
					}
				)
				todo.insert()

	def get_todo_priority(self):
		"""Convert agreement priority to ToDo priority"""
		priority_map = {"Crítica": "High", "Alta": "High", "Media": "Medium", "Baja": "Low"}
		return priority_map.get(self.priority, "Medium")

	def send_progress_notifications(self):
		"""Send notifications about progress updates"""
		# This would integrate with Communication System
		pass

	def update_related_todos(self):
		"""Update status of related ToDo items"""
		if self.status == "Completado":
			# Close related ToDo items
			todos = frappe.get_all(
				"ToDo",
				filters={
					"reference_type": "Agreement Tracking",
					"reference_name": self.name,
					"status": "Open",
				},
			)

			for todo in todos:
				todo_doc = frappe.get_doc("ToDo", todo.name)
				todo_doc.status = "Closed"
				todo_doc.save()

	def add_progress_update(self, description, percentage_complete=None, attachments=None):
		"""Add a progress update"""
		update = {
			"update_date": now_datetime(),
			"updated_by": frappe.session.user,
			"update_description": description,
			"percentage_complete": percentage_complete,
			"attachments": attachments,
		}

		self.append("progress_updates", update)
		self.save()

		return update

	def get_days_until_due(self):
		"""Get number of days until due date"""
		if not self.due_date:
			return None

		today = getdate(nowdate())
		due_date = getdate(self.due_date)

		return (due_date - today).days

	def is_overdue(self):
		"""Check if agreement is overdue"""
		days_until_due = self.get_days_until_due()
		return days_until_due is not None and days_until_due < 0

	def is_due_soon(self, days_threshold=7):
		"""Check if agreement is due soon"""
		days_until_due = self.get_days_until_due()
		return days_until_due is not None and 0 <= days_until_due <= days_threshold

	def get_progress_summary(self):
		"""Get progress summary statistics"""
		total_updates = len(self.progress_updates)

		if total_updates == 0:
			return {
				"total_updates": 0,
				"latest_update_date": None,
				"completion_percentage": self.completion_percentage or 0,
				"days_until_due": self.get_days_until_due(),
				"is_overdue": self.is_overdue(),
				"is_due_soon": self.is_due_soon(),
			}

		latest_update = max(self.progress_updates, key=lambda x: x.update_date)

		return {
			"total_updates": total_updates,
			"latest_update_date": latest_update.update_date,
			"latest_update_by": latest_update.updated_by,
			"completion_percentage": self.completion_percentage or 0,
			"days_until_due": self.get_days_until_due(),
			"is_overdue": self.is_overdue(),
			"is_due_soon": self.is_due_soon(),
		}

	@staticmethod
	def get_pending_agreements(responsible_party=None, limit=10):
		"""Get pending agreements"""
		filters = {"status": ["in", ["Pendiente", "En Proceso"]]}

		if responsible_party:
			filters["responsible_party"] = responsible_party

		return frappe.get_all(
			"Agreement Tracking",
			filters=filters,
			fields=[
				"name",
				"agreement_text",
				"due_date",
				"priority",
				"completion_percentage",
				"responsible_party",
			],
			order_by="due_date asc",
			limit=limit,
		)

	@staticmethod
	def get_overdue_agreements(limit=10):
		"""Get overdue agreements"""
		return frappe.get_all(
			"Agreement Tracking",
			filters={"due_date": ["<", nowdate()], "status": ["in", ["Pendiente", "En Proceso"]]},
			fields=["name", "agreement_text", "due_date", "priority", "responsible_party"],
			order_by="due_date asc",
			limit=limit,
		)

	@staticmethod
	def get_agreements_due_soon(days_threshold=7, limit=10):
		"""Get agreements due soon"""
		due_date_threshold = add_days(nowdate(), days_threshold)

		return frappe.get_all(
			"Agreement Tracking",
			filters={
				"due_date": ["between", [nowdate(), due_date_threshold]],
				"status": ["in", ["Pendiente", "En Proceso"]],
			},
			fields=["name", "agreement_text", "due_date", "priority", "responsible_party"],
			order_by="due_date asc",
			limit=limit,
		)

	@staticmethod
	def get_completion_statistics(date_range=None):
		"""Get completion statistics"""
		filters = {}

		if date_range:
			filters["agreement_date"] = ["between", date_range]

		all_agreements = frappe.get_all(
			"Agreement Tracking", filters=filters, fields=["status", "completion_percentage", "priority"]
		)

		total_agreements = len(all_agreements)
		if total_agreements == 0:
			return {}

		completed = len([a for a in all_agreements if a.status == "Completado"])
		pending = len([a for a in all_agreements if a.status == "Pendiente"])
		in_progress = len([a for a in all_agreements if a.status == "En Proceso"])
		overdue = len([a for a in all_agreements if a.status == "Vencido"])
		cancelled = len([a for a in all_agreements if a.status == "Cancelado"])

		# Average completion percentage for non-completed agreements
		non_completed = [a for a in all_agreements if a.status not in ["Completado", "Cancelado"]]
		avg_completion = (
			sum([a.completion_percentage or 0 for a in non_completed]) / len(non_completed)
			if non_completed
			else 0
		)

		return {
			"total_agreements": total_agreements,
			"completed": completed,
			"pending": pending,
			"in_progress": in_progress,
			"overdue": overdue,
			"cancelled": cancelled,
			"completion_rate": (completed / total_agreements) * 100,
			"average_completion_percentage": avg_completion,
		}

	def mark_as_completed(self, completion_note=None):
		"""Mark agreement as completed with optional note"""
		self.status = "Completado"
		self.completion_percentage = 100

		if completion_note:
			self.add_progress_update(completion_note, 100)

		self.save()
		return self

	@staticmethod
	def send_due_date_reminders():
		"""Send reminders for agreements approaching due date"""
		# This would be called by a scheduled job
		agreements_due_soon = frappe.get_all(
			"Agreement Tracking",
			filters={
				"due_date": [">=", nowdate()],
				"status": ["in", ["Pendiente", "En Proceso"]],
				"reminder_days_before": [">", 0],
			},
			fields=["name", "due_date", "reminder_days_before", "responsible_party", "secondary_responsible"],
		)

		for agreement in agreements_due_soon:
			due_date = getdate(agreement.due_date)
			reminder_date = add_days(due_date, -agreement.reminder_days_before)

			if getdate(nowdate()) == reminder_date:
				# Send reminder (would integrate with Communication System)
				pass
