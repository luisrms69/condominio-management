# 🔧 TEMPLATE DE HOOKS OBLIGATORIOS PARA NUEVOS MÓDULOS
# ======================================================
#
# PROPÓSITO: Asegurar que cada módulo nuevo implemente hooks específicos
# para auto-detección de configuraciones sin olvidar ningún DocType crítico
#
# BASADO EN: REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md
# FECHA: 2025-07-04
# ESTADO: ✅ WORKFLOW PERMANENTE DOCUMENTADO

"""
🚨 REGLA CRÍTICA: HOOKS OBLIGATORIOS POR MÓDULO

Cada módulo nuevo DEBE:
1. Identificar DocTypes que necesitan auto-detección
2. Agregar hooks específicos a hooks.py
3. Implementar handlers correspondientes
4. Agregar tests para hooks
5. Documentar en este template

❌ HOOKS UNIVERSALES NO FACTIBLES por conflictos con setup wizard ERPNext
✅ HOOKS ESPECÍFICOS POR DOCTYPE - ESTRATEGIA SEGURA Y ESCALABLE
"""

# ============================================================================
# TEMPLATE DE CONFIGURACIÓN POR MÓDULO
# ============================================================================

MODULE_HOOKS_TEMPLATE = {
	"companies": {
		"doctypes": {
			"Company": {
				"events": ["after_insert", "on_update"],
				"handler": "companies.hooks_handlers.company_detection",
				"reason": "Detectar nuevas empresas administradoras que necesitan configuración",
				"priority": "high",
			},
			"Service Management Contract": {
				"events": ["validate", "on_update"],
				"handler": "companies.hooks_handlers.contract_detection",
				"reason": "Validar contratos y detectar configuraciones automáticas",
				"priority": "high",
			},
			"Company Account": {
				"events": ["after_insert"],
				"handler": "companies.hooks_handlers.account_detection",
				"reason": "Detectar nuevas cuentas que requieren templates",
				"priority": "medium",
			},
		}
	},
	"physical_spaces": {
		"doctypes": {
			"Building": {
				"events": ["after_insert", "on_update"],
				"handler": "physical_spaces.hooks_handlers.building_detection",
				"reason": "Detectar nuevos edificios que necesitan configuración de espacios",
				"priority": "high",
			},
			"Space": {
				"events": ["after_insert"],
				"handler": "physical_spaces.hooks_handlers.space_detection",
				"reason": "Auto-configurar espacios según tipo y edificio",
				"priority": "medium",
			},
			"Common Area": {
				"events": ["after_insert"],
				"handler": "physical_spaces.hooks_handlers.common_area_detection",
				"reason": "Configurar áreas comunes con templates específicos",
				"priority": "medium",
			},
		}
	},
	"residents": {
		"doctypes": {
			"Resident": {
				"events": ["after_insert", "on_update"],
				"handler": "residents.hooks_handlers.resident_detection",
				"reason": "Detectar nuevos residentes para configuración de documentos",
				"priority": "high",
			},
			"Family Member": {
				"events": ["after_insert"],
				"handler": "residents.hooks_handlers.family_detection",
				"reason": "Auto-configurar familiares con permisos heredados",
				"priority": "medium",
			},
		}
	},
	"access_control": {
		"doctypes": {
			"Access Card": {
				"events": ["after_insert", "on_update"],
				"handler": "access_control.hooks_handlers.card_detection",
				"reason": "Configurar tarjetas con templates de acceso",
				"priority": "high",
			},
			"Access Point": {
				"events": ["after_insert"],
				"handler": "access_control.hooks_handlers.point_detection",
				"reason": "Detectar nuevos puntos de acceso para configuración",
				"priority": "medium",
			},
		}
	},
	"maintenance_professional": {
		"doctypes": {
			"Maintenance Request": {
				"events": ["after_insert", "on_update"],
				"handler": "maintenance_professional.hooks_handlers.request_detection",
				"reason": "Auto-asignar profesionales según tipo de mantenimiento",
				"priority": "high",
			},
			"Professional": {
				"events": ["after_insert"],
				"handler": "maintenance_professional.hooks_handlers.professional_detection",
				"reason": "Configurar profesionales con templates específicos",
				"priority": "medium",
			},
		}
	},
	"committee_management": {
		"doctypes": {
			"Committee": {
				"events": ["after_insert", "on_update"],
				"handler": "committee_management.hooks_handlers.committee_detection",
				"reason": "Configurar comités con templates de documentos",
				"priority": "high",
			},
			"Committee Member": {
				"events": ["after_insert"],
				"handler": "committee_management.hooks_handlers.member_detection",
				"reason": "Auto-configurar miembros con permisos específicos",
				"priority": "medium",
			},
		}
	},
	"compliance_legal": {
		"doctypes": {
			"Legal Document": {
				"events": ["after_insert", "validate"],
				"handler": "compliance_legal.hooks_handlers.document_detection",
				"reason": "Validar documentos legales y aplicar templates",
				"priority": "high",
			},
			"Compliance Check": {
				"events": ["after_insert"],
				"handler": "compliance_legal.hooks_handlers.compliance_detection",
				"reason": "Auto-configurar checks según tipo de cumplimiento",
				"priority": "medium",
			},
		}
	},
	"communication_system": {
		"doctypes": {
			"Communication": {
				"events": ["after_insert"],
				"handler": "communication_system.hooks_handlers.communication_detection",
				"reason": "Aplicar templates según tipo de comunicación",
				"priority": "medium",
			},
			"Notification": {
				"events": ["after_insert"],
				"handler": "communication_system.hooks_handlers.notification_detection",
				"reason": "Auto-configurar notificaciones por canal",
				"priority": "low",
			},
		}
	},
	"package_correspondence": {
		"doctypes": {
			"Package": {
				"events": ["after_insert", "on_update"],
				"handler": "package_correspondence.hooks_handlers.package_detection",
				"reason": "Configurar paquetes con templates de entrega",
				"priority": "medium",
			},
			"Correspondence": {
				"events": ["after_insert"],
				"handler": "package_correspondence.hooks_handlers.correspondence_detection",
				"reason": "Auto-configurar correspondencia según tipo",
				"priority": "medium",
			},
		}
	},
}

