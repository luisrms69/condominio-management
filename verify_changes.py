#!/usr/bin/env python3

import frappe


def verify_changes():
	"""Verificar que todos los cambios se aplicaron correctamente"""

	print("🔍 Verificando cambios aplicados en domika.dev...")
	print("=" * 60)

	# 1. Verificar módulo Companies
	try:
		module_def = frappe.get_doc("Module Def", "Companies")
		print("✅ Module Def 'Companies' existe")
		print(f"   App: {module_def.app_name}")
	except frappe.DoesNotExistError:
		print("❌ Module Def 'Companies' no encontrado")
		return

	# 2. Verificar DocTypes del módulo
	doctypes = frappe.get_all(
		"DocType",
		filters={"module": "Companies", "app": "condominium_management"},
		fields=["name", "custom", "label"],
	)

	print(f"\n📋 DocTypes encontrados: {len(doctypes)}")
	print("-" * 40)

	expected_doctypes = [
		"Service Management Contract",
		"Condominium Information",
		"Master Data Sync Configuration",
		"Access Point Detail",
		"Contact Information",
		"Contract Service Item",
		"Nearby Reference",
		"Operating Hours",
		"Public Transport Option",
		"Service Information",
		"Sync Data Type",
		"Target Company Sync",
	]

	found_names = [dt.name for dt in doctypes]

	for expected in expected_doctypes:
		if expected in found_names:
			dt = next(dt for dt in doctypes if dt.name == expected)
			label = dt.get("label", "Sin label")
			print(f"   ✅ {expected}")
			if label and label != "Sin label":
				print(f"      📱 Label: {label}")
		else:
			print(f"   ❌ {expected} - NO ENCONTRADO")

	# 3. Verificar campos específicos modificados
	print("\n🔧 Verificando campos modificados...")
	print("-" * 40)

	# Verificar Nearby Reference - distance field
	try:
		meta = frappe.get_meta("Nearby Reference")
		distance_field = meta.get_field("distance")
		if distance_field:
			print("   ✅ Nearby Reference - distance:")
			print(f"      Tipo: {distance_field.fieldtype}")
			if hasattr(distance_field, "options"):
				print(f"      Opciones: {distance_field.options}")
		else:
			print("   ❌ Nearby Reference - campo distance no encontrado")
	except Exception as e:
		print(f"   ❌ Error verificando Nearby Reference: {e}")

	# Verificar Access Point Detail - nuevos campos
	try:
		meta = frappe.get_meta("Access Point Detail")
		new_fields = [
			"who_can_access",
			"access_vehicle_type",
			"opening_time",
			"closing_time",
			"operating_days",
		]

		print("   ✅ Access Point Detail - campos nuevos:")
		for field_name in new_fields:
			field = meta.get_field(field_name)
			if field:
				print(f"      ✅ {field_name}: {field.fieldtype}")
				if hasattr(field, "options") and field.options:
					print(f"         Opciones: {field.options[:50]}...")
			else:
				print(f"      ❌ {field_name}: NO ENCONTRADO")

	except Exception as e:
		print(f"   ❌ Error verificando Access Point Detail: {e}")

	# Verificar Condominium Information - campos modificados
	try:
		meta = frappe.get_meta("Condominium Information")

		# Verificar que se eliminó pestaña Contacto y Servicios
		tab_fields = [f for f in meta.fields if f.fieldtype == "Tab Break"]
		tab_labels = [f.label for f in tab_fields if f.label]

		print("   ✅ Condominium Information - pestañas:")
		for label in tab_labels:
			print(f"      📑 {label}")

		if "Contacto y Servicios" in tab_labels:
			print("      ❌ Pestaña 'Contacto y Servicios' aún existe (debería eliminarse)")
		else:
			print("      ✅ Pestaña 'Contacto y Servicios' eliminada correctamente")

		# Verificar campo GPS coordinates
		gps_field = meta.get_field("gps_coordinates")
		if gps_field:
			print(f"      ✅ Campo gps_coordinates agregado: {gps_field.fieldtype}")
		else:
			print("      ❌ Campo gps_coordinates no encontrado")

	except Exception as e:
		print(f"   ❌ Error verificando Condominium Information: {e}")

	print("\n🎯 Verificación completada")
	print("=" * 60)


if __name__ == "__main__":
	verify_changes()
