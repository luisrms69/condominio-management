# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, nowdate


class CommitteeMember(Document):
	def validate(self):
		self.validate_unique_role()
		self.validate_dates()
		self.set_default_permissions()
		self.validate_property_registry()
		self.set_committee_position_weight()

	def validate_unique_role(self):
		"""Validate that certain roles are unique within the committee"""
		unique_roles = ["Presidente", "Secretario", "Tesorero"]

		if self.role_in_committee in unique_roles:
			existing = frappe.get_all(
				"Committee Member",
				filters={
					"role_in_committee": self.role_in_committee,
					"is_active": 1,
					"name": ["!=", self.name],
				},
			)

			if existing:
				frappe.throw(
					f"Ya existe un miembro activo con el cargo de {self.role_in_committee}. "
					f"Solo puede haber un miembro activo por cargo único."
				)

	def validate_dates(self):
		"""Validate start and end dates"""
		if self.start_date and self.end_date:
			if self.start_date >= self.end_date:
				frappe.throw("La fecha de inicio debe ser anterior a la fecha de finalización")

		# If no start date, set to today
		if not self.start_date:
			self.start_date = nowdate()

	def set_default_permissions(self):
		"""Set default permissions based on role"""
		role_permissions = {
			"Presidente": {
				"can_approve_expenses": 1,
				"can_call_assembly": 1,
				"can_sign_documents": 1,
				"can_create_polls": 1,
			},
			"Secretario": {"can_call_assembly": 1, "can_sign_documents": 1, "can_create_polls": 1},
			"Tesorero": {"can_approve_expenses": 1, "can_sign_documents": 1, "can_create_polls": 1},
			"Vocal": {"can_create_polls": 1},
		}

		if self.role_in_committee in role_permissions:
			permissions = role_permissions[self.role_in_committee]
			for perm, value in permissions.items():
				if not getattr(self, perm, None):
					setattr(self, perm, value)

	def validate_property_registry(self):
		"""Validate that the property registry exists and is active"""
		if self.property_registry:
			property_doc = frappe.get_doc("Property Registry", self.property_registry)
			if not property_doc.is_active:
				frappe.throw(
					f"La propiedad {self.property_registry} no está activa. "
					f"Solo se pueden asignar propiedades activas a miembros del comité."
				)

	def set_committee_position_weight(self):
		"""Set position weight based on role hierarchy"""
		weight_map = {"Presidente": 4, "Secretario": 3, "Tesorero": 2, "Vocal": 1}

		if self.role_in_committee in weight_map:
			self.committee_position_weight = weight_map[self.role_in_committee]

	def on_update(self):
		"""Update user permissions when committee member is updated"""
		self.update_user_permissions()

	def update_user_permissions(self):
		"""Update user permissions based on committee role"""
		if not self.user:
			return

		# Get or create user roles based on committee position
		user_roles = self.get_user_roles_for_committee_position()

		# Add roles to user
		for role in user_roles:
			if not frappe.db.exists("Has Role", {"parent": self.user, "role": role}):
				frappe.get_doc(
					{
						"doctype": "Has Role",
						"parent": self.user,
						"parenttype": "User",
						"parentfield": "roles",
						"role": role,
					}
				).insert(ignore_permissions=True)

	def get_user_roles_for_committee_position(self):
		"""Get user roles based on committee position"""
		role_map = {
			"Presidente": ["Committee President"],
			"Secretario": ["Committee Secretary"],
			"Tesorero": ["Committee Treasurer"],
			"Vocal": ["Committee Member"],
		}

		base_roles = ["Committee Member"]  # All committee members get this role
		specific_roles = role_map.get(self.role_in_committee, [])

		return base_roles + specific_roles

	def before_cancel(self):
		"""Clean up before canceling"""
		self.remove_user_permissions()

	def remove_user_permissions(self):
		"""Remove user permissions when committee member is deactivated"""
		if not self.user:
			return

		# Remove committee-specific roles
		committee_roles = [
			"Committee President",
			"Committee Secretary",
			"Committee Treasurer",
			"Committee Member",
		]

		for role in committee_roles:
			role_doc = frappe.db.get_value("Has Role", {"parent": self.user, "role": role}, "name")
			if role_doc:
				frappe.delete_doc("Has Role", role_doc, ignore_permissions=True)

	@staticmethod
	def get_active_committee_members():
		"""Get all active committee members"""
		return frappe.get_all(
			"Committee Member",
			filters={"is_active": 1},
			fields=["name", "full_name", "role_in_committee", "committee_position_weight"],
			order_by="committee_position_weight desc",
		)

	@staticmethod
	def get_committee_member_by_role(role):
		"""Get committee member by specific role"""
		return frappe.get_value(
			"Committee Member",
			{"role_in_committee": role, "is_active": 1},
			["name", "full_name", "user", "property_registry"],
		)

	def has_permission_to_approve_expense(self, amount):
		"""Check if member can approve expense of given amount"""
		if not self.can_approve_expenses:
			return False

		if not self.expense_approval_limit:
			return True  # No limit means can approve any amount

		return cint(amount) <= cint(self.expense_approval_limit)
