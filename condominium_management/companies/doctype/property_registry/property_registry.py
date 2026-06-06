# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class PropertyRegistry(Document):
	def autoname(self):
		"""Generar código automático de propiedad"""
		if not self.property_code:
			self.property_code = self.generate_property_code()
		self.name = make_autoname(self.naming_series)

	def before_save(self):
		self.validate_physical_space_company()
		self.validate_property_fields()
		self.validate_declared_owners()
		self.calculate_declared_owners_total()
		self.calculate_current_owner_display()

	def validate_physical_space_company(self):
		"""Verifica que el Physical Space pertenezca al mismo condominio que el registro."""
		if not self.physical_space or not self.company:
			return
		space_company = frappe.db.get_value("Physical Space", self.physical_space, "company")
		if space_company and space_company != self.company:
			frappe.throw(
				_(
					"El espacio físico '{0}' pertenece al condominio '{1}', "
					"pero este registro pertenece a '{2}'."
				).format(self.physical_space, space_company, self.company),
				title=_("Condominio inconsistente"),
			)

	def validate_property_fields(self):
		"""Validar campos básicos de propiedad"""
		if self.total_area_sqm and self.built_area_sqm:
			if self.built_area_sqm > self.total_area_sqm:
				frappe.throw(_("El área construida no puede ser mayor al área total"))

		if self.acquisition_date and self.registration_date:
			if self.acquisition_date < self.registration_date:
				frappe.throw(_("La fecha de adquisición no puede ser anterior a la fecha de registro"))

		if self.total_area_sqm and self.total_area_sqm <= 0:
			frappe.throw(_("El área total debe ser mayor a 0"))

		if self.built_area_sqm and self.built_area_sqm <= 0:
			frappe.throw(_("El área construida debe ser mayor a 0"))

		if self.indiviso_percentage is not None:
			if self.indiviso_percentage <= 0 or self.indiviso_percentage > 100:
				frappe.throw(_("El indiviso debe ser mayor a 0 y no puede exceder 100%"))

	def validate_declared_owners(self):
		"""Validar titulares declarados"""
		if not self.declared_owners:
			return

		for row in self.declared_owners:
			if row.ownership_percentage <= 0:
				frappe.throw(_("El porcentaje debe ser mayor a 0 para: {0}").format(row.owner_name))
			if row.ownership_percentage > 100:
				frappe.throw(_("El porcentaje no puede exceder 100% para: {0}").format(row.owner_name))
			if row.start_date and row.end_date and row.end_date < row.start_date:
				frappe.throw(
					_("La fecha 'Titular Hasta' no puede ser anterior a 'Titular Desde' para: {0}").format(
						row.owner_name
					)
				)
			if row.owner_id:
				self.validate_owner_id(row.owner_id, row.owner_type)

		current_owners = [r for r in self.declared_owners if r.is_current]
		if current_owners:
			total = sum(float(r.ownership_percentage) for r in current_owners)
			if abs(total - 100.0) > 0.01:
				frappe.throw(
					_("Los titulares actuales deben sumar exactamente 100%. Suma actual: {0}%").format(
						round(total, 2)
					)
				)

	def calculate_declared_owners_total(self):
		"""Calcular total de porcentajes de titulares actuales"""
		current = [r for r in self.declared_owners if r.is_current] if self.declared_owners else []
		self.current_owners_total_percentage = sum(float(r.ownership_percentage) for r in current)

	def calculate_current_owner_display(self):
		"""Calcular campo informativo del titular actual"""
		if not self.declared_owners:
			self.current_owner_display = ""
			return
		current = [r for r in self.declared_owners if r.is_current]
		if not current:
			self.current_owner_display = ""
		elif len(current) == 1:
			self.current_owner_display = current[0].owner_name
		else:
			self.current_owner_display = _("Copropiedad ({0})").format(len(current))

	def validate_owner_id(self, owner_id, owner_type):
		"""Validar formato RFC/CURP mexicano — advertencia no bloqueante"""
		if not owner_id:
			return
		owner_id_clean = owner_id.strip().upper()
		rfc_moral = re.compile(r"^[A-ZÑ&]{3}\d{6}[A-Z\d]{3}$")
		rfc_fisica = re.compile(r"^[A-ZÑ&]{4}\d{6}[A-Z\d]{3}$")
		curp = re.compile(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$")
		if owner_type == "Persona Moral":
			valid = bool(rfc_moral.match(owner_id_clean))
		else:
			valid = bool(rfc_fisica.match(owner_id_clean)) or bool(curp.match(owner_id_clean))
		if not valid:
			frappe.msgprint(
				_("El identificador '{0}' no tiene el formato esperado de RFC o CURP mexicano").format(
					owner_id
				),
				indicator="orange",
				alert=True,
			)

	def generate_property_code(self):
		"""Generar código único de propiedad"""
		if not self.property_name:
			return "PROP-NEW"

		# Limpiar nombre para código
		clean_name = re.sub(r"[^A-Za-z0-9\s]", "", self.property_name)
		words = clean_name.upper().split()

		if len(words) >= 2:
			# Tomar primeras 2-3 letras de cada palabra
			code = "".join([word[:3] for word in words[:2]])
		else:
			# Una sola palabra, tomar primeras 6 letras
			code = words[0][:6] if words else "PROP"

		# Agregar sufijo de empresa si está disponible
		if self.company:
			company_abbr = frappe.get_value("Company", self.company, "abbr")
			if company_abbr:
				code = f"{code}-{company_abbr}"

		# Verificar unicidad
		counter = 1
		original_code = code
		while frappe.db.exists("Property Registry", {"property_code": code}):
			code = f"{original_code}-{counter}"
			counter += 1

		return code

	def get_ownership_summary(self):
		if not self.declared_owners:
			return "Sin titulares declarados"
		current = [r for r in self.declared_owners if r.is_current]
		if not current:
			return "Sin titulares actuales"
		if len(current) == 1:
			return "Titular único"
		return f"Copropiedad - {len(current)} titulares actuales"

	def get_main_owner(self):
		current = [r for r in self.declared_owners if r.is_current] if self.declared_owners else []
		if not current:
			return "N/A"
		main_owner = max(current, key=lambda x: x.ownership_percentage)
		return f"{main_owner.owner_name} ({main_owner.ownership_percentage}%)"

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay referencias"""
		# Verificar si hay referencias en otros DocTypes
		# Esto se puede expandir según otros DocTypes que referencien Property Registry
		pass

	def on_trash(self):
		"""Prevenir eliminación si hay referencias"""
		# Verificar si hay referencias en otros DocTypes
		# Esto se puede expandir según otros DocTypes que referencien Property Registry
		pass
