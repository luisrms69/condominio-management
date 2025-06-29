# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAccessPointDetail(FrappeTestCase):
	"""Test cases for Access Point Detail DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")
		self.test_data = {
			"access_point_type": "Mixto",
			"access_point_name": "Entrada Principal Test",
			"security_level": "Alto",
			"access_control_method": "Tarjeta",
			"who_can_access": "Residentes y Condóminos",
			"access_vehicle_type": "Vehículos y Peatones",
			"opening_time": "06:00:00",
			"closing_time": "22:00:00",
			"operating_days": "Lunes\nMartes\nMiércoles\nJueves\nViernes\nSábado\nDomingo",
		}

	def test_access_point_detail_creation(self):
		"""Test basic creation of Access Point Detail."""
		# Create a new Access Point Detail
		access_point = frappe.get_doc({"doctype": "Access Point Detail", **self.test_data})
		access_point.insert()

		# Verify the document was created successfully
		self.assertTrue(access_point.name)
		self.assertEqual(access_point.access_point_name, "Entrada Principal Test")
		self.assertEqual(access_point.access_control_method, "Tarjeta")
		self.assertEqual(access_point.access_vehicle_type, "Vehículos y Peatones")

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_required_fields_validation(self):
		"""Test that required fields are validated."""
		# Test missing access_point_type
		with self.assertRaises(frappe.ValidationError):
			access_point = frappe.get_doc(
				{"doctype": "Access Point Detail", "access_point_name": "Test Point"}
			)
			access_point.insert()

		# Test missing access_point_name
		with self.assertRaises(frappe.ValidationError):
			access_point = frappe.get_doc({"doctype": "Access Point Detail", "access_point_type": "Mixto"})
			access_point.insert()

	def test_access_control_method_options(self):
		"""Test access control method field accepts valid Spanish options."""
		valid_methods = ["Tarjeta", "Código", "Huella", "Reconocimiento Facial", "QR", "Otro"]

		for method in valid_methods:
			access_point = frappe.get_doc(
				{
					"doctype": "Access Point Detail",
					"access_point_type": "Mixto",
					"access_point_name": f"Test Point {method}",
					"access_control_method": method,
				}
			)
			access_point.insert()
			self.assertEqual(access_point.access_control_method, method)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_who_can_access_options(self):
		"""Test who can access field accepts valid Spanish options."""
		valid_access = ["Residentes y Condóminos", "Visitas", "Proveedores", "Personal de Servicio"]

		for access_type in valid_access:
			access_point = frappe.get_doc(
				{
					"doctype": "Access Point Detail",
					"access_point_type": "Mixto",
					"access_point_name": f"Test Point {access_type}",
					"who_can_access": access_type,
				}
			)
			access_point.insert()
			self.assertEqual(access_point.who_can_access, access_type)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_vehicle_type_options(self):
		"""Test vehicle type field accepts valid Spanish options."""
		valid_vehicle_types = ["Solo Peatonal", "Solo Vehículos", "Vehículos y Peatones"]

		for vehicle_type in valid_vehicle_types:
			access_point = frappe.get_doc(
				{
					"doctype": "Access Point Detail",
					"access_point_type": "Mixto",
					"access_point_name": f"Test Point {vehicle_type}",
					"access_vehicle_type": vehicle_type,
				}
			)
			access_point.insert()
			self.assertEqual(access_point.access_vehicle_type, vehicle_type)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_operating_days_options(self):
		"""Test operating days field accepts valid Spanish options."""
		valid_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

		# Test individual days
		for day in valid_days:
			access_point = frappe.get_doc(
				{
					"doctype": "Access Point Detail",
					"access_point_type": "Mixto",
					"access_point_name": f"Test Point {day}",
					"operating_days": day,
				}
			)
			access_point.insert()
			self.assertEqual(access_point.operating_days, day)
			# FrappeTestCase will handle cleanup automatically via rollback

		# Test multiple days
		multiple_days = "Lunes\nMartes\nMiércoles"
		access_point = frappe.get_doc(
			{
				"doctype": "Access Point Detail",
				"access_point_type": "Mixto",
				"access_point_name": "Test Point Multiple Days",
				"operating_days": multiple_days,
			}
		)
		access_point.insert()
		self.assertEqual(access_point.operating_days, multiple_days)
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_time_fields_validation(self):
		"""Test time fields accept valid time formats."""
		access_point = frappe.get_doc(
			{
				"doctype": "Access Point Detail",
				"access_point_type": "Mixto",
				"access_point_name": "Test Point Times",
				"opening_time": "08:30:00",
				"closing_time": "18:45:00",
			}
		)
		access_point.insert()

		self.assertEqual(str(access_point.opening_time), "08:30:00")
		self.assertEqual(str(access_point.closing_time), "18:45:00")

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_security_level_options(self):
		"""Test security level field accepts valid Spanish options."""
		valid_levels = ["Bajo", "Medio", "Alto", "Restringido"]

		for level in valid_levels:
			access_point = frappe.get_doc(
				{
					"doctype": "Access Point Detail",
					"access_point_type": "Mixto",
					"access_point_name": f"Test Point {level}",
					"security_level": level,
				}
			)
			access_point.insert()
			self.assertEqual(access_point.security_level, level)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Access Point Detail")

		# Check DocType label
		self.assertEqual(meta.get("label"), "Detalle de Punto de Acceso")

		# Check field labels for new fields
		method_field = meta.get_field("access_control_method")
		self.assertEqual(method_field.label, "Método de Control de Acceso")

		access_field = meta.get_field("who_can_access")
		self.assertEqual(access_field.label, "Quiénes Pueden Acceder")

		vehicle_field = meta.get_field("access_vehicle_type")
		self.assertEqual(vehicle_field.label, "Tipo de Acceso")

		opening_field = meta.get_field("opening_time")
		self.assertEqual(opening_field.label, "Hora de Apertura")

		closing_field = meta.get_field("closing_time")
		self.assertEqual(closing_field.label, "Hora de Cierre")

		days_field = meta.get_field("operating_days")
		self.assertEqual(days_field.label, "Días de Operación")

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase automatically handles transaction rollback
