#!/usr/bin/env python3
"""Script para debug de DocTypes en CI"""

import os
import sys

# Agregar el path de frappe
sys.path.insert(0, "/home/runner/frappe-bench/apps/frappe")
sys.path.insert(0, "/home/runner/frappe-bench/apps/erpnext")
sys.path.insert(0, "/home/runner/frappe-bench/apps/condominium_management")

try:
	import frappe

	frappe.init(site="test_site")
	frappe.connect()

	print("=" * 50)
	print("DEBUG: DocTypes en base de datos")
	print("=" * 50)

	# Listar todos los DocTypes
	all_doctypes = frappe.get_all("DocType", fields=["name", "module"])
	print(f"Total DocTypes encontrados: {len(all_doctypes)}")

	# Filtrar por módulo Companies
	companies_doctypes = [d for d in all_doctypes if d.module == "Companies"]
	print(f"DocTypes del módulo Companies: {len(companies_doctypes)}")

	for dt in companies_doctypes:
		print(f"  - {dt.name}")

	print("\n" + "=" * 50)
	print("DEBUG: Archivos físicos en el directorio")
	print("=" * 50)

	doctype_dir = "/home/runner/work/condominio-management/condominio-management/condominium_management/companies/doctype"
	if os.path.exists(doctype_dir):
		subdirs = [
			d
			for d in os.listdir(doctype_dir)
			if os.path.isdir(os.path.join(doctype_dir, d)) and not d.startswith("__")
		]
		print(f"Directorios de DocTypes físicos: {len(subdirs)}")
		for subdir in subdirs:
			json_file = os.path.join(doctype_dir, subdir, f"{subdir}.json")
			exists = "✓" if os.path.exists(json_file) else "✗"
			print(f"  {exists} {subdir}")
	else:
		print("ERROR: Directorio de DocTypes no encontrado")

	print("\n" + "=" * 50)
	print("DEBUG: Apps instaladas")
	print("=" * 50)

	installed_apps = frappe.get_installed_apps()
	print(f"Apps instaladas: {installed_apps}")

	if "condominium_management" in installed_apps:
		print("✓ condominium_management está instalado")
	else:
		print("✗ condominium_management NO está instalado")

	print("\n" + "=" * 50)
	print("DEBUG: Módulos disponibles")
	print("=" * 50)

	modules = frappe.get_all("Module Def", fields=["name", "app_name"])
	condominium_modules = [m for m in modules if m.app_name == "condominium_management"]
	print(f"Módulos de condominium_management: {len(condominium_modules)}")
	for mod in condominium_modules:
		print(f"  - {mod.name}")

	frappe.destroy()

except Exception as e:
	print(f"ERROR en debug: {e}")
	import traceback

	traceback.print_exc()
	sys.exit(1)
