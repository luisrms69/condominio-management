#!/usr/bin/env python3
"""
Script de configuración para ejecutar desde console de frappe.
"""

import json

import frappe

# Establecer usuario
frappe.set_user("Administrator")

print("🚀 Configurando domika.dev como receptor central...")

# 1. Crear categoría de contribución para document_generation
if not frappe.db.exists("Contribution Category", "document_generation-template"):
	category = frappe.new_doc("Contribution Category")
	category.update(
		{
			"name": "document_generation-template",
			"module_name": "Document Generation",
			"contribution_type": "template",
			"description": "Contribuciones de templates de generación de documentos",
			"is_active": 1,
			"required_fields": json.dumps(
				["template_code", "template_description", "infrastructure_templates"]
			),
		}
	)
	category.insert(ignore_permissions=True)
	print("✅ Categoría document_generation-template creada")
else:
	print("ℹ️ Categoría document_generation-template ya existe")

# 2. Crear site de prueba admin1.test.com para simular admin1.dev
if not frappe.db.exists("Registered Contributor Site", "https://admin1.test.com"):
	test_site = frappe.new_doc("Registered Contributor Site")
	test_site.update(
		{
			"site_url": "https://admin1.test.com",
			"company_name": "Test Administradora #1",
			"contact_email": "admin1@test.com",
			"business_justification": "Site de prueba para testing cross-site representando admin1.dev",
			"is_active": 1,
		}
	)
	test_site.insert(ignore_permissions=True)
	print(f"✅ Site de prueba creado: https://admin1.test.com")
	print(f"   Representa: admin1.dev (administradora real)")
	print(f"   API Key: {test_site.get_masked_api_key()}")
	print(f"   API Key completo (para testing): {test_site.api_key}")
else:
	test_site = frappe.get_doc("Registered Contributor Site", "https://admin1.test.com")
	print(f"ℹ️ Site de prueba ya existe: https://admin1.test.com")
	print(f"   API Key: {test_site.get_masked_api_key()}")

# 3. Crear site adicional para admin2 si es necesario
if not frappe.db.exists("Registered Contributor Site", "https://admin2.test.com"):
	test_site2 = frappe.new_doc("Registered Contributor Site")
	test_site2.update(
		{
			"site_url": "https://admin2.test.com",
			"company_name": "Test Administradora #2",
			"contact_email": "admin2@test.com",
			"business_justification": "Site de prueba adicional para testing cross-site",
			"is_active": 1,
		}
	)
	test_site2.insert(ignore_permissions=True)
	print(f"✅ Site de prueba #2 creado: https://admin2.test.com")
	print(f"   API Key: {test_site2.get_masked_api_key()}")
else:
	print("ℹ️ Site de prueba #2 ya existe: https://admin2.test.com")

frappe.db.commit()

print("\n🎯 ARQUITECTURA CONFIGURADA:")
print("=" * 50)
print("📍 DOMIKA.DEV = RECEPTOR CENTRAL (Matriz)")
print("   • Recibe contribuciones de administradoras")
print("   • Centraliza pool de templates universales")
print("   • Maneja review, aprobación e integración")
print("")
print("📍 ADMIN1.TEST.COM = SIMULACIÓN DE ADMIN1.DEV")
print("   • Representa site administradora real")
print("   • Enviará contribuciones a domika.dev")
print("   • Testing de flujo cross-site")
print("")
print("✅ domika.dev configurado como receptor central!")

# Mostrar estadísticas
print(f"\n📊 ESTADÍSTICAS:")
total_sites = frappe.db.count("Registered Contributor Site", {"is_active": 1})
total_categories = frappe.db.count("Contribution Category", {"is_active": 1})
print(f"   • Sites registrados activos: {total_sites}")
print(f"   • Categorías de contribución: {total_categories}")
print(f"   • APIs cross-site: Habilitadas")
print("")
print("🚀 ¡Sistema cross-site listo para testing!")
