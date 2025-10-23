# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

# ============================================================================
# ⚠️ ARCHIVO OBSOLETO - NO USAR
# ============================================================================
# Fecha deprecación: 2025-10-20
# Razón: Custom fields migrados a fixtures (RG-009 compliance)
# Reemplazo: condominium_management/fixtures/custom_field.json
# Ver: docs/instructions/CUSTOM-FIELDS-AUDIT-REPORT.md
# Ver: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md
#
# Este archivo creaba 27 custom fields programáticamente violando RG-009.
# Los custom fields ahora se instalan automáticamente via fixtures.
#
# NO llamar install_company_customizations() - causará duplicados
# NO usar en hooks.py
# NO ejecutar manualmente
#
# Preservado solo como referencia histórica.
# ============================================================================

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
