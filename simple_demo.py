import json

import frappe

# Demo simplificado del workflow de contribuciones
print("🎪 DEMO: Community Contributions Workflow")
print("=" * 60)

# Paso 1: Crear categoría si no existe
category_name = "Document Generation-Infrastructure Template"
if not frappe.db.exists("Contribution Category", category_name):
	category = frappe.new_doc("Contribution Category")
	category.update(
		{
			"module_name": "Document Generation",
			"contribution_type": "Infrastructure Template",
			"description": "Templates para configuración de infraestructura",
			"export_doctype": "Master Template Registry",
			"required_fields": json.dumps(["template_code", "template_name", "infrastructure_type"]),
			"is_active": 1,
		}
	)
	category.insert()
	print(f"✅ Categoría creada: {category.name}")
else:
	print(f"✅ Categoría existe: {category_name}")

# Paso 2: Crear solicitud de contribución
contribution_data = {
	"template_code": "EVENT_HALL",
	"template_name": "Salón de Eventos",
	"infrastructure_type": "Amenity",
	"description": "Template para salones de eventos",
	"fields": [
		{"field_name": "event_capacity", "field_label": "Capacidad", "field_type": "Int", "is_required": 1},
		{
			"field_name": "rental_rate",
			"field_label": "Tarifa por Hora",
			"field_type": "Float",
			"is_required": 1,
		},
	],
}

# Buscar compañía existente
company = frappe.db.get_value("Company", filters={}, fieldname="name")
if not company:
	print("❌ No se encontró ninguna compañía")
	company = "Test Company"

request = frappe.new_doc("Contribution Request")
request.update(
	{
		"title": "Template Salón de Eventos",
		"contribution_category": category_name,
		"business_justification": "Template requerido para condominios premium",
		"contribution_data": json.dumps(contribution_data),
		"company": company,
	}
)
request.insert()

print(f"✅ Solicitud creada: {request.name}")
print(f"📊 Estado: {request.status}")

# Paso 3: Preview
preview = request.preview_contribution()
print("\n🔍 PREVIEW:")
print(f"• Template: {preview['template_info']['name']}")
print(f"• Campos: {preview['field_count']}")

# Paso 4: Workflow de aprobación
request.submit()
print(f"\n✅ Enviado: {request.status}")

request.status = "Under Review"
request.save()
print(f"🔍 En revisión: {request.status}")

request.status = "Approved"
request.save()
print(f"✅ Aprobado: {request.status}")

# Paso 5: Export
exported = request.export_to_fixtures()
print("\n📦 EXPORTADO:")
print(f"• DocType: {exported['doctype']}")
print(f"• Templates: {len(exported['infrastructure_templates'])}")

request.status = "Integrated"
request.save()
print(f"\n🎯 FINALIZADO: {request.status}")

frappe.db.commit()

print("\n" + "=" * 60)
print("🎉 DEMO COMPLETADO EXITOSAMENTE")
print("✅ Framework Community Contributions funcional")
print("✅ Workflow de aprobación completo")
print("✅ Export a fixtures automático")
print("=" * 60)
