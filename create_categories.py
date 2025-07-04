import json

import frappe

# Categoría para Document Generation
doc_gen_category = frappe.new_doc("Contribution Category")
doc_gen_category.update(
	{
		"module_name": "Document Generation",
		"contribution_type": "Infrastructure Template",
		"description": "Templates para configuración de infraestructura de condominios",
		"export_doctype": "Master Template Registry",
		"required_fields": json.dumps(["template_code", "template_name", "infrastructure_type", "fields"]),
		"validation_rules": "Template code debe ser único y seguir naming convention",
		"is_active": 1,
	}
)

try:
	doc_gen_category.insert()
	print(f"✅ Creada categoría: {doc_gen_category.name}")
except Exception as e:
	print(f"Error: {e}")

frappe.db.commit()
print("Categoría creada exitosamente")
