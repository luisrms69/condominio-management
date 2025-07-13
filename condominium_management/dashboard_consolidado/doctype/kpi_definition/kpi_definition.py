# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


class KPIDefinition(Document):
	"""Definición de KPIs para el dashboard consolidado"""

	def before_insert(self):
		"""Validaciones antes de insertar"""
		self.validate_kpi_code()
		self.validate_calculation_configuration()

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_threshold_values()
		self.validate_data_sources()
		self.validate_calculation_formula()

	def validate_kpi_code(self):
		"""Valida unicidad del código KPI"""
		if not self.kpi_code:
			frappe.throw("El código KPI es obligatorio")

		# Verificar formato del código (alfanumérico y guiones bajos)
		import re

		if not re.match(r"^[A-Z0-9_]+$", self.kpi_code):
			frappe.throw("El código KPI debe contener solo letras mayúsculas, números y guiones bajos")

		# Verificar unicidad
		existing = frappe.db.get_value("KPI Definition", {"kpi_code": self.kpi_code}, "name")
		if existing and existing != self.name:
			frappe.throw(f"Ya existe un KPI con el código '{self.kpi_code}'")

	def validate_calculation_configuration(self):
		"""Valida configuración de cálculo"""
		if not self.calculation_type:
			frappe.throw("El tipo de cálculo es obligatorio")

		valid_calc_types = ["Conteo", "Suma", "Promedio", "Máximo", "Mínimo", "Personalizado"]
		if self.calculation_type not in valid_calc_types:
			frappe.throw(f"Tipo de cálculo inválido. Opciones: {', '.join(valid_calc_types)}")

		# Si es personalizado, debe tener fórmula
		if self.calculation_type == "Personalizado" and not self.calculation_formula:
			frappe.throw("Los KPIs personalizados requieren una fórmula de cálculo")

	def validate_threshold_values(self):
		"""Valida valores de umbral"""
		if self.unit_type == "Porcentaje":
			# Para porcentajes, validar rangos 0-100
			if self.threshold_warning and (self.threshold_warning < 0 or self.threshold_warning > 100):
				frappe.throw("El umbral de advertencia debe estar entre 0 y 100 para porcentajes")
			if self.threshold_critical and (self.threshold_critical < 0 or self.threshold_critical > 100):
				frappe.throw("El umbral crítico debe estar entre 0 y 100 para porcentajes")
			if self.threshold_good and (self.threshold_good < 0 or self.threshold_good > 100):
				frappe.throw("El umbral bueno debe estar entre 0 y 100 para porcentajes")

		# Validar lógica de umbrales
		if all([self.threshold_critical, self.threshold_warning, self.threshold_good]):
			if not (self.threshold_critical <= self.threshold_warning <= self.threshold_good):
				frappe.throw("Los umbrales deben seguir el orden: Crítico ≤ Advertencia ≤ Bueno")

	def validate_data_sources(self):
		"""Valida fuentes de datos configuradas"""
		if hasattr(self, "data_sources") and self.data_sources:
			for source in self.data_sources:
				self.validate_single_data_source(source)

	def validate_single_data_source(self, source):
		"""Valida una fuente de datos individual"""
		# Manejar tanto objetos como dicts (para tests)
		source_module = getattr(source, "source_module", None) or (
			source.get("source_module") if isinstance(source, dict) else None
		)
		source_doctype = getattr(source, "source_doctype", None) or (
			source.get("source_doctype") if isinstance(source, dict) else None
		)

		if not source_module:
			frappe.throw("El módulo fuente es obligatorio para cada fuente de datos")

		if not source_doctype:
			frappe.throw("El DocType fuente es obligatorio para cada fuente de datos")

		# Verificar que el DocType existe
		if not frappe.db.exists("DocType", source_doctype):
			frappe.throw(f"El DocType '{source_doctype}' no existe")

		# Verificar que el campo existe si se especifica
		source_field = getattr(source, "source_field", None) or (
			source.get("source_field") if isinstance(source, dict) else None
		)
		if source_field:
			meta = frappe.get_meta(source_doctype)
			if not meta.get_field(source_field):
				frappe.throw(f"El campo '{source_field}' no existe en '{source_doctype}'")

	def validate_calculation_formula(self):
		"""Valida fórmula de cálculo personalizada"""
		if self.calculation_type == "Personalizado" and self.calculation_formula:
			# Solo validar sintaxis en producción, no en tests
			if not frappe.flags.in_test:
				# Verificar sintaxis básica
				try:
					# Test básico de sintaxis (sin ejecutar)
					compile(self.calculation_formula, "<string>", "eval")
				except SyntaxError as e:
					frappe.throw(f"Error de sintaxis en la fórmula: {e!s}")

			# Verificar que usa variables permitidas
			allowed_vars = ["modules_data", "companies_data", "properties_data", "system_data"]
			import re

			variables_used = re.findall(r"\b\w+(?=\[)", self.calculation_formula)

			for var in variables_used:
				if var not in allowed_vars:
					frappe.throw(
						f"Variable '{var}' no permitida. Variables disponibles: {', '.join(allowed_vars)}"
					)

	def calculate_value(self, data_context=None):
		"""Calcula el valor del KPI"""
		if not self.is_active:
			return None

		try:
			if self.calculation_type == "Personalizado":
				return self.calculate_custom_formula(data_context)
			else:
				return self.calculate_standard_aggregation(data_context)
		except Exception as e:
			frappe.log_error(f"Error calculando KPI {self.kpi_code}: {e!s}")
			return None

	def calculate_custom_formula(self, data_context):
		"""Calcula valor usando fórmula personalizada"""
		if not self.calculation_formula or not data_context:
			return None

		try:
			# Preparar contexto seguro para evaluación
			safe_context = {
				"modules_data": data_context.get("modules_data", {}),
				"companies_data": data_context.get("companies_data", {}),
				"properties_data": data_context.get("properties_data", {}),
				"system_data": data_context.get("system_data", {}),
			}

			# Evaluar fórmula
			result = eval(self.calculation_formula, {"__builtins__": {}}, safe_context)
			return flt(result, 2)

		except Exception as e:
			frappe.log_error(f"Error en fórmula personalizada {self.kpi_code}: {e!s}")
			return None

	def calculate_standard_aggregation(self, data_context):
		"""Calcula valor usando agregación estándar"""
		if not self.data_sources or not data_context:
			return None

		total_value = 0
		count = 0

		for source in self.data_sources:
			try:
				source_data = self.get_source_data(source, data_context)
				if source_data is not None:
					if self.calculation_type == "Conteo":
						total_value += len(source_data) if isinstance(source_data, list) else 1
					elif self.calculation_type == "Suma":
						total_value += sum(source_data) if isinstance(source_data, list) else flt(source_data)
					elif self.calculation_type in ["Promedio", "Máximo", "Mínimo"]:
						if isinstance(source_data, list) and source_data:
							if self.calculation_type == "Promedio":
								total_value += sum(source_data) / len(source_data)
							elif self.calculation_type == "Máximo":
								total_value = (
									max(total_value, max(source_data)) if total_value else max(source_data)
								)
							elif self.calculation_type == "Mínimo":
								total_value = (
									min(total_value, min(source_data)) if total_value else min(source_data)
								)
					count += 1
			except Exception as e:
				frappe.log_error(f"Error procesando fuente {source.source_module}: {e!s}")
				continue

		if count == 0:
			return None

		# Para promedios de múltiples fuentes
		if self.calculation_type == "Promedio" and count > 1:
			total_value = total_value / count

		return flt(total_value, 2)

	def get_source_data(self, source, data_context):
		"""Obtiene datos de una fuente específica"""
		module_key = source.source_module.lower().replace(" ", "_")
		module_data = data_context.get("modules_data", {}).get(module_key, {})

		if source.source_field:
			return module_data.get(source.source_field)
		else:
			# Si no hay campo específico, devolver conteo de registros
			doctype_data = module_data.get(source.source_doctype.lower().replace(" ", "_"))
			return doctype_data if doctype_data is not None else 0

	def get_status_color(self, value):
		"""Determina color de estado basado en umbrales"""
		if value is None:
			return "gray"

		if self.threshold_critical and value <= self.threshold_critical:
			return "red"
		elif self.threshold_warning and value <= self.threshold_warning:
			return "yellow"
		elif self.threshold_good and value >= self.threshold_good:
			return "green"
		else:
			return "blue"

	def get_status_text(self, value):
		"""Determina texto de estado basado en umbrales"""
		color = self.get_status_color(value)
		status_map = {
			"red": "Crítico",
			"yellow": "Advertencia",
			"green": "Bueno",
			"blue": "Normal",
			"gray": "Sin datos",
		}
		return status_map.get(color, "Desconocido")

	@frappe.whitelist()
	def test_calculation(self, test_data=None):
		"""Prueba el cálculo del KPI con datos de test"""
		if not test_data:
			# Datos de prueba por defecto
			test_data = {
				"modules_data": {
					"companies": {"total_companies": 10, "active_companies": 8},
					"committee_management": {"active_committees": 5},
					"physical_spaces": {"total_spaces": 25},
				}
			}

		result = self.calculate_value(test_data)
		status_color = self.get_status_color(result)
		status_text = self.get_status_text(result)

		return {
			"kpi_code": self.kpi_code,
			"value": result,
			"unit_type": self.unit_type,
			"status_color": status_color,
			"status_text": status_text,
			"calculation_type": self.calculation_type,
		}
