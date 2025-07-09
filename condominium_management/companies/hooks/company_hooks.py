# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate_company_fields(doc, method):
	"""Validar campos personalizados de Company"""
	# Solo validar si los campos personalizados existen
	if not hasattr(doc, "company_type"):
		return

	validate_company_type_fields(doc)
	validate_management_fields(doc)
	validate_financial_fields(doc)
	validate_legal_fields(doc)


def validate_company_type_fields(doc):
	"""Validar campos específicos del tipo de empresa"""
	# Verificar que el campo company_type existe y es requerido
	if hasattr(doc, "company_type") and not doc.company_type:
		frappe.throw(_("El tipo de empresa es requerido"))
	elif not hasattr(doc, "company_type"):
		return

	if doc.company_type == "Condominio":
		# Validar campos requeridos para condominios
		if hasattr(doc, "property_usage_type") and not doc.property_usage_type:
			frappe.throw(_("El tipo de uso de propiedad es requerido para condominios"))

		if hasattr(doc, "total_units") and doc.total_units and doc.total_units <= 0:
			frappe.throw(_("El total de unidades debe ser mayor a 0"))

		if hasattr(doc, "total_area_sqm") and doc.total_area_sqm and doc.total_area_sqm <= 0:
			frappe.throw(_("El área total debe ser mayor a 0"))

		if hasattr(doc, "construction_year") and doc.construction_year:
			import datetime

			current_year = datetime.datetime.now().year
			if doc.construction_year < 1900 or doc.construction_year > current_year:
				frappe.throw(_("El año de construcción debe estar entre 1900 y {}").format(current_year))

		if hasattr(doc, "floors_count") and doc.floors_count and doc.floors_count <= 0:
			frappe.throw(_("El número de pisos debe ser mayor a 0"))

	elif doc.company_type == "Administradora":
		# Validar campos específicos para administradoras
		pass


def validate_management_fields(doc):
	"""Validar campos de administración"""
	if not hasattr(doc, "management_company") or not doc.management_company:
		return

	if doc.management_company:
		# Verificar que la empresa administradora existe y es del tipo correcto
		admin_company = frappe.get_doc("Company", doc.management_company)
		# Solo validar company_type si el campo existe
		if hasattr(admin_company, "company_type") and admin_company.company_type != "Administradora":
			frappe.throw(_("La empresa seleccionada debe ser de tipo 'Administradora'"))

		# Validar fechas de administración
		if (
			hasattr(doc, "management_start_date")
			and hasattr(doc, "management_contract_end_date")
			and doc.management_start_date
			and doc.management_contract_end_date
		):
			if doc.management_start_date >= doc.management_contract_end_date:
				frappe.throw(_("La fecha de inicio debe ser anterior a la fecha de fin del contrato"))


def validate_financial_fields(doc):
	"""Validar campos financieros"""
	if hasattr(doc, "monthly_admin_fee") and doc.monthly_admin_fee and doc.monthly_admin_fee < 0:
		frappe.throw(_("La cuota de administración mensual no puede ser negativa"))

	if hasattr(doc, "reserve_fund") and doc.reserve_fund and doc.reserve_fund < 0:
		frappe.throw(_("El fondo de reserva no puede ser negativo"))

	if hasattr(doc, "insurance_expiry_date") and doc.insurance_expiry_date:
		from datetime import datetime

		if doc.insurance_expiry_date < datetime.now().date():
			frappe.msgprint(_("La póliza de seguro está vencida"), alert=True)


def validate_legal_fields(doc):
	"""Validar campos legales"""
	if hasattr(doc, "legal_representative_id") and doc.legal_representative_id:
		# Validar formato de cédula colombiana (básico)
		if not doc.legal_representative_id.isdigit() or len(doc.legal_representative_id) < 6:
			frappe.throw(_("La cédula del representante legal debe tener al menos 6 dígitos numéricos"))


def update_managed_properties_count(doc, method):
	"""Actualizar contador de propiedades administradas"""
	if not hasattr(doc, "company_type") or not doc.company_type:
		return

	if doc.company_type == "Administradora":
		# Contar propiedades administradas por esta empresa
		managed_count = frappe.db.count(
			"Company", filters={"management_company": doc.name, "company_type": "Condominio"}
		)

		# Actualizar el campo sin disparar hooks para evitar recursión
		frappe.db.set_value("Company", doc.name, "managed_properties", managed_count, update_modified=False)


def on_company_save(doc, method):
	"""Hook después de guardar Company"""
	update_managed_properties_count(doc, method)

	# Si es un condominio con administradora, actualizar el contador de la administradora
	if (
		hasattr(doc, "company_type")
		and hasattr(doc, "management_company")
		and doc.company_type == "Condominio"
		and doc.management_company
	):
		admin_company = frappe.get_doc("Company", doc.management_company)
		update_managed_properties_count(admin_company, method)


def on_company_trash(doc, method):
	"""Hook antes de eliminar Company"""
	if not hasattr(doc, "company_type") or not doc.company_type:
		return

	# Si es administradora, verificar que no tenga propiedades administradas
	if doc.company_type == "Administradora":
		managed_count = frappe.db.count(
			"Company", filters={"management_company": doc.name, "company_type": "Condominio"}
		)

		if managed_count > 0:
			frappe.throw(
				_(
					"No se puede eliminar esta administradora porque tiene {} propiedades administradas"
				).format(managed_count)
			)

	# Si es condominio con administradora, actualizar el contador de la administradora
	if (
		hasattr(doc, "company_type")
		and hasattr(doc, "management_company")
		and doc.company_type == "Condominio"
		and doc.management_company
	):
		admin_company = frappe.get_doc("Company", doc.management_company)
		update_managed_properties_count(admin_company, method)
