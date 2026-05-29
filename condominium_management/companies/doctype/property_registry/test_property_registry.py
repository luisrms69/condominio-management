# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import date, datetime

import frappe
from frappe.tests import UnitTestCase


class TestPropertyRegistry(UnitTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		self.create_test_data()

		# Limpiar propiedades de prueba
		frappe.db.delete("Property Registry", {"property_name": ["like", "Test%"]})
		frappe.db.commit()

	def create_test_data(self):
		"""Crear datos de prueba necesarios"""
		# Crear Company Type si no existe
		if not frappe.db.exists("Company Type", "CONDO"):
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

		# Usar la company del test site si existe, sino crear una simple
		if frappe.db.exists("Company", "Condominio Test LLC"):
			self.test_company_name = "Condominio Test LLC"
		else:
			# Buscar cualquier company existente
			existing_companies = frappe.db.get_list("Company", limit=1)
			if existing_companies:
				self.test_company_name = existing_companies[0].name
			else:
				# Crear una company muy simple
				try:
					simple_company = frappe.get_doc(
						{
							"doctype": "Company",
							"company_name": "Test Company",
							"abbr": "TC",
							"default_currency": "USD",
							"country": "United States",
						}
					)
					simple_company.insert(ignore_permissions=True)
					self.test_company_name = "Test Company"
				except Exception:
					self.test_company_name = "Test Company"

	def _base_doc(self, property_name, extra=None):
		"""Devuelve dict base con todos los campos obligatorios."""
		doc = {
			"doctype": "Property Registry",
			"naming_series": "PROP-.YYYY.-",
			"property_name": property_name,
			"company": self.test_company_name,
			"property_usage_type": "Residencial",
			"acquisition_type": "Compra",
			"property_status_type": "Activo",
			"registration_date": datetime.now().date(),
			"indiviso_percentage": 1.5,
		}
		if extra:
			doc.update(extra)
		return doc

	def test_property_registry_creation(self):
		"""Test crear registro de propiedad básico"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Edificio Central",
				{"total_area_sqm": 5000.0, "built_area_sqm": 4000.0},
			)
		)
		property_registry.insert(ignore_permissions=True)

		self.assertEqual(property_registry.property_name, "Test Edificio Central")
		self.assertEqual(property_registry.company, self.test_company_name)
		self.assertTrue(property_registry.property_code)
		self.assertEqual(property_registry.total_area_sqm, 5000.0)
		self.assertEqual(property_registry.built_area_sqm, 4000.0)

	def test_property_area_validation(self):
		"""Test validación de áreas"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Invalid Area",
				{"total_area_sqm": 1000.0, "built_area_sqm": 1500.0},
			)
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_declared_owners_validation(self):
		"""Test validación de titulares declarados — titulares actuales suman 100%"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Copropiedad",
				{
					"declared_owners": [
						{
							"owner_name": "Juan Pérez",
							"owner_type": "Persona Física",
							"ownership_percentage": 60.0,
							"is_current": 1,
						},
						{
							"owner_name": "María González",
							"owner_type": "Persona Física",
							"ownership_percentage": 40.0,
							"is_current": 1,
						},
					],
				},
			)
		)
		property_registry.insert(ignore_permissions=True)

		self.assertEqual(property_registry.current_owners_total_percentage, 100.0)
		self.assertEqual(len(property_registry.declared_owners), 2)

	def test_declared_owners_percentage_validation(self):
		"""Test validación — titulares actuales que no suman 100% bloquean"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Invalid Percentage",
				{
					"declared_owners": [
						{
							"owner_name": "Juan Pérez",
							"owner_type": "Persona Física",
							"ownership_percentage": 60.0,
							"is_current": 1,
						},
						{
							"owner_name": "María González",
							"owner_type": "Persona Física",
							"ownership_percentage": 30.0,  # Suma = 90%
							"is_current": 1,
						},
					],
				},
			)
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_historical_owners_not_counted(self):
		"""Titulares históricos (is_current=0) no cuentan para la suma del 100%"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Historical Owners",
				{
					"declared_owners": [
						{
							"owner_name": "Propietario Actual",
							"owner_type": "Persona Física",
							"ownership_percentage": 100.0,
							"is_current": 1,
						},
						{
							"owner_name": "Propietario Anterior",
							"owner_type": "Persona Física",
							"ownership_percentage": 100.0,  # no suma — es histórico
							"is_current": 0,
						},
					],
				},
			)
		)

		# Debe pasar: solo el titular actual (100%) cuenta
		property_registry.insert(ignore_permissions=True)
		self.assertEqual(property_registry.current_owners_total_percentage, 100.0)

	def test_end_date_before_start_date(self):
		"""Validar que end_date no puede ser anterior a start_date"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test End Date Validation",
				{
					"declared_owners": [
						{
							"owner_name": "Juan Pérez",
							"owner_type": "Persona Física",
							"ownership_percentage": 100.0,
							"is_current": 1,
							"start_date": date(2025, 6, 1),
							"end_date": date(2025, 1, 1),  # anterior a start_date
						},
					],
				},
			)
		)

		with self.assertRaises(frappe.ValidationError):
			property_registry.insert()

	def test_indiviso_validation(self):
		"""Validar que indiviso_percentage debe ser mayor a 0 y no exceder 100%"""
		# Cero — falla (también activa validación de mandatorio)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(self._base_doc("Test Indiviso Zero", {"indiviso_percentage": 0})).insert()

		# Mayor a 100 — falla
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(self._base_doc("Test Indiviso Over", {"indiviso_percentage": 101})).insert()

	def test_current_owner_display_single(self):
		"""Un titular actual: current_owner_display muestra su nombre"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Display Single",
				{
					"declared_owners": [
						{
							"owner_name": "Ana Torres",
							"owner_type": "Persona Física",
							"ownership_percentage": 100.0,
							"is_current": 1,
						},
					],
				},
			)
		)
		property_registry.insert(ignore_permissions=True)

		self.assertEqual(property_registry.current_owner_display, "Ana Torres")

	def test_current_owner_display_multiple(self):
		"""Varios titulares actuales: current_owner_display muestra 'Copropiedad (N)'"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Display Multiple",
				{
					"declared_owners": [
						{
							"owner_name": "Ana Torres",
							"owner_type": "Persona Física",
							"ownership_percentage": 60.0,
							"is_current": 1,
						},
						{
							"owner_name": "Carlos Ruiz",
							"owner_type": "Persona Física",
							"ownership_percentage": 40.0,
							"is_current": 1,
						},
					],
				},
			)
		)
		property_registry.insert(ignore_permissions=True)

		self.assertEqual(property_registry.current_owner_display, "Copropiedad (2)")

	def test_property_code_generation(self):
		"""Test generación de código de propiedad"""
		property_registry = frappe.get_doc(self._base_doc("Edificio Nuevo Central"))
		property_registry.insert(ignore_permissions=True)

		self.assertTrue(property_registry.property_code)
		self.assertIn("EDINU", property_registry.property_code)

	def test_ownership_summary(self):
		"""Test resumen de propiedad"""
		# Sin titulares declarados
		pr1 = frappe.get_doc(self._base_doc("Test Single Owner"))
		pr1.insert(ignore_permissions=True)

		self.assertEqual(pr1.get_ownership_summary(), "Sin titulares declarados")

		# Varios titulares actuales
		pr2 = frappe.get_doc(
			self._base_doc(
				"Test Multiple Owners",
				{
					"declared_owners": [
						{
							"owner_name": "Juan Pérez",
							"owner_type": "Persona Física",
							"ownership_percentage": 50.0,
							"is_current": 1,
						},
						{
							"owner_name": "María González",
							"owner_type": "Persona Física",
							"ownership_percentage": 50.0,
							"is_current": 1,
						},
					],
				},
			)
		)
		pr2.insert(ignore_permissions=True)

		self.assertEqual(pr2.get_ownership_summary(), "Copropiedad - 2 titulares actuales")

	def test_main_owner(self):
		"""Test obtener propietario principal"""
		property_registry = frappe.get_doc(
			self._base_doc(
				"Test Main Owner",
				{
					"declared_owners": [
						{
							"owner_name": "Juan Pérez",
							"owner_type": "Persona Física",
							"ownership_percentage": 70.0,
							"is_current": 1,
						},
						{
							"owner_name": "María González",
							"owner_type": "Persona Física",
							"ownership_percentage": 30.0,
							"is_current": 1,
						},
					],
				},
			)
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
