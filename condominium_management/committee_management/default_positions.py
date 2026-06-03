# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Cargos de comité por defecto para condominios.

Ejecutado en after_migrate y en el patch de migración.
Idempotente: solo agrega cargos que no existen — nunca modifica ni elimina.
"""

import frappe

DEFAULT_POSITIONS = [
	{
		"position_name": "Presidente",
		"hierarchy_level": 5,
		"responsibilities": "Representación legal del comité. Preside asambleas y reuniones. Firma documentos oficiales.",
		"can_approve_expenses": 1,
		"can_call_assembly": 1,
		"can_sign_documents": 1,
		"can_create_polls": 1,
	},
	{
		"position_name": "Vicepresidente",
		"hierarchy_level": 4,
		"responsibilities": "Suplente del Presidente. Apoya la gestión y representa al comité en ausencia del Presidente.",
		"can_approve_expenses": 1,
		"can_call_assembly": 1,
		"can_sign_documents": 1,
		"can_create_polls": 1,
	},
	{
		"position_name": "Secretario",
		"hierarchy_level": 3,
		"responsibilities": "Redacción y custodia de actas. Convocatoria de reuniones. Correspondencia oficial.",
		"can_approve_expenses": 0,
		"can_call_assembly": 1,
		"can_sign_documents": 1,
		"can_create_polls": 1,
	},
	{
		"position_name": "Tesorero",
		"hierarchy_level": 3,
		"responsibilities": "Administración de fondos. Cobro de cuotas. Rendición de cuentas al comité.",
		"can_approve_expenses": 1,
		"can_call_assembly": 0,
		"can_sign_documents": 1,
		"can_create_polls": 1,
	},
	{
		"position_name": "Síndico",
		"hierarchy_level": 2,
		"responsibilities": "Supervisión del manejo financiero. Revisión de cuentas. Vigilancia del cumplimiento del reglamento.",
		"can_approve_expenses": 0,
		"can_call_assembly": 0,
		"can_sign_documents": 0,
		"can_create_polls": 1,
	},
	{
		"position_name": "Vocal",
		"hierarchy_level": 1,
		"responsibilities": "Participación en sesiones. Comisiones de trabajo asignadas por el comité.",
		"can_approve_expenses": 0,
		"can_call_assembly": 0,
		"can_sign_documents": 0,
		"can_create_polls": 1,
	},
]


def setup_positions_for_all_condo_companies():
	"""Crea cargos por defecto para todos los condominios registrados.

	Solo añade cargos que no existen. No modifica ni elimina existentes.
	Idempotente — seguro de llamar múltiples veces.
	"""
	# company_type is a custom field added via fixtures.
	# On fresh installs, the column may not exist yet when after_migrate runs.
	if not frappe.db.has_column("Company", "company_type"):
		return

	condo_companies = frappe.get_all(
		"Company",
		filters={"company_type": "CONDO"},
		pluck="name",
	)

	if not condo_companies:
		return

	created_total = 0
	for company in condo_companies:
		created = _create_missing_positions(company)
		created_total += len(created)

	if created_total:
		frappe.db.commit()


def setup_positions_for_company(company):
	"""Crea cargos por defecto para un condominio específico.

	Llamado automáticamente cuando se crea una nueva Company de tipo CONDO.
	"""
	created = _create_missing_positions(company)
	if created:
		frappe.db.commit()
	return created


def _create_missing_positions(company):
	"""Crea los cargos que no existen para la company dada."""
	created = []
	for pos in DEFAULT_POSITIONS:
		name = f"{company}::{pos['position_name']}"
		if frappe.db.exists("Committee Position", name):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Committee Position",
				"company": company,
				**pos,
			}
		)
		doc.insert(ignore_permissions=True)
		created.append(pos["position_name"])
	return created
