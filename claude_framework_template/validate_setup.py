#!/usr/bin/env python3
"""
VALIDADOR DE SETUP CLAUDE FRAMEWORK
Script para validar que la instalación fue exitosa
"""

import argparse
import json
import os
import sys
from pathlib import Path


class ClaudeFrameworkValidator:
	"""
	Validador de configuración e instalación de Claude Framework
	"""

	def __init__(self, app_path: str = "."):
		self.app_path = Path(app_path).resolve()
		self.errors = []
		self.warnings = []
		self.info = []

	def validate_critical_files(self) -> bool:
		"""Validar que existen archivos críticos"""
		critical_files = [
			"CLAUDE.md",
			"docs/core/CLAUDE_CONFIG.md",
			"docs/operational/MODULE_STATUS.md",
			"claude_framework_config.json",
		]

		missing_files = []
		for file in critical_files:
			if not (self.app_path / file).exists():
				missing_files.append(file)

		if missing_files:
			self.errors.append(f"Archivos críticos faltantes: {', '.join(missing_files)}")
			return False

		self.info.append("✅ Todos los archivos críticos presentes")
		return True

	def validate_claude_md(self) -> bool:
		"""Validar contenido de CLAUDE.md"""
		claude_file = self.app_path / "CLAUDE.md"

		if not claude_file.exists():
			self.errors.append("CLAUDE.md no existe")
			return False

		with open(claude_file, encoding="utf-8") as f:
			content = f.read()

		# Verificar que no hay placeholders sin reemplazar
		if "{{" in content and "}}" in content:
			self.errors.append("CLAUDE.md contiene placeholders sin reemplazar")
			return False

		# Verificar longitud
		lines = content.split("\n")
		if len(lines) > 300:
			self.warnings.append(f"CLAUDE.md tiene {len(lines)} líneas (recomendado <300)")
		else:
			self.info.append(f"✅ CLAUDE.md tiene {len(lines)} líneas (<300)")

		# Verificar secciones obligatorias
		required_sections = ["REGLAS CRÍTICAS", "ESTADO ACTUAL", "COMANDOS FRECUENTES"]

		for section in required_sections:
			if section not in content:
				self.warnings.append(f"Sección recomendada faltante en CLAUDE.md: {section}")

		return True

	def validate_config_file(self) -> bool:
		"""Validar archivo de configuración JSON"""
		config_file = self.app_path / "claude_framework_config.json"

		if not config_file.exists():
			self.errors.append("claude_framework_config.json no existe")
			return False

		try:
			with open(config_file, encoding="utf-8") as f:
				config = json.load(f)

			# Validar estructura básica
			required_sections = ["app_info", "development", "dependencies", "modules"]
			for section in required_sections:
				if section not in config:
					self.errors.append(f"Sección faltante en config: {section}")
					return False

			# Validar campos críticos
			app_name = config.get("app_info", {}).get("app_name", "")
			if not app_name or not app_name.isidentifier():
				self.errors.append(f"app_name inválido: {app_name}")
				return False

			self.info.append(f"✅ Configuración válida para app: {app_name}")
			return True

		except json.JSONDecodeError as e:
			self.errors.append(f"Error JSON en config file: {e}")
			return False

	def validate_docs_structure(self) -> bool:
		"""Validar estructura de directorio docs/"""
		docs_dir = self.app_path / "docs"

		if not docs_dir.exists():
			self.errors.append("Directorio docs/ no existe")
			return False

		required_subdirs = ["core", "operational", "workflows"]
		missing_dirs = []

		for subdir in required_subdirs:
			if not (docs_dir / subdir).exists():
				missing_dirs.append(subdir)

		if missing_dirs:
			self.errors.append(f"Subdirectorios faltantes en docs/: {', '.join(missing_dirs)}")
			return False

		self.info.append("✅ Estructura docs/ correcta")
		return True

	def validate_scripts(self) -> bool:
		"""Validar scripts generados"""
		scripts_dir = self.app_path / "scripts"

		if not scripts_dir.exists():
			self.warnings.append("Directorio scripts/ no existe")
			return False

		expected_scripts = ["generate_module_hooks.py"]
		missing_scripts = []

		for script in expected_scripts:
			script_path = scripts_dir / script
			if not script_path.exists():
				missing_scripts.append(script)
			elif not os.access(script_path, os.X_OK):
				self.warnings.append(f"Script no ejecutable: {script}")

		if missing_scripts:
			self.warnings.append(f"Scripts faltantes: {', '.join(missing_scripts)}")
		else:
			self.info.append("✅ Scripts generados y ejecutables")

		return len(missing_scripts) == 0

	def validate_pre_commit(self) -> bool:
		"""Validar configuración pre-commit"""
		precommit_file = self.app_path / ".pre-commit-config.yaml"

		if not precommit_file.exists():
			self.warnings.append(".pre-commit-config.yaml no existe")
			return False

		with open(precommit_file) as f:
			content = f.read()

		# Verificar hooks básicos
		basic_hooks = ["ruff", "trailing-whitespace", "check-json"]
		missing_hooks = []

		for hook in basic_hooks:
			if hook not in content:
				missing_hooks.append(hook)

		if missing_hooks:
			self.warnings.append(f"Pre-commit hooks faltantes: {', '.join(missing_hooks)}")
		else:
			self.info.append("✅ Pre-commit hooks configurados")

		return len(missing_hooks) == 0

	def validate_frappe_compatibility(self) -> bool:
		"""Validar compatibilidad con Frappe Framework"""
		# Verificar que estamos en entorno Frappe
		if not any((self.app_path / f).exists() for f in ["hooks.py", "pyproject.toml", "setup.py"]):
			self.warnings.append("No parece ser una app Frappe válida (falta hooks.py/pyproject.toml)")
			return False

		# Verificar hooks.py si existe
		hooks_file = self.app_path / "hooks.py"
		if hooks_file.exists():
			with open(hooks_file) as f:
				hooks_content = f.read()

			if "app_name" not in hooks_content:
				self.warnings.append("hooks.py no contiene app_name")

		self.info.append("✅ Estructura compatible con Frappe Framework")
		return True

	def validate_template_integrity(self) -> bool:
		"""Validar integridad del template"""
		template_dir = self.app_path / "claude_framework_template"

		if not template_dir.exists():
			self.warnings.append("Directorio claude_framework_template/ no preservado")
			return False

		template_files = ["setup_claude_framework.py", "config_template.py", "README.md"]

		missing_template_files = []
		for file in template_files:
			if not (template_dir / file).exists():
				missing_template_files.append(file)

		if missing_template_files:
			self.warnings.append(f"Archivos template faltantes: {', '.join(missing_template_files)}")
		else:
			self.info.append("✅ Template preservado para reutilización")

		return len(missing_template_files) == 0

	def run_full_validation(self) -> tuple[bool, dict]:
		"""Ejecutar validación completa"""
		results = {
			"critical_files": self.validate_critical_files(),
			"claude_md": self.validate_claude_md(),
			"config_file": self.validate_config_file(),
			"docs_structure": self.validate_docs_structure(),
			"scripts": self.validate_scripts(),
			"pre_commit": self.validate_pre_commit(),
			"frappe_compatibility": self.validate_frappe_compatibility(),
			"template_integrity": self.validate_template_integrity(),
		}

		# Determinar éxito general
		critical_checks = ["critical_files", "claude_md", "config_file", "docs_structure"]
		success = all(results[check] for check in critical_checks)

		return success, results

	def print_results(self, success: bool, results: dict) -> None:
		"""Imprimir resultados de validación"""
		print("\n" + "=" * 60)
		print("🔍 RESULTADO DE VALIDACIÓN CLAUDE FRAMEWORK")
		print("=" * 60)

		if success:
			print("✅ VALIDACIÓN EXITOSA - Setup completo y funcional")
		else:
			print("❌ VALIDACIÓN FALLIDA - Requiere correcciones")

		print("\n📊 RESUMEN:")
		print(f"  ✅ Checks exitosos: {sum(results.values())}")
		print(f"  ❌ Checks fallidos: {len(results) - sum(results.values())}")
		print(f"  ⚠️  Advertencias: {len(self.warnings)}")
		print(f"  i  Información: {len(self.info)}")

		# Mostrar errores
		if self.errors:
			print("\n❌ ERRORES CRÍTICOS:")
			for error in self.errors:
				print(f"  - {error}")

		# Mostrar advertencias
		if self.warnings:
			print("\n⚠️ ADVERTENCIAS:")
			for warning in self.warnings:
				print(f"  - {warning}")

		# Mostrar información
		if self.info:
			print("\n✅ INFORMACIÓN:")
			for info in self.info:
				print(f"  - {info}")

		print("\n" + "=" * 60)

		if success:
			print("🎉 ¡Setup de Claude Framework completado exitosamente!")
			print("📖 Próximo paso: Revisar CLAUDE.md para comenzar desarrollo")
		else:
			print("🛠️ Corrije los errores críticos y ejecuta validación nuevamente")
			print("💡 Usa: python claude_framework_template/validate_setup.py")


def main():
	"""Función principal CLI"""
	parser = argparse.ArgumentParser(description="Validar setup de Claude Framework")
	parser.add_argument("--path", default=".", help="Ruta de la app a validar")
	parser.add_argument("--full-check", action="store_true", help="Validación completa")
	parser.add_argument("--quiet", action="store_true", help="Solo mostrar errores")

	args = parser.parse_args()

	validator = ClaudeFrameworkValidator(args.path)

	if args.full_check:
		success, results = validator.run_full_validation()
	else:
		# Validación básica
		success = (
			validator.validate_critical_files()
			and validator.validate_claude_md()
			and validator.validate_config_file()
		)
		results = {"basic_validation": success}

	if not args.quiet:
		validator.print_results(success, results)

	# Exit code para scripts automatizados
	sys.exit(0 if success else 1)


if __name__ == "__main__":
	main()
