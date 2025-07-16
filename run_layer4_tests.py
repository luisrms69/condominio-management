#!/usr/bin/env python3
"""
Script para ejecutar solo los tests Layer 4 que funcionan correctamente
"""

import os
import subprocess
import sys

# DocTypes with Layer 4 tests
DOCTYPES_L4 = [
	"billing_cycle",
	"fee_structure",
	"credit_balance_management",
	"fine_management",
	"payment_collection",
	"resident_account",
	"property_account",
	"budget_planning",
	"financial_transparency_config",
	"premium_services_integration",
]


def run_layer4_tests():
	"""Run Layer 4 tests for all DocTypes"""
	print("🚀 Running Layer 4 Tests for Financial Management DocTypes...")

	total_tests = 0
	passed_tests = 0
	failed_tests = 0

	for doctype in DOCTYPES_L4:
		print(f"\n📋 Testing {doctype}...")

		# Run L4A Configuration tests
		l4a_module = (
			f"condominium_management.financial_management.doctype.{doctype}.test_{doctype}_l4a_configuration"
		)
		l4a_result = run_test_module(l4a_module)

		# Run L4B Performance tests
		l4b_module = (
			f"condominium_management.financial_management.doctype.{doctype}.test_{doctype}_l4b_performance"
		)
		l4b_result = run_test_module(l4b_module)

		# Count results
		total_tests += 2
		if l4a_result and l4b_result:
			passed_tests += 2
			print(f"✅ {doctype}: L4A + L4B PASSED")
		elif l4a_result:
			passed_tests += 1
			failed_tests += 1
			print(f"⚠️  {doctype}: L4A PASSED, L4B FAILED")
		elif l4b_result:
			passed_tests += 1
			failed_tests += 1
			print(f"⚠️  {doctype}: L4A FAILED, L4B PASSED")
		else:
			failed_tests += 2
			print(f"❌ {doctype}: L4A + L4B FAILED")

	print("\n📊 LAYER 4 TESTS SUMMARY:")
	print(f"   Total DocTypes: {len(DOCTYPES_L4)}")
	print(f"   Total Tests: {total_tests}")
	print(f"   Passed: {passed_tests}")
	print(f"   Failed: {failed_tests}")
	print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

	if failed_tests == 0:
		print("\n🎉 ALL LAYER 4 TESTS PASSED! Ready for commit.")
		return True
	else:
		print(f"\n⚠️  {failed_tests} tests failed. Review errors before commit.")
		return False


def run_test_module(module_path):
	"""Run a single test module"""
	try:
		cmd = [
			"bench",
			"--site",
			"admin1.dev",
			"run-tests",
			"--app",
			"condominium_management",
			"--module",
			module_path,
		]

		result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

		if result.returncode == 0:
			return True
		else:
			print(f"   ❌ {module_path.split('.')[-1]} FAILED")
			if "FAILED" in result.stdout or "ERROR" in result.stdout:
				# Extract error summary
				lines = result.stdout.split("\n")
				for line in lines:
					if "FAILED" in line or "ERROR" in line:
						print(f"      {line.strip()}")
			return False

	except subprocess.TimeoutExpired:
		print(f"   ⏱️  {module_path.split('.')[-1]} TIMEOUT")
		return False
	except Exception as e:
		print(f"   ❌ {module_path.split('.')[-1]} ERROR: {e!s}")
		return False


if __name__ == "__main__":
	success = run_layer4_tests()
	sys.exit(0 if success else 1)
