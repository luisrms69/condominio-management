# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAcquisitionType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Acquisition Type", {"acquisition_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_acquisition_type_creation(self):
		"""Test crear tipo de adquisición básico"""
		acquisition_type = frappe.get_doc({"doctype": "Acquisition Type", "acquisition_name": "Test Compra"})
		acquisition_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(acquisition_type.acquisition_name, "Test Compra")
		self.assertTrue(acquisition_type.is_active)
		self.assertFalse(acquisition_type.requires_notary)

	def test_notary_requirements(self):
		"""Test requerimientos de notario"""
		acquisition_type = frappe.get_doc(
			{
				"doctype": "Acquisition Type",
				"acquisition_name": "Test Herencia",
				"requires_notary": 1,
				"required_documents": "Acta de defunción\nTestamento\nIdentificación herederos",
			}
		)
		acquisition_type.insert()

		# Verificar configuración
		self.assertTrue(acquisition_type.requires_notary)
		self.assertTrue(acquisition_type.required_documents)

	def test_document_checklist(self):
		"""Test obtener lista de documentos"""
		acquisition_type = frappe.get_doc(
			{
				"doctype": "Acquisition Type",
				"acquisition_name": "Test Donación",
				"required_documents": "Escritura de donación\nIFE del donante\nIFE del donatario",
			}
		)
		acquisition_type.insert()

		# Verificar lista de documentos
		checklist = acquisition_type.get_document_checklist()
		self.assertEqual(len(checklist), 3)
		self.assertIn("Escritura de donación", checklist)

	def test_unique_acquisition_name(self):
		"""Test unicidad del nombre de adquisición"""
		# Crear primer tipo
		acquisition1 = frappe.get_doc(
			{"doctype": "Acquisition Type", "acquisition_name": "Test Adjudicación"}
		)
		acquisition1.insert()

		# Intentar crear segundo con mismo nombre
		acquisition2 = frappe.get_doc(
			{"doctype": "Acquisition Type", "acquisition_name": "Test Adjudicación"}
		)

		with self.assertRaises(frappe.DuplicateEntryError):
			acquisition2.insert()

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Acquisition Type", {"acquisition_name": ["like", "Test%"]})
		frappe.db.commit()
