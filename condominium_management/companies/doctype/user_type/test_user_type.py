# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestUserType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("User Type", {"user_type_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_user_type_creation(self):
		"""Test crear tipo de usuario básico"""
		user_type = frappe.get_doc({"doctype": "User Type", "user_type_name": "Test Residente"})
		user_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(user_type.user_type_name, "Test Residente")
		self.assertTrue(user_type.is_active)
		self.assertFalse(user_type.can_access_admin)

	def test_admin_permissions_validation(self):
		"""Test validación de permisos administrativos"""
		# Usuario administrativo sin permisos específicos
		user_type = frappe.get_doc(
			{"doctype": "User Type", "user_type_name": "Test Admin Invalid", "can_access_admin": 1}
		)

		with self.assertRaises(frappe.ValidationError):
			user_type.insert()

		# Usuario administrativo con permisos específicos
		user_type2 = frappe.get_doc(
			{
				"doctype": "User Type",
				"user_type_name": "Test Admin Valid",
				"can_access_admin": 1,
				"can_manage_policies": 1,
				"can_view_reports": 1,
			}
		)
		user_type2.insert()

		# Verificar que se creó correctamente
		self.assertTrue(user_type2.can_access_admin)
		self.assertTrue(user_type2.can_manage_policies)
		self.assertTrue(user_type2.can_view_reports)

	def test_get_permissions_list(self):
		"""Test obtener lista de permisos"""
		user_type = frappe.get_doc(
			{
				"doctype": "User Type",
				"user_type_name": "Test Multi Permissions",
				"can_manage_policies": 1,
				"can_manage_complaints": 1,
				"can_view_reports": 1,
			}
		)
		user_type.insert()

		permissions = user_type.get_permissions_list()
		expected_permissions = ["Gestionar Políticas", "Gestionar Quejas", "Ver Reportes"]
		self.assertEqual(len(permissions), 3)
		for perm in expected_permissions:
			self.assertIn(perm, permissions)

	def test_user_type_without_permissions(self):
		"""Test tipo de usuario sin permisos específicos"""
		user_type = frappe.get_doc({"doctype": "User Type", "user_type_name": "Test Basic User"})
		user_type.insert()

		permissions = user_type.get_permissions_list()
		self.assertEqual(len(permissions), 0)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("User Type", {"user_type_name": ["like", "Test%"]})
		frappe.db.commit()
