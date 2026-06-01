# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CommitteePosition(Document):
	def validate(self):
		self.validate_unique_per_company()
		self.validate_hierarchy_level()

	def validate_unique_per_company(self):
		"""El par company + position_name debe ser único.

		Con autoname format:{company}::{position_name}, el name generado es idéntico
		para docs con la misma company+position_name. Para docs nuevos, comparamos
		directamente contra el name generado; para ediciones, excluimos self.name.
		"""
		if self.is_new():
			# El autoname ya generó self.name — verificar si ese name existe en BD
			if frappe.db.exists("Committee Position", self.name):
				frappe.throw(
					_("Ya existe el cargo '{0}' para el condominio '{1}'.").format(
						self.position_name, self.company
					)
				)
		else:
			existing = frappe.db.exists(
				"Committee Position",
				{
					"company": self.company,
					"position_name": self.position_name,
					"name": ["!=", self.name],
				},
			)
			if existing:
				frappe.throw(
					_("Ya existe el cargo '{0}' para el condominio '{1}'.").format(
						self.position_name, self.company
					)
				)

	def validate_hierarchy_level(self):
		if self.hierarchy_level < 1:
			frappe.throw(_("El nivel jerárquico debe ser mayor a 0."))

	@staticmethod
	def setup_default_positions(company):
		"""Crea los 4 cargos base para un condominio si no existen.

		Idempotente: puede llamarse varias veces sin duplicar.
		Jerarquía: 4=Presidente (mayor), 3=Secretario, 2=Tesorero, 1=Vocal.
		"""
		defaults = [
			{
				"position_name": "Presidente",
				"hierarchy_level": 4,
				"responsibilities": "Representación legal y dirección del comité.",
				"can_approve_expenses": 1,
				"can_call_assembly": 1,
				"can_sign_documents": 1,
				"can_create_polls": 1,
			},
			{
				"position_name": "Secretario",
				"hierarchy_level": 3,
				"responsibilities": "Actas, convocatorias y archivo del comité.",
				"can_approve_expenses": 0,
				"can_call_assembly": 1,
				"can_sign_documents": 1,
				"can_create_polls": 1,
			},
			{
				"position_name": "Tesorero",
				"hierarchy_level": 2,
				"responsibilities": "Administración financiera y rendición de cuentas.",
				"can_approve_expenses": 1,
				"can_call_assembly": 0,
				"can_sign_documents": 1,
				"can_create_polls": 1,
			},
			{
				"position_name": "Vocal",
				"hierarchy_level": 1,
				"responsibilities": "Participación en sesiones y comisiones asignadas.",
				"can_approve_expenses": 0,
				"can_call_assembly": 0,
				"can_sign_documents": 0,
				"can_create_polls": 1,
			},
		]

		created = []
		for pos in defaults:
			name = f"{company}::{pos['position_name']}"
			if not frappe.db.exists("Committee Position", name):
				doc = frappe.get_doc(
					{
						"doctype": "Committee Position",
						"company": company,
						**pos,
					}
				)
				doc.insert(ignore_permissions=True)
				created.append(pos["position_name"])

		if created:
			frappe.db.commit()

		return created
