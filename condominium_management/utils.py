import frappe
from frappe.utils import now_datetime
from frappe.utils.user import is_website_user


def before_tests():
	"""
	Configuración pre-tests minimalista para evitar errores de setup complejo.

	Solo crea registros básicos necesarios para tests, evitando setup_complete.
	"""
	frappe.clear_cache()

	# Solo crear Company básica sin setup complejo
	_create_minimal_company()
	_create_basic_erpnext_records()

	# Reemplazar enable_all_roles_and_domains con función Frappe pura
	_setup_basic_roles_frappe_only()

	# Force migrate DocTypes to ensure they exist in CI
	_reload_custom_doctypes()

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
		print(f"Warning: setup_complete failed: {e}")
		# Fallback: crear solo Company si setup_complete falla
		_create_minimal_company()
		_create_basic_erpnext_records()


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


def _create_basic_erpnext_records():
	"""
	Crear registros básicos de ERPNext necesarios para tests.

	Fallback cuando setup_complete falla.
	"""
	# Item Group
	if not frappe.db.exists("Item Group", "All Item Groups"):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": "All Item Groups",
				"is_group": 1,
			}
		).insert(ignore_permissions=True)

	# UOM
	if not frappe.db.exists("UOM", "Nos"):
		frappe.get_doc(
			{
				"doctype": "UOM",
				"uom_name": "Nos",
			}
		).insert(ignore_permissions=True)

	# Department
	if not frappe.db.exists("Department", "All Departments"):
		frappe.get_doc(
			{
				"doctype": "Department",
				"department_name": "All Departments",
				"is_group": 1,
			}
		).insert(ignore_permissions=True)


def _reload_custom_doctypes():
	"""
	Force reload de DocTypes personalizados para asegurar que existan en CI.

	Previene errores de 'DocType not found' durante ejecución de tests.
	"""
	custom_doctypes = [
		("document_generation", "master_template_registry"),
		("document_generation", "entity_type_configuration"),
		("document_generation", "entity_configuration"),
		("document_generation", "infrastructure_template_definition"),
		("document_generation", "template_auto_assignment_rule"),
		("document_generation", "configuration_field"),
		("document_generation", "conflict_detection_field"),
		("community_contributions", "contribution_category"),
		("community_contributions", "contribution_request"),
	]

	for module, doctype in custom_doctypes:
		try:
			frappe.reload_doc(module, "doctype", doctype)
		except Exception as e:
			print(f"Warning: Could not reload {module}.{doctype}: {e}")


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True