# ============================================================================
# IMPLEMENTACIÓN AUTOMÁTICA EN HOOKS.PY
# ============================================================================


def generate_hooks_configuration():
	"""
	Generar configuración automática de hooks para hooks.py

	Usage:
	    from TEMPLATE_MODULE_HOOKS import generate_hooks_configuration
	    hooks_config = generate_hooks_configuration()
	"""
	doc_events = {}

	for module_name, module_config in MODULE_HOOKS_TEMPLATE.items():
		for doctype, doctype_config in module_config["doctypes"].items():
			if doctype not in doc_events:
				doc_events[doctype] = {}

			for event in doctype_config["events"]:
				handler_path = f"condominium_management.{module_name}.{doctype_config['handler']}.{event}"
				doc_events[doctype][event] = handler_path

	return doc_events


# ============================================================================
# TEMPLATE DE HANDLER PARA NUEVOS MÓDULOS
# ============================================================================

HANDLER_TEMPLATE = '''
# {module_name}/hooks_handlers/{handler_name}.py
# Auto-generado desde TEMPLATE_MODULE_HOOKS.py

import frappe
from condominium_management.document_generation.api.entity_detection import auto_detect_configuration_needed

def after_insert(doc, method):
    """
    Hook ejecutado después de insertar {doctype}.

    Args:
        doc: Documento insertado
        method: Método que activó el hook
    """
    try:
        # Verificar si necesita configuración automática
        entity_config = frappe.get_doc("Entity Type Configuration", {{"entity_doctype": doc.doctype}})
        if entity_config:
            result = auto_detect_configuration_needed(doc, entity_config)
            if result.get("needs_configuration"):
                frappe.msgprint(f"Se detectó que {{doc.doctype}} {{doc.name}} requiere configuración automática")

    except Exception as e:
        frappe.log_error(f"Error en hook after_insert para {{doc.doctype}}: {{str(e)}}")

def on_update(doc, method):
    """
    Hook ejecutado al actualizar {doctype}.

    Args:
        doc: Documento actualizado
        method: Método que activó el hook
    """
    try:
        # Verificar cambios que requieren reconfiguración
        # Implementar lógica específica del módulo
        pass

    except Exception as e:
        frappe.log_error(f"Error en hook on_update para {{doc.doctype}}: {{str(e)}}")

def validate(doc, method):
    """
    Hook ejecutado al validar {doctype}.

    Args:
        doc: Documento a validar
        method: Método que activó el hook
    """
    try:
        # Implementar validaciones específicas
        # Verificar configuraciones requeridas
        pass

    except Exception as e:
        frappe.throw(f"Error en validación de {{doc.doctype}}: {{str(e)}}")
'''

