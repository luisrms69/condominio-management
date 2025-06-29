# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNearbyReference(FrappeTestCase):
	"""Test cases for Nearby Reference DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")
		self.test_data = {
			"reference_type": "Centro Comercial",
			"reference_name": "Plaza Central Test",
			"distance": "Entre 50 y 150 metros",
			"directions": "Salir por la puerta principal y caminar hacia el norte",
		}

	def test_nearby_reference_creation(self):
		"""Test basic creation of Nearby Reference."""
		# Create a new Nearby Reference
		nearby_ref = frappe.get_doc({"doctype": "Nearby Reference", **self.test_data})
		nearby_ref.insert()

		# Verify the document was created successfully
		self.assertTrue(nearby_ref.name)
		self.assertEqual(nearby_ref.reference_type, "Centro Comercial")
		self.assertEqual(nearby_ref.reference_name, "Plaza Central Test")
		self.assertEqual(nearby_ref.distance, "Entre 50 y 150 metros")

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_distance_field_options(self):
		"""Test that distance field only accepts valid Spanish options."""
		valid_distances = [
			"Menos de 50 metros",
			"Entre 50 y 150 metros",
			"Entre 150 y 500 metros",
			"Más de 500 metros",
		]

		# Test each valid option
		for distance in valid_distances:
			nearby_ref = frappe.get_doc(
				{
					"doctype": "Nearby Reference",
					"reference_type": "Centro Comercial",
					"reference_name": f"Test Ref {distance}",
					"distance": distance,
				}
			)
			nearby_ref.insert()
			self.assertEqual(nearby_ref.distance, distance)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_required_fields_validation(self):
		"""Test that required fields are validated."""
		# Test missing reference_type
		with self.assertRaises(frappe.ValidationError):
			nearby_ref = frappe.get_doc(
				{
					"doctype": "Nearby Reference",
					"reference_name": "Test Reference",
					"distance": "Menos de 50 metros",
				}
			)
			nearby_ref.insert()

		# Test missing reference_name
		with self.assertRaises(frappe.ValidationError):
			nearby_ref = frappe.get_doc(
				{
					"doctype": "Nearby Reference",
					"reference_type": "Centro Comercial",
					"distance": "Menos de 50 metros",
				}
			)
			nearby_ref.insert()

	def test_reference_type_options(self):
		"""Test reference type field accepts valid Spanish options."""
		valid_types = [
			"Centro Comercial",
			"Parque",
			"Hospital",
			"Escuela",
			"Universidad",
			"Centro Deportivo",
			"Supermercado",
			"Restaurante",
			"Otro",
		]

		for ref_type in valid_types:
			nearby_ref = frappe.get_doc(
				{
					"doctype": "Nearby Reference",
					"reference_type": ref_type,
					"reference_name": f"Test {ref_type}",
					"distance": "Menos de 50 metros",
				}
			)
			nearby_ref.insert()
			self.assertEqual(nearby_ref.reference_type, ref_type)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Nearby Reference")

		# Check DocType label
		self.assertEqual(meta.get("label"), "Referencia Cercana")

		# Check field labels
		distance_field = meta.get_field("distance")
		self.assertEqual(distance_field.label, "Distancia")

		ref_type_field = meta.get_field("reference_type")
		self.assertEqual(ref_type_field.label, "Tipo de Referencia")

		ref_name_field = meta.get_field("reference_name")
		self.assertEqual(ref_name_field.label, "Nombre de Referencia")

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase automatically handles transaction rollback
