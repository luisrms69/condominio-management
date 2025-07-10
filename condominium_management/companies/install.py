# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe

from .custom_fields.company_custom_fields import create_company_custom_fields


def install_company_customizations():
	"""Instalar personalizaciones de Company"""
	try:
		create_company_custom_fields()
		frappe.db.commit()
		print("✅ Personalizaciones de Company instaladas exitosamente")
	except Exception as e:
		frappe.db.rollback()
		print(f"❌ Error instalando personalizaciones de Company: {e}")
		raise


def uninstall_company_customizations():
	"""Desinstalar personalizaciones de Company"""
	try:
		from .custom_fields.company_custom_fields import remove_company_custom_fields

		remove_company_custom_fields()
		frappe.db.commit()
		print("✅ Personalizaciones de Company desinstaladas exitosamente")
	except Exception as e:
		frappe.db.rollback()
		print(f"❌ Error desinstalando personalizaciones de Company: {e}")
		raise
