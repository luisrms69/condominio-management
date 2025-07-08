# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr


def validate(doc, method):
	"""Hook de validación para Component Type"""
	try:
		# Validar y normalizar prefijo de código
		validate_and_normalize_code_prefix(doc)

		# Validar configuración de template
		validate_template_configuration(doc)

		# Validar configuración de mantenimiento
		validate_maintenance_configuration(doc)

		# Validar configuración UI
		validate_ui_configuration(doc)

		# Validar coherencia de configuración
		validate_configuration_consistency(doc)

	except Exception as e:
		frappe.log_error(f"Error en validación de Component Type: {e!s}")
		raise


def validate_and_normalize_code_prefix(doc):
	"""Validar y normalizar prefijo de código"""
	if not doc.code_prefix:
		frappe.throw("El prefijo de código es obligatorio")

	# Normalizar prefijo (mayúsculas, sin espacios)
	doc.code_prefix = cstr(doc.code_prefix).upper().replace(" ", "").replace("-", "")

	# Validar formato
	if not doc.code_prefix.isalnum():
		frappe.throw("El prefijo de código solo puede contener letras y números")

	if len(doc.code_prefix) < 2 or len(doc.code_prefix) > 10:
		frappe.throw("El prefijo de código debe tener entre 2 y 10 caracteres")

	# Validar unicidad
	validate_code_prefix_uniqueness(doc)


def validate_code_prefix_uniqueness(doc):
	"""Validar que el prefijo de código sea único"""
	existing = frappe.db.get_value(
		"Component Type", filters={"code_prefix": doc.code_prefix, "name": ["!=", doc.name]}
	)
	if existing:
		frappe.throw(f"Ya existe un tipo de componente con el prefijo '{doc.code_prefix}' ({existing})")


def validate_template_configuration(doc):
	"""Validar configuración del template"""
	if doc.component_template_code:
		# Validar formato del código de template
		if not doc.component_template_code.replace("_", "").replace("-", "").isalnum():
			frappe.throw(
				"El código del template solo puede contener letras, números, guiones y guiones bajos"
			)

		# Establecer versión por defecto
		if not doc.template_version:
			doc.template_version = "1.0"

		# TODO: Validar que el template existe cuando esté implementado el template system
		if doc.auto_load_template:
			validate_template_exists(doc.component_template_code)

	# Si no hay template pero se marcó auto_load, desactivar
	if not doc.component_template_code and doc.auto_load_template:
		doc.auto_load_template = 0
		frappe.msgprint("Se desactivó 'Auto-cargar Template' porque no se especificó código de template")


def validate_template_exists(template_code):
	"""Validar que el template especificado existe"""
	# TODO: Implementar cuando esté disponible el template system
	# Por ahora solo validamos el formato
	pass


def validate_maintenance_configuration(doc):
	"""Validar configuración de mantenimiento"""
	# Validar vida útil estimada
	if doc.estimated_lifespan_years is not None:
		if doc.estimated_lifespan_years <= 0:
			frappe.throw("La vida útil estimada debe ser mayor a cero")

		if doc.estimated_lifespan_years > 100:
			frappe.msgprint("Advertencia: La vida útil estimada parece muy alta (>100 años)")

	# Validar coherencia de mantenimiento
	if doc.critical_component and not doc.default_maintenance_frequency:
		frappe.msgprint(
			"Recomendación: Los componentes críticos deberían tener una frecuencia de mantenimiento definida"
		)

	if doc.requires_certification and not doc.critical_component:
		frappe.msgprint("Información: Los componentes que requieren certificación normalmente son críticos")


def validate_ui_configuration(doc):
	"""Validar configuración de UI"""
	# Validar código de color
	if doc.color_code:
		if not doc.color_code.startswith("#") or len(doc.color_code) not in [4, 7]:
			frappe.throw("El código de color debe ser un color hexadecimal válido (ej: #FF0000 o #F00)")

	# Validar clase de icono
	if doc.icon_class:
		# Validación básica - debe contener al menos "fa" o "octicon"
		if not any(prefix in doc.icon_class.lower() for prefix in ["fa", "octicon", "icon"]):
			frappe.msgprint(
				"Advertencia: La clase de icono no parece ser válida. "
				"Use clases como 'fa fa-cog' o 'octicon octicon-gear'"
			)

	# Validar orden de visualización
	if doc.display_order is not None and doc.display_order < 0:
		frappe.throw("El orden de visualización debe ser un número positivo")


def validate_configuration_consistency(doc):
	"""Validar coherencia de la configuración"""
	# Validar coherencia entre categoría y requisitos
	validate_category_requirements_consistency(doc)

	# Validar coherencia de mantenimiento
	validate_maintenance_consistency(doc)

	# Validar coherencia de validaciones
	validate_validations_consistency(doc)


