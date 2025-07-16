#!/usr/bin/env python3
"""
Script para corregir TODOS los errores de decoradores mal posicionados en Layer 4
"""

import os
import re
from pathlib import Path


def fix_decorator_indentation(file_path):
	"""Fix all decorator positioning issues in a file"""

	with open(file_path, encoding="utf-8") as f:
		content = f.read()

	original_content = content

	# Pattern 1: Fix @skip_if_ci_cd inside function
	pattern1 = r'(\tdef [^:]*:)\n(\t@skip_if_ci_cd)\n(\t\t""".*?""")'
	replacement1 = r"\t@skip_if_ci_cd\n\1\n\3"
	content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

	# Pattern 2: Fix @mock_sql_operations_in_ci_cd inside function
	pattern2 = r'(\tdef [^:]*:)\n(\t@mock_sql_operations_in_ci_cd)\n(\t\t""".*?""")'
	replacement2 = r"\t@mock_sql_operations_in_ci_cd\n\1\n\3"
	content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

	# Check if file was modified
	if content != original_content:
		with open(file_path, "w", encoding="utf-8") as f:
			f.write(content)
		print(f"✅ Fixed decorator positioning in: {file_path}")
		return True

	return False


def main():
	"""Fix all Layer 4 files"""

	print("🔧 Fixing all decorator positioning errors in Layer 4 files...")

	base_path = Path("./condominium_management/financial_management/doctype")
	files_fixed = 0

	# Find all Layer 4A and 4B files
	for pattern in ["*l4a_configuration.py", "*l4b_performance.py"]:
		for file_path in base_path.glob(f"*/{pattern}"):
			if fix_decorator_indentation(file_path):
				files_fixed += 1

	print(f"✅ Fixed decorator positioning in {files_fixed} files")
	print("🚀 All Layer 4 decorator errors should be resolved!")


if __name__ == "__main__":
	main()
