# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime, nowdate


class CommunityEvent(Document):
	def validate(self):
		self.validate_event_date()
		self.validate_times()
		self.validate_physical_space_capacity()
		self.validate_registration_settings()
		self.validate_budget_approval()
		self.calculate_costs()
		self.calculate_registration_capacity()

	def validate_event_date(self):
		"""Validate event date is not in the past for new events"""
		if self.event_date and self.status == "Planificado":
			if getdate(self.event_date) < getdate(nowdate()):
				frappe.throw("No se puede planificar un evento en una fecha pasada")

	def validate_times(self):
		"""Validate start and end times"""
		if self.start_time and self.end_time:
			if self.start_time >= self.end_time:
				frappe.throw("La hora de inicio debe ser anterior a la hora de finalización")

	def validate_physical_space_capacity(self):
		"""Validate expected attendance doesn't exceed space capacity"""
		if self.physical_space and self.expected_attendance:
			space_capacity = frappe.get_value("Physical Space", self.physical_space, "capacity")
			if space_capacity and self.expected_attendance > space_capacity:
				frappe.msgprint(
					f"La asistencia esperada ({self.expected_attendance}) excede la capacidad del espacio ({space_capacity}). "
					f"Considere cambiar de espacio o reducir la asistencia esperada.",
					alert=True,
				)

	def validate_registration_settings(self):
		"""Validate registration settings"""
		if self.registration_required:
			if not self.registration_deadline:
				frappe.throw("Debe especificar una fecha límite de registro cuando el registro es requerido")

			if getdate(self.registration_deadline) > getdate(self.event_date):
				frappe.throw("La fecha límite de registro debe ser anterior a la fecha del evento")

			if self.max_capacity and self.expected_attendance:
				if self.max_capacity > self.expected_attendance:
					frappe.msgprint(
						f"La capacidad máxima ({self.max_capacity}) es mayor que la asistencia esperada ({self.expected_attendance})",
						alert=True,
					)

	def validate_budget_approval(self):
		"""Validate budget approval requirements"""
		if (
			self.require_assembly_approval
			and not self.assembly_approved
			and self.status not in ["Planificado", "En Organización"]
		):
			frappe.throw("Este evento requiere aprobación de asamblea antes de poder confirmarse")

	def calculate_costs(self):
		"""Calculate total estimated and actual costs"""
		estimated_total = 0
		actual_total = 0

		for expense in self.expense_tracking:
			if expense.estimated_cost:
				estimated_total += flt(expense.estimated_cost)
			if expense.actual_cost:
				actual_total += flt(expense.actual_cost)

		self.total_estimated_cost = estimated_total
		self.total_actual_cost = actual_total

		# Calculate profit/loss
		if self.budget_amount:
			self.profit_loss = flt(self.budget_amount) - actual_total

	def calculate_registration_capacity(self):
		"""Calculate current registrations and available capacity"""
		if self.registration_required and self.attendee_registration:
			total_registrations = 0
			for registration in self.attendee_registration:
				total_registrations += cint(
					registration.total_attendees or (registration.adults_count + registration.children_count)
				)

			self.current_registrations = total_registrations

			if self.max_capacity:
				self.available_capacity = self.max_capacity - total_registrations

	def before_save(self):
		"""Actions before saving the document"""
		# Auto-calculate total attendees for each registration
		for registration in self.attendee_registration:
			registration.total_attendees = cint(registration.adults_count or 1) + cint(
				registration.children_count or 0
			)

	def on_update(self):
		"""Actions after document is updated"""
		if self.status == "Completado":
			self.create_event_summary()

		# Create recurring events if applicable
		if self.is_recurring and self.status == "Completado":
			self.create_next_recurring_event()

	def create_event_summary(self):
		"""Create event summary for completed events"""
		# This would integrate with Document Generation for event reports
		pass

	def create_next_recurring_event(self):
		"""Create next event in recurring series"""
		if not self.recurrence_pattern:
			return

		from dateutil.relativedelta import relativedelta

		next_date = getdate(self.event_date)

		if self.recurrence_pattern == "Semanal":
			next_date += relativedelta(weeks=1)
		elif self.recurrence_pattern == "Mensual":
			next_date += relativedelta(months=1)
		elif self.recurrence_pattern == "Trimestral":
			next_date += relativedelta(months=3)
		elif self.recurrence_pattern == "Semestral":
			next_date += relativedelta(months=6)
		elif self.recurrence_pattern == "Anual":
			next_date += relativedelta(years=1)

		# Create new event
		new_event = frappe.copy_doc(self)
		new_event.event_date = next_date
		new_event.status = "Planificado"
		new_event.actual_attendance = None
		new_event.event_success_rating = None
		new_event.event_photos_link = None
		new_event.lessons_learned = None

		# Clear post-event data
		new_event.attendee_registration = []
		new_event.expense_tracking = []

		# Reset calculated fields
		new_event.current_registrations = 0
		new_event.total_actual_cost = 0
		new_event.profit_loss = 0

		new_event.insert()

		frappe.msgprint(f"Próximo evento recurrente creado para {next_date}")

	def register_attendee(
		self,
		property_registry,
		adults_count=1,
		children_count=0,
		contact_phone=None,
		contact_email=None,
		special_requirements=None,
	):
		"""Register an attendee for the event"""
		# Validate registration is open
		if not self.registration_required:
			frappe.throw("Este evento no requiere registro")

		if self.registration_deadline and getdate(nowdate()) > getdate(self.registration_deadline):
			frappe.throw("El período de registro ha finalizado")

		if self.status not in ["Planificado", "En Organización", "Confirmado"]:
			frappe.throw("No se puede registrar para este evento en su estado actual")

		# Check if already registered
		for existing_registration in self.attendee_registration:
			if existing_registration.property_registry == property_registry:
				frappe.throw("Esta propiedad ya está registrada para el evento")

		# Check capacity
		total_attendees = adults_count + children_count
		if self.max_capacity and (self.current_registrations + total_attendees) > self.max_capacity:
			frappe.throw(
				f"No hay capacidad suficiente. Disponible: {self.available_capacity}, Solicitado: {total_attendees}"
			)

		# Add registration
		self.append(
			"attendee_registration",
			{
				"property_registry": property_registry,
				"adults_count": adults_count,
				"children_count": children_count,
				"contact_phone": contact_phone,
				"contact_email": contact_email,
				"special_requirements": special_requirements,
				"registration_date": now_datetime(),
			},
		)

		self.save()

		return True

	def cancel_registration(self, property_registry):
		"""Cancel registration for a property"""
		registration_found = None
		for registration in self.attendee_registration:
			if registration.property_registry == property_registry:
				registration_found = registration
				break

		if not registration_found:
			frappe.throw("No se encontró registro para esta propiedad")

		self.remove(registration_found)
		self.save()

		return True

	def add_expense(self, category, description, estimated_cost, supplier=None, notes=None):
		"""Add an expense to the event"""
		self.append(
			"expense_tracking",
			{
				"expense_category": category,
				"description": description,
				"estimated_cost": estimated_cost,
				"supplier": supplier,
				"expense_notes": notes,
				"payment_status": "Pendiente",
			},
		)

		self.save()

		return True

	def record_actual_expense(
		self, expense_description, actual_cost, invoice_reference=None, payment_status="Pagado"
	):
		"""Record actual expense for an existing expense item"""
		expense_found = None
		for expense in self.expense_tracking:
			if expense.description == expense_description:
				expense_found = expense
				break

		if not expense_found:
			frappe.throw(f"No se encontró el gasto: {expense_description}")

		expense_found.actual_cost = actual_cost
		expense_found.invoice_reference = invoice_reference
		expense_found.payment_status = payment_status

		self.save()

		return True

	def get_event_summary(self):
		"""Get event summary statistics"""
		summary = {
			"event_name": self.event_name,
			"event_type": self.event_type,
			"event_date": self.event_date,
			"status": self.status,
			"expected_attendance": self.expected_attendance,
			"actual_attendance": self.actual_attendance,
			"budget_amount": self.budget_amount,
			"total_estimated_cost": self.total_estimated_cost,
			"total_actual_cost": self.total_actual_cost,
			"profit_loss": self.profit_loss,
			"registration_stats": {},
			"expense_stats": {},
			"activity_count": len(self.activities_schedule),
		}

		# Registration statistics
		if self.registration_required:
			summary["registration_stats"] = {
				"current_registrations": self.current_registrations,
				"max_capacity": self.max_capacity,
				"available_capacity": self.available_capacity,
				"registration_rate": (self.current_registrations / self.max_capacity * 100)
				if self.max_capacity
				else 0,
			}

		# Expense statistics
		paid_expenses = len([e for e in self.expense_tracking if e.payment_status == "Pagado"])
		total_expenses = len(self.expense_tracking)

		summary["expense_stats"] = {
			"total_expense_items": total_expenses,
			"paid_expenses": paid_expenses,
			"pending_expenses": total_expenses - paid_expenses,
			"budget_utilization": (self.total_actual_cost / self.budget_amount * 100)
			if self.budget_amount
			else 0,
		}

		return summary

	@staticmethod
	def get_upcoming_events(limit=10):
		"""Get upcoming community events"""
		return frappe.get_all(
			"Community Event",
			filters={
				"event_date": [">=", nowdate()],
				"status": ["in", ["Planificado", "En Organización", "Confirmado"]],
			},
			fields=["name", "event_name", "event_type", "event_date", "status", "expected_attendance"],
			order_by="event_date asc",
			limit=limit,
		)

	@staticmethod
	def get_event_history(event_type=None, limit=10):
		"""Get event history"""
		filters = {"status": "Completado"}

		if event_type:
			filters["event_type"] = event_type

		return frappe.get_all(
			"Community Event",
			filters=filters,
			fields=[
				"name",
				"event_name",
				"event_type",
				"event_date",
				"actual_attendance",
				"event_success_rating",
			],
			order_by="event_date desc",
			limit=limit,
		)

	@staticmethod
	def get_event_statistics(date_range=None):
		"""Get event statistics"""
		filters = {}

		if date_range:
			filters["event_date"] = ["between", date_range]

		all_events = frappe.get_all(
			"Community Event",
			filters=filters,
			fields=[
				"status",
				"event_type",
				"actual_attendance",
				"event_success_rating",
				"total_actual_cost",
				"budget_amount",
			],
		)

		total_events = len(all_events)
		if total_events == 0:
			return {}

		completed_events = [e for e in all_events if e.status == "Completado"]

		# Calculate averages for completed events
		avg_attendance = (
			sum([e.actual_attendance or 0 for e in completed_events]) / len(completed_events)
			if completed_events
			else 0
		)
		avg_success_rating = (
			sum([e.event_success_rating or 0 for e in completed_events]) / len(completed_events)
			if completed_events
			else 0
		)
		total_cost = sum([e.total_actual_cost or 0 for e in all_events])
		total_budget = sum([e.budget_amount or 0 for e in all_events])

		return {
			"total_events": total_events,
			"completed_events": len(completed_events),
			"average_attendance": avg_attendance,
			"average_success_rating": avg_success_rating,
			"total_cost": total_cost,
			"total_budget": total_budget,
			"budget_efficiency": (total_cost / total_budget * 100) if total_budget else 0,
		}
