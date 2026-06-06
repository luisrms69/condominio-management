# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate


class PropertyUserAuthorization(Document):
	def before_save(self):
		self._derive_company()
		self._set_audit_fields()

	def validate(self):
		self._validate_company_consistency()
		self._validate_dates()
		self._validate_no_duplicate_active()

	def _derive_company(self):
		if self.property_registry and not self.company:
			self.company = frappe.db.get_value("Property Registry", self.property_registry, "company")

	def _set_audit_fields(self):
		if self.is_new():
			self.authorized_by = frappe.session.user
			self.authorized_on = now_datetime()

	def _validate_company_consistency(self):
		if not self.property_registry or not self.company:
			return
		registry_company = frappe.db.get_value("Property Registry", self.property_registry, "company")
		if registry_company and registry_company != self.company:
			frappe.throw(
				f"El condominio '{self.company}' no coincide con el condominio de la propiedad "
				f"'{self.property_registry}' ({registry_company}).",
				title="Inconsistencia de condominio",
			)

	def _validate_dates(self):
		if self.valid_from and self.valid_until:
			if getdate(self.valid_until) < getdate(self.valid_from):
				frappe.throw(
					"La fecha de expiración debe ser posterior a la fecha de inicio.",
					title="Fechas inválidas",
				)

	def _validate_no_duplicate_active(self):
		"""One active PUA per user + property_registry (D2 — Fase 1 MVP rule)."""
		if not self.is_active:
			return
		filters = {
			"user": self.user,
			"property_registry": self.property_registry,
			"is_active": 1,
		}
		if not self.is_new():
			filters["name"] = ["!=", self.name]
		existing = frappe.db.get_value("Property User Authorization", filters, "name")
		if existing:
			frappe.throw(
				f"Ya existe una autorización activa ({existing}) para el usuario "
				f"'{self.user}' sobre la propiedad '{self.property_registry}'. "
				"Solo puede existir una autorización activa por usuario y propiedad.",
				title="Autorización duplicada",
			)
