#!/usr/bin/env python3
"""
Script de diagnóstico para revisar tipos de almacén en ERPNext
Identifica qué tipos están instalados y sus nombres exactos
"""

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

	print("=" * 70)
	print("DIAGNÓSTICO DE TIPOS DE ALMACÉN EN ERPNEXT")
	print("=" * 70)

	# 1. Verificar todos los tipos de almacén disponibles
	def check_warehouse_types():
		"""Verificar tipos de almacén en el sistema"""
		print("\n🏭 TIPOS DE ALMACÉN INSTALADOS:")
		print("-" * 50)

		try:
			warehouse_types = frappe.db.get_all("Warehouse Type", fields=["name", "type"], order_by="name")

			if warehouse_types:
				print(f"Total tipos encontrados: {len(warehouse_types)}")
				for wt in warehouse_types:
					print(f"  ✓ {wt.name} (tipo: {wt.get('type', 'N/A')})")
			else:
				print("  ❌ NO se encontraron tipos de almacén")

		except Exception as e:
			print(f"  ❌ Error consultando Warehouse Type: {e}")

		return warehouse_types if "warehouse_types" in locals() else []

	# 2. Verificar tipos específicos que busca ERPNext
	def check_specific_warehouse_types():
		"""Verificar tipos específicos que ERPNext necesita"""
		print("\n🎯 VERIFICACIÓN DE TIPOS ESPECÍFICOS:")
		print("-" * 50)

		required_types = ["Transit", "Finished Goods", "Work In Progress", "Raw Material", "Stores"]

		for req_type in required_types:
			try:
				exists = frappe.db.exists("Warehouse Type", req_type)
				status = "✓" if exists else "❌"
				print(f"  {status} {req_type}: {'ENCONTRADO' if exists else 'NO ENCONTRADO'}")
			except Exception as e:
				print(f"  ❌ {req_type}: Error - {e}")

	# 3. Verificar almacenes existentes
	def check_warehouses():
		"""Verificar almacenes en el sistema"""
		print("\n📦 ALMACENES EXISTENTES:")
		print("-" * 50)

		try:
			warehouses = frappe.db.get_all(
				"Warehouse", fields=["name", "warehouse_type", "company"], limit=10, order_by="name"
			)

			if warehouses:
				print(f"Total almacenes (primeros 10): {len(warehouses)}")
				for wh in warehouses:
					wh_type = wh.get("warehouse_type", "Sin tipo")
					company = wh.get("company", "Sin empresa")
					print(f"  📦 {wh.name}")
					print(f"     Tipo: {wh_type}")
					print(f"     Empresa: {company}")
					print()
			else:
				print("  ❌ NO se encontraron almacenes")

		except Exception as e:
			print(f"  ❌ Error consultando Warehouse: {e}")

	# 4. Verificar configuración de ERPNext
	def check_erpnext_setup():
		"""Verificar configuración de ERPNext"""
		print("\n⚙️ CONFIGURACIÓN DE ERPNEXT:")
		print("-" * 50)

		try:
			# Verificar si ERPNext está instalado
			installed_apps = frappe.get_installed_apps()
			erpnext_installed = "erpnext" in installed_apps
			print(f"  ERPNext instalado: {'✓ SÍ' if erpnext_installed else '❌ NO'}")

			# Verificar setup completo
			if erpnext_installed:
				try:
					global_defaults = frappe.db.get_single_value("Global Defaults", "default_company")
					print(f"  Empresa por defecto: {global_defaults or 'No configurada'}")
				except Exception:
					print("  Empresa por defecto: No disponible")

				# Verificar si hay empresas
				companies = frappe.db.count("Company")
				print(f"  Total empresas: {companies}")

		except Exception as e:
			print(f"  ❌ Error verificando ERPNext: {e}")

	# 5. Verificar traducciones de tipos de almacén
	def check_warehouse_translations():
		"""Verificar si hay problemas de traducción"""
		print("\n🌐 VERIFICACIÓN DE TRADUCCIONES:")
		print("-" * 50)

		# Tipos en inglés vs posibles traducciones
		translations = {
			"Transit": ["Tránsito", "Transito", "En Tránsito"],
			"Finished Goods": ["Productos Terminados", "Productos Acabados"],
			"Work In Progress": ["Trabajo en Proceso", "En Proceso"],
			"Raw Material": ["Material Prima", "Materia Prima"],
			"Stores": ["Almacenes", "Tiendas"],
		}

		for english, spanish_variants in translations.items():
			print(f"\n  Buscando '{english}':")

			# Buscar en inglés
			exists_en = frappe.db.exists("Warehouse Type", english)
			print(f"    En inglés: {'✓' if exists_en else '❌'} {english}")

			# Buscar variantes en español
			for variant in spanish_variants:
				exists_es = frappe.db.exists("Warehouse Type", variant)
				if exists_es:
					print(f"    En español: ✓ {variant}")

	# Ejecutar todos los diagnósticos
	warehouse_types = check_warehouse_types()
	check_specific_warehouse_types()
	check_warehouses()
	check_erpnext_setup()
	check_warehouse_translations()

	# 6. Resumen y recomendaciones
	print("\n" + "=" * 70)
	print("RESUMEN Y RECOMENDACIONES")
	print("=" * 70)

	if not warehouse_types:
		print("\n🚨 PROBLEMA CRÍTICO:")
		print("   No se encontraron tipos de almacén en el sistema")
		print("   Esto indica una instalación incompleta de ERPNext")
		print("\n💡 SOLUCIÓN RECOMENDADA:")
		print("   Ejecutar: bench --site domika.dev execute erpnext.setup.install.after_install")
	else:
		print(f"\n✅ ESTADO: Se encontraron {len(warehouse_types)} tipos de almacén")
		transit_exists = any(wt.name == "Transit" for wt in warehouse_types)
		if not transit_exists:
			print("\n⚠️  PROBLEMA ESPECÍFICO:")
			print("   El tipo 'Transit' no existe, pero otros tipos sí")
			print("   Esto puede indicar instalación parcial o problema de traducción")

	frappe.destroy()

except Exception as e:
	print(f"ERROR GENERAL: {e}")
	import traceback

	traceback.print_exc()
