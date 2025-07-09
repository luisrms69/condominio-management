# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDocumentTemplateType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Document Template Type", {"template_type_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_document_template_type_creation(self):
		"""Test crear tipo de plantilla básico"""
		template_type = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Memorando",
				"category": "Administrativo",
			}
		)
		template_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(template_type.template_type_name, "Test Memorando")
		self.assertEqual(template_type.category, "Administrativo")
		self.assertTrue(template_type.is_active)
		self.assertEqual(template_type.retention_period_days, 365)

	def test_legal_document_validation(self):
		"""Test validación de documentos legales"""
		# Documento legal sin firma
		template_type1 = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Legal Invalid",
				"category": "Legal",
				"is_legal_document": 1,
				"requires_signature": 0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			template_type1.insert()

		# Documento legal con período de retención corto
		template_type2 = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Legal Short",
				"category": "Legal",
				"is_legal_document": 1,
				"requires_signature": 1,
				"retention_period_days": 365,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			template_type2.insert()

		# Documento legal válido
		template_type3 = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Legal Valid",
				"category": "Legal",
				"is_legal_document": 1,
				"requires_signature": 1,
				"requires_notarization": 1,
				"retention_period_days": 1095,
			}
		)
		template_type3.insert()

		# Verificar que se creó correctamente
		self.assertTrue(template_type3.is_legal_document)
		self.assertTrue(template_type3.requires_signature)
		self.assertTrue(template_type3.requires_notarization)

	def test_retention_period_validation(self):
		"""Test validación del período de retención"""
		template_type = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Invalid Retention",
				"category": "Administrativo",
				"retention_period_days": -100,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			template_type.insert()

	def test_get_requirements_checklist(self):
		"""Test obtener lista de requerimientos"""
		template_type = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Requirements",
				"category": "Legal",
				"requires_signature": 1,
				"requires_notarization": 1,
				"is_legal_document": 1,
				"retention_period_days": 1095,
			}
		)
		template_type.insert()

		requirements = template_type.get_requirements_checklist()
		expected_requirements = ["Requiere Firma", "Requiere Notarización", "Es Documento Legal"]
		self.assertEqual(len(requirements), 3)
		for req in expected_requirements:
			self.assertIn(req, requirements)

	def test_get_retention_years(self):
		"""Test obtener período de retención en años"""
		template_type = frappe.get_doc(
			{
				"doctype": "Document Template Type",
				"template_type_name": "Test Retention Years",
				"category": "Legal",
				"retention_period_days": 1095,
				"requires_signature": 1,
				"is_legal_document": 1,
			}
		)
		template_type.insert()

		years = template_type.get_retention_years()
		self.assertEqual(years, 3.0)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Document Template Type", {"template_type_name": ["like", "Test%"]})
		frappe.db.commit()
