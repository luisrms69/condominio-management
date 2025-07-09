# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserType(Document):
	def validate(self):
		"""Validaciones del tipo de usuario"""
		self.validate_permissions()

	def validate_permissions(self):
		"""Validar configuración de permisos"""
		if self.can_access_admin:
			# Usuario administrativo debe tener otros permisos habilitados
			if not any(
				[
					self.can_manage_policies,
					self.can_manage_complaints,
					self.can_manage_finances,
					self.can_view_reports,
				]
			):
				frappe.throw("Usuario administrativo debe tener al menos un permiso específico habilitado.")

	def before_rename(self, olddn, newdn, merge=False):
		"""Prevenir renombrado si hay User Profile usando este tipo"""
		if frappe.db.count("User Profile", filters={"user_type": olddn}) > 0:
			frappe.throw("No se puede renombrar. Hay perfiles de usuario usando este tipo.")

	def on_trash(self):
		"""Prevenir eliminación si hay User Profile usando este tipo"""
		if frappe.db.count("User Profile", filters={"user_type": self.name}) > 0:
			frappe.throw("No se puede eliminar. Hay perfiles de usuario usando este tipo.")

	def get_permissions_list(self):
		"""Obtener lista de permisos habilitados"""
		permissions = []
		if self.can_access_admin:
			permissions.append("Acceso Administrativo")
		if self.can_manage_policies:
			permissions.append("Gestionar Políticas")
		if self.can_manage_complaints:
			permissions.append("Gestionar Quejas")
		if self.can_manage_finances:
			permissions.append("Gestionar Finanzas")
		if self.can_view_reports:
			permissions.append("Ver Reportes")
		return permissions
