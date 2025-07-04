#!/usr/bin/env python3
"""
Script para configurar categorías iniciales de contribución.
"""

import json

import frappe


def setup_initial_categories():
	"""Crear categorías iniciales de contribución."""

	# Conectar a la base de datos
	frappe.init(site="domika.dev")
	frappe.connect()

	# Configurar usuario
	frappe.set_user("Administrator")

	# Categoría para Document Generation
	doc_gen_category = frappe.new_doc("Contribution Category")
	doc_gen_category.update(
		{
			"module_name": "Document Generation",
			"contribution_type": "Infrastructure Template",
			"description": "Templates para configuración de infraestructura de condominios",
			"export_doctype": "Master Template Registry",
			"required_fields": json.dumps(
				["template_code", "template_name", "infrastructure_type", "fields"]
			),
			"validation_rules": "Template code debe ser único y seguir naming convention",
			"is_active": 1,
		}
	)

	try:
		doc_gen_category.insert()
		print(f"✅ Creada categoría: {doc_gen_category.name}")
	except Exception as e:
		if "already exists" in str(e).lower():
			print("⚠️ Categoría ya existe: Document Generation-Infrastructure Template")
		else:
			print(f"❌ Error creando categoría: {e}")

	# Categorías para módulos futuros (preparación)
	future_categories = [
		{
			"module_name": "Maintenance",
			"contribution_type": "Maintenance Routine",
			"description": "Rutinas de mantenimiento preventivo y correctivo",
			"export_doctype": "Maintenance Routine Template",
			"required_fields": ["routine_code", "routine_name", "frequency", "steps"],
		},
		{
			"module_name": "Contracts",
			"contribution_type": "Contract Template",
			"description": "Templates de contratos para servicios de condominio",
			"export_doctype": "Contract Template",
			"required_fields": ["contract_type", "template_name", "clauses"],
		},
	]

	for category_data in future_categories:
		category = frappe.new_doc("Contribution Category")
		category.update(
			{**category_data, "required_fields": json.dumps(category_data["required_fields"]), "is_active": 1}
		)

		try:
			category.insert()
			print(f"✅ Creada categoría: {category.name}")
		except Exception as e:
			if "already exists" in str(e).lower():
				print(
					f"⚠️ Categoría ya existe: {category_data['module_name']}-{category_data['contribution_type']}"
				)
			else:
				print(f"❌ Error creando categoría: {e}")

	# Commit cambios
	frappe.db.commit()
	print("\n🎉 Configuración de categorías completada")


if __name__ == "__main__":
	setup_initial_categories()
