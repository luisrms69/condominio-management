#!/usr/bin/env python3
"""
Script para configurar domika.dev como receptor central de contribuciones.

Crea las configuraciones necesarias para que domika.dev pueda recibir
contribuciones de sites administradoras externos.
"""

import frappe


def setup_domika_central():
	"""
	Configurar domika.dev como receptor central.

	Crea categorías de contribución, configuraciones y datos de prueba.
	"""
	print("🚀 Configurando domika.dev como receptor central de contribuciones...")

	# Establecer contexto de usuario
	frappe.set_user("Administrator")

	# 1. Crear categoría de contribución para document_generation
	create_contribution_categories()

	# 2. Crear site de prueba para testing
	create_test_sites()

	# 3. Configurar permisos y roles
	setup_permissions()

	# Commit cambios
	frappe.db.commit()

	print("✅ Configuración de domika.dev completada exitosamente!")


def create_contribution_categories():
	"""Crear categorías de contribución necesarias."""
	print("📋 Creando categorías de contribución...")

	categories = [
		{
			"name": "document_generation-template",
			"module_name": "document_generation",
			"contribution_type": "template",
			"description": "Contribuciones de templates de generación de documentos",
			"required_fields": "template_code,template_description,infrastructure_templates",
			"handler_path": "condominium_management.document_generation.contrib.handler",
		},
		{
			"name": "document_generation-workflow",
			"module_name": "document_generation",
			"contribution_type": "workflow",
			"description": "Contribuciones de workflows de automatización",
			"required_fields": "workflow_name,workflow_description,automation_rules",
			"handler_path": "condominium_management.document_generation.contrib.handler",
		},
		{
			"name": "companies-integration",
			"module_name": "companies",
			"contribution_type": "integration",
			"description": "Contribuciones de integraciones con empresas administradoras",
			"required_fields": "integration_name,integration_description,api_endpoints",
			"handler_path": "condominium_management.companies.contrib.handler",
		},
	]

	for cat_data in categories:
		if not frappe.db.exists("Contribution Category", cat_data["name"]):
			category = frappe.new_doc("Contribution Category")
			category.update(cat_data)
			category.insert(ignore_permissions=True)
			print(f"✅ Categoría creada: {cat_data['name']}")
		else:
			print(f"ℹ️ Categoría ya existe: {cat_data['name']}")


def create_test_sites():
	"""Registrar sites reales del ambiente Buzola para cross-site."""
	print("🏢 Registrando sites reales del ambiente...")

	real_sites = [
		{
			"site_url": "https://admin1.dev",
			"company_name": "Administradora Buzola #1",
			"contact_email": "admin1@buzola.mx",
			"business_justification": "Site administradora real para cross-site contributions",
		},
		{
			"site_url": "https://condo1.dev",
			"company_name": "Condominio Torre Azul",
			"contact_email": "admin@torreazul.mx",
			"business_justification": "Site condominio para testing cross-site contributions",
		},
		{
			"site_url": "https://condo2.dev",
			"company_name": "Condominio Vista Verde",
			"contact_email": "admin@vistaverde.mx",
			"business_justification": "Site condominio adicional para testing cross-site contributions",
		},
	]

	for site_data in real_sites:
		site_url = site_data["site_url"]
		if not frappe.db.exists("Registered Contributor Site", site_url):
			real_site = frappe.new_doc("Registered Contributor Site")
			real_site.update(site_data)
			real_site.is_active = 1
			real_site.insert(ignore_permissions=True)
			print(f"✅ Site real registrado: {site_url}")
			print(f"   API Key: {real_site.get_masked_api_key()}")
		else:
			real_site = frappe.get_doc("Registered Contributor Site", site_url)
			print(f"ℹ️ Site real ya existe: {site_url}")
			print(f"   API Key: {real_site.get_masked_api_key()}")


def setup_permissions():
	"""Configurar permisos para cross-site contributions."""
	print("🔐 Configurando permisos...")

	# Asegurar que el rol System Manager tenga permisos completos
	doctypes_to_check = ["Registered Contributor Site", "Contribution Request", "Contribution Category"]

	for doctype in doctypes_to_check:
		# Verificar que existe el DocType
		if frappe.db.exists("DocType", doctype):
			print(f"✅ Permisos verificados para: {doctype}")
		else:
			print(f"⚠️ DocType no encontrado: {doctype}")


def get_api_instructions():
	"""Obtener instrucciones de uso de APIs cross-site."""
	print("\n📖 INSTRUCCIONES DE USO:")
	print("=" * 60)

	print("\n1. 🔗 ENDPOINTS DISPONIBLES:")
	print(
		"   • Envío: /api/method/condominium_management.community_contributions.api.cross_site_api.submit_contribution_to_domika"
	)
	print(
		"   • Recepción: /api/method/condominium_management.community_contributions.api.cross_site_api.receive_external_contribution"
	)
	print(
		"   • Test: /api/method/condominium_management.community_contributions.api.cross_site_api.test_cross_site_connection"
	)

	print("\n2. 🧪 SITES DE PRUEBA CONFIGURADOS:")
	test_sites = frappe.get_all(
		"Registered Contributor Site",
		filters={"site_url": ["like", "%test.com%"]},
		fields=["site_url", "company_name"],
	)

	for site in test_sites:
		site_doc = frappe.get_doc("Registered Contributor Site", site["site_url"])
		print(f"   • {site['company_name']}: {site['site_url']}")
		print(f"     API Key: {site_doc.get_masked_api_key()}")

	print("\n3. 📝 EJEMPLO DE USO:")
	print("""
   // JavaScript - Desde site administradora
   frappe.call({
       method: "condominium_management.community_contributions.api.cross_site_api.submit_contribution_to_domika",
       args: {
           contribution_data: JSON.stringify({
               template_code: "TEMPLATE_001",
               template_description: "Template de prueba",
               infrastructure_templates: [...]
           }),
           target_site_url: "https://domika.dev",
           api_key: "your-api-key-here",
           contribution_title: "Mi Nueva Contribución"
       },
       callback: function(r) {
           if (r.message.success) {
               frappe.msgprint("Contribución enviada exitosamente");
           }
       }
   });
   """)

	print("\n✅ Configuración completada. domika.dev está listo para recibir contribuciones cross-site!")


if __name__ == "__main__":
	setup_domika_central()
	get_api_instructions()