# ============================================================================
# FUNCIONES DE UTILIDAD PARA DESARROLLO
# ============================================================================


def create_module_handlers(module_name):
	"""
	Crear handlers automáticamente para un módulo.

	Args:
	    module_name: Nombre del módulo (ej: "companies")
	"""
	import os

	import frappe

	if module_name not in MODULE_HOOKS_TEMPLATE:
		frappe.throw(f"Módulo {module_name} no encontrado en template")

	module_config = MODULE_HOOKS_TEMPLATE[module_name]
	handlers_dir = f"condominium_management/{module_name}/hooks_handlers"

	# Crear directorio si no existe
	os.makedirs(handlers_dir, exist_ok=True)

	# Crear __init__.py
	with open(f"{handlers_dir}/__init__.py", "w") as f:
		f.write("# Hooks handlers para " + module_name)

	# Crear handlers por DocType
	for doctype, config in module_config["doctypes"].items():
		handler_name = config["handler"].split(".")[-1]
		handler_file = f"{handlers_dir}/{handler_name}.py"

		with open(handler_file, "w") as f:
			content = HANDLER_TEMPLATE.format(
				module_name=module_name, handler_name=handler_name, doctype=doctype
			)
			f.write(content)

	print(f"✅ Handlers creados para módulo {module_name}")


def validate_module_hooks(module_name):
	"""
	Validar que un módulo tenga todos los hooks implementados.

	Args:
	    module_name: Nombre del módulo a validar

	Returns:
	    dict: Resultado de validación
	"""
	results = {"valid": True, "missing_handlers": [], "missing_doctypes": []}

	if module_name not in MODULE_HOOKS_TEMPLATE:
		results["valid"] = False
		results["error"] = f"Módulo {module_name} no encontrado en template"
		return results

	module_config = MODULE_HOOKS_TEMPLATE[module_name]

	# Verificar que existan los handlers
	for _doctype, config in module_config["doctypes"].items():
		handler_path = f"condominium_management.{module_name}.{config['handler']}"
		try:
			import frappe

			frappe.get_attr(handler_path)
		except Exception:
			results["valid"] = False
			results["missing_handlers"].append(handler_path)

	# Verificar que existan los DocTypes
	for doctype in module_config["doctypes"].keys():
		import frappe

		if not frappe.db.exists("DocType", doctype):
			results["valid"] = False
			results["missing_doctypes"].append(doctype)

	return results


# ============================================================================
# COMANDO CLI PARA GENERAR HOOKS AUTOMÁTICAMENTE
# ============================================================================


def generate_hooks_for_module(module_name):
	"""
	Comando CLI para generar hooks automáticamente.

	Usage:
	    bench console
	    >>> from TEMPLATE_MODULE_HOOKS import generate_hooks_for_module
	    >>> generate_hooks_for_module("companies")
	"""
	print(f"🔧 Generando hooks para módulo: {module_name}")

	# 1. Crear handlers
	create_module_handlers(module_name)

	# 2. Generar configuración para hooks.py
	module_config = MODULE_HOOKS_TEMPLATE[module_name]
	hooks_config = {}

	for doctype, config in module_config["doctypes"].items():
		hooks_config[doctype] = {}
		for event in config["events"]:
			handler_path = f"condominium_management.{module_name}.{config['handler']}.{event}"
			hooks_config[doctype][event] = handler_path

	print("✅ Configuración para hooks.py:")
	print("doc_events.update({")
	for doctype, events in hooks_config.items():
		print(f'    "{doctype}": {{')
		for event, handler in events.items():
			print(f'        "{event}": "{handler}",')
		print("    },")
	print("})")

	# 3. Validar
	validation = validate_module_hooks(module_name)
	if validation["valid"]:
		print("✅ Validación exitosa")
	else:
		print("❌ Errores encontrados:")
		for error in validation.get("missing_handlers", []):
			print(f"  - Handler faltante: {error}")
		for error in validation.get("missing_doctypes", []):
			print(f"  - DocType faltante: {error}")


if __name__ == "__main__":
	# Ejemplo de uso
	print("🔧 TEMPLATE DE HOOKS OBLIGATORIOS")
	print("Para usar este template:")
	print("1. bench console")
	print("2. from TEMPLATE_MODULE_HOOKS import generate_hooks_for_module")
	print("3. generate_hooks_for_module('nombre_modulo')")
