#!/usr/bin/env python3

import frappe


def create_companies_module():
	"""Crear Module Def para Companies si no existe"""
	try:
		# Verificar si ya existe
		existing = frappe.get_doc("Module Def", "Companies")
		print(f"Module Def 'Companies' ya existe: {existing.name}")
		return True
	except frappe.DoesNotExistError:
		pass

	# Crear nuevo Module Def
	module_def = frappe.get_doc(
		{
			"doctype": "Module Def",
			"module_name": "Companies",
			"app_name": "condominium_management",
			"color": "blue",
			"icon": "octicon octicon-organization",
		}
	)

	try:
		module_def.insert()
		frappe.db.commit()
		print("✅ Module Def 'Companies' creado exitosamente")
		return True
	except Exception as e:
		print(f"❌ Error creando Module Def: {e}")
		frappe.db.rollback()
		return False


if __name__ == "__main__":
	create_companies_module()
