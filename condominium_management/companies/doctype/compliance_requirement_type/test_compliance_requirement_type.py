# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestComplianceRequirementType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Compliance Requirement Type", {"requirement_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_compliance_requirement_type_creation(self):
		"""Test crear tipo de requerimiento básico"""
		requirement_type = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Renovación Permiso",
				"category": "Permisos",
				"priority_level": "Media",
			}
		)
		requirement_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(requirement_type.requirement_name, "Test Renovación Permiso")
		self.assertEqual(requirement_type.category, "Permisos")
		self.assertEqual(requirement_type.priority_level, "Media")
		self.assertTrue(requirement_type.is_active)
		self.assertEqual(requirement_type.estimated_completion_days, 30)

	def test_completion_days_validation(self):
		"""Test validación de días de cumplimiento"""
		requirement_type = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Invalid Days",
				"category": "Documentación",
				"priority_level": "Baja",
				"estimated_completion_days": -10,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			requirement_type.insert()

	def test_critical_penalty_validation(self):
		"""Test validación de penalización crítica"""
		# Requerimiento crítico sin penalización
		requirement_type1 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Critical No Penalty",
				"category": "Seguridad",
				"priority_level": "Crítica",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			requirement_type1.insert()

		# Requerimiento crítico con penalización
		requirement_type2 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Critical With Penalty",
				"category": "Seguridad",
				"priority_level": "Crítica",
				"penalty_type": "Multa",
			}
		)
		requirement_type2.insert()

		self.assertEqual(requirement_type2.penalty_type, "Multa")

	def test_severe_penalty_approval_validation(self):
		"""Test validación de aprobación para penalizaciones severas"""
		# Penalización severa sin aprobación
		requirement_type = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Severe No Approval",
				"category": "Seguridad",
				"priority_level": "Alta",
				"penalty_type": "Suspensión",
				"requires_approval": 0,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			requirement_type.insert()

		# Penalización severa con aprobación
		requirement_type2 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Severe With Approval",
				"category": "Seguridad",
				"priority_level": "Alta",
				"penalty_type": "Suspensión",
				"requires_approval": 1,
			}
		)
		requirement_type2.insert()

		self.assertTrue(requirement_type2.requires_approval)

	def test_get_priority_score(self):
		"""Test obtener puntaje de prioridad"""
		requirement_type = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Priority Score",
				"category": "Inspecciones",
				"priority_level": "Alta",
			}
		)
		requirement_type.insert()

		self.assertEqual(requirement_type.get_priority_score(), 3)

	def test_get_completion_urgency(self):
		"""Test obtener urgencia de cumplimiento"""
		# Inmediata
		requirement_type1 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Immediate",
				"category": "Seguridad",
				"priority_level": "Crítica",
				"estimated_completion_days": 3,
				"penalty_type": "Multa",
			}
		)
		requirement_type1.insert()
		self.assertEqual(requirement_type1.get_completion_urgency(), "Inmediata")

		# Urgente
		requirement_type2 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Urgent",
				"category": "Permisos",
				"priority_level": "Alta",
				"estimated_completion_days": 15,
			}
		)
		requirement_type2.insert()
		self.assertEqual(requirement_type2.get_completion_urgency(), "Urgente")

		# Normal
		requirement_type3 = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Normal",
				"category": "Reportes",
				"priority_level": "Media",
				"estimated_completion_days": 60,
			}
		)
		requirement_type3.insert()
		self.assertEqual(requirement_type3.get_completion_urgency(), "Normal")

	def test_get_requirements_summary(self):
		"""Test obtener resumen de requerimientos"""
		requirement_type = frappe.get_doc(
			{
				"doctype": "Compliance Requirement Type",
				"requirement_name": "Test Full Requirements",
				"category": "Documentación",
				"priority_level": "Alta",
				"requires_documentation": 1,
				"requires_approval": 1,
				"penalty_type": "Multa",
			}
		)
		requirement_type.insert()

		summary = requirement_type.get_requirements_summary()
		self.assertEqual(len(summary), 3)
		self.assertIn("Documentación", summary)
		self.assertIn("Aprobación", summary)
		self.assertIn("Penalización: Multa", summary)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Compliance Requirement Type", {"requirement_name": ["like", "Test%"]})
		frappe.db.commit()
