# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class KPIDataSource(Document):
	"""Fuente de datos para KPIs - Child table de KPI Definition"""

	def validate(self):
		"""Validaciones de la fuente de datos"""
		self.validate_source_configuration()
		self.validate_aggregation_settings()

	def validate_source_configuration(self):
		"""Valida configuración básica de la fuente"""
		if not self.source_module:
			frappe.throw("El módulo fuente es obligatorio")

		if not self.source_doctype:
			frappe.throw("El DocType fuente es obligatorio")

		# Verificar que el DocType existe
		if not frappe.db.exists("DocType", self.source_doctype):
			frappe.throw(f"El DocType '{self.source_doctype}' no existe")

		# Verificar que el campo existe si se especifica
		if self.source_field:
			meta = frappe.get_meta(self.source_doctype)
			if not meta.get_field(self.source_field):
				frappe.throw(f"El campo '{self.source_field}' no existe en '{self.source_doctype}'")

	def validate_aggregation_settings(self):
		"""Valida configuración de agregación"""
		if not self.aggregation:
			self.aggregation = "Conteo"  # Valor por defecto

		valid_aggregations = ["Conteo", "Suma", "Promedio", "Máximo", "Mínimo", "Mediana"]
		if self.aggregation not in valid_aggregations:
			frappe.throw(f"Tipo de agregación inválido. Opciones: {', '.join(valid_aggregations)}")

		# Validar que agregaciones numéricas tengan campo especificado
		numeric_aggregations = ["Suma", "Promedio", "Máximo", "Mínimo", "Mediana"]
		if self.aggregation in numeric_aggregations and not self.source_field:
			frappe.throw(f"La agregación '{self.aggregation}' requiere especificar un campo fuente")

	def get_source_data(self, filters=None):
		"""Obtiene datos de la fuente"""
		try:
			# Construir filtros base
			base_filters = {}
			if filters:
				base_filters.update(filters)

			# Agregar filtros específicos de la fuente
			if hasattr(self, "filter_conditions") and self.filter_conditions:
				# Parsear condiciones de filtro JSON
				import json

				try:
					source_filters = json.loads(self.filter_conditions)
					base_filters.update(source_filters)
				except Exception:
					pass

			# Obtener datos según el tipo de agregación
			if self.aggregation == "Conteo":
				return self.get_count_data(base_filters)
			elif self.source_field:
				return self.get_field_aggregation(base_filters)
			else:
				return self.get_count_data(base_filters)

		except Exception as e:
			frappe.log_error(f"Error getting source data from {self.source_module}: {e!s}")
			return None

	def get_count_data(self, filters):
		"""Obtiene conteo de registros"""
		try:
			count = frappe.db.count(self.source_doctype, filters)
			return count
		except Exception as e:
			frappe.log_error(f"Error counting {self.source_doctype}: {e!s}")
			return 0

	def get_field_aggregation(self, filters):
		"""Obtiene agregación de campo específico"""
		try:
			if self.aggregation == "Suma":
				result = frappe.db.sql(
					f"""
					SELECT SUM({self.source_field}) as total
					FROM `tab{self.source_doctype}`
					WHERE {self.build_where_clause(filters)}
				""",
					as_dict=True,
				)
				return result[0]["total"] if result and result[0]["total"] else 0

			elif self.aggregation == "Promedio":
				result = frappe.db.sql(
					f"""
					SELECT AVG({self.source_field}) as average
					FROM `tab{self.source_doctype}`
					WHERE {self.build_where_clause(filters)}
				""",
					as_dict=True,
				)
				return result[0]["average"] if result and result[0]["average"] else 0

			elif self.aggregation == "Máximo":
				result = frappe.db.sql(
					f"""
					SELECT MAX({self.source_field}) as maximum
					FROM `tab{self.source_doctype}`
					WHERE {self.build_where_clause(filters)}
				""",
					as_dict=True,
				)
				return result[0]["maximum"] if result and result[0]["maximum"] else 0

			elif self.aggregation == "Mínimo":
				result = frappe.db.sql(
					f"""
					SELECT MIN({self.source_field}) as minimum
					FROM `tab{self.source_doctype}`
					WHERE {self.build_where_clause(filters)}
				""",
					as_dict=True,
				)
				return result[0]["minimum"] if result and result[0]["minimum"] else 0

			elif self.aggregation == "Mediana":
				# Implementación básica de mediana
				values = frappe.db.get_all(
					self.source_doctype,
					filters=filters,
					fields=[self.source_field],
					order_by=self.source_field,
				)

				if not values:
					return 0

				numeric_values = [v[self.source_field] for v in values if v[self.source_field] is not None]
				if not numeric_values:
					return 0

				n = len(numeric_values)
				if n % 2 == 0:
					return (numeric_values[n // 2 - 1] + numeric_values[n // 2]) / 2
				else:
					return numeric_values[n // 2]

		except Exception as e:
			frappe.log_error(f"Error getting {self.aggregation} for {self.source_field}: {e!s}")
			return 0

	def build_where_clause(self, filters):
		"""Construye cláusula WHERE para consultas SQL"""
		if not filters:
			return "1=1"

		conditions = []
		for field, value in filters.items():
			if isinstance(value, str):
				conditions.append(f"`{field}` = '{value}'")
			elif isinstance(value, int | float):
				conditions.append(f"`{field}` = {value}")
			elif isinstance(value, list):
				values_str = "', '".join(str(v) for v in value)
				conditions.append(f"`{field}` IN ('{values_str}')")

		return " AND ".join(conditions) if conditions else "1=1"

	def get_data_for_period(self, start_date, end_date, date_field="creation"):
		"""Obtiene datos para un período específico"""
		filters = {date_field: ["between", [start_date, end_date]]}

		return self.get_source_data(filters)

	def get_trend_data(self, periods=6, period_type="month"):
		"""Obtiene datos de tendencia por períodos"""
		from frappe.utils import add_to_date, get_first_day, get_last_day

		trend_data = []
		current_date = frappe.utils.getdate()

		for i in range(periods):
			if period_type == "month":
				period_start = get_first_day(add_to_date(current_date, months=-i))
				period_end = get_last_day(add_to_date(current_date, months=-i))
			elif period_type == "week":
				period_start = add_to_date(current_date, weeks=-i, days=-6)
				period_end = add_to_date(current_date, weeks=-i)
			elif period_type == "day":
				period_start = period_end = add_to_date(current_date, days=-i)
			else:
				continue

			period_value = self.get_data_for_period(period_start, period_end)
			trend_data.append({"period": period_start.strftime("%Y-%m-%d"), "value": period_value})

		return list(reversed(trend_data))  # Orden cronológico

	def test_connection(self):
		"""Prueba la conexión y configuración de la fuente de datos"""
		try:
			test_data = self.get_source_data()
			return {
				"status": "success",
				"message": f"Conexión exitosa. Valor obtenido: {test_data}",
				"test_value": test_data,
			}
		except Exception as e:
			return {"status": "error", "message": f"Error en la conexión: {e!s}", "test_value": None}
