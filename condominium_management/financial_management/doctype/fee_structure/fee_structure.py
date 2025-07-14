# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now


class FeeStructure(Document):
	"""Estructura de cuotas del condominio con cálculo automático por indiviso"""

	def before_insert(self):
		"""Configuración inicial antes de insertar"""
		self.validate_fee_structure_name()
		self.validate_effective_dates()
		self.set_default_values()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_calculation_method()
		self.validate_base_amount()
		self.validate_reserve_fund()
		self.validate_adjustments()
		self.validate_fee_components()
		self.validate_committee_approval()

	def before_submit(self):
		"""Validaciones antes de enviar"""
		if self.requires_committee_approval and self.approval_status != "Aprobado":
			frappe.throw(_("La estructura de cuotas requiere aprobación del comité antes de ser enviada"))

		self.check_overlapping_structures()

	def validate_fee_structure_name(self):
		"""Valida unicidad del nombre de estructura"""
		if not self.fee_structure_name:
			frappe.throw(_("El nombre de la estructura es obligatorio"))

		# Verificar unicidad por condominio
		existing = frappe.db.get_value(
			"Fee Structure",
			{
				"fee_structure_name": self.fee_structure_name,
				"company": self.company,
				"name": ["!=", self.name],
			},
			"name",
		)
		if existing:
			frappe.throw(
				_("Ya existe una estructura con el nombre '{0}' para este condominio").format(
					self.fee_structure_name
				)
			)

	def validate_effective_dates(self):
		"""Valida fechas de vigencia"""
		if not self.effective_from:
			frappe.throw(_("La fecha de inicio de vigencia es obligatoria"))

		if self.effective_to and self.effective_to < self.effective_from:
			frappe.throw(_("La fecha fin de vigencia no puede ser anterior a la fecha de inicio"))

		# No permitir fechas retroactivas a menos que sea administrador
		if self.effective_from < getdate() and not frappe.has_permission("Fee Structure", "write"):
			frappe.throw(_("No se pueden crear estructuras con fecha de inicio retroactiva"))

	def validate_calculation_method(self):
		"""Valida método de cálculo"""
		valid_methods = ["Por Indiviso", "Monto Fijo", "Por M2", "Mixto"]
		if self.calculation_method not in valid_methods:
			frappe.throw(
				_("Método de cálculo inválido. Opciones válidas: {0}").format(", ".join(valid_methods))
			)

	def validate_base_amount(self):
		"""Valida monto base"""
		if not self.base_amount or self.base_amount <= 0:
			frappe.throw(_("El monto base debe ser mayor a 0"))

		# Validar límites razonables
		if self.base_amount > 1000000:  # 1 millón
			frappe.throw(_("El monto base excede el límite máximo permitido"))

	def validate_reserve_fund(self):
		"""Valida configuración del fondo de reserva"""
		if self.include_reserve_fund:
			if not self.reserve_fund_percentage or self.reserve_fund_percentage <= 0:
				frappe.throw(_("El porcentaje del fondo de reserva debe ser mayor a 0"))

			if self.reserve_fund_percentage > 50:
				frappe.throw(_("El porcentaje del fondo de reserva no puede exceder 50%"))

	def validate_adjustments(self):
		"""Valida descuentos y recargos"""
		if self.early_payment_discount:
			if self.early_payment_discount <= 0 or self.early_payment_discount > 20:
				frappe.throw(_("El descuento por pronto pago debe estar entre 0 y 20%"))

			if not self.early_payment_days or self.early_payment_days <= 0:
				frappe.throw(_("Los días para descuento por pronto pago son obligatorios"))

		if self.late_payment_charge:
			if self.late_payment_charge <= 0 or self.late_payment_charge > 10:
				frappe.throw(_("El recargo por mora debe estar entre 0 y 10%"))

		if self.grace_period_days and self.grace_period_days < 0:
			frappe.throw(_("Los días de gracia no pueden ser negativos"))

	def validate_fee_components(self):
		"""Valida componentes de la cuota"""
		if not self.fee_components:
			return

		total_percentage = 0
		component_names = []

		for component in self.fee_components:
			# Validar nombres únicos
			if component.component_name in component_names:
				frappe.throw(_("El componente '{0}' está duplicado").format(component.component_name))
			component_names.append(component.component_name)

			# Sumar porcentajes para validación
			if component.amount_type == "Porcentaje":
				total_percentage += component.percentage or 0

		# Validar que porcentajes no excedan 100%
		if total_percentage > 100:
			frappe.throw(_("La suma de porcentajes de componentes no puede exceder 100%"))

	def validate_committee_approval(self):
		"""Valida configuración de aprobación del comité"""
		if self.requires_committee_approval:
			if not self.approval_status:
				self.approval_status = "Pendiente"

			if self.approval_status == "Aprobado":
				if not self.approved_by:
					frappe.throw(_("Debe especificar quién aprobó la estructura"))
				if not self.approval_date:
					self.approval_date = getdate()

	def check_overlapping_structures(self):
		"""Verifica que no haya estructuras superpuestas activas"""
		if not self.is_active:
			return

		# Verificar superposición de fechas
		overlapping = frappe.db.sql(
			"""
			SELECT name, fee_structure_name, effective_from, effective_to
			FROM `tabFee Structure`
			WHERE company = %(company)s
				AND is_active = 1
				AND docstatus = 1
				AND name != %(name)s
				AND (
					(effective_from <= %(effective_from)s AND (effective_to IS NULL OR effective_to >= %(effective_from)s))
					OR (effective_from <= %(effective_to)s AND (effective_to IS NULL OR effective_to >= %(effective_to)s))
					OR (effective_from >= %(effective_from)s AND effective_from <= %(effective_to)s)
				)
		""",
			{
				"company": self.company,
				"name": self.name,
				"effective_from": self.effective_from,
				"effective_to": self.effective_to or "2099-12-31",
			},
			as_dict=True,
		)

		if overlapping:
			frappe.throw(
				_("Existe una estructura activa superpuesta: {0}").format(overlapping[0].fee_structure_name)
			)

	def set_default_values(self):
		"""Establece valores por defecto"""
		if not self.grace_period_days:
			self.grace_period_days = 5

		if not self.approval_status and self.requires_committee_approval:
			self.approval_status = "Pendiente"

	@frappe.whitelist()
	def calculate_fee_for_property(self, property_registry_name):
		"""
		Calcula la cuota para una propiedad específica

		Args:
			property_registry_name: Nombre del registro de propiedad

		Returns:
			dict: Desglose de la cuota calculada
		"""
		property_doc = frappe.get_doc("Property Registry", property_registry_name)

		if self.calculation_method == "Por Indiviso":
			base_fee = self.base_amount * (property_doc.ownership_percentage / 100)
		elif self.calculation_method == "Monto Fijo":
			base_fee = self.base_amount
		elif self.calculation_method == "Por M2":
			base_fee = self.base_amount * (property_doc.built_area_sqm or 0)
		else:  # Mixto
			# Implementar lógica mixta según componentes
			base_fee = self.calculate_mixed_fee(property_doc)

		# Aplicar componentes
		components_total = self.calculate_components_for_property(property_doc, base_fee)

		# Calcular fondo de reserva
		reserve_fund = 0
		if self.include_reserve_fund:
			reserve_fund = (base_fee + components_total) * (self.reserve_fund_percentage / 100)

		total_fee = base_fee + components_total + reserve_fund

		return {
			"base_fee": flt(base_fee, 2),
			"components_total": flt(components_total, 2),
			"reserve_fund": flt(reserve_fund, 2),
			"total_fee": flt(total_fee, 2),
			"calculation_method": self.calculation_method,
			"components_breakdown": self.get_components_breakdown(property_doc, base_fee),
		}

	def calculate_mixed_fee(self, property_doc):
		"""Calcula cuota usando método mixto"""
		# Lógica por implementar según componentes específicos
		return self.base_amount * (property_doc.ownership_percentage / 100)

	def calculate_components_for_property(self, property_doc, base_fee):
		"""Calcula el total de componentes para una propiedad"""
		total = 0

		for component in self.fee_components:
			if self.component_applies_to_property(component, property_doc):
				if component.amount_type == "Fijo":
					total += component.amount or 0
				else:  # Porcentaje
					total += base_fee * ((component.percentage or 0) / 100)

		return total

	def component_applies_to_property(self, component, property_doc):
		"""Verifica si un componente aplica a una propiedad específica"""
		if component.apply_to_all:
			return True

		# Verificar tipos de propiedad específicos
		if component.property_types:
			property_types = [pt.property_type for pt in component.property_types if pt.active]
			return property_doc.property_type in property_types

		return True

	def get_components_breakdown(self, property_doc, base_fee):
		"""Obtiene desglose detallado de componentes"""
		breakdown = []

		for component in self.fee_components:
			if self.component_applies_to_property(component, property_doc):
				if component.amount_type == "Fijo":
					amount = component.amount or 0
				else:
					amount = base_fee * ((component.percentage or 0) / 100)

				breakdown.append(
					{
						"component_name": component.component_name,
						"amount_type": component.amount_type,
						"amount": flt(amount, 2),
					}
				)

		return breakdown

	@frappe.whitelist()
	def get_total_monthly_income(self):
		"""Calcula el ingreso mensual total estimado"""
		if not self.company:
			return 0

		# Obtener todas las propiedades del condominio
		properties = frappe.get_all(
			"Property Registry",
			filters={"company": self.company, "status": "Activa"},
			fields=["name", "ownership_percentage", "built_area_sqm", "property_type"],
		)

		total_income = 0
		for prop in properties:
			fee_calc = self.calculate_fee_for_property(prop["name"])  # REGLA #34: Dictionary access
			total_income += fee_calc["total_fee"]

		return flt(total_income, 2)

	def on_submit(self):
		"""Acciones al enviar la estructura"""
		# Desactivar otras estructuras activas si hay superposición
		self.deactivate_overlapping_structures()

		# Log de auditoría
		self.add_comment("Submitted", _("Estructura de cuotas enviada y activada"))

	def deactivate_overlapping_structures(self):
		"""Desactiva estructuras superpuestas al activar esta"""
		overlapping = frappe.get_all(
			"Fee Structure",
			filters={"company": self.company, "is_active": 1, "docstatus": 1, "name": ["!=", self.name]},
		)

		for structure in overlapping:
			doc = frappe.get_doc("Fee Structure", structure.name)
			doc.is_active = 0
			doc.save()
			doc.add_comment(
				"Info",
				_("Desactivada automáticamente por nueva estructura: {0}").format(self.fee_structure_name),
			)
