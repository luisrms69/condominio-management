# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate


class TestAssemblyManagement(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-ASM-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Assembly Company"')
		frappe.db.sql('DELETE FROM `tabAssembly Management` WHERE assembly_type = "Ordinaria"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-ASM-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Assembly Company"')
		frappe.db.sql('DELETE FROM `tabAssembly Management` WHERE assembly_type = "Ordinaria"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for assembly management tests"""
		# Use existing company from test environment or create minimal one
		if not frappe.db.exists("Company", "Test Assembly Company"):
			# Try to use existing company or create minimal one
			existing_company = frappe.db.get_value("Company", filters={}, fieldname="name")
			if existing_company:
				# Use existing company and create an alias
				frappe.db.sql(
					"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Assembly Company', 'Test Assembly Company', 'TAC', 'USD') ON DUPLICATE KEY UPDATE name=name"
				)
				frappe.db.commit()
			else:
				# Create minimal company bypassing ERPNext hooks
				frappe.db.sql(
					"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Assembly Company', 'Test Assembly Company', 'TAC', 'USD')"
				)
				frappe.db.commit()

		# Create test properties for quorum
		cls.test_properties = []
		for i in range(3):
			prop_code = f"TEST-PROP-ASM-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test Property {i+1}",
						"property_usage_type": "Residencial",
						"acquisition_type": "Compra",
						"property_status_type": "Activo",
						"registration_date": nowdate(),
						"unit_area": 100,
						"owner_name": f"Owner {i+1}",
						"status": "Activo",
					}
				)
				property_doc.insert(ignore_permissions=True)
				cls.test_properties.append(prop_code)

		# Create test physical space
		if not frappe.db.exists("Physical Space", "TEST-SALON-ASAMBLEAS"):
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": "Salón de Asambleas Test",
					"space_code": "TEST-SALON-ASAMBLEAS",
					"space_type": "Salón de Eventos",
					"capacity": 50,
					"is_active": 1,
				}
			)
			space.insert(ignore_permissions=True)

	def test_assembly_management_creation(self):
		"""Test basic assembly management creation"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30) + " 09:00:00",
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
				"physical_space": "TEST-SALON-ASAMBLEAS",
			}
		)

		assembly.insert()

		# Verify the document was created
		self.assertTrue(assembly.name)
		self.assertEqual(assembly.assembly_title, "Asamblea de Prueba")
		self.assertEqual(assembly.status, "Convocada")
		self.assertEqual(assembly.current_quorum_percentage, 0)

		# Clean up
		assembly.delete()

	def test_convocation_date_validation(self):
		"""Test that convocation date must be before assembly date"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 15),
				"convocation_date": add_days(nowdate(), 30),  # After assembly date
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			assembly.insert()

	def test_quorum_percentage_validation(self):
		"""Test that first call quorum must be greater than second call"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 30,  # Lower than second call
				"minimum_quorum_second": 60,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			assembly.insert()

	def test_load_all_properties_to_quorum(self):
		"""Test loading all active properties to quorum registration"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		assembly.insert()

		# Load properties to quorum
		assembly.load_all_properties_to_quorum()

		# Verify properties were loaded
		self.assertTrue(len(assembly.quorum_registration) >= 3)
		property_codes = [q.property_registry for q in assembly.quorum_registration]

		for prop_code in self.__class__.test_properties:
			self.assertIn(prop_code, property_codes)

		# Clean up
		assembly.delete()

	def test_quorum_calculation(self):
		"""Test quorum percentage calculation"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		# Add quorum records manually
		for i, prop_code in enumerate(self.__class__.test_properties):
			assembly.append(
				"quorum_registration",
				{
					"property_registry": prop_code,
					"attendance_status": "Presente" if i < 2 else "Ausente",
					"check_in_method": "Manual",
				},
			)

		assembly.insert()

		# Calculate quorum percentage
		assembly.calculate_quorum_percentage()

		# Should be 66.67% (2 out of 3 present)
		expected_percentage = (2 / 3) * 100
		self.assertAlmostEqual(assembly.current_quorum_percentage, expected_percentage, places=1)

		# Clean up
		assembly.delete()

	def test_add_agenda_item(self):
		"""Test adding agenda items"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		assembly.insert()

		# Add agenda item
		assembly.add_agenda_item("Aprobación de Estados Financieros", "Financiero", True, "Mayoría Simple")

		# Verify agenda item was added
		self.assertEqual(len(assembly.agenda_items), 1)
		self.assertEqual(assembly.agenda_items[0].topic_title, "Aprobación de Estados Financieros")
		self.assertTrue(assembly.agenda_items[0].requires_voting)
		self.assertEqual(assembly.agenda_items[0].voting_type, "Mayoría Simple")

		# Clean up
		assembly.delete()

	def test_extraordinary_assembly_validation(self):
		"""Test that extraordinary assemblies require a reason"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Extraordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
				# No extraordinary_reason specified
			}
		)

		with self.assertRaises(frappe.ValidationError):
			assembly.insert()

	def test_get_upcoming_assemblies(self):
		"""Test getting upcoming assemblies"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		assembly.insert()

		# Get upcoming assemblies
		upcoming = assembly.get_upcoming_assemblies()

		# Should include our test assembly
		assembly_names = [a["name"] for a in upcoming]
		self.assertIn(assembly.name, assembly_names)

		# Clean up
		assembly.delete()

	def test_submission_validation(self):
		"""Test that assembly cannot be submitted without minimum quorum"""
		assembly = frappe.get_doc(
			{
				"doctype": "Assembly Management",
				"assembly_type": "Ordinaria",
				"assembly_date": add_days(nowdate(), 30),
				"convocation_date": add_days(nowdate(), 15),
				"first_call_time": "09:00:00",
				"second_call_time": "09:30:00",
				"minimum_quorum_first": 60,
				"minimum_quorum_second": 30,
			}
		)

		# Add insufficient quorum (only 1 out of 3 properties)
		assembly.append(
			"quorum_registration",
			{
				"property_registry": self.__class__.test_properties[0],
				"attendance_status": "Presente",
				"check_in_method": "Manual",
			},
		)

		assembly.insert()

		# Should fail submission due to insufficient quorum
		with self.assertRaises(frappe.ValidationError):
			assembly.submit()

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
