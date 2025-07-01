import frappe
from erpnext.setup.utils import enable_all_roles_and_domains
from frappe.utils import now_datetime
from frappe.utils.user import is_website_user


def before_tests():
	frappe.clear_cache()
	# complete setup if missing
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	year = now_datetime().year
	if not frappe.get_list("Company"):
		setup_complete(
			{
				"currency": "MXN",
				"full_name": "Test User",
				"company_name": "Condominio Test LLC",
				"timezone": "America/Mexico_City",
				"company_abbr": "CT",
				"industry": "Real Estate",
				"country": "Mexico",
				"fy_start_date": f"{year}-01-01",
				"fy_end_date": f"{year}-12-31",
				"language": "spanish",
				"company_tagline": "Testing",
				"email": "test@condominium.com",
				"password": "test",
				"chart_of_accounts": "Standard",
			}
		)

	enable_all_roles_and_domains()
	frappe.db.commit()  # nosemgrep


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True

	if is_website_user():
		return False

	return True
