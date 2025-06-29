# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCondominiumInformation(FrappeTestCase):
	"""Test cases for Condominium Information DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_company()

	@classmethod
	def create_test_company(cls):
		"""Create test company if it doesn't exist."""
		if getattr(frappe.flags, "test_condominium_company_created", False):
			return

		if not frappe.db.exists("Company", "Test Condominium"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Condominium",
					"abbr": "TC",
					"default_currency": "MXN",
					"country": "Mexico",
				}
			)
			company.insert(ignore_permissions=True)

		frappe.flags.test_condominium_company_created = True

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")

	def test_condominium_information_creation(self):
		"""Test basic creation of Condominium Information."""
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"total_units": 50,
				"total_area": 5000.0,
				"common_area": 2000.0,
				"private_area": 3000.0,
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.total_units, 50)

	def test_area_validation(self):
		"""Test area validation logic."""
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"total_units": 50,
				"total_area": 5000.0,
				"common_area": 2000.0,
				"private_area": 2500.0,  # Total doesn't match
			}
		)
		# This should trigger a warning but not fail
		doc.insert(ignore_permissions=True)

	def test_units_validation(self):
		"""Test units validation."""
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"total_units": -5,  # Invalid negative value
			}
		)
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_gps_coordinates_field(self):
		"""Test GPS coordinates field functionality."""
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"gps_coordinates": "19.432608, -99.133209",
				"total_units": 50,
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.gps_coordinates, "19.432608, -99.133209")
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_gps_coordinates_validation(self):
		"""Test GPS coordinates format validation."""
		# Test valid formats
		valid_coordinates = ["19.432608, -99.133209", "40.7128, -74.0060", "-34.6037, -58.3816"]

		for coordinates in valid_coordinates:
			doc = frappe.get_doc(
				{
					"doctype": "Condominium Information",
					"company": "Test Condominium",
					"gps_coordinates": coordinates,
					"total_units": 50,
				}
			)
			doc.insert(ignore_permissions=True)
			self.assertEqual(doc.gps_coordinates, coordinates)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_how_to_arrive_field(self):
		"""Test how to arrive field with description."""
		instructions = """Para llegar al condominio:
        1. Tome la Av. Principal hacia el norte
        2. Gire a la derecha en la calle secundaria
        3. El condominio está a 200 metros"""

		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"how_to_arrive": instructions,
				"total_units": 50,
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.how_to_arrive, instructions)
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_tab_structure(self):
		"""Test that DocType has correct tab structure."""
		meta = frappe.get_meta("Condominium Information")

		# Get all tab break fields
		tab_fields = [f for f in meta.fields if f.fieldtype == "Tab Break"]
		tab_labels = [f.label for f in tab_fields if f.label]

		# Should have 3 tabs
		expected_tabs = ["Información General", "Cómo Llegar", "Accesos"]
		self.assertEqual(len(tab_labels), 3)

		for expected_tab in expected_tabs:
			self.assertIn(expected_tab, tab_labels)

		# Should NOT have "Contacto y Servicios" tab
		self.assertNotIn("Contacto y Servicios", tab_labels)

	def test_table_fields(self):
		"""Test table fields for transport and references."""
		doc = frappe.get_doc(
			{"doctype": "Condominium Information", "company": "Test Condominium", "total_units": 50}
		)
		doc.insert(ignore_permissions=True)

		# Test that table fields exist
		self.assertTrue(hasattr(doc, "public_transport"))
		self.assertTrue(hasattr(doc, "nearby_references"))
		self.assertTrue(hasattr(doc, "access_points"))

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Condominium Information")

		# Check DocType label
		self.assertEqual(meta.get_label(), "Información del Condominio")

		# Check key field labels
		company_field = meta.get_field("company")
		self.assertEqual(company_field.label, "Condominio")

		units_field = meta.get_field("total_units")
		self.assertEqual(units_field.label, "Total de Unidades")

		area_field = meta.get_field("total_area")
		self.assertEqual(area_field.label, "Superficie Total (m²)")

		gps_field = meta.get_field("gps_coordinates")
		self.assertEqual(gps_field.label, "Coordenadas GPS")

		arrive_field = meta.get_field("how_to_arrive")
		self.assertEqual(arrive_field.label, "Instrucciones Generales de Cómo Llegar")

	def test_gps_field_description(self):
		"""Test GPS field has proper description."""
		meta = frappe.get_meta("Condominium Information")
		gps_field = meta.get_field("gps_coordinates")

		expected_description = "Coordenadas GPS del condominio para navegación (formato: latitud, longitud). Ejemplo: 19.432608, -99.133209"
		self.assertEqual(gps_field.description, expected_description)

	def test_arrive_field_description(self):
		"""Test how to arrive field has proper description."""
		meta = frappe.get_meta("Condominium Information")
		arrive_field = meta.get_field("how_to_arrive")

		expected_description = "Coloca direcciones generales de como llegar al sitio, particularmente si se tienen que tomar caminos no claramente definidos, puedes además indicar las principales vías de acceso y demás información que consideres ayude a alguien sin conocimiento del área a llegar"
		self.assertEqual(arrive_field.description, expected_description)

	def test_construction_year_validation(self):
		"""Test construction year field validation."""
		import datetime

		current_year = datetime.datetime.now().year

		# Test reasonable construction year
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"construction_year": current_year - 10,
				"total_units": 50,
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.construction_year, current_year - 10)
		# FrappeTestCase will handle cleanup automatically via rollback

		# Test future year (should be allowed but might trigger warning)
		doc = frappe.get_doc(
			{
				"doctype": "Condominium Information",
				"company": "Test Condominium",
				"construction_year": current_year + 2,
				"total_units": 50,
			}
		)
		doc.insert(ignore_permissions=True)
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_precision_fields(self):
		"""Test precision for area fields."""
		meta = frappe.get_meta("Condominium Information")

		total_area_field = meta.get_field("total_area")
		common_area_field = meta.get_field("common_area")
		private_area_field = meta.get_field("private_area")

		# All area fields should have precision 2
		self.assertEqual(int(total_area_field.precision), 2)
		self.assertEqual(int(common_area_field.precision), 2)
		self.assertEqual(int(private_area_field.precision), 2)

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase automatically handles transaction rollback
