import frappe


def execute():
	"""Crear cargos de comité por defecto para todos los condominios.

	Idempotente: solo añade los que no existen, no modifica ni elimina.
	"""
	from condominium_management.committee_management.default_positions import (
		setup_positions_for_all_condo_companies,
	)

	setup_positions_for_all_condo_companies()
