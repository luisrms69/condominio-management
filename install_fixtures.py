#!/usr/bin/env python3

import json
import os

import frappe


def install_fixtures():
	frappe.init(site="admin1.dev")
	frappe.connect()

	# Get app path
	app_path = frappe.get_app_path("condominium_management")
	fixtures_path = os.path.join(app_path, "fixtures")

	# Install fixtures
	fixture_files = [
		"company_type.json",
		"property_usage_type.json",
		"acquisition_type.json",
		"property_status_type.json",
		"policy_category.json",
		"enforcement_level.json",
		"user_type.json",
		"document_template_type.json",
		"jurisdiction_level.json",
		"compliance_requirement_type.json",
	]

	for fixture_file in fixture_files:
		fixture_path = os.path.join(fixtures_path, fixture_file)
		if os.path.exists(fixture_path):
			with open(fixture_path) as f:
				data = json.load(f)
				for record in data:
					doctype = record["doctype"]
					name = None
					if doctype == "Company Type":
						name = record["type_name"]
					elif doctype == "Property Usage Type":
						name = record["usage_name"]
					elif doctype == "Acquisition Type":
						name = record["acquisition_name"]
					elif doctype == "Property Status Type":
						name = record["status_name"]
					elif doctype == "Policy Category":
						name = record["category_name"]
					elif doctype == "Enforcement Level":
						name = record["level_name"]
					elif doctype == "User Type":
						name = record["user_type_name"]
					elif doctype == "Document Template Type":
						name = record["template_type_name"]
					elif doctype == "Jurisdiction Level":
						name = record["level_name"]
					elif doctype == "Compliance Requirement Type":
						name = record["requirement_name"]

					if name and not frappe.db.exists(doctype, name):
						doc = frappe.get_doc(record)
						doc.insert(ignore_permissions=True)
						print(f"Created {doctype}: {name}")
					else:
						print(f"Skipped {doctype}: {name} (already exists)")

	frappe.db.commit()
	print("✅ Fixtures installed successfully")


if __name__ == "__main__":
	install_fixtures()
