#!/usr/bin/env python3
"""
Debug script para configuración
"""

import json

from config_template import ClaudeFrameworkConfig

# Crear configuración de prueba
config_generator = ClaudeFrameworkConfig("test_erp")
config = config_generator.generate_app_config(
	app_name="test_erp",
	app_title="Test ERP System",
	app_publisher="Test Company",
	app_description="App Frappe: Test ERP System",
	app_email="dev@testcompany.com",
	primary_language="es",
	dev_site="test.dev",
	test_sites='["test1.dev", "test2.dev"]',
	main_branch="main",
	commit_scopes='["core", "setup", "tests", "docs", "config"]',
	required_apps='["frappe"]',
	business_domain="Test ERP System",
	initial_modules='["core"]',
)

print("CONFIG DEBUG:")
print(json.dumps(config, indent=2))
