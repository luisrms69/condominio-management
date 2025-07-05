#!/usr/bin/env python3
"""
CLAUDE FRAMEWORK SETUP SCRIPT
Script principal para configurar Claude Framework en apps Frappe
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from config_template import ClaudeFrameworkConfig

class ClaudeFrameworkSetup:
    """
    Configurador automático de Claude Framework para apps Frappe
    """
    
    def __init__(self, app_path: str):
        self.app_path = Path(app_path).resolve()
        self.template_path = Path(__file__).parent
        self.config_generator = ClaudeFrameworkConfig("")
        
    def detect_app_info(self) -> Dict:
        """
        Detectar información automáticamente desde la app existente
        """
        app_info = {}
        
        # Detectar nombre de app desde hooks.py
        hooks_file = self.app_path / "hooks.py"
        if hooks_file.exists():
            with open(hooks_file, 'r') as f:
                content = f.read()
                # Buscar app_name
                for line in content.split('\n'):
                    if line.startswith('app_name ='):
                        app_info['app_name'] = line.split('=')[1].strip().strip('"\'')
                        break
        
        # Detectar desde pyproject.toml o setup.py
        pyproject_file = self.app_path / "pyproject.toml"
        setup_file = self.app_path / "setup.py"
        
        if pyproject_file.exists():
            # Leer pyproject.toml
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    pyproject = tomli.load(f)
                    project = pyproject.get('project', {})
                    app_info.update({
                        'app_title': project.get('name', ''),
                        'app_description': project.get('description', ''),
                        'app_publisher': project.get('authors', [{}])[0].get('name', '') if project.get('authors') else '',
                        'app_email': project.get('authors', [{}])[0].get('email', '') if project.get('authors') else ''
                    })
            except ImportError:
                print("⚠️ tomli no disponible para leer pyproject.toml")
        
        # Fallback: usar nombre del directorio
        if not app_info.get('app_name'):
            app_info['app_name'] = self.app_path.name
        
        return app_info
    
    def create_backup(self) -> str:
        """
        Crear backup completo antes de modificaciones
        """
        backup_dir = self.app_path / f"claude_framework_backup_{int(__import__('time').time())}"
        
        # Backup de archivos críticos
        critical_files = [
            "CLAUDE.md",
            "docs/",
            "hooks.py",
            ".github/workflows/",
            ".pre-commit-config.yaml"
        ]
        
        backup_dir.mkdir(exist_ok=True)
        
        for item in critical_files:
            source = self.app_path / item
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, backup_dir / source.name)
                else:
                    shutil.copytree(source, backup_dir / source.name, dirs_exist_ok=True)
        
        print(f"✅ Backup creado en: {backup_dir}")
        return str(backup_dir)
    
    def generate_templates(self, config: Dict) -> None:
        """
        Generar archivos desde templates con configuración
        """
        templates = {
            "CLAUDE.md.template": "CLAUDE.md",
            "docs/core/CLAUDE_CONFIG.md.template": "docs/core/CLAUDE_CONFIG.md",
            "docs/operational/MODULE_STATUS.md.template": "docs/operational/MODULE_STATUS.md",
            "docs/workflows/NEW_MODULE_PROCESS.md.template": "docs/workflows/NEW_MODULE_PROCESS.md",
            "docs/workflows/TROUBLESHOOTING_CI.md.template": "docs/workflows/TROUBLESHOOTING_CI.md"
        }
        
        for template_file, output_file in templates.items():
            self._process_template(template_file, output_file, config)
    
    def _process_template(self, template_file: str, output_file: str, config: Dict) -> None:
        """
        Procesar un template individual
        """
        # Leer template (desde sistema actual primero, luego desde templates)
        template_content = self._get_template_content(template_file)
        
        # Reemplazar placeholders
        processed_content = self._replace_placeholders(template_content, config)
        
        # Escribir archivo de salida
        output_path = self.app_path / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"✅ Generado: {output_file}")
    
    def _get_template_content(self, template_file: str) -> str:
        """
        Obtener contenido de template desde sistema actual o template base
        """
        # Primero intentar desde sistema actual (como base)
        if template_file.endswith('.template'):
            actual_file = template_file.replace('.template', '')
            actual_path = self.app_path / actual_file
            
            if actual_path.exists():
                with open(actual_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # Fallback: template base (crear template básico)
        return self._create_basic_template(template_file)
    
    def _create_basic_template(self, template_file: str) -> str:
        """
        Crear template básico cuando no existe archivo base
        """
        if "CLAUDE.md" in template_file:
            return '''# 🤖 CLAUDE - {{APP_TITLE}}

**MEMORIA OPERACIONAL PERMANENTE - CONFIGURACIÓN MODULAR**

## 📋 **REGLAS CRÍTICAS INMUTABLES**
👉 **[CONFIGURACIÓN COMPLETA](docs/core/CLAUDE_CONFIG.md)**

### **TOP 5 REGLAS MÁS CRÍTICAS:**
1. **🇪🇸 Etiquetas en español** - TODAS las labels de DocTypes en {{PRIMARY_LANGUAGE}} SIEMPRE
2. **🧪 Tests obligatorios** - Cada DocType DEBE tener tests con FrappeTestCase
3. **🔧 Hooks específicos** - NO universales (bloqueados por setup wizard)
4. **🌿 Branch strategy** - Nunca trabajar en {{MAIN_BRANCH}}, siempre feature/ branches
5. **✅ Verificación OBLIGATORIA** - Tests después de modificar hooks.py

## 🏗️ **ESTADO ACTUAL DEL PROYECTO**
👉 **[ESTADO COMPLETO](docs/operational/MODULE_STATUS.md)**

### **🔄 EN DESARROLLO:**
- **{{BUSINESS_DOMAIN}}** - Iniciando desarrollo

## 📝 **COMANDOS FRECUENTES**

### **Testing (OBLIGATORIO después de hooks.py):**
```bash
# Verificar TODOS los módulos
bench --site {{DEV_SITE}} run-tests --app {{APP_NAME}}

# Test específico por DocType  
bench --site {{DEV_SITE}} run-tests --doctype "DocType Name"
```

### **Desarrollo:**
```bash
# Migrar cambios
bench --site {{DEV_SITE}} migrate
bench --site {{DEV_SITE}} build
```

---

**Última actualización:** {{CURRENT_DATE}}  
**Líneas totales:** <300 (cumple límite establecido)'''
        
        elif "MODULE_STATUS.md" in template_file:
            return '''# 📊 ESTADO OPERACIONAL DE MÓDULOS

## ✅ MÓDULOS COMPLETOS:
(Ninguno aún)

## 🔄 EN DESARROLLO:
- **{{INITIAL_MODULES}}**: 🔄 INICIANDO - Hooks: ❌ | Tests: ❌

## 📅 PLANIFICADOS:
(Por definir)

---
**Última actualización**: {{CURRENT_DATE}}  
**Total módulos**: {{MODULE_COUNT}} módulos planificados  
**Completados**: 0/{{MODULE_COUNT}} (0%)'''
        
        elif "CLAUDE_CONFIG.md" in template_file:
            return '''# 🤖 CONFIGURACIÓN PERMANENTE CLAUDE CODE - {{APP_TITLE}}

**ARCHIVO INMUTABLE - NO MODIFICAR SIN APROBACIÓN USUARIO**

## 🎯 **SEPARACIÓN CRÍTICA DE RESPONSABILIDADES**

### **📁 UBICACIONES FÍSICAS DEFINITIVAS:**

#### **A. MEMORIA OPERACIONAL CLAUDE CODE:**
```
CLAUDE.md                              # Índice principal (MAX 300 líneas)
docs/core/                            # Reglas y configuración inmutable
docs/operational/                     # Estado actual del proyecto
docs/workflows/                       # Procesos de desarrollo
```

#### **B. CÓDIGO FRAPPE:**
```
{{APP_NAME}}/                         # Código fuente del sistema
```

## 🚨 **REGLAS INMUTABLES**

### **ESTRUCTURA:**
1. **CLAUDE.md**: Máximo 300 líneas (solo índice + reglas críticas)
2. **docs/core/**: NUNCA modificar sin aprobación usuario
3. **docs/operational/**: Actualizar frecuentemente con estado real

---

**FECHA CREACIÓN:** {{CURRENT_DATE}}  
**ESTADO:** ACTIVO - CONFIGURACIÓN PERMANENTE  
**APP:** {{APP_NAME}} v1.0.0'''
        
        return f"# Template para {template_file}\n\nPlaceholder content for {template_file}"
    
    def _replace_placeholders(self, content: str, config: Dict) -> str:
        """
        Reemplazar placeholders en contenido
        """
        from datetime import datetime
        
        # Crear diccionario plano de reemplazos
        replacements = {
            "APP_NAME": config['app_info']['app_name'],
            "APP_TITLE": config['app_info']['app_title'],
            "APP_PUBLISHER": config['app_info']['app_publisher'],
            "APP_DESCRIPTION": config['app_info']['app_description'],
            "APP_EMAIL": config['app_info']['app_email'],
            "PRIMARY_LANGUAGE": config['development']['primary_language'],
            "DEV_SITE": config['development']['dev_site'],
            "MAIN_BRANCH": config['development']['git_main_branch'],
            "BUSINESS_DOMAIN": config['modules']['business_domain'],
            "INITIAL_MODULES": config['modules']['initial_modules'] if isinstance(config['modules']['initial_modules'], str) else ', '.join(config['modules']['initial_modules']),
            "MODULE_COUNT": str(len(config['modules']['initial_modules']) if isinstance(config['modules']['initial_modules'], list) else 1),
            "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
            "REQUIRED_APPS": config['dependencies']['required_apps'] if isinstance(config['dependencies']['required_apps'], str) else ', '.join(config['dependencies']['required_apps'])
        }
        
        # Reemplazar placeholders
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value))
        
        return content
    
    def setup_development_tools(self, config: Dict) -> None:
        """
        Configurar herramientas de desarrollo
        """
        # Crear .pre-commit-config.yaml si no existe
        precommit_file = self.app_path / ".pre-commit-config.yaml"
        if not precommit_file.exists():
            precommit_content = '''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-json
      - id: check-yaml
      - id: check-ast'''
            
            with open(precommit_file, 'w') as f:
                f.write(precommit_content)
            print("✅ Configurado: .pre-commit-config.yaml")
        
        # Crear directorio scripts si no existe
        scripts_dir = self.app_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Crear script de generación de hooks
        hooks_script = scripts_dir / "generate_module_hooks.py"
        if not hooks_script.exists():
            hooks_content = f'''#!/usr/bin/env python3
"""
Generador de hooks específicos para módulos de {config['app_info']['app_name']}
"""

def generate_hooks_for_module(module_name: str) -> str:
    """Generar hooks específicos para un módulo"""
    hooks_code = f"""
