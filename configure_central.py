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
	print("[INFO] Categoría document_generation-template ya existe")

# 2. Registrar admin1.dev como site contribuyente real
if not frappe.db.exists("Registered Contributor Site", "https://admin1.dev"):
	admin_site = frappe.new_doc("Registered Contributor Site")
	admin_site.update(
		{
			"site_url": "https://admin1.dev",
			"company_name": "Administradora Buzola #1",
			"contact_email": "admin1@buzola.mx",
			"business_justification": "Site administradora real para testing cross-site contributions",
			"is_active": 1,
		}
	)
	admin_site.insert(ignore_permissions=True)
	print("✅ Site administradora registrado: https://admin1.dev")
	print("   Site real de administradora Buzola")
	print(f"   API Key: {admin_site.get_masked_api_key()}")
	print(f"   API Key completo (para testing): {admin_site.api_key}")
else:
	admin_site = frappe.get_doc("Registered Contributor Site", "https://admin1.dev")
	print("[INFO] Site administradora ya existe: https://admin1.dev")
	print(f"   API Key: {admin_site.get_masked_api_key()}")

# 3. Registrar condo1.dev como site condominio para testing adicional
if not frappe.db.exists("Registered Contributor Site", "https://condo1.dev"):
	condo_site = frappe.new_doc("Registered Contributor Site")
	condo_site.update(
		{
			"site_url": "https://condo1.dev",
			"company_name": "Condominio Torre Azul",
			"contact_email": "admin@torreazul.mx",
			"business_justification": "Site condominio para testing cross-site contributions",
			"is_active": 1,
		}
	)
	condo_site.insert(ignore_permissions=True)
	print("✅ Site condominio registrado: https://condo1.dev")
	print(f"   API Key: {condo_site.get_masked_api_key()}")
else:
	print("[INFO] Site condominio ya existe: https://condo1.dev")

frappe.db.commit()

print("\n🎯 ARQUITECTURA CONFIGURADA:")
print("=" * 50)
print("📍 DOMIKA.DEV = RECEPTOR CENTRAL (Matriz)")
print("   • Recibe contribuciones de administradoras y condominios")
print("   • Centraliza pool de templates universales")
print("   • Maneja review, aprobación e integración")
print("")
print("📍 ADMIN1.DEV = SITE ADMINISTRADORA REAL")
print("   • Site administradora Buzola registrado")
print("   • Enviará contribuciones a domika.dev")
print("   • Testing de flujo cross-site administradora → central")
print("")
print("📍 CONDO1.DEV = SITE CONDOMINIO")
print("   • Site condominio independiente registrado")
print("   • Puede enviar contribuciones específicas")
print("   • Testing de flujo cross-site condominio → central")
print("")
print("✅ domika.dev configurado como receptor central!")

# Mostrar estadísticas
print("\n📊 ESTADÍSTICAS:")
total_sites = frappe.db.count("Registered Contributor Site", {"is_active": 1})
total_categories = frappe.db.count("Contribution Category", {"is_active": 1})
print(f"   • Sites registrados activos: {total_sites}")
print(f"   • Categorías de contribución: {total_categories}")
print("   • APIs cross-site: Habilitadas")
print("")
print("🚀 ¡Sistema cross-site listo para testing!")
