#!/usr/bin/env python3

import os

import frappe


def verify_module_setup():
	"""Verificar configuración completa del módulo Companies"""

	print("🔍 Verificando configuración del módulo Companies...")

	# 1. Verificar developer mode
	print(f"Developer Mode: {frappe.conf.get('developer_mode', 'Not enabled')}")

	# 2. Verificar app instalada
	installed_apps = frappe.get_installed_apps()
	print(f"App instalada: {'condominium_management' in installed_apps}")

	# 3. Verificar Module Def existe
	try:
		module_def = frappe.get_doc("Module Def", "Companies")
		print(f"Module Def existe: {module_def.name}")
		print(f"App asociada: {module_def.app_name}")
	except frappe.DoesNotExistError:
		print("❌ Module Def 'Companies' no existe")
		return False

	# 4. Verificar estructura de archivos
	app_path = frappe.get_app_path("condominium_management")
	companies_path = os.path.join(app_path, "companies")

	print(f"Ruta del módulo: {companies_path}")
	print(f"Módulo existe: {os.path.exists(companies_path)}")

	# 5. Verificar DocTypes del módulo
	doctypes = frappe.get_all(
		"DocType", filters={"module": "Companies", "app": "condominium_management"}, fields=["name", "custom"]
	)

	print(f"DocTypes encontrados: {len(doctypes)}")
	for dt in doctypes:
		print(f"  - {dt.name} (Custom: {dt.custom})")

	# 6. Verificar archivos de DocTypes
	doctype_path = os.path.join(companies_path, "doctype")
	if os.path.exists(doctype_path):
		print("Carpetas de DocTypes:")
		for item in os.listdir(doctype_path):
			item_path = os.path.join(doctype_path, item)
			if os.path.isdir(item_path):
				files = os.listdir(item_path)
				print(f"  - {item}: {files}")

	return True


if __name__ == "__main__":
	verify_module_setup()