# Hooks para módulo {{module_name}}
doc_events = {{
    # Agregar DocTypes específicos del módulo aquí
    # "DocType Name": {{
    #     "before_save": "{config['app_info']['app_name']}.{{module_name}}.handlers.before_save",
    #     "after_insert": "{config['app_info']['app_name']}.{{module_name}}.handlers.after_insert"
    # }}
}}
"""
    return hooks_code

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        module = sys.argv[1]
        print(generate_hooks_for_module(module))
    else:
        print("Uso: python generate_module_hooks.py <module_name>")'''
            
            with open(hooks_script, 'w') as f:
                f.write(hooks_content)
            hooks_script.chmod(0o755)
            print("✅ Creado: scripts/generate_module_hooks.py")
    
    def validate_setup(self) -> List[str]:
        """
        Validar que el setup fue exitoso
        """
        errors = []
        
        # Verificar archivos críticos
        critical_files = [
            "CLAUDE.md",
            "docs/core/CLAUDE_CONFIG.md",
            "docs/operational/MODULE_STATUS.md"
        ]
        
        for file in critical_files:
            if not (self.app_path / file).exists():
                errors.append(f"Archivo faltante: {file}")
        
        # Verificar que no hay placeholders sin reemplazar
        claude_file = self.app_path / "CLAUDE.md"
        if claude_file.exists():
            with open(claude_file, 'r') as f:
                content = f.read()
                if "{{" in content and "}}" in content:
                    errors.append("CLAUDE.md contiene placeholders sin reemplazar")
        
        return errors
    
    def run_setup(self, config: Dict, create_backup: bool = True) -> bool:
        """
        Ejecutar setup completo
        """
        try:
            print(f"🚀 Iniciando setup Claude Framework para: {config['app_info']['app_name']}")
            
            # 1. Crear backup si se solicita
            if create_backup:
                self.create_backup()
            
            # 2. Crear estructura de directorios
            for dir_path in ["docs/core", "docs/operational", "docs/workflows", "scripts"]:
                (self.app_path / dir_path).mkdir(parents=True, exist_ok=True)
            
            # 3. Generar templates
            self.generate_templates(config)
            
            # 4. Configurar herramientas de desarrollo
            self.setup_development_tools(config)
            
            # 5. Guardar configuración
            config_file = self.app_path / "claude_framework_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 6. Validar setup
            errors = self.validate_setup()
            if errors:
                print("❌ Errores encontrados:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print("✅ Setup completado exitosamente!")
            print(f"📁 Configuración guardada en: claude_framework_config.json")
            print(f"📖 Documentación principal: CLAUDE.md")
            
            return True
            
        except Exception as e:
            print(f"❌ Error durante setup: {e}")
            return False


def main():
    """Función principal CLI"""
    parser = argparse.ArgumentParser(description="Configurar Claude Framework para app Frappe")
    parser.add_argument("--app-name", required=True, help="Nombre de la app")
    parser.add_argument("--app-title", required=True, help="Título de la app")
    parser.add_argument("--language", default="es", help="Idioma principal (es, en, fr, de)")
    parser.add_argument("--publisher", required=True, help="Publisher de la app")
    parser.add_argument("--dev-site", help="Sitio de desarrollo")
    parser.add_argument("--no-backup", action="store_true", help="No crear backup")
    parser.add_argument("--migrate-existing", action="store_true", help="Migrar app existente")
    
    args = parser.parse_args()
    
    # Determinar ruta de la app
    app_path = os.getcwd()
    
    # Crear configurador
    setup = ClaudeFrameworkSetup(app_path)
    
    # Detectar información existente si es migración
    if args.migrate_existing:
        detected_info = setup.detect_app_info()
        print(f"📊 Información detectada: {detected_info}")
    
    # Crear configuración
    config_generator = ClaudeFrameworkConfig(args.app_name)
    config = config_generator.generate_app_config(
        app_name=args.app_name,
        app_title=args.app_title,
        app_publisher=args.publisher,
        app_description=f"App Frappe: {args.app_title}",
        app_email=f"dev@{args.publisher.lower().replace(' ', '')}.com",
        primary_language=args.language,
        dev_site=args.dev_site or f"{args.app_name}.dev",
        test_sites='["test1.dev", "test2.dev"]',
        main_branch="main",
        commit_scopes='["core", "setup", "tests", "docs", "config"]',
        required_apps='["frappe"]',
        business_domain=args.app_title,
        initial_modules='["core"]'
    )
    
    # Validar configuración
    errors = config_generator.validate_config(config)
    if errors:
        print("❌ Errores en configuración:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    # Ejecutar setup
    success = setup.run_setup(config, create_backup=not args.no_backup)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()