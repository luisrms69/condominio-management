#!/usr/bin/env python3
import os
import sys

# Configurar paths para Frappe
bench_path = "/home/erpnext/frappe-bench"
sys.path.insert(0, os.path.join(bench_path, "apps", "frappe"))
sys.path.insert(0, os.path.join(bench_path, "apps", "condominium_management"))
sys.path.insert(0, bench_path)

import frappe


def diagnose_doctypes():
	# Inicializar Frappe
	frappe.init(site="localhost")
	frappe.connect()

	try:
		# Verificar DocTypes existentes
		existing_doctypes = frappe.get_all(
			"DocType", filters={"module": "Companies"}, fields=["name", "module"]
		)

		print("DocTypes encontrados:")
		for dt in existing_doctypes:
			print(f"- {dt['name']} (Módulo: {dt['module']})")

		if not existing_doctypes:
			print("No se encontraron DocTypes en el módulo Companies")

		# Verificar la estructura del módulo
		app_path = frappe.get_app_path("condominium_management")
		companies_path = os.path.join(app_path, "companies", "doctype")

		print("\nEstructura de DocTypes en el sistema de archivos:")
		for root, _dirs, files in os.walk(companies_path):
			for file in files:
				if file.endswith(".json"):
					print(os.path.join(root, file))

	except Exception as e:
		print(f"Error durante el diagnóstico: {e}")
	finally:
		frappe.destroy()


if __name__ == "__main__":
	diagnose_doctypes()
