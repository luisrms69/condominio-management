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
		"""Hook antes de guardar - validaciones"""
		self.validate_property_fields()
		self.validate_copropiedades()
		self.calculate_copropiedades_total()
		self.validate_financial_fields()

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

	def validate_copropiedades(self):
		"""Validar configuración de copropiedades"""
		if not self.has_copropiedades:
			return

		if not self.copropiedades_table:
			frappe.throw(_("Debe agregar al menos una copropiedad"))

		# Validar porcentajes individuales
		for copropiedad in self.copropiedades_table:
			if copropiedad.copropiedad_percentage <= 0:
				frappe.throw(_("El porcentaje de copropiedad debe ser mayor a 0"))

			if copropiedad.copropiedad_percentage > 100:
				frappe.throw(_("El porcentaje de copropiedad no puede exceder 100%"))

			# Validar formato de identificación
			if not self.validate_owner_id(copropiedad.owner_id, copropiedad.owner_type):
				frappe.throw(_("Formato de identificación inválido para {0}").format(copropiedad.owner_name))

		# Validar que la suma de porcentajes sea 100%
		total_percentage = sum(float(c.copropiedad_percentage) for c in self.copropiedades_table)
		if abs(total_percentage - 100.0) > 0.01:  # Tolerancia para decimales
			frappe.throw(
				_("La suma de porcentajes de copropiedades debe ser exactamente 100%. Actual: {0}%").format(
					total_percentage
				)
			)

		# Validar propietarios únicos
		owner_ids = [c.owner_id for c in self.copropiedades_table]
		if len(owner_ids) != len(set(owner_ids)):
			frappe.throw(_("No puede haber propietarios duplicados en las copropiedades"))

	def calculate_copropiedades_total(self):
		"""Calcular total de porcentajes de copropiedades"""
		if self.has_copropiedades and self.copropiedades_table:
			self.total_copropiedades_percentage = sum(
				float(c.copropiedad_percentage) for c in self.copropiedades_table
			)
		else:
			self.total_copropiedades_percentage = 0

	def validate_financial_fields(self):
		"""Validar campos financieros"""
		if self.property_value and self.property_value < 0:
			frappe.throw(_("El valor de la propiedad no puede ser negativo"))

		if self.assessed_value and self.assessed_value < 0:
			frappe.throw(_("El avalúo catastral no puede ser negativo"))

		if self.monthly_tax and self.monthly_tax < 0:
			frappe.throw(_("El impuesto mensual no puede ser negativo"))

		if self.insurance_value and self.insurance_value < 0:
			frappe.throw(_("El valor asegurado no puede ser negativo"))

		# Validar vencimiento de seguro
		if self.insurance_expiry:
			from datetime import datetime

			if self.insurance_expiry < datetime.now().date():
				frappe.msgprint(_("La póliza de seguro está vencida"), alert=True)

	def validate_owner_id(self, owner_id, owner_type):
		"""Validar formato de identificación según tipo"""
		if owner_type == "Persona Natural":
			# Validar cédula colombiana (básico)
			return owner_id.isdigit() and len(owner_id) >= 6 and len(owner_id) <= 11
		elif owner_type == "Persona Jurídica":
			# Validar NIT colombiano (básico)
			return len(owner_id) >= 9 and len(owner_id) <= 11
		return False

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
		"""Obtener resumen de propiedad"""
		if not self.has_copropiedades:
			return "Propiedad única"

		if not self.copropiedades_table:
			return "Sin copropiedades definidas"

		owners_count = len(self.copropiedades_table)
		return f"Copropiedad - {owners_count} propietarios"

	def get_compliance_status(self):
		"""Obtener estado de cumplimiento"""
		compliance_items = [
			("Impuesto Predial", self.predial_tax_current),
			("Valorización", self.valorization_current),
			("Permisos", self.permits_status == "Vigente"),
			("Licencia Ambiental", self.environmental_clearance == "Vigente"),
			("Certificado Bomberos", self.fire_safety_certificate == "Vigente"),
		]

		compliant_count = sum(1 for _, status in compliance_items if status)
		total_count = len(compliance_items)

		if compliant_count == total_count:
			return "Completo"
		elif compliant_count >= total_count * 0.8:
			return "Parcial"
		else:
			return "Deficiente"

	def get_main_owner(self):
		"""Obtener propietario principal (mayor porcentaje)"""
		if not self.has_copropiedades or not self.copropiedades_table:
			return "N/A"

		main_owner = max(self.copropiedades_table, key=lambda x: x.copropiedad_percentage)
		return f"{main_owner.owner_name} ({main_owner.copropiedad_percentage}%)"

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
