import frappe
from frappe.utils import now_datetime
from frappe.utils.user import is_website_user


def before_tests():
	"""
	Configuración pre-tests usando solo Frappe Framework.

	Reemplaza dependencias de ERPNext con funciones equivalentes de Frappe
	para máxima compatibilidad y evitar errores de importación.
	"""
	frappe.clear_cache()

	if not frappe.get_list("Company"):
		# Crear empresa básica para testing si no existe
		_create_test_company()

	# Reemplazar enable_all_roles_and_domains con función Frappe pura
	_setup_basic_roles_frappe_only()
	frappe.db.commit()  # nosemgrep


def _create_test_company():
	"""
	Crear empresa mínima para testing usando solo Frappe.

	Evita usar setup_complete de ERPNext que puede fallar en CI.
	"""
	if not frappe.db.exists("Company", "Condominio Test LLC"):
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Condominio Test LLC",
				"abbr": "CT",
				"default_currency": "MXN",
				"country": "Mexico",
			}
		)
		company.insert(ignore_permissions=True)


def _setup_basic_roles_frappe_only():
	"""
	Setup roles básicos usando solo funciones de Frappe Framework.

	Reemplaza enable_all_roles_and_domains de ERPNext con funcionalidad
	equivalente pero usando solo APIs de Frappe.
	"""
	# Verificar que Administrator tiene roles básicos necesarios
	if frappe.db.exists("User", "Administrator"):
		user = frappe.get_doc("User", "Administrator")
		required_roles = ["System Manager", "Desk User"]

		for role in required_roles:
			# Verificar si el rol ya existe para evitar duplicados
			if not any(r.role == role for r in user.roles):
				user.append("roles", {"role": role})

		user.save(ignore_permissions=True)


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True
