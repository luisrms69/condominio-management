import frappe

from condominium_management.testing_workflow import run_testing

frappe.init("condo1.dev")
frappe.connect()
frappe.set_user("Administrator")

result = run_testing()
