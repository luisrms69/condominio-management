#!/usr/bin/env python3
"""
Generador de hooks específicos para módulos de test_erp
"""

def generate_hooks_for_module(module_name: str) -> str:
    """Generar hooks específicos para un módulo"""
    hooks_code = f"""
# Hooks para módulo {module_name}
doc_events = {
    # Agregar DocTypes específicos del módulo aquí
    # "DocType Name": {
    #     "before_save": "test_erp.{module_name}.handlers.before_save",
    #     "after_insert": "test_erp.{module_name}.handlers.after_insert"
    # }
}
"""
    return hooks_code

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        module = sys.argv[1]
        print(generate_hooks_for_module(module))
    else:
        print("Uso: python generate_module_hooks.py <module_name>")