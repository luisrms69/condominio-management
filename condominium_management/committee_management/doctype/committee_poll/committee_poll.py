# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime, nowdate


class CommitteePoll(Document):
	def validate(self):
		self.validate_dates()
		self.validate_poll_options()
		self.set_created_by()
		self.calculate_eligible_voters()
		self.calculate_results()

	def validate_dates(self):
		"""Validate start and end dates"""
		if self.end_date and self.start_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw("La fecha de cierre debe ser posterior a la fecha de inicio")

		# If end date is in the past and poll is open, close it
		if self.end_date and getdate(self.end_date) < getdate(nowdate()) and self.status == "Abierta":
			self.status = "Cerrada"
			self.closed_date = now_datetime()

	def validate_poll_options(self):
		"""Validate poll options"""
		if not self.poll_options:
			frappe.throw("Debe agregar al menos una opción de respuesta")

		if len(self.poll_options) < 2:
			frappe.throw("Debe agregar al menos dos opciones de respuesta")

		# Check for duplicate options
		option_texts = [option.option_text for option in self.poll_options]
		if len(option_texts) != len(set(option_texts)):
			frappe.throw("No puede haber opciones de respuesta duplicadas")

		# Set order numbers if not set
		for i, option in enumerate(self.poll_options):
			if not option.option_order:
				option.option_order = i + 1

	def set_created_by(self):
		"""Set created_by field to current committee member if applicable"""
		if not self.created_by:
			# Try to find current user's committee member record
			current_user = frappe.session.user
			committee_member = frappe.db.get_value(
				"Committee Member", {"user": current_user, "is_active": 1}, "name"
			)
			if committee_member:
				self.created_by = committee_member

	def calculate_eligible_voters(self):
		"""Calculate number of eligible voters based on target audience"""
		if self.target_audience == "Solo Comité":
			self.total_eligible_voters = frappe.db.count("Committee Member", {"is_active": 1})
		elif self.target_audience == "Todos los Propietarios":
			self.total_eligible_voters = frappe.db.count("Property Registry", {"is_active": 1})
		elif self.target_audience == "Propietarios Residentes":
			# TODO: Fix property_status field - column doesn't exist in Property Registry
			# Fallback to all active properties for now
			self.total_eligible_voters = frappe.db.count("Property Registry", {"is_active": 1})
		else:  # Grupo Específico
			# This would need custom logic based on specific criteria
			self.total_eligible_voters = 0

	def calculate_results(self):
		"""Calculate poll results from responses"""
		if not self.poll_options:
			return

		# Get poll responses (this would come from a Poll Response DocType)
		# For now, we'll calculate from the poll_options table if it has response data
		total_responses = 0

		for option in self.poll_options:
			if option.response_count:
				total_responses += option.response_count

		self.total_responses = total_responses

		# Calculate participation rate
		if self.total_eligible_voters > 0:
			self.participation_rate = (self.total_responses / self.total_eligible_voters) * 100
		else:
			self.participation_rate = 0

		# Calculate percentages for each option
		for option in self.poll_options:
			if self.total_responses > 0 and option.response_count:
				option.response_percentage = (option.response_count / self.total_responses) * 100
			else:
				option.response_percentage = 0

	def submit_response(self, option_text, respondent_type, respondent_id, comment=None):
		"""Submit a response to the poll"""
		# Validate poll is open
		if self.status != "Abierta":
			frappe.throw("Esta encuesta no está abierta para respuestas")

		# Validate dates
		today = getdate(nowdate())
		if self.start_date and getdate(self.start_date) > today:
			frappe.throw("Esta encuesta aún no ha comenzado")

		if self.end_date and getdate(self.end_date) < today:
			frappe.throw("Esta encuesta ya ha finalizado")

		# Validate respondent eligibility
		if not self.is_eligible_respondent(respondent_type, respondent_id):
			frappe.throw("No está autorizado para responder esta encuesta")

		# Check if already responded
		if self.has_already_responded(respondent_type, respondent_id):
			frappe.throw("Ya ha respondido esta encuesta")

		# Find the option
		option_found = None
		for option in self.poll_options:
			if option.option_text == option_text:
				option_found = option
				break

		if not option_found:
			frappe.throw(f"Opción '{option_text}' no encontrada")

		# Create poll response record (this would be a separate DocType)
		# response_data = {
		#     "doctype": "Poll Response",
		#     "poll": self.name,
		#     "option_text": option_text,
		#     "respondent_type": respondent_type,
		#     "respondent_id": respondent_id,
		#     "response_date": now_datetime(),
		#     "comment": comment,
		#     "is_anonymous": self.is_anonymous,
		# }

		# For now, just update the count in the option
		option_found.response_count = (option_found.response_count or 0) + 1

		# Recalculate results
		self.calculate_results()
		self.save()

		return True

	def is_eligible_respondent(self, respondent_type, respondent_id):
		"""Check if respondent is eligible to vote in this poll"""
		if self.target_audience == "Solo Comité":
			return respondent_type == "Committee Member" and frappe.db.exists(
				"Committee Member", {"name": respondent_id, "is_active": 1}
			)
		elif self.target_audience == "Todos los Propietarios":
			return respondent_type == "Property Registry" and frappe.db.exists(
				"Property Registry", {"name": respondent_id, "is_active": 1}
			)
		elif self.target_audience == "Propietarios Residentes":
			return respondent_type == "Property Registry" and frappe.db.exists(
				"Property Registry", {"name": respondent_id, "is_active": 1, "property_status": "Habitada"}
			)
		else:  # Grupo Específico
			# Custom logic would go here
			return False

	def has_already_responded(self, respondent_type, respondent_id):
		"""Check if respondent has already responded to this poll"""
		# This would check the Poll Response DocType
		# For now, return False
		return False

	def close_poll(self, closed_by=None):
		"""Close the poll and finalize results"""
		if self.status != "Abierta":
			frappe.throw("Solo se pueden cerrar encuestas abiertas")

		self.status = "Cerrada"
		self.closed_date = now_datetime()
		self.closed_by = closed_by

		# Final calculation of results
		self.calculate_results()
		self.save()

		# Send notifications (would integrate with Communication System)
		self.notify_poll_results()

		return True

	def notify_poll_results(self):
		"""Notify participants about poll results"""
		# This would integrate with Communication System module
		pass

	def get_poll_summary(self):
		"""Get poll summary statistics"""
		summary = {
			"poll_title": self.poll_title,
			"poll_type": self.poll_type,
			"status": self.status,
			"total_eligible_voters": self.total_eligible_voters,
			"total_responses": self.total_responses,
			"participation_rate": self.participation_rate,
			"start_date": self.start_date,
			"end_date": self.end_date,
			"is_anonymous": self.is_anonymous,
			"options": [],
		}

		for option in self.poll_options:
			summary["options"].append(
				{
					"option_text": option.option_text,
					"response_count": option.response_count or 0,
					"response_percentage": option.response_percentage or 0,
				}
			)

		return summary

	def get_winning_option(self):
		"""Get the option with the most responses"""
		if not self.poll_options:
			return None

		max_responses = 0
		winning_option = None

		for option in self.poll_options:
			response_count = option.response_count or 0
			if response_count > max_responses:
				max_responses = response_count
				winning_option = option

		return winning_option

	def is_tie(self):
		"""Check if there's a tie in the results"""
		if not self.poll_options or len(self.poll_options) < 2:
			return False

		response_counts = [option.response_count or 0 for option in self.poll_options]
		max_count = max(response_counts)

		# Count how many options have the maximum count
		max_count_options = sum(1 for count in response_counts if count == max_count)

		return max_count_options > 1

	@staticmethod
	def get_active_polls(poll_type=None, limit=10):
		"""Get active polls"""
		filters = {"status": "Abierta"}

		if poll_type:
			filters["poll_type"] = poll_type

		return frappe.get_all(
			"Committee Poll",
			filters=filters,
			fields=["name", "poll_title", "poll_type", "start_date", "end_date", "participation_rate"],
			order_by="start_date desc",
			limit=limit,
		)

	@staticmethod
	def get_recent_polls(limit=10):
		"""Get recently closed polls"""
		return frappe.get_all(
			"Committee Poll",
			filters={"status": "Cerrada"},
			fields=[
				"name",
				"poll_title",
				"poll_type",
				"closed_date",
				"participation_rate",
				"total_responses",
			],
			order_by="closed_date desc",
			limit=limit,
		)

	@staticmethod
	def get_poll_statistics(date_range=None):
		"""Get poll statistics"""
		filters = {}

		if date_range:
			filters["start_date"] = ["between", date_range]

		all_polls = frappe.get_all(
			"Committee Poll",
			filters=filters,
			fields=["status", "poll_type", "participation_rate", "total_responses"],
		)

		total_polls = len(all_polls)
		if total_polls == 0:
			return {}

		active_polls = len([p for p in all_polls if p.status == "Abierta"])
		closed_polls = len([p for p in all_polls if p.status == "Cerrada"])
		cancelled_polls = len([p for p in all_polls if p.status == "Cancelada"])

		# Average participation rate for closed polls
		closed_polls_data = [p for p in all_polls if p.status == "Cerrada"]
		avg_participation = (
			sum([p.participation_rate or 0 for p in closed_polls_data]) / len(closed_polls_data)
			if closed_polls_data
			else 0
		)

		# Total responses
		total_responses = sum([p.total_responses or 0 for p in all_polls])

		return {
			"total_polls": total_polls,
			"active_polls": active_polls,
			"closed_polls": closed_polls,
			"cancelled_polls": cancelled_polls,
			"average_participation_rate": avg_participation,
			"total_responses": total_responses,
		}

	def on_update(self):
		"""Hook method called after document update"""
		# Recalculate results and update status if needed
		self.calculate_results()

		# Check if poll should be automatically closed
		if self.end_date and getdate(self.end_date) < getdate(nowdate()) and self.status == "Abierta":
			self.status = "Cerrada"
			self.closed_date = now_datetime()
