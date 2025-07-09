# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyRegistry(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		self.create_test_data()

		# Limpiar propiedades de prueba
		frappe.db.delete("Property Registry", {"property_name": ["like", "Test%"]})
		frappe.db.commit()

	def create_test_data(self):
		"""Crear datos de prueba necesarios"""
		# Crear Company Type si no existe
		if not frappe.db.exists("Company Type", "Condominio"):
			company_type = frappe.get_doc(
				{"doctype": "Company Type", "type_name": "Condominio", "type_code": "CONDO"}
			)
			try:
				company_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

		# Crear Property Usage Type si no existe
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Residencial"})
			try:
				usage_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

		# Crear Acquisition Type si no existe
		if not frappe.db.exists("Acquisition Type", "Compra"):
			acquisition_type = frappe.get_doc(
				{"doctype": "Acquisition Type", "acquisition_name": "Compra", "requires_notary": 1}
			)
			try:
				acquisition_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

		# Crear Property Status Type si no existe
		if not frappe.db.exists("Property Status Type", "Activo"):
			status_type = frappe.get_doc({"doctype": "Property Status Type", "status_name": "Activo"})
			try:
				status_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

		# Crear Company si no existe
		if not frappe.db.exists("Company", "Test Condominio ABC"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Condominio ABC",
					"abbr": "TCABC",
					"default_currency": "COP",
					"country": "Colombia",
				}
			)
			try:
				company.insert(ignore_permissions=True)
			except (frappe.DuplicateEntryError, frappe.LinkValidationError, frappe.MandatoryError):
				pass

	def test_property_registry_creation(self):
		"""Test crear registro de propiedad básico"""
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Edificio Central",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"total_area_sqm": 5000.0,
				"built_area_sqm": 4000.0,
			}
		)
		property_registry.insert(ignore_permissions=True)

		# Verificar que se creó correctamente
		self.assertEqual(property_registry.property_name, "Test Edificio Central")
		self.assertEqual(property_registry.company, "Test Condominio ABC")
		self.assertTrue(property_registry.property_code)
		self.assertEqual(property_registry.total_area_sqm, 5000.0)
		self.assertEqual(property_registry.built_area_sqm, 4000.0)

	def test_property_area_validation(self):
		"""Test validación de áreas"""
		# Área construida mayor que área total
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Invalid Area",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"total_area_sqm": 1000.0,
				"built_area_sqm": 1500.0,  # Mayor que total
			}
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_copropiedades_validation(self):
		"""Test validación de copropiedades"""
		# Crear propiedad con copropiedades
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Copropiedad",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 1,
				"copropiedades_table": [
					{
						"owner_name": "Juan Pérez",
						"owner_id": "12345678",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 60.0,
					},
					{
						"owner_name": "María González",
						"owner_id": "87654321",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 40.0,
					},
				],
			}
		)
		property_registry.insert(ignore_permissions=True)

		# Verificar que se creó correctamente
		self.assertEqual(property_registry.total_copropiedades_percentage, 100.0)
		self.assertEqual(len(property_registry.copropiedades_table), 2)

	def test_copropiedades_percentage_validation(self):
		"""Test validación de porcentajes de copropiedades"""
		# Suma no igual a 100%
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Invalid Percentage",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 1,
				"copropiedades_table": [
					{
						"owner_name": "Juan Pérez",
						"owner_id": "12345678",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 60.0,
					},
					{
						"owner_name": "María González",
						"owner_id": "87654321",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 30.0,  # Suma = 90%
					},
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_duplicate_owners_validation(self):
		"""Test validación de propietarios duplicados"""
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Duplicate Owners",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 1,
				"copropiedades_table": [
					{
						"owner_name": "Juan Pérez",
						"owner_id": "12345678",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 50.0,
					},
					{
						"owner_name": "Juan Pérez Duplicado",
						"owner_id": "12345678",  # Mismo ID
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 50.0,
					},
				],
			}
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_financial_validation(self):
		"""Test validación de campos financieros"""
		# Valor negativo
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Negative Value",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"property_value": -1000000,  # Negativo
			}
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_property_code_generation(self):
		"""Test generación de código de propiedad"""
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Edificio Nuevo Central",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
			}
		)
		property_registry.insert(ignore_permissions=True)

		# Verificar que se generó un código
		self.assertTrue(property_registry.property_code)
		self.assertIn("EDINCE", property_registry.property_code)  # Primeras letras de las palabras

	def test_ownership_summary(self):
		"""Test resumen de propiedad"""
		# Propiedad única
		property_registry1 = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Single Owner",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 0,
			}
		)
		property_registry1.insert(ignore_permissions=True)

		self.assertEqual(property_registry1.get_ownership_summary(), "Propiedad única")

		# Copropiedad
		property_registry2 = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Multiple Owners",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 1,
				"copropiedades_table": [
					{
						"owner_name": "Juan Pérez",
						"owner_id": "12345678",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 50.0,
					},
					{
						"owner_name": "María González",
						"owner_id": "87654321",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 50.0,
					},
				],
			}
		)
		property_registry2.insert(ignore_permissions=True)

		self.assertEqual(property_registry2.get_ownership_summary(), "Copropiedad - 2 propietarios")

	def test_main_owner(self):
		"""Test obtener propietario principal"""
		property_registry = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Main Owner",
				"company": "Test Condominio ABC",
				"property_usage_type": "Residencial",
				"acquisition_type": "Compra",
				"property_status_type": "Activo",
				"registration_date": datetime.now().date(),
				"has_copropiedades": 1,
				"copropiedades_table": [
					{
						"owner_name": "Juan Pérez",
						"owner_id": "12345678",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 70.0,
					},
					{
						"owner_name": "María González",
						"owner_id": "87654321",
						"owner_type": "Persona Natural",
						"copropiedad_percentage": 30.0,
					},
				],
			}
		)
		property_registry.insert(ignore_permissions=True)

		main_owner = property_registry.get_main_owner()
		self.assertIn("Juan Pérez", main_owner)
		self.assertIn("70.0%", main_owner)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Property Registry", {"property_name": ["like", "Test%"]})
		frappe.db.delete("Company", {"company_name": ["like", "Test%"]})
		frappe.db.commit()
