# Copyright (c) 2025, Buzola and Contributors
# See license.txt

"""
Test Data Factory para Condominium Management
=============================================

Factory pattern para crear test data complejo de manera consistente
siguiendo mejores prácticas de Frappe Framework.
"""

import json

import frappe
from frappe.utils import now_datetime


class TestDataFactory:
	"""Factory para crear datos de test reutilizables y consistentes."""

	@staticmethod
	def create_test_company(company_name="Test Company Default", abbr=None):
		"""
		Crear empresa de prueba si no existe.

		Args:
		    company_name (str): Nombre de la empresa
		    abbr (str): Abreviación (auto-generada si no se proporciona)

		Returns:
		    frappe.Document: Documento Company creado o existente
		"""
		if not abbr:
			abbr = "".join([word[0].upper() for word in company_name.split()[:3]])

		if not frappe.db.exists("Company", company_name):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company_name,
					"abbr": abbr,
					"default_currency": "MXN",
					"country": "Mexico",
					"is_group": 1,
				}
			)
			company.insert(ignore_permissions=True)
			return company
		else:
			return frappe.get_doc("Company", company_name)

	@staticmethod
	def create_test_user(email="test@example.com", full_name="Test User"):
		"""
		Crear usuario de prueba si no existe.

		Args:
		    email (str): Email del usuario
		    full_name (str): Nombre completo

		Returns:
		    frappe.Document: Documento User creado o existente
		"""
		if not frappe.db.exists("User", email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": full_name.split()[0],
					"last_name": " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
					"enabled": 1,
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)
			return user
		else:
			return frappe.get_doc("User", email)

	@staticmethod
	def create_contribution_category(
		module_name="Document Generation", contribution_type="Test Infrastructure"
	):
		"""
		Crear categoría de contribución para tests usando timestamp para unicidad.

		Args:
		    module_name (str): Nombre del módulo
		    contribution_type (str): Tipo de contribución

		Returns:
		    frappe.Document: Documento Contribution Category creado o existente
		"""

		# Usar timestamp para evitar duplicación en tests paralelos
		timestamp = now_datetime().strftime("%Y%m%d%H%M%S%f")[:17]  # 17 chars precision

		category = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": module_name,
				"contribution_type": f"{contribution_type} {timestamp}",  # Make unique
				"description": f"Categoría de prueba para {contribution_type.lower()}",
				"export_doctype": "Master Template Registry",
				"required_fields": json.dumps(["template_code", "template_name", "infrastructure_type"]),
				"is_active": 1,
			}
		)
		category.insert(ignore_permissions=True)
		frappe.db.commit()  # Ensure persistence in CI
		return category

	@staticmethod
	def create_entity_type_configuration(
		entity_doctype="User", entity_name="Usuario", entity_name_plural="Usuarios"
	):
		"""
		Crear configuración de tipo de entidad para tests.

		Args:
		    entity_doctype (str): DocType de la entidad
		    entity_name (str): Nombre en singular
		    entity_name_plural (str): Nombre en plural

		Returns:
		    frappe.Document: Documento Entity Type Configuration creado o existente
		"""
		filters = {"entity_doctype": entity_doctype}

		if not frappe.db.exists("Entity Type Configuration", filters):
			config = frappe.get_doc(
				{
					"doctype": "Entity Type Configuration",
					"entity_doctype": entity_doctype,
					"entity_name": entity_name,
					"entity_name_plural": entity_name_plural,
					"owning_module": "Document Generation",
					"entity_description": f"Configuración de prueba para {entity_name}",
					"requires_configuration": 1,
					"is_active": 1,
					"applies_to_manual": 1,
				}
			)
			config.insert(ignore_permissions=True)
			return config
		else:
			return frappe.get_doc("Entity Type Configuration", filters)

	@staticmethod
	def create_test_item(item_code="TEST-ITEM-001", item_name="Test Item"):
		"""
		Crear item de prueba si no existe.

		Args:
		    item_code (str): Código del item
		    item_name (str): Nombre del item

		Returns:
		    frappe.Document: Documento Item creado o existente
		"""
		if not frappe.db.exists("Item", item_code):
			item = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_name,
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"include_item_in_manufacturing": 0,
				}
			)
			item.insert(ignore_permissions=True)
			return item
		else:
			return frappe.get_doc("Item", item_code)

	@staticmethod
	def create_master_template_data():
		"""
		Crear datos base para Master Template Registry.

		Returns:
		    dict: Datos de template listos para usar
		"""
		return {
			"template_code": "TEST_POOL_AREA",
			"template_name": "Área de Piscina de Prueba",
			"infrastructure_type": "Amenity",
			"template_content": json.dumps(
				{
					"fields": [
						{"name": "capacity", "label": "Capacidad", "type": "Int"},
						{"name": "area_size", "label": "Tamaño del Área", "type": "Float"},
					]
				}
			),
		}

	@staticmethod
	def create_template_with_assignment_rules(registry):
		"""
		Crear template completo con reglas de asignación PERSISTIENDO CORRECTAMENTE.

		Args:
		    registry: Instancia de Master Template Registry

		Returns:
		    dict: Template data con reglas válidas
		"""
		# ✅ STEP 1: Limpiar templates/rules existentes para evitar duplicados
		registry.infrastructure_templates = []
		registry.auto_assignment_rules = []

		# ✅ STEP 2: Agregar template PRIMERO
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "POOL_TEMPLATE",
				"template_name": "Template Piscina Completo",
				"infrastructure_type": "Amenity",
				"template_content": json.dumps(
					{
						"fields": [
							{"name": "capacity", "label": "Capacidad", "type": "Int"},
							{"name": "pool_type", "label": "Tipo de Piscina", "type": "Select"},
						]
					}
				),
			},
		)

		# ✅ STEP 3: GUARDAR TEMPLATE ANTES de agregar reglas
		registry.save()

		# ✅ STEP 4: Reload para asegurar persistencia
		registry.reload()

		# ✅ STEP 5: Agregar regla QUE YA REFERENCIA TEMPLATE EXISTENTE
		registry.append(
			"auto_assignment_rules",
			{"entity_type": "Amenity", "entity_subtype": "piscina", "target_template": "POOL_TEMPLATE"},
		)

		return {"template_code": "POOL_TEMPLATE", "template_name": "Template Piscina Completo"}

	@staticmethod
	def create_contribution_request_data(category_name=None, company_name=None):
		"""
		Crear datos completos para Contribution Request.

		Args:
		    category_name (str): Nombre de categoría (auto-creada si no se proporciona)
		    company_name (str): Nombre de empresa (auto-creada si no se proporciona)

		Returns:
		    dict: Datos completos para crear Contribution Request
		"""
		if not category_name:
			category = TestDataFactory.create_contribution_category()
			category_name = category.name

		if not company_name:
			company = TestDataFactory.create_test_company()
			company_name = company.company_name

		contribution_data = {
			"template_code": "TEST_CONTRIBUTION_POOL",
			"template_name": "Piscina de Contribución",
			"infrastructure_type": "Amenity",
			"fields": [{"field_name": "capacity", "field_label": "Capacidad", "field_type": "Int"}],
		}

		return {
			"title": "Template de Piscina - Contribución de Prueba",
			"contribution_category": category_name,
			"business_justification": "Necesario para testing del sistema de contribuciones",
			"contribution_data": json.dumps(contribution_data),
			"company": company_name,
		}

	@staticmethod
	def create_entity_configuration_data():
		"""
		Crear datos completos para Entity Configuration usando CAMPOS REALES del JSON.

		Returns:
		    dict: Datos completos para crear Entity Configuration
		"""
		# Asegurar que existe el documento origen
		if not frappe.db.exists("User", "Administrator"):
			admin_user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "administrator@test.com",
					"first_name": "Administrator",
					"enabled": 1,
					"user_type": "System User",
				}
			)
			admin_user.insert(ignore_permissions=True)

		# ✅ USAR CAMPOS EXACTOS DEL JSON DocType
		return {
			"naming_series": "EC-.YYYY.-",
			"configuration_name": "Configuración de Prueba Completa",
			"configuration_status": "Borrador",  # ✅ Campo real del JSON
			"source_doctype": "User",  # ✅ Campo real del JSON
			"source_docname": "Administrator",  # ✅ Campo real del JSON
			"entity_subtype": "Test Entity Config",
			"applied_template": "TEST_TEMPLATE_CONFIG",  # ✅ Campo real del JSON
			"target_document_type": "Estatuto",
			"target_section": "Configuración General",
			"approval_required": 1,
			"auto_assigned": 0,
		}

	@staticmethod
	def setup_complete_test_environment():
		"""
		Setup completo del ambiente de test con todas las dependencias.

		Returns:
		    dict: Referencias a todos los objetos creados
		"""
		# Crear dependencias base (evitar Items que requieren más configuración)
		company = TestDataFactory.create_test_company()
		user = TestDataFactory.create_test_user()

		# Crear configuraciones específicas del módulo
		category = TestDataFactory.create_contribution_category()
		entity_type = TestDataFactory.create_entity_type_configuration()

		return {
			"company": company,
			"user": user,
			"contribution_category": category,
			"entity_type_configuration": entity_type,
		}

	@staticmethod
	def cleanup_test_data(created_objects=None):
		"""
		Limpieza opcional de datos de test (normalmente no necesario con rollback).

		Args:
		    created_objects (dict): Referencias a objetos creados para limpiar
		"""
		# En Frappe, normalmente no es necesario cleanup manual
		# porque FrappeTestCase maneja rollback automático
		# Este método está disponible para casos especiales
		pass
