# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class CommitteeMember(Document):
	def validate(self):
		self.validate_required_fields()
		self.set_default_start_date()
		self.validate_dates()
		self.validate_company_consistency()
		self.validate_no_duplicate_active_member()

	def validate_required_fields(self):
		if not self.company:
			frappe.throw(_("El campo 'Condominio' es obligatorio."))
		if not self.committee_position:
			frappe.throw(_("El campo 'Cargo' es obligatorio."))

	def set_default_start_date(self):
		if not self.start_date:
			self.start_date = nowdate()

	def validate_dates(self):
		if self.start_date and self.end_date:
			if self.end_date < self.start_date:
				frappe.throw(_("La fecha 'Miembro Hasta' no puede ser anterior a 'Miembro Desde'."))

	def validate_company_consistency(self):
		"""property_registry y committee_position deben pertenecer al mismo condominio."""
		if self.property_registry:
			pr_company = frappe.db.get_value("Property Registry", self.property_registry, "company")
			if pr_company and pr_company != self.company:
				frappe.throw(
					_("La propiedad '{0}' pertenece a '{1}', no a '{2}'.").format(
						self.property_registry, pr_company, self.company
					)
				)

		if self.committee_position:
			pos_company = frappe.db.get_value("Committee Position", self.committee_position, "company")
			if pos_company and pos_company != self.company:
				frappe.throw(
					_("El cargo '{0}' pertenece a '{1}', no a '{2}'.").format(
						self.committee_position, pos_company, self.company
					)
				)

	def validate_no_duplicate_active_member(self):
		"""Un usuario no puede ser miembro activo dos veces en el mismo condominio."""
		if not self.user or not self.company or not self.is_active:
			return

		existing = frappe.db.exists(
			"Committee Member",
			{
				"user": self.user,
				"company": self.company,
				"is_active": 1,
				"name": ["!=", self.name or ""],
			},
		)
		if existing:
			frappe.throw(_("El usuario ya es miembro activo del comité en '{0}'.").format(self.company))

	@staticmethod
	def get_active_committee_members(company=None):
		filters = {"is_active": 1}
		if company:
			filters["company"] = company
		return frappe.get_all(
			"Committee Member",
			filters=filters,
			fields=["name", "full_name", "committee_position", "company", "user"],
		)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_condomino_users(doctype, txt, searchfield, start, page_len, filters):
	"""Retorna usuarios con rol Condómino para el selector de Committee Member."""
	return frappe.db.sql(
		"""
		SELECT DISTINCT u.name, u.full_name
		FROM `tabUser` u
		INNER JOIN `tabHas Role` hr ON hr.parent = u.name
		WHERE hr.role = 'Condómino'
		  AND u.enabled = 1
		  AND u.name NOT IN ('Administrator', 'Guest')
		  AND (u.name LIKE %(txt)s OR u.full_name LIKE %(txt)s)
		ORDER BY u.full_name
		LIMIT %(page_len)s OFFSET %(start)s
		""",
		{"txt": f"%{txt}%", "page_len": page_len, "start": start},
	)
