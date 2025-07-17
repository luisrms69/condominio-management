# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Budget Planning - Sistema de Planeación Presupuestal
===================================================

DocType para manejo completo de presupuestos con:
- Planeación de ingresos y gastos
- Análisis de variaciones real vs presupuesto
- Integración con Physical Spaces
- Workflow de aprobación
- Reportes automáticos
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, nowdate


class BudgetPlanning(Document):
	"""Budget Planning DocType con business logic completa"""

	def before_save(self):
		"""Validaciones antes de guardar"""
		self.validate_budget_configuration()
		self.validate_income_expenses_balance()
		self.calculate_totals()
		self.validate_approval_requirements()
		self.set_fiscal_year_defaults()

	def on_submit(self):
		"""Acciones al aprobar el presupuesto"""
		self.activate_budget()
		self.create_monitoring_schedule()
		self.distribute_to_stakeholders()

	# =============================================================================
	# VALIDATION METHODS
	# =============================================================================

	def validate_budget_configuration(self):
		"""Validar configuración básica del presupuesto"""
		if not self.budget_name:
			frappe.throw(_("Nombre del Presupuesto es obligatorio"))

		if not self.budget_period:
			frappe.throw(_("Período Presupuestal es obligatorio"))

		if not self.company:
			frappe.throw(_("Condominio es obligatorio"))

		# Validar que no exista otro presupuesto activo para el mismo período
		existing_budget = frappe.db.exists(
			"Budget Planning",
			{
				"company": self.company,
				"budget_period": self.budget_period,
				"fiscal_year": self.fiscal_year,
				"budget_status": ["in", ["Activo", "Aprobado"]],
				"name": ["!=", self.name],
			},
		)

		if existing_budget:
			frappe.throw(
				_("Ya existe un presupuesto activo para {0} en {1}").format(
					self.budget_period, self.fiscal_year
				)
			)

	def validate_income_expenses_balance(self):
		"""Validar balance entre ingresos y gastos"""
		total_income = flt(self.total_income_budgeted)
		total_expenses = flt(self.total_expenses_budgeted)

		if total_income <= 0 and self.budget_status not in ["Borrador", "En Revisión"]:
			frappe.throw(_("Total de Ingresos debe ser mayor a cero"))

		if total_expenses <= 0 and self.budget_status not in ["Borrador", "En Revisión"]:
			frappe.throw(_("Total de Gastos debe ser mayor a cero"))

		# Validar que los gastos no excedan significativamente los ingresos
		if total_income > 0 and total_expenses > 0:
			expense_ratio = (total_expenses / total_income) * 100
			if expense_ratio > 110:  # 110% permite 10% de déficit
				frappe.msgprint(
					_("Advertencia: Gastos exceden ingresos en {0:.1f}%").format(expense_ratio - 100),
					alert=True,
				)

	def calculate_totals(self):
		"""Calcular totales de ingresos y gastos"""
		# Calcular total de ingresos
		income_fields = [
			"maintenance_fees_budget",
			"special_assessments_budget",
			"other_income_budget",
			"reserve_fund_contribution",
		]

		total_income = sum(flt(self.get(field)) for field in income_fields)
		self.total_income_budgeted = total_income

		# Calcular total de gastos
		expense_fields = [
			"administrative_expenses",
			"maintenance_expenses",
			"utilities_expenses",
			"insurance_expenses",
		]

		total_expenses = sum(flt(self.get(field)) for field in expense_fields)

		# Agregar asignaciones de reserva
		reserve_fields = [
			"emergency_reserve_allocation",
			"maintenance_reserve_allocation",
			"replacement_reserve_allocation",
			"capital_improvement_allocation",
		]

		total_reserves = sum(flt(self.get(field)) for field in reserve_fields)
		self.total_expenses_budgeted = total_expenses + total_reserves

	def validate_approval_requirements(self):
		"""Validar requerimientos de aprobación"""
		# Presupuestos por encima de cierto monto requieren aprobación
		total_budget = flt(self.total_income_budgeted)

		if total_budget > 1000000:  # 1M MXN
			self.requires_committee_approval = 1
			self.approval_required = 1

		# Presupuestos de emergencia siempre requieren aprobación
		if self.budget_type == "Emergencia":
			self.requires_committee_approval = 1
			self.approval_required = 1

		# Validar estado de aprobación
		if self.budget_status == "Aprobado" and self.approval_required:
			if not self.approved_by or not self.approval_date:
				frappe.throw(_("Presupuesto marcado como aprobado requiere información de aprobación"))

	def set_fiscal_year_defaults(self):
		"""Establecer año fiscal por defecto"""
		if not self.fiscal_year:
			# Obtener año fiscal actual
			current_fiscal_year = frappe.db.get_value(
				"Fiscal Year", {"is_short_year": 0}, "name", order_by="year_start_date desc"
			)
			if current_fiscal_year:
				self.fiscal_year = current_fiscal_year

	# =============================================================================
	# BUSINESS LOGIC METHODS
	# =============================================================================

	def activate_budget(self):
		"""Activar presupuesto y desactivar otros"""
		if self.budget_status == "Aprobado":
			# Desactivar otros presupuestos activos del mismo período
			frappe.db.sql(
				"""
				UPDATE `tabBudget Planning`
				SET budget_status = 'Cerrado'
				WHERE company = %s
				AND budget_period = %s
				AND fiscal_year = %s
				AND budget_status = 'Activo'
				AND name != %s
			""",
				(self.company, self.budget_period, self.fiscal_year, self.name),
			)

			# Activar este presupuesto
			self.budget_status = "Activo"
			frappe.db.set_value("Budget Planning", self.name, "budget_status", "Activo")

	def create_monitoring_schedule(self):
		"""Crear calendario de monitoreo del presupuesto"""
		if self.monthly_review_required:
			# Crear eventos de revisión mensual
			self.schedule_monthly_reviews()

		if self.quarterly_review_enabled:
			# Crear eventos de revisión trimestral
			self.schedule_quarterly_reviews()

	def schedule_monthly_reviews(self):
		"""Programar revisiones mensuales"""
		# Esta función se puede expandir para crear eventos en Calendar
		frappe.logger().info(f"Programando revisiones mensuales para presupuesto {self.name}")

	def schedule_quarterly_reviews(self):
		"""Programar revisiones trimestrales"""
		frappe.logger().info(f"Programando revisiones trimestrales para presupuesto {self.name}")

	def distribute_to_stakeholders(self):
		"""Distribuir presupuesto a interesados"""
		if self.stakeholder_distribution == "Automática":
			# Enviar a roles financieros
			self.send_to_financial_roles()

	def send_to_financial_roles(self):
		"""Enviar presupuesto a roles financieros"""
		roles = ["Administrador Financiero", "Contador Condominio", "Comité Administración"]

		for role in roles:
			users = frappe.get_all("Has Role", filters={"role": role}, fields=["parent as user"])

			for user in users:
				# Crear notificación
				frappe.share.add("Budget Planning", self.name, user.user, read=1)

	# =============================================================================
	# CALCULATION METHODS
	# =============================================================================

	def calculate_variance_analysis(self):
		"""Calcular análisis de variaciones real vs presupuesto"""
		if not self.actual_vs_budget_enabled:
			return

		# Obtener datos reales de ERPNext
		actual_income = self.get_actual_income()
		actual_expenses = self.get_actual_expenses()

		self.total_actual_income = actual_income
		self.total_actual_expenses = actual_expenses

		# Calcular variaciones porcentuales
		if flt(self.total_income_budgeted) > 0:
			income_variance = (
				(actual_income - flt(self.total_income_budgeted)) / flt(self.total_income_budgeted)
			) * 100
			self.income_variance_percentage = income_variance

		if flt(self.total_expenses_budgeted) > 0:
			expense_variance = (
				(actual_expenses - flt(self.total_expenses_budgeted)) / flt(self.total_expenses_budgeted)
			) * 100
			self.expense_variance_percentage = expense_variance

		# Calcular tasa de utilización
		if flt(self.total_expenses_budgeted) > 0:
			utilization_rate = (actual_expenses / flt(self.total_expenses_budgeted)) * 100
			self.budget_utilization_rate = utilization_rate

		# Verificar umbrales de alerta
		self.check_variance_thresholds()

	def get_actual_income(self):
		"""Obtener ingresos reales de ERPNext"""
		# Query para obtener ingresos reales del período
		conditions = self.get_period_conditions()

		actual_income = frappe.db.sql(
			f"""
			SELECT COALESCE(SUM(grand_total), 0) as total
			FROM `tabSales Invoice`
			WHERE company = %s
			AND docstatus = 1
			{conditions}
		""",
			[self.company],
		)[0][0]

		return flt(actual_income)

	def get_actual_expenses(self):
		"""Obtener gastos reales de ERPNext"""
		conditions = self.get_period_conditions()

		actual_expenses = frappe.db.sql(
			f"""
			SELECT COALESCE(SUM(grand_total), 0) as total
			FROM `tabPurchase Invoice`
			WHERE company = %s
			AND docstatus = 1
			{conditions}
		""",
			[self.company],
		)[0][0]

		return flt(actual_expenses)

	def get_period_conditions(self):
		"""Obtener condiciones SQL para el período presupuestal"""
		if self.budget_period == "Anual":
			return "AND YEAR(posting_date) = YEAR(CURDATE())"
		elif self.budget_period == "Trimestral":
			return "AND QUARTER(posting_date) = QUARTER(CURDATE()) AND YEAR(posting_date) = YEAR(CURDATE())"
		elif self.budget_period == "Mensual":
			return "AND MONTH(posting_date) = MONTH(CURDATE()) AND YEAR(posting_date) = YEAR(CURDATE())"
		else:
			return ""

	def check_variance_thresholds(self):
		"""Verificar umbrales de variación y generar alertas"""
		threshold = flt(self.variance_threshold_percentage) or 10.0

		# Alerta por exceso en gastos
		if self.alert_on_overspending and flt(self.expense_variance_percentage) > threshold:
			self.create_overspending_alert()

		# Alerta por déficit en ingresos
		if flt(self.income_variance_percentage) < -threshold:
			self.create_income_deficit_alert()

	def create_overspending_alert(self):
		"""Crear alerta por sobregasto"""
		message = _("Alerta: Gastos exceden presupuesto en {0:.1f}%").format(
			flt(self.expense_variance_percentage)
		)

		frappe.msgprint(message, alert=True, indicator="red")

		# Log para auditoría
		frappe.log_error(f"Sobregasto detectado en presupuesto {self.name}: {message}")

	def create_income_deficit_alert(self):
		"""Crear alerta por déficit en ingresos"""
		message = _("Alerta: Ingresos por debajo del presupuesto en {0:.1f}%").format(
			abs(flt(self.income_variance_percentage))
		)

		frappe.msgprint(message, alert=True, indicator="orange")

	# =============================================================================
	# API METHODS
	# =============================================================================

	@frappe.whitelist()
	def update_from_template(self, template_name):
		"""Actualizar presupuesto desde plantilla"""
		if not template_name:
			frappe.throw(_("Nombre de plantilla es requerido"))

		template = frappe.get_doc("Budget Planning", template_name)

		# Copiar campos de configuración
		config_fields = [
			"budget_type",
			"planning_method",
			"approval_required",
			"auto_adjustment_enabled",
			"allocation_method",
		]

		for field in config_fields:
			if hasattr(template, field):
				setattr(self, field, getattr(template, field))

		# Copiar montos base (se pueden ajustar después)
		amount_fields = [
			"maintenance_fees_budget",
			"administrative_expenses",
			"maintenance_expenses",
			"utilities_expenses",
		]

		for field in amount_fields:
			if hasattr(template, field) and flt(getattr(template, field)) > 0:
				setattr(self, field, getattr(template, field))

		self.save()

		return {
			"success": True,
			"message": _("Presupuesto actualizado desde plantilla {0}").format(template_name),
		}

	@frappe.whitelist()
	def generate_monthly_report(self):
		"""Generar reporte mensual del presupuesto"""
		if not self.generate_monthly_reports:
			frappe.throw(_("Reportes mensuales no están habilitados"))

		# Actualizar análisis de variaciones
		self.calculate_variance_analysis()

		report_data = {
			"budget_name": self.budget_name,
			"period": f"{self.budget_period} - {getdate().strftime('%B %Y')}",
			"income": {
				"budgeted": self.total_income_budgeted,
				"actual": self.total_actual_income,
				"variance": self.income_variance_percentage,
			},
			"expenses": {
				"budgeted": self.total_expenses_budgeted,
				"actual": self.total_actual_expenses,
				"variance": self.expense_variance_percentage,
			},
			"utilization": self.budget_utilization_rate,
			"alerts": self.get_current_alerts(),
		}

		return report_data

	@frappe.whitelist()
	def approve_budget(self, approved_by, approval_notes=None):
		"""Aprobar presupuesto (solo para roles autorizados)"""
		if self.budget_status != "En Revisión":
			frappe.throw(_("Solo se pueden aprobar presupuestos en revisión"))

		if self.requires_committee_approval and not self.committee_decision:
			frappe.throw(_("Requiere decisión del comité antes de aprobar"))

		# Registrar aprobación
		self.approved_by = approved_by
		self.approval_date = getdate()
		self.approval_notes = approval_notes
		self.budget_status = "Aprobado"

		self.save()

		# Activar presupuesto
		self.activate_budget()

		return {
			"success": True,
			"message": _("Presupuesto aprobado exitosamente"),
			"new_status": self.budget_status,
		}

	@frappe.whitelist()
	def get_budget_summary(self):
		"""Obtener resumen completo del presupuesto"""
		# Calcular análisis actualizado
		self.calculate_variance_analysis()

		return {
			"basic_info": {
				"budget_name": self.budget_name,
				"budget_period": self.budget_period,
				"budget_status": self.budget_status,
				"company": self.company,
				"fiscal_year": self.fiscal_year,
			},
			"financial_summary": {
				"total_income_budgeted": self.total_income_budgeted,
				"total_expenses_budgeted": self.total_expenses_budgeted,
				"total_actual_income": self.total_actual_income,
				"total_actual_expenses": self.total_actual_expenses,
				"net_budget": flt(self.total_income_budgeted) - flt(self.total_expenses_budgeted),
			},
			"performance": {
				"income_variance": self.income_variance_percentage,
				"expense_variance": self.expense_variance_percentage,
				"utilization_rate": self.budget_utilization_rate,
			},
			"approval": {
				"requires_approval": self.approval_required,
				"approved_by": self.approved_by,
				"approval_date": self.approval_date,
				"committee_decision": self.committee_decision,
			},
		}

	def get_current_alerts(self):
		"""Obtener alertas actuales del presupuesto"""
		alerts = []

		threshold = flt(self.variance_threshold_percentage) or 10.0

		if flt(self.expense_variance_percentage) > threshold:
			alerts.append(
				{
					"type": "overspending",
					"message": f"Gastos exceden presupuesto en {self.expense_variance_percentage:.1f}%",
					"severity": "high",
				}
			)

		if flt(self.income_variance_percentage) < -threshold:
			alerts.append(
				{
					"type": "income_deficit",
					"message": f"Ingresos por debajo del presupuesto en {abs(self.income_variance_percentage):.1f}%",
					"severity": "medium",
				}
			)

		return alerts

	# =============================================================================
	# STATIC METHODS
	# =============================================================================

	@staticmethod
	def get_active_budgets(company=None):
		"""Obtener presupuestos activos"""
		filters = {"budget_status": "Activo"}
		if company:
			filters["company"] = company

		return frappe.get_all(
			"Budget Planning",
			filters=filters,
			fields=[
				"name",
				"budget_name",
				"budget_period",
				"total_income_budgeted",
				"total_expenses_budgeted",
			],
		)

	@staticmethod
	def get_budget_performance_summary(fiscal_year=None):
		"""Obtener resumen de performance de presupuestos"""
		conditions = ""
		if fiscal_year:
			conditions = f"AND fiscal_year = '{fiscal_year}'"

		return frappe.db.sql(
			f"""
			SELECT
				budget_period,
				COUNT(*) as total_budgets,
				AVG(budget_utilization_rate) as avg_utilization,
				AVG(income_variance_percentage) as avg_income_variance,
				AVG(expense_variance_percentage) as avg_expense_variance
			FROM `tabBudget Planning`
			WHERE budget_status IN ('Activo', 'Cerrado')
			{conditions}
			GROUP BY budget_period
		""",
			as_dict=True,
		)
