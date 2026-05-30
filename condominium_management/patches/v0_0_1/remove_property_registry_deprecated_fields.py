import frappe


def execute():
	"""Eliminar columnas obsoletas de tabProperty Registry.

	Motivo: Property Registry representa una unidad privativa.
	Los campos de dirección externa, compliance, seguros y financieros
	pertenecen al edificio/Company, no a cada unidad.
	has_copropiedades fue reemplazado por la lógica de is_current en la tabla de titulares.
	"""
	doctype = "Property Registry"
	table = "tabProperty Registry"

	columns_to_drop = [
		# Dirección externa — pertenece al condominio (Company), no a la unidad
		"property_address",
		"neighborhood",
		"city",
		"department",
		"postal_code",
		# Compliance / permisos — nivel edificio
		"predial_tax_current",
		"valorization_current",
		"last_inspection_date",
		"permits_status",
		"environmental_clearance",
		"fire_safety_certificate",
		# Financiero / seguros / avalúos — nivel edificio o expediente fiscal
		"property_value",
		"assessed_value",
		"monthly_tax",
		"insurance_policy",
		"insurance_value",
		"insurance_expiry",
		# Flag redundante — reemplazado por is_current en declared_owners
		"has_copropiedades",
	]

	for col in columns_to_drop:
		if frappe.db.has_column(doctype, col):
			frappe.db.sql(f"ALTER TABLE `{table}` DROP COLUMN `{col}`")

	frappe.db.commit()
