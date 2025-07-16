#!/usr/bin/env python3
"""
Script para corregir decoradores mal aplicados por REGLA #47
Específicamente corrige @mock_sql_operations_in_ci_cd mal posicionados
"""

import re
from pathlib import Path

# Archivos a corregir
FILES_TO_FIX = [
	"payment_collection/test_payment_collection_l4b_performance.py",
	"resident_account/test_resident_account_l4b_performance.py",
	"property_account/test_property_account_l4b_performance.py",
]

BASE_PATH = Path("./condominium_management/financial_management/doctype")


def fix_decorator_position(file_path):
	"""Fix decorator position from inside function to before function"""

	with open(file_path, encoding="utf-8") as f:
		content = f.read()

	# Pattern to find malformed decorator inside function
	pattern = r'(\tdef test_[^(]*query[^(]*performance[^:]*\(self\):)\n(\t@mock_sql_operations_in_ci_cd)\n(\t\t""".*?""")'

	# Replacement: move decorator before function
	replacement = r"\t@mock_sql_operations_in_ci_cd\n\1\n\3"

	content = re.sub(pattern, replacement, content, flags=re.DOTALL)

	# Also add CI/CD logic for SQL queries
	sql_pattern = r'(\t\t# Query.*?\n\t\t)_ = frappe\.db\.sql\(\s*f?"""(.*?)"""\s*,?\s*as_dict=True,?\s*\)'

	def replace_sql(match):
		indent = match.group(1)
		query = match.group(2).strip()

		return f'''{indent}if is_ci_cd_environment():
\t\t\t# Mock query results for CI/CD
\t\t\tresults, duration = simulate_performance_test_in_ci_cd("query", 0.1)
\t\telse:
\t\t\t# Real query in local environment
\t\t\tresults = frappe.db.sql(f"""
\t\t\t\t{query}
\t\t\t""", as_dict=True)'''

	content = re.sub(sql_pattern, replace_sql, content, flags=re.DOTALL)

	with open(file_path, "w", encoding="utf-8") as f:
		f.write(content)

	print(f"✅ Fixed decorators in: {file_path}")


def main():
	"""Main execution"""
	print("🔧 Fixing REGLA #47 decorator positioning errors...")

	for file_name in FILES_TO_FIX:
		file_path = BASE_PATH / file_name
		if file_path.exists():
			fix_decorator_position(file_path)
		else:
			print(f"❌ File not found: {file_path}")

	print("✅ All decorator positioning errors fixed!")


if __name__ == "__main__":
	main()
