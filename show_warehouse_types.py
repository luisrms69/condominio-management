#!/usr/bin/env python3
"""Script simple para mostrar tipos de almacén disponibles."""

import frappe


def show_warehouse_types():
	"""Mostrar tipos de almacén en el sistema."""
	print("=== TIPOS DE ALMACÉN DISPONIBLES ===")

	try:
		warehouse_types = frappe.db.get_all("Warehouse Type", fields=["name"], order_by="name")

		if warehouse_types:
			print(f"Total encontrados: {len(warehouse_types)}")
			for wt in warehouse_types:
				print(f"  - {wt.name}")
		else:
			print("No se encontraron tipos de almacén")

	except Exception as e:
		print(f"Error: {e}")


if __name__ == "__main__":
	show_warehouse_types()
