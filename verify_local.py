#!/usr/bin/env python3

# Script para verificar DocTypes localmente usando SQL directo
import os
import subprocess


def run_sql_query(query):
	"""Ejecutar query SQL usando bench mariadb"""
	try:
		cmd = f'echo "{query}" | bench --site domika.dev mariadb'
		result = subprocess.run(
			cmd, shell=True, capture_output=True, text=True, cwd="/home/erpnext/frappe-bench"
		)
		return result.stdout.strip()
	except Exception as e:
		return f"Error: {e}"


print("=" * 60)
print("VERIFICACIÓN DE DOCTYPES EN INSTALACIÓN LOCAL")
print("=" * 60)

# 1. Verificar si existen DocTypes del módulo Companies
query1 = "SELECT COUNT(*) as count FROM `tabDocType` WHERE module = 'Companies';"
result1 = run_sql_query(query1)
print(f"DocTypes del módulo Companies: {result1}")

# 2. Listar DocTypes específicos del módulo Companies
query2 = "SELECT name FROM `tabDocType` WHERE module = 'Companies';"
result2 = run_sql_query(query2)
print(f"Lista de DocTypes:\n{result2}")

# 3. Verificar específicamente Access Point Detail
query3 = "SELECT name FROM `tabDocType` WHERE name = 'Access Point Detail';"
result3 = run_sql_query(query3)
print(f"Access Point Detail encontrado: {bool(result3.strip())}")

# 4. Verificar módulo Companies en Module Def
query4 = "SELECT name, app_name FROM `tabModule Def` WHERE name = 'Companies';"
result4 = run_sql_query(query4)
print(f"Módulo Companies:\n{result4}")

# 5. Verificar app condominium_management
query5 = "SELECT name FROM `tabModule Def` WHERE app_name = 'condominium_management';"
result5 = run_sql_query(query5)
print(f"Módulos de app condominium_management:\n{result5}")

# 5. Verificar archivos físicos
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
	for subdir in subdirs[:5]:  # Solo mostrar primeros 5
		print(f"  - {subdir}")
else:
	print("Directorio de DocTypes no encontrado")
