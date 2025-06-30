#!/usr/bin/env python3
"""Script para debug de DocTypes en CI usando bench execute"""

import subprocess
import sys


def run_bench_command(command):
	"""Ejecutar comando bench y capturar output"""
	try:
		result = subprocess.run(
			["bench", "--site", "test_site", "execute", command],
			cwd="/home/runner/frappe-bench",
			capture_output=True,
			text=True,
			check=True,
		)
		return result.stdout.strip()
	except subprocess.CalledProcessError as e:
		sys.stderr.write(f"Error ejecutando: {command}\n")
		sys.stderr.write(f"Error: {e.stderr}\n")
		return None


def main():
	"""Función principal de debug"""
	commands = [
		# Verificar DocTypes del módulo Companies
		"frappe.get_all('DocType', filters={'module': 'Companies'}, fields=['name'])",
		# Verificar apps instaladas
		"frappe.get_installed_apps()",
		# Verificar módulos disponibles
		"frappe.get_all('Module Def', filters={'app_name': 'condominium_management'}, fields=['name'])",
	]

	results = {}
	for i, cmd in enumerate(commands):
		result = run_bench_command(cmd)
		if result:
			results[f"query_{i+1}"] = result

	# Mostrar resultados
	sys.stdout.write("=== DEBUG RESULTS ===\n")
	for key, value in results.items():
		sys.stdout.write(f"{key}: {value}\n")

	# Verificar archivos físicos
	import os

	doctype_dir = "/home/runner/work/condominio-management/condominio-management/condominium_management/companies/doctype"
	if os.path.exists(doctype_dir):
		subdirs = [d for d in os.listdir(doctype_dir) if not d.startswith("__")]
		sys.stdout.write(f"Physical DocTypes: {len(subdirs)}\n")
		for subdir in subdirs[:5]:  # Solo mostrar primeros 5
			sys.stdout.write(f"  - {subdir}\n")


if __name__ == "__main__":
	main()