def validate_category_requirements_consistency(doc):
	"""Validar coherencia entre categoría y requisitos"""
	category_requirements = {
		"Eléctrico": {
			"should_require": ["specifications"],
			"recommendations": "Los componentes eléctricos normalmente requieren especificaciones técnicas",
		},
		"Mecánico": {
			"should_require": ["brand", "model"],
			"recommendations": "Los componentes mecánicos normalmente requieren marca y modelo",
		},
		"Seguridad": {
			"should_require": ["installation_date", "specifications"],
			"critical": True,
			"recommendations": "Los componentes de seguridad normalmente son críticos y requieren certificación",
		},
		"Electrónico": {
			"should_require": ["warranty", "specifications"],
			"recommendations": "Los componentes electrónicos normalmente requieren garantía y especificaciones",
		},
	}

	if doc.category in category_requirements:
		config = category_requirements[doc.category]

		# Verificar requisitos recomendados
		should_require = config.get("should_require", [])
		missing_requirements = []

		if "brand" in should_require and not doc.requires_brand:
			missing_requirements.append("marca")
		if "model" in should_require and not doc.requires_model:
			missing_requirements.append("modelo")
		if "specifications" in should_require and not doc.requires_specifications:
			missing_requirements.append("especificaciones técnicas")
		if "installation_date" in should_require and not doc.requires_installation_date:
			missing_requirements.append("fecha de instalación")
		if "warranty" in should_require and not doc.requires_warranty:
			missing_requirements.append("información de garantía")

		if missing_requirements:
			frappe.msgprint(f"Recomendación: {config['recommendations']}")

		# Verificar si debería ser crítico
		if config.get("critical") and not doc.critical_component:
			frappe.msgprint(
				f"Recomendación: Los componentes de categoría '{doc.category}' normalmente son críticos"
			)


def validate_maintenance_consistency(doc):
	"""Validar coherencia de configuración de mantenimiento"""
	# Si es crítico, debería tener mantenimiento definido
	if doc.critical_component:
		if not doc.default_maintenance_frequency:
			frappe.msgprint(
				"Recomendación: Los componentes críticos deberían tener frecuencia de mantenimiento definida"
			)

		if not doc.maintenance_type:
			frappe.msgprint(
				"Recomendación: Los componentes críticos deberían tener tipo de mantenimiento definido"
			)

	# Validar coherencia de tipo de mantenimiento con frecuencia
	maintenance_type_frequencies = {
		"Preventivo": ["Semanal", "Quincenal", "Mensual", "Trimestral", "Semestral", "Anual"],
		"Correctivo": ["Según Condición"],
		"Predictivo": ["Mensual", "Trimestral", "Semestral"],
		"Condicional": ["Según Condición"],
	}

	if doc.maintenance_type and doc.default_maintenance_frequency:
		expected_frequencies = maintenance_type_frequencies.get(doc.maintenance_type, [])
		if expected_frequencies and doc.default_maintenance_frequency not in expected_frequencies:
			frappe.msgprint(
				f"Información: Para mantenimiento '{doc.maintenance_type}' se recomienda "
				f"frecuencia: {', '.join(expected_frequencies)}"
			)


def validate_validations_consistency(doc):
	"""Validar coherencia de validaciones"""
	# Si requiere especificaciones, probablemente debería requerir marca/modelo
	if doc.requires_specifications and not (doc.requires_brand or doc.requires_model):
		frappe.msgprint(
			"Recomendación: Si requiere especificaciones técnicas, "
			"considere requerir también marca y modelo"
		)

	# Si requiere garantía, debería requerir fecha de instalación
	if doc.requires_warranty and not doc.requires_installation_date:
		frappe.msgprint(
			"Recomendación: Si requiere garantía, " "considere requerir también fecha de instalación"
		)


def validate_business_logic(doc):
	"""Validar lógica de negocio específica"""
	# Validar que no haya demasiados tipos con el mismo prefijo base
	base_prefix = doc.code_prefix[:3]
	similar_types = frappe.db.count("Component Type", filters={"code_prefix": ["like", f"{base_prefix}%"]})

	if similar_types > 5:
		frappe.msgprint(
			f"Información: Ya hay varios tipos con prefijo similar a '{base_prefix}'. "
			"Considere usar un prefijo más específico para mejor organización."
		)


def validate_reserved_prefixes(doc):
	"""Validar prefijos reservados"""
	reserved_prefixes = ["COMP", "GEN", "SYS", "ADMIN", "TEST"]

	if doc.code_prefix in reserved_prefixes:
		frappe.throw(f"El prefijo '{doc.code_prefix}' está reservado. Use un prefijo diferente.")

	# Advertir sobre prefijos que podrían causar confusión
	confusing_prefixes = ["CON", "NEW", "OLD", "TMP"]
	if doc.code_prefix in confusing_prefixes:
		frappe.msgprint(
			f"Advertencia: El prefijo '{doc.code_prefix}' podría causar confusión. "
			"Considere usar un prefijo más descriptivo."
		)
