# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, getdate, now_datetime, nowdate


class AssemblyManagement(Document):
	def validate(self):
		self.validate_assembly_dates()
		self.validate_quorum_requirements()
		self.validate_call_times()
		self.set_assembly_number()
		self.calculate_current_quorum()
		self.validate_hybrid_meeting()

	def validate_assembly_dates(self):
		"""Validate assembly and convocation dates"""
		if self.convocation_date and self.assembly_date:
			assembly_date_only = get_datetime(self.assembly_date).date()
			convocation_date_only = getdate(self.convocation_date)
			if convocation_date_only >= assembly_date_only:
				frappe.throw("La fecha de convocatoria debe ser anterior a la fecha de asamblea")

		# Assembly cannot be in the past (unless it's completed)
		if self.assembly_date and self.status == "Planificada":
			if get_datetime(self.assembly_date) < now_datetime():
				frappe.throw("No se puede planificar una asamblea en una fecha pasada")

	def validate_quorum_requirements(self):
		"""Validate quorum percentages"""
		if self.minimum_quorum_first <= self.minimum_quorum_second:
			frappe.throw("El quórum de primera convocatoria debe ser mayor al de segunda convocatoria")

		if self.minimum_quorum_first > 100 or self.minimum_quorum_second > 100:
			frappe.throw("Los porcentajes de quórum no pueden exceder el 100%")

	def validate_call_times(self):
		"""Validate call times"""
		if self.first_call_time and self.second_call_time:
			if self.first_call_time >= self.second_call_time:
				frappe.throw("La hora de primera convocatoria debe ser anterior a la segunda convocatoria")

	def set_assembly_number(self):
		"""Auto-generate assembly number if not set"""
		if not self.assembly_number:
			year = get_datetime(self.assembly_date).year if self.assembly_date else nowdate()[:4]

			# Get count of assemblies for this year
			count = frappe.db.count(
				"Assembly Management",
				filters={
					"assembly_date": ["between", [f"{year}-01-01", f"{year}-12-31"]],
					"name": ["!=", self.name],
				},
			)

			assembly_number = f"{self.assembly_type[:3].upper()}-{year}-{str(count + 1).zfill(3)}"
			self.assembly_number = assembly_number

	def validate_hybrid_meeting(self):
		"""Validate hybrid meeting requirements"""
		if self.hybrid_meeting_enabled and not self.virtual_platform_link:
			frappe.throw("Se requiere especificar el enlace de la plataforma virtual para reuniones híbridas")

	def calculate_current_quorum(self):
		"""Calculate current quorum percentage based on registrations"""
		if not self.quorum_registration:
			self.current_quorum_percentage = 0
			self.quorum_reached = 0
			return

		total_attending_percentage = 0

		for record in self.quorum_registration:
			if record.attendance_status in ["Presente", "Representado"]:
				total_attending_percentage += flt(record.ownership_percentage or 0)

		self.current_quorum_percentage = total_attending_percentage

		# Check if quorum is reached based on current time and call times
		current_time = now_datetime().time()
		assembly_date = get_datetime(self.assembly_date).date()

		if nowdate() == str(assembly_date):
			if current_time >= self.second_call_time:
				# After second call
				self.quorum_reached = 1 if total_attending_percentage >= self.minimum_quorum_second else 0
			elif current_time >= self.first_call_time:
				# After first call
				self.quorum_reached = 1 if total_attending_percentage >= self.minimum_quorum_first else 0
			else:
				# Before first call
				self.quorum_reached = 0
		else:
			# Not assembly day yet
			self.quorum_reached = 0

	def load_all_properties_to_quorum(self):
		"""Load all active properties to quorum registration"""
		properties = frappe.get_all(
			"Property Registry",
			filters={"is_active": 1},
			fields=["name", "owner_name", "ownership_percentage"],
		)

		# Clear existing quorum records
		self.quorum_registration = []

		# Add all properties
		for prop in properties:
			self.append(
				"quorum_registration",
				{
					"property_registry": prop.name,
					"attendance_status": "Ausente",  # Default to absent
				},
			)

		self.save()

	def register_property_attendance(
		self, property_registry, attendance_status, proxy_holder=None, proxy_document=None
	):
		"""Register property attendance"""
		# Find existing record
		existing_record = None
		for record in self.quorum_registration:
			if record.property_registry == property_registry:
				existing_record = record
				break

		if not existing_record:
			# Add new record
			self.append(
				"quorum_registration",
				{
					"property_registry": property_registry,
					"attendance_status": attendance_status,
					"attendance_time": now_datetime(),
					"check_in_method": "Manual",
					"proxy_holder": proxy_holder,
					"proxy_document": proxy_document,
				},
			)
		else:
			# Update existing record
			existing_record.attendance_status = attendance_status
			existing_record.attendance_time = now_datetime()
			if proxy_holder:
				existing_record.proxy_holder = proxy_holder
			if proxy_document:
				existing_record.proxy_document = proxy_document

		# Recalculate quorum
		self.calculate_current_quorum()
		self.save()

	def before_submit(self):
		"""Validation before submitting assembly"""
		if self.status != "Completada":
			frappe.throw("Solo se pueden enviar asambleas completadas")

		if not self.quorum_reached:
			frappe.throw("No se puede enviar una asamblea sin quórum suficiente")

		# Validate that all voting agenda items have been processed
		pending_votes = []
		for agenda_item in self.formal_agenda:
			if agenda_item.requires_vote:
				# Check if there's a voting system record for this agenda item
				voting_exists = frappe.db.exists(
					"Voting System", {"assembly": self.name, "motion_title": agenda_item.agenda_topic}
				)
				if not voting_exists:
					pending_votes.append(agenda_item.agenda_topic)

		if pending_votes:
			frappe.throw(
				f"Los siguientes puntos de agenda requieren votación pero no han sido procesados: "
				f"{', '.join(pending_votes)}"
			)

	def on_submit(self):
		"""Actions after assembly is submitted"""
		self.create_assembly_minutes()
		self.create_agreement_tracking_items()

	def create_assembly_minutes(self):
		"""Create assembly minutes document"""
		# This would integrate with Document Generation module
		pass

	def create_agreement_tracking_items(self):
		"""Create agreement tracking items for assembly decisions"""
		for agenda_item in self.formal_agenda:
			if agenda_item.requires_vote:
				# Get voting result
				voting_result = frappe.get_value(
					"Voting System",
					{"assembly": self.name, "motion_title": agenda_item.agenda_topic},
					["result", "name"],
				)

				if voting_result and voting_result[0] == "Aprobado":
					# Create agreement tracking
					agreement = frappe.get_doc(
						{
							"doctype": "Agreement Tracking",
							"source_type": "Asamblea",
							"source_reference": self.name,
							"agreement_text": f"Acuerdo aprobado en asamblea: {agenda_item.agenda_topic}\n\n{agenda_item.topic_description or ''}",
							"agreement_category": "Legal",
							"responsible_party": agenda_item.presenter,
							"priority": "Alta",
							"status": "Pendiente",
						}
					)
					agreement.insert()

	def get_quorum_summary(self):
		"""Get quorum summary statistics"""
		if not self.quorum_registration:
			return {}

		total_properties = len(self.quorum_registration)
		present_count = len([r for r in self.quorum_registration if r.attendance_status == "Presente"])
		represented_count = len(
			[r for r in self.quorum_registration if r.attendance_status == "Representado"]
		)
		absent_count = len([r for r in self.quorum_registration if r.attendance_status == "Ausente"])

		return {
			"total_properties": total_properties,
			"present_count": present_count,
			"represented_count": represented_count,
			"absent_count": absent_count,
			"attending_count": present_count + represented_count,
			"attendance_rate": ((present_count + represented_count) / total_properties) * 100
			if total_properties > 0
			else 0,
			"current_quorum_percentage": self.current_quorum_percentage,
			"quorum_reached": self.quorum_reached,
			"required_quorum_first": self.minimum_quorum_first,
			"required_quorum_second": self.minimum_quorum_second,
		}

	def get_agenda_summary(self):
		"""Get agenda summary statistics"""
		if not self.formal_agenda:
			return {}

		total_items = len(self.formal_agenda)
		voting_items = len([item for item in self.formal_agenda if item.requires_vote])
		informative_items = total_items - voting_items

		return {
			"total_items": total_items,
			"voting_items": voting_items,
			"informative_items": informative_items,
		}

	@staticmethod
	def get_upcoming_assemblies(limit=5):
		"""Get upcoming assemblies"""
		return frappe.get_all(
			"Assembly Management",
			filters={"assembly_date": [">=", now_datetime()], "status": ["in", ["Planificada", "Convocada"]]},
			fields=["name", "assembly_type", "assembly_number", "assembly_date", "status"],
			order_by="assembly_date asc",
			limit=limit,
		)

	@staticmethod
	def get_assembly_history(limit=10):
		"""Get assembly history"""
		return frappe.get_all(
			"Assembly Management",
			filters={"docstatus": 1},
			fields=["name", "assembly_type", "assembly_number", "assembly_date", "current_quorum_percentage"],
			order_by="assembly_date desc",
			limit=limit,
		)
