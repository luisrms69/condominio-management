#!/usr/bin/env python3
"""
Demo completo del workflow de contribuciones Community Contributions.

Este script demuestra:
1. Creación de categoría de contribución
2. Envío de contribución desde administradora
3. Validación y preview
4. Workflow de aprobación
5. Export a fixtures
"""

import json
from datetime import datetime

import frappe


def demo_contribution_workflow():
	"""Ejecutar demo completo del workflow de contribuciones."""

	frappe.init("domika.dev")
	frappe.connect()
	frappe.set_user("Administrator")

	print("🎪 DEMO: Community Contributions Workflow")
	print("=" * 60)

	# Paso 1: Crear categoría de contribución
	print("\n📋 PASO 1: Creando categoría de contribución...")

	category_name = "Document Generation-Infrastructure Template"
	if frappe.db.exists("Contribution Category", category_name):
		print(f"✅ Categoría ya existe: {category_name}")
	else:
		category = frappe.new_doc("Contribution Category")
		category.update(
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
		category.insert()
		print(f"✅ Categoría creada: {category.name}")

	# Paso 2: Preparar datos de contribución de ejemplo
	print("\n🏗️ PASO 2: Preparando contribución de template 'Salón de Eventos'...")

	contribution_data = {
		"template_code": "EVENT_HALL",
		"template_name": "Salón de Eventos",
		"infrastructure_type": "Amenity",
		"description": "Template para configuración de salones de eventos en condominios",
		"fields": [
			{
				"field_name": "event_capacity",
				"field_label": "Capacidad del Evento",
				"field_type": "Int",
				"is_required": 1,
				"description": "Número máximo de personas para eventos",
			},
			{
				"field_name": "event_type",
				"field_label": "Tipo de Eventos Permitidos",
				"field_type": "Select",
				"field_options": "Bodas\nCumpleaños\nReuniones Corporativas\nFiestas Familiares",
				"is_required": 1,
			},
			{
				"field_name": "catering_allowed",
				"field_label": "Permite Catering Externo",
				"field_type": "Check",
				"default_value": "1",
			},
			{
				"field_name": "sound_system",
				"field_label": "Sistema de Sonido Incluido",
				"field_type": "Check",
				"default_value": "0",
			},
			{
				"field_name": "rental_rate",
				"field_label": "Tarifa de Renta por Hora",
				"field_type": "Float",
				"description": "Costo en MXN por hora de uso",
				"is_required": 1,
			},
		],
		"auto_assignment": {
			"entity_type": "Physical Space",
			"condition": "space_type == 'Event Hall'",
			"priority": 6,
		},
	}

	print(f"📊 Template: {contribution_data['template_name']}")
	print(f"📊 Código: {contribution_data['template_code']}")
	print(f"📊 Campos: {len(contribution_data['fields'])}")

	# Paso 3: Crear solicitud de contribución
	print("\n📤 PASO 3: Creando solicitud de contribución...")

	request = frappe.new_doc("Contribution Request")
	request.update(
		{
			"title": "Template Salón de Eventos para Condominios Premium",
			"contribution_category": category_name,
			"business_justification": "Múltiples condominios premium requieren gestión de salones de eventos. Este template estandarizará la configuración y simplificará el proceso de reservas para administradoras.",
			"contribution_data": json.dumps(contribution_data),
			"company": frappe.db.get_value("Company", filters={}, fieldname="name") or "Test Company",
		}
	)
	request.insert()

	print(f"✅ Solicitud creada: {request.name}")
	print(f"📊 Estado inicial: {request.status}")

	# Paso 4: Preview de la contribución
	print("\n🔍 PASO 4: Generando preview de la contribución...")

	preview = request.preview_contribution()

	print("📋 PREVIEW DEL TEMPLATE:")
	print(f"  • Código: {preview['template_info']['code']}")
	print(f"  • Nombre: {preview['template_info']['name']}")
	print(f"  • Tipo: {preview['template_info']['type']}")
	print(f"  • Campos definidos: {preview['field_count']}")

	print("\n📝 CAMPOS DEL TEMPLATE:")
	for field in preview["fields_preview"]:
		print(f"  • {field['label']} ({field['type']}) - Ejemplo: {field['sample_value']}")

	print(
		f"\n🤖 Auto-asignación: {'Habilitada' if preview['auto_assignment']['enabled'] else 'Deshabilitada'}"
	)
	if preview["auto_assignment"]["enabled"]:
		print(f"  • Condición: {preview['auto_assignment']['condition']}")
		print(f"  • Prioridad: {preview['auto_assignment']['priority']}")

	# Paso 5: Workflow de aprobación
	print("\n✅ PASO 5: Simulando workflow de aprobación...")

	# Enviar para revisión
	request.submit()
	print(f"📤 Contribución enviada. Estado: {request.status}")

	# Pasar a revisión
	request.status = "Under Review"
	request.save()
	print(f"🔍 En revisión. Estado: {request.status}")
	print(f"📅 Revisado por: {request.reviewed_by}")
	print(f"📅 Fecha de revisión: {request.review_date}")

	# Aprobar contribución
	request.status = "Approved"
	request.save()
	print(f"✅ Contribución aprobada. Estado: {request.status}")
	print(f"👤 Aprobado por: {request.approved_by}")
	print(f"📅 Fecha de aprobación: {request.approval_date}")

	# Paso 6: Export a fixtures
	print("\n📦 PASO 6: Exportando a formato fixtures...")

	exported_data = request.export_to_fixtures()

	print("🔧 ESTRUCTURA DEL FIXTURE GENERADO:")
	print(f"  • DocType destino: {exported_data['doctype']}")
	print(f"  • Templates incluidos: {len(exported_data['infrastructure_templates'])}")
	print(f"  • Reglas de auto-asignación: {len(exported_data['template_assignment_rules'])}")

	# Mostrar template exportado
	template = exported_data["infrastructure_templates"][0]
	print("\n📋 TEMPLATE EXPORTADO:")
	print(f"  • Código: {template['template_code']}")
	print(f"  • Nombre: {template['template_name']}")
	print(f"  • Campos: {len(template['template_fields'])}")
	print(f"  • Versión: {template['version']}")

	# Paso 7: Marcar como integrado
	print("\n🔄 PASO 7: Finalizando integración...")

	request.status = "Integrated"
	request.save()
	print(f"🎯 Contribución integrada. Estado final: {request.status}")
	print(f"📅 Fecha de integración: {request.integration_date}")

	# Resumen final
	print("\n" + "=" * 60)
	print("🎉 DEMO COMPLETADO EXITOSAMENTE")
	print("=" * 60)

	print("\n📊 RESUMEN:")
	print(f"✅ Categoría: {category_name}")
	print(f"✅ Contribución: {request.name}")
	print(f"✅ Template: {contribution_data['template_name']} ({contribution_data['template_code']})")
	print(f"✅ Estado final: {request.status}")
	print(f"✅ Campos configurados: {len(contribution_data['fields'])}")

	print("\n🔄 WORKFLOW DEMOSTRADO:")
	print("1. ✅ Creación de categoría de contribución")
	print("2. ✅ Desarrollo de template por administradora")
	print("3. ✅ Envío de solicitud de contribución")
	print("4. ✅ Preview y validación automática")
	print("5. ✅ Workflow de aprobación (Draft → Submitted → Under Review → Approved)")
	print("6. ✅ Export automático a formato fixtures")
	print("7. ✅ Integración final al sistema")

	print("\n🚀 PRÓXIMO PASO:")
	print("El JSON exportado estaría listo para:")
	print("• Integración a fixtures globales")
	print("• Distribución vía bench update a todos los sites")
	print("• Disponibilidad automática en condo1.dev, condo2.dev, etc.")

	frappe.db.commit()

	return {
		"category": category_name,
		"request": request.name,
		"template_code": contribution_data["template_code"],
		"exported_data": exported_data,
	}


if __name__ == "__main__":
	try:
		result = demo_contribution_workflow()
		print(f"\n✅ Demo ejecutado exitosamente. Contribución: {result['request']}")
	except Exception as e:
		print(f"\n❌ Error en demo: {e!s}")
		import traceback

		traceback.print_exc()
