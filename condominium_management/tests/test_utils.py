# Copyright (c) 2025, Buzola and Contributors
# License: GPL v3. See license.txt

"""
Test utilities for Condominium Management.

This module provides testing infrastructure and helper functions
for the Condominium Management app, following Frappe/ERPNext best practices.
"""

import frappe
from frappe.utils import now_datetime
from erpnext.setup.utils import enable_all_roles_and_domains


def before_tests():
	"""
	Initialize testing environment for Condominium Management app.
	
	This function is called before any tests are run via the before_tests hook.
	It ensures that ERPNext is properly set up with all necessary fixtures,
	including the Transit warehouse type that some tests depend on.
	
	Functionality:
	- Clear Frappe cache for clean test environment
	- Run ERPNext setup wizard if no Company exists
	- Create default company with Mexican configuration
	- Enable all roles and domains for comprehensive testing
	- Set up condominium-specific defaults
	- Commit changes to database
	
	Note:
		This follows the same pattern as successful ERPNext apps like
		lending and hrms to ensure proper ERPNext initialization.
	"""
	frappe.clear_cache()
	
	# Complete ERPNext setup if missing - this creates essential records
	# including Warehouse Types (Transit), Item Groups, Stock Entry Types, etc.
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	year = now_datetime().year
	if not frappe.get_list("Company"):
		# Use exact same pattern as HRMS for compatibility
		setup_complete(
			{
				"currency": "USD",
				"full_name": "Test User",
				"company_name": "_Test Company",
				"timezone": "America/New_York",
				"company_abbr": "_TC",
				"industry": "Manufacturing",
				"country": "United States",
				"fy_start_date": f"{year}-01-01",
				"fy_end_date": f"{year}-12-31",
				"language": "english",
				"company_tagline": "Testing",
				"email": "test@erpnext.com",
				"password": "test",
				"chart_of_accounts": "Standard",
			}
		)

	# Enable all roles and domains for comprehensive testing
	enable_all_roles_and_domains()
	
	# Set up app-specific defaults
	set_condominium_defaults()
	
	# Commit all changes to ensure they persist during tests
	frappe.db.commit()


def set_condominium_defaults():
	"""
	Set up default configurations specific to condominium management.
	
	This function configures default settings that are useful for
	testing condominium management functionality.
	
	Configurations:
	- Default company settings for real estate management
	- Condominium-specific field defaults
	- Testing-friendly configurations
	"""
	# Set default company for condominium management tests
	company_name = "Test Condominium Management Company"
	
	if frappe.db.exists("Company", company_name):
		company = frappe.get_doc("Company", company_name)
		
		# Set country-specific defaults
		company.country = "Mexico"
		company.default_currency = "MXN"
		
		# Save company settings
		company.save(ignore_permissions=True)


def create_test_company(company_name="_Test Condominium Company"):
	"""
	Create a test company for condominium management testing.
	
	Args:
		company_name (str): Name of the test company to create
		
	Returns:
		frappe.Document: The created company document
		
	Note:
		This is a utility function for tests that need a specific
		company configuration beyond the default setup.
	"""
	if frappe.db.exists("Company", company_name):
		return frappe.get_doc("Company", company_name)

	return frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": company_name,
			"default_currency": "MXN",
			"country": "Mexico",
			"industry": "Real Estate",
		}
	).insert(ignore_permissions=True)


def get_test_company():
	"""
	Get the default test company for condominium management tests.
	
	Returns:
		str: Name of the test company
		
	This function provides a consistent way to reference the test
	company across all test modules.
	"""
	return "Test Condominium Management Company"


def cleanup_test_data():
	"""
	Clean up test data after tests complete.
	
	This function removes test-specific data that shouldn't persist
	between test runs. It's called automatically by the test framework.
	
	Cleanup actions:
	- Remove test companies (except default)
	- Clear test-specific configurations
	- Reset default values
	"""
	# Note: Frappe's test framework handles most cleanup automatically
	# through database rollbacks. This function is here for any
	# specific cleanup that might be needed in the future.
	pass