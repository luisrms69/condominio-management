#!/usr/bin/env python3
"""
Script para asegurar que existen los tipos de almacén necesarios en ERPNext
Se ejecuta en CI antes de los tests para resolver el error de Transit
"""

import sys

import frappe


def ensure_warehouse_types():
	"""Crear tipos de almacén necesarios si no existen"""

	required_types = [
		{"name": "Transit", "description": "Transit Warehouse Type for ERPNext"},
		{"name": "Finished Goods", "description": "Finished Goods Warehouse Type"},
		{"name": "Work In Progress", "description": "Work In Progress Warehouse Type"},
		{"name": "Raw Material", "description": "Raw Material Warehouse Type"},
		{"name": "Stores", "description": "Stores Warehouse Type"},
	]

	created_count = 0
	existing_count = 0

	print("🏭 Verificando y creando tipos de almacén necesarios...")
	print("-" * 60)

	for wh_type in required_types:
		try:
			if not frappe.db.exists("Warehouse Type", wh_type["name"]):
				# Crear el tipo de almacén
				doc = frappe.get_doc(
					{
						"doctype": "Warehouse Type",
						"name": wh_type["name"],
						"description": wh_type["description"],
					}
				)
				doc.insert(ignore_permissions=True)
				print(f"  ✅ Creado: {wh_type['name']}")
				created_count += 1
			else:
				print(f"  ✓ Ya existe: {wh_type['name']}")
				existing_count += 1

		except Exception as e:
			print(f"  ❌ Error creando {wh_type['name']}: {e}")

	print("-" * 60)
	print(f"📊 Resumen: {existing_count} existentes, {created_count} creados")

	# Commit los cambios
	frappe.db.commit()

	return created_count + existing_count == len(required_types)


def main():
	"""Función principal para ejecutar desde CLI o CI"""
	try:
		# Este script se ejecutará en contexto de bench
		success = ensure_warehouse_types()

		if success:
			print("\n✅ Todos los tipos de almacén están disponibles")
			sys.exit(0)
		else:
			print("\n❌ No se pudieron crear todos los tipos de almacén")
			sys.exit(1)

	except Exception as e:
		print(f"\n💥 Error general: {e}")
		import traceback

		traceback.print_exc()
		sys.exit(1)


if __name__ == "__main__":
	main()
