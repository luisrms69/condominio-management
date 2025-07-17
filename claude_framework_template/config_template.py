#!/usr/bin/env python3
"""
CLAUDE FRAMEWORK CONFIG TEMPLATE
Configuración base para nuevas apps Frappe Framework
"""

import json
import os
from typing import Optional


class ClaudeFrameworkConfig:
	"""
	Configuración centralizada para Claude Framework en apps Frappe
	"""

	def __init__(self, app_name: str):
		self.app_name = app_name
		self.config_file = f"{app_name}_claude_config.json"

	@property
	def default_config(self) -> dict:
		"""Configuración por defecto para cualquier app Frappe"""
		return {
			# Información básica de la app
			"app_info": {
				"app_name": "{{APP_NAME}}",
				"app_title": "{{APP_TITLE}}",
				"app_publisher": "{{APP_PUBLISHER}}",
				"app_description": "{{APP_DESCRIPTION}}",
				"app_email": "{{APP_EMAIL}}",
				"app_license": "MIT",
			},
			# Configuración de desarrollo
			"development": {
				"primary_language": "{{PRIMARY_LANGUAGE}}",
				"dev_site": "{{DEV_SITE}}",
				"test_sites": "{{TEST_SITES}}",
				"git_main_branch": "{{MAIN_BRANCH}}",
				"conventional_commit_scopes": "{{COMMIT_SCOPES}}",
			},
			# Dependencias de la app
			"dependencies": {
				"required_apps": "{{REQUIRED_APPS}}",
				"python_version": "3.10+",
				"frappe_version": "15.x",
				"node_version": "18.x",
			},
			# Configuración de módulos
			"modules": {
				"business_domain": "{{BUSINESS_DOMAIN}}",
				"initial_modules": "{{INITIAL_MODULES}}",
				"module_icon_pack": "octicon",
				"module_color_scheme": "blue",
			},
			# Configuración de hooks
			"hooks": {
				"use_universal_hooks": False,  # SIEMPRE False para evitar setup wizard conflicts
				"performance_monitoring": True,
				"auto_backup_before_migration": True,
				"enable_audit_trail": True,
			},
			# Configuración de testing
			"testing": {
				"test_runner": "FrappeTestCase",
				"coverage_threshold": 80,
				"require_tests_for_new_doctypes": True,
				"auto_run_tests_on_hooks_change": True,
			},
			# Configuración de CI/CD
			"cicd": {
				"enable_github_actions": True,
				"enable_pre_commit_hooks": True,
				"yarn_registry": "https://registry.npmjs.org/",
				"yarn_timeout": 600000,
				"yarn_retries": 3,
			},
			# Rutas críticas
			"paths": {
				"claude_md": "CLAUDE.md",
				"docs_core": "docs/core/",
				"docs_operational": "docs/operational/",
				"docs_workflows": "docs/workflows/",
				"hooks_file": "hooks.py",
				"translations_dir": "translations/",
			},
		}

	def generate_app_config(self, **kwargs) -> dict:
		"""
		Generar configuración específica para una app

		Args:
		    **kwargs: Variables de configuración específicas

		Returns:
		    Dict: Configuración personalizada para la app
		"""
		config = self.default_config.copy()

		# Reemplazar placeholders con valores reales
		config_str = json.dumps(config)
		for key, value in kwargs.items():
			placeholder = f"{{{{{key.upper()}}}}}"
			# Escapar comillas para valores JSON válidos
			if isinstance(value, str) and (value.startswith("[") or value.startswith("{")):
				# Es JSON string, usar directamente
				config_str = config_str.replace(f'"{placeholder}"', value)
			else:
				# Es string normal, mantener comillas
				config_str = config_str.replace(placeholder, str(value))

		try:
			return json.loads(config_str)
		except json.JSONDecodeError as e:
			print(f"Error JSON en posición {e.pos}: {config_str[max(0, e.pos - 50) : e.pos + 50]}")
			raise

	def save_config(self, config: dict) -> str:
		"""
		Guardar configuración en archivo JSON

		Args:
		    config: Configuración a guardar

		Returns:
		    str: Ruta del archivo guardado
		"""
		with open(self.config_file, "w", encoding="utf-8") as f:
			json.dump(config, f, indent=2, ensure_ascii=False)

		return os.path.abspath(self.config_file)

	def load_config(self) -> dict | None:
		"""
		Cargar configuración desde archivo

		Returns:
		    Dict o None: Configuración cargada o None si no existe
		"""
		if os.path.exists(self.config_file):
			with open(self.config_file, encoding="utf-8") as f:
				return json.load(f)
		return None

	def validate_config(self, config: dict) -> list[str]:
		"""
		Validar configuración

		Args:
		    config: Configuración a validar

		Returns:
		    List[str]: Lista de errores encontrados
		"""
		errors = []

		# Validar campos obligatorios
		required_fields = [
			"app_info.app_name",
			"app_info.app_title",
			"development.primary_language",
			"development.dev_site",
			"dependencies.required_apps",
			"modules.business_domain",
		]

		for field in required_fields:
			keys = field.split(".")
			value = config
			try:
				for key in keys:
					value = value[key]
				if not value or (isinstance(value, str) and value.startswith("{{")):
					errors.append(f"Campo obligatorio no configurado: {field}")
			except KeyError:
				errors.append(f"Campo obligatorio faltante: {field}")

		# Validar idioma soportado
		supported_languages = ["es", "en", "fr", "de", "pt", "it"]
		lang = config.get("development", {}).get("primary_language", "")
		if lang not in supported_languages:
			errors.append(f"Idioma no soportado: {lang}. Soportados: {supported_languages}")

		# Validar nombre de app (sin caracteres especiales)
		app_name = config.get("app_info", {}).get("app_name", "")
		if not app_name.isidentifier():
			errors.append(f"Nombre de app inválido: {app_name}. Debe ser un identificador Python válido")

		return errors


# EJEMPLO DE USO
if __name__ == "__main__":
	# Crear configuración para nueva app
	config_generator = ClaudeFrameworkConfig("my_erp_app")

	# Generar configuración con valores específicos
	app_config = config_generator.generate_app_config(
		app_name="my_erp_app",
		app_title="My ERP Application",
		app_publisher="My Company",
		app_description="Sistema ERP personalizado",
		app_email="dev@mycompany.com",
		primary_language="es",
		dev_site="myerp.dev",
		test_site_1="test1.dev",
		test_site_2="test2.dev",
		main_branch="main",
		scope_1="inventory",
		scope_2="sales",
		required_apps='["erpnext"]',
		business_domain="Enterprise Resource Planning",
		initial_modules='["inventory", "sales"]',
	)

	# Validar configuración
	errors = config_generator.validate_config(app_config)
	if errors:
		print("❌ Errores en configuración:")
		for error in errors:
			print(f"  - {error}")
	else:
		print("✅ Configuración válida")

		# Guardar configuración
		config_file = config_generator.save_config(app_config)
		print(f"📁 Configuración guardada en: {config_file}")
