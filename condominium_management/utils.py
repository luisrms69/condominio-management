import frappe
from frappe.utils import now_datetime
from frappe.utils.user import is_website_user


def before_tests():
	"""
	Configuración pre-tests usando setup de ERPNext básico.

	Utiliza setup_complete cuando no hay Company existente para asegurar
	que todos los DocTypes y registros básicos estén creados.
	"""
	frappe.clear_cache()

	if not frappe.get_list("Company"):
		# Ejecutar setup completo de ERPNext para CI
		_setup_erpnext_for_tests()

	# Reemplazar enable_all_roles_and_domains con función Frappe pura
	_setup_basic_roles_frappe_only()
	frappe.db.commit()  # nosemgrep


def _setup_erpnext_for_tests():
	"""
	Ejecutar setup completo de ERPNext para testing.

	Crea Company, Warehouse Types, y otros registros necesarios para testing.
	"""
	try:
		from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

		year = now_datetime().year
		setup_complete(
			{
				"currency": "MXN",
				"full_name": "Administrator",
				"company_name": "Condominio Test LLC",
				"timezone": "America/Mexico_City",
				"company_abbr": "CT",
				"industry": "Real Estate",
				"country": "Mexico",
				"fy_start_date": f"{year}-01-01",
				"fy_end_date": f"{year}-12-31",
				"company_tagline": "Testing Company",
				"bank_account": "Test Bank Account",
				"chart_of_accounts": "Standard",
			}
		)
	except Exception as e:
		frappe.log_error(f"Error en setup_complete: {e}")
		# Fallback: crear solo Company si setup_complete falla
		_create_minimal_company()


def _create_minimal_company():
	"""
	Crear Company mínima como fallback cuando setup_complete falla.

	Solo crea la Company sin registros adicionales para evitar errores.
	"""
	if not frappe.db.exists("Company", "Condominio Test LLC"):
		# Primero crear registros básicos que Company necesita
		_create_basic_warehouse_types()

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


def _create_basic_warehouse_types():
	"""
	Crear tipos de warehouse básicos que Company necesita.

	Evita el error 'Could not find Warehouse Type: Transit'.
	"""
	warehouse_types = ["Stores", "Work In Progress", "Finished Goods", "Transit"]

	for wh_type in warehouse_types:
		if not frappe.db.exists("Warehouse Type", wh_type):
			frappe.get_doc(
				{
					"doctype": "Warehouse Type",
					"name": wh_type,
				}
			).insert(ignore_permissions=True)


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
