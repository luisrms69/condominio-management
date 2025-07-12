#!/usr/bin/env python3
"""
Auto-Generate Corrected Tests for Committee Management Module

This script analyzes DocType JSON files and generates corrected test files
with all required fields and proper master data setup.

Usage:
    python scripts/auto_generate_tests.py
    python scripts/auto_generate_tests.py --doctype "Agreement Tracking"
"""

import argparse
import glob
import json
import os
from pathlib import Path


def analyze_doctype_json(json_path):
	"""Analyze DocType JSON to extract required fields and dependencies."""
	with open(json_path) as f:
		doctype_data = json.load(f)

	analysis = {
		"doctype_name": doctype_data.get("name"),
		"module": doctype_data.get("module"),
		"required_fields": [],
		"link_fields": [],
		"child_tables": [],
		"field_types": {},
	}

	for field in doctype_data.get("fields", []):
		field_name = field.get("fieldname")
		field_type = field.get("fieldtype")
		is_required = field.get("reqd") == 1

		if field_name and field_type:
			analysis["field_types"][field_name] = field_type

			if is_required:
				analysis["required_fields"].append(
					{
						"fieldname": field_name,
						"fieldtype": field_type,
						"label": field.get("label"),
						"options": field.get("options"),
					}
				)

			if field_type == "Link":
				analysis["link_fields"].append(
					{"fieldname": field_name, "target_doctype": field.get("options"), "required": is_required}
				)

			if field_type == "Table":
				analysis["child_tables"].append(
					{"fieldname": field_name, "child_doctype": field.get("options")}
				)

	return analysis


def generate_test_setup_code(analysis):
	"""Generate setup code for test data creation."""
	setup_code = []

	# Generate master data creation based on Link fields
	master_doctypes = set()
	for link_field in analysis["link_fields"]:
		if link_field["target_doctype"]:
			master_doctypes.add(link_field["target_doctype"])

	setup_code.append("def create_test_masters(self):")
	setup_code.append('    """Create required master data for tests"""')

	for master_doctype in sorted(master_doctypes):
		if master_doctype in ["User", "Company", "Property Registry"]:
			setup_code.append(f"    # Create {master_doctype}")
			setup_code.append(
				f'    if not frappe.db.exists("{master_doctype}", "TEST-{master_doctype.upper()}-001"):'
			)
			setup_code.append("        # TODO: Implement master creation")
			setup_code.append("        pass")
			setup_code.append("")

	return "\n".join(setup_code)


def generate_test_creation_code(analysis):
	"""Generate test creation code with all required fields."""
	doctype_name = analysis["doctype_name"]
	var_name = doctype_name.lower().replace(" ", "_")

	creation_code = []
	creation_code.append(f"def test_{var_name}_creation(self):")
	creation_code.append(f'    """Test basic {doctype_name} creation"""')
	creation_code.append(f"    {var_name} = frappe.get_doc({{")
	creation_code.append(f'        "doctype": "{doctype_name}",')

	for field in analysis["required_fields"]:
		field_name = field["fieldname"]
		field_type = field["fieldtype"]

		if field_type == "Data":
			creation_code.append(f'        "{field_name}": "Test {field_name}",')
		elif field_type == "Date":
			creation_code.append(f'        "{field_name}": nowdate(),')
		elif field_type == "Datetime":
			creation_code.append(f'        "{field_name}": nowdate() + " 09:00:00",')
		elif field_type == "Time":
			creation_code.append(f'        "{field_name}": "09:00:00",')
		elif field_type == "Link":
			target = field.get("options", "Test")
			creation_code.append(f'        "{field_name}": "TEST-{target.upper()}-001",')
		elif field_type == "Select":
			options = field.get("options", "").split("\n")
			if options and options[0]:
				creation_code.append(f'        "{field_name}": "{options[0]}",')
		elif field_type == "Check":
			creation_code.append(f'        "{field_name}": 1,')
		elif field_type == "Int":
			creation_code.append(f'        "{field_name}": 1,')
		elif field_type == "Float" or field_type == "Currency":
			creation_code.append(f'        "{field_name}": 100.0,')
		else:
			creation_code.append(f'        "{field_name}": "Test Value",  # {field_type}')

	creation_code.append("    })")
	creation_code.append(f"    {var_name}.insert()")
	creation_code.append(f"    self.assertTrue({var_name}.name)")

	return "\n".join(creation_code)


def generate_complete_test_file(analysis):
	"""Generate complete test file content."""
	doctype_name = analysis["doctype_name"]
	class_name = doctype_name.replace(" ", "")

	template = f"""# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate

class Test{class_name}(FrappeTestCase):
    def setUp(self):
        \"\"\"Set up test data\"\"\"
        self.setup_test_data()

    def setup_test_data(self):
        \"\"\"Create test data for {doctype_name.lower()} tests\"\"\"
        # Create required master data
        self.create_test_masters()

        # Additional setup as needed

    {generate_test_setup_code(analysis)}

    {generate_test_creation_code(analysis)}

    # Additional test methods would be generated here
    # based on the specific DocType functionality
"""

	return template


def find_doctype_json_files():
	"""Find all DocType JSON files in Committee Management module."""
	pattern = "condominium_management/committee_management/doctype/*/*.json"
	json_files = []

	for file_path in glob.glob(pattern):
		# Only include main DocType JSON files (not child tables)
		file_name = os.path.basename(file_path)
		dir_name = os.path.basename(os.path.dirname(file_path))

		if file_name == f"{dir_name}.json":
			json_files.append(file_path)

	return json_files


def main():
	parser = argparse.ArgumentParser(description="Auto-generate corrected tests for Committee Management")
	parser.add_argument("--doctype", help="Specific DocType to generate test for")
	parser.add_argument(
		"--output-dir", default="generated_tests", help="Output directory for generated tests"
	)
	args = parser.parse_args()

	# Create output directory
	os.makedirs(args.output_dir, exist_ok=True)

	# Find DocType JSON files
	json_files = find_doctype_json_files()

	if args.doctype:
		# Filter for specific DocType
		json_files = [f for f in json_files if args.doctype.lower().replace(" ", "_") in f]

	print(f"Found {len(json_files)} DocType JSON files to process")

	for json_path in json_files:
		print(f"\\nProcessing: {json_path}")

		try:
			# Analyze DocType
			analysis = analyze_doctype_json(json_path)
			doctype_name = analysis["doctype_name"]

			print(f"  DocType: {doctype_name}")
			print(f"  Required fields: {len(analysis['required_fields'])}")
			print(f"  Link fields: {len(analysis['link_fields'])}")

			# Generate test file
			test_content = generate_complete_test_file(analysis)

			# Write to output
			test_filename = f"test_{doctype_name.lower().replace(' ', '_')}_generated.py"
			output_path = os.path.join(args.output_dir, test_filename)

			with open(output_path, "w") as f:
				f.write(test_content)

			print(f"  Generated: {output_path}")

			# Print analysis summary
			print("  Analysis Summary:")
			for field in analysis["required_fields"]:
				print(f"    - {field['fieldname']} ({field['fieldtype']}) - REQUIRED")

		except Exception as e:
			print(f"  ERROR: {e!s}")

	print(f"\\nGeneration complete. Check {args.output_dir}/ for generated test files.")
	print("\\nNext steps:")
	print("1. Review generated test files")
	print("2. Copy corrected tests to replace existing ones")
	print("3. Run tests locally to verify")
	print("4. Commit and push to trigger GitHub Actions workflow")


if __name__ == "__main__":
	main()
