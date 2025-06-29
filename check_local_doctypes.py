#!/usr/bin/env python3
"""Verificar DocTypes en instalación local"""

import os
import sys

# Cambiar al directorio bench
os.chdir("/home/erpnext/frappe-bench")

# Agregar paths
sys.path.insert(0, "/home/erpnext/frappe-bench/apps/frappe")
sys.path.insert(0, "/home/erpnext/frappe-bench/apps/erpnext")
sys.path.insert(0, "/home/erpnext/frappe-bench/apps/condominium_management")

try:
	import frappe

	frappe.init(site="domika.dev")
	frappe.connect()

	print("=" * 60)
	print("VERIFICACIÓN DE DOCTYPES EN INSTALACIÓN LOCAL")
	print("=" * 60)

	# 1. Verificar si condominium_management está instalado
	installed_apps = frappe.get_installed_apps()
	print(f"Apps instaladas: {installed_apps}")
	print(f"condominium_management instalado: {'condominium_management' in installed_apps}")

	# 2. Verificar DocTypes del módulo Companies
	companies_doctypes = frappe.db.get_all(
		"DocType", filters={"module": "Companies"}, fields=["name", "module"]
	)
	print(f"\nDocTypes del módulo Companies en BD: {len(companies_doctypes)}")
	for dt in companies_doctypes:
		print(f"  - {dt.name}")

	# 3. Verificar archivos físicos
	doctype_dir = (
		"/home/erpnext/frappe-bench/apps/condominium_management/condominium_management/companies/doctype"
	)
	if os.path.exists(doctype_dir):
		subdirs = [
			d
			for d in os.listdir(doctype_dir)
			if os.path.isdir(os.path.join(doctype_dir, d)) and not d.startswith("__")
		]
		print(f"\nArchivos físicos DocTypes: {len(subdirs)}")
		for subdir in subdirs:
			json_file = os.path.join(doctype_dir, subdir, f"{subdir}.json")
			exists = "✓" if os.path.exists(json_file) else "✗"
			print(f"  {exists} {subdir}")

	# 4. Verificar módulos de la app
	modules = frappe.db.get_all(
		"Module Def", filters={"app_name": "condominium_management"}, fields=["name", "app_name"]
	)
	print(f"\nMódulos de condominium_management: {len(modules)}")
	for mod in modules:
		print(f"  - {mod.name}")

	# 5. Intentar acceder específicamente a Access Point Detail
	try:
		access_point = frappe.get_meta("Access Point Detail")
		print(f"\n✓ Access Point Detail ENCONTRADO: {access_point.name}")
	except frappe.DoesNotExistError:
		print("\n✗ Access Point Detail NO ENCONTRADO")

	frappe.destroy()

except Exception as e:
	print(f"ERROR: {e}")
	import traceback

	traceback.print_exc()
