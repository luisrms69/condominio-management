# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import calendar
from datetime import datetime, timedelta

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, cint, flt, getdate, nowdate


class CommitteeKPI(Document):
	def validate(self):
		self.validate_period()
		self.set_calculation_date()

	def validate_period(self):
		"""Validate period year and month"""
		if self.period_month < 1 or self.period_month > 12:
			frappe.throw("El mes debe estar entre 1 y 12")

		current_year = datetime.now().year
		if self.period_year > current_year:
			frappe.throw("No se pueden calcular KPIs para períodos futuros")

	def set_calculation_date(self):
		"""Set calculation date to today"""
		if not self.calculation_date:
			self.calculation_date = nowdate()

	def calculate_all_kpis(self):
		"""Calculate all KPIs for the period"""
		start_date, end_date = self.get_period_dates()

		# Governance KPIs
		self.calculate_governance_kpis(start_date, end_date)

		# Financial KPIs
		self.calculate_financial_kpis(start_date, end_date)

		# Operational KPIs
		self.calculate_operational_kpis(start_date, end_date)

		# Compliance KPIs
		self.calculate_compliance_kpis(start_date, end_date)

		# Update status
		self.status = "Calculado"
		self.calculation_date = nowdate()

		# Set data sources
		self.data_sources = self.get_data_sources_text()

		self.save()

	def get_period_dates(self):
		"""Get start and end dates for the period"""
		start_date = datetime(self.period_year, self.period_month, 1).date()

		# Get last day of the month
		last_day = calendar.monthrange(self.period_year, self.period_month)[1]
		end_date = datetime(self.period_year, self.period_month, last_day).date()

		return start_date, end_date

	def calculate_governance_kpis(self, start_date, end_date):
		"""Calculate governance-related KPIs"""
		# Assembly Participation Rate
		assemblies = frappe.get_all(
			"Assembly Management",
			filters={"assembly_date": ["between", [start_date, end_date]], "docstatus": 1},
			fields=["current_quorum_percentage"],
		)

		if assemblies:
			avg_participation = sum([a.current_quorum_percentage or 0 for a in assemblies]) / len(assemblies)
			self.assembly_participation_rate = avg_participation

		# Agreement Completion Rate
		agreements = frappe.get_all(
			"Agreement Tracking",
			filters={"agreement_date": ["between", [start_date, end_date]]},
			fields=["status"],
		)

		if agreements:
			completed = len([a for a in agreements if a.status == "Completado"])
			self.agreement_completion_rate = (completed / len(agreements)) * 100

		# Meeting Attendance Rate
		meetings = frappe.get_all(
			"Committee Meeting", filters={"meeting_date": ["between", [start_date, end_date]]}
		)

		if meetings:
			total_attendance = 0
			total_possible = 0

			for meeting in meetings:
				meeting_doc = frappe.get_doc("Committee Meeting", meeting.name)
				attendance_summary = meeting_doc.get_attendance_summary()
				total_attendance += attendance_summary.get("attending_count", 0)
				total_possible += attendance_summary.get("total_attendees", 0)

			if total_possible > 0:
				self.meeting_attendance_rate = (total_attendance / total_possible) * 100

		# Poll Participation Rate
		polls = frappe.get_all(
			"Committee Poll",
			filters={"start_date": ["between", [start_date, end_date]]},
			fields=["participation_rate"],
		)

		if polls:
			avg_poll_participation = sum([p.participation_rate or 0 for p in polls]) / len(polls)
			self.poll_participation_rate = avg_poll_participation

		# Voting Participation Rate
		votings = frappe.get_all(
			"Voting System",
			filters={"voting_start_time": ["between", [start_date, end_date]]},
			fields=["total_voting_power_present"],
		)

		if votings:
			avg_voting_participation = sum([v.total_voting_power_present or 0 for v in votings]) / len(
				votings
			)
			self.voting_participation_rate = avg_voting_participation

		# Calculate Community Engagement Score (composite)
		self.calculate_community_engagement_score()

	def calculate_financial_kpis(self, start_date, end_date):
		"""Calculate financial KPIs"""
		# Event Budget Efficiency
		events = frappe.get_all(
			"Community Event",
			filters={"event_date": ["between", [start_date, end_date]], "status": "Completado"},
			fields=["budget_amount", "total_actual_cost"],
		)

		if events:
			total_budget = sum([e.budget_amount or 0 for e in events])
			total_actual = sum([e.total_actual_cost or 0 for e in events])

			if total_budget > 0:
				self.event_budget_efficiency = (total_actual / total_budget) * 100

		# These would integrate with financial modules when available
		# For now, set placeholder values
		self.collection_efficiency = 95.0  # Placeholder
		self.budget_variance = 5.0  # Placeholder
		self.expense_reduction = 3.0  # Placeholder
		self.reserve_fund_months = 6.0  # Placeholder
		self.cost_per_resident = 150000  # Placeholder

	def calculate_operational_kpis(self, start_date, end_date):
		"""Calculate operational KPIs"""
		# Community Event Participation
		events = frappe.get_all(
			"Community Event",
			filters={"event_date": ["between", [start_date, end_date]], "status": "Completado"},
			fields=["expected_attendance", "actual_attendance"],
		)

		if events:
			total_expected = sum([e.expected_attendance or 0 for e in events])
			total_actual = sum([e.actual_attendance or 0 for e in events])

			if total_expected > 0:
				self.community_event_participation = (total_actual / total_expected) * 100

		# Agreement Fulfillment Rate (same as completion rate but for operational context)
		self.agreement_fulfillment_rate = self.agreement_completion_rate

		# Space Utilization Rate
		space_usage = frappe.get_all(
			"Committee Meeting",
			filters={"meeting_date": ["between", [start_date, end_date]]},
			fields=["physical_space"],
		)

		events_space_usage = frappe.get_all(
			"Community Event",
			filters={"event_date": ["between", [start_date, end_date]]},
			fields=["physical_space"],
		)

		total_space_uses = len(space_usage) + len(events_space_usage)
		total_available_spaces = frappe.db.count("Physical Space", {"is_active": 1})

		if total_available_spaces > 0:
			# Simple calculation - could be more sophisticated
			days_in_month = (end_date - start_date).days + 1
			possible_uses = total_available_spaces * days_in_month
			self.space_utilization_rate = (total_space_uses / possible_uses) * 100

		# Placeholder values for metrics that require other modules
		self.maintenance_resolution_time = "2:00:00"  # 2 hours placeholder
		self.supplier_performance_avg = 4.2  # Placeholder rating
		self.incident_response_time = "0:30:00"  # 30 minutes placeholder

	def calculate_compliance_kpis(self, start_date, end_date):
		"""Calculate compliance KPIs"""
		# Document Update Status
		documents_requiring_update = frappe.get_all(
			"Agreement Tracking", filters={"due_date": ["<=", end_date], "status": ["!=", "Completado"]}
		)

		all_agreements = frappe.get_all("Agreement Tracking", filters={"agreement_date": ["<=", end_date]})

		if all_agreements:
			overdue_count = len(documents_requiring_update)
			total_count = len(all_agreements)
			update_rate = ((total_count - overdue_count) / total_count) * 100
			self.document_update_status = update_rate

		# Transparency Index (based on document availability and meeting minutes)
		completed_meetings = frappe.db.count(
			"Committee Meeting", {"meeting_date": ["between", [start_date, end_date]], "status": "Completada"}
		)

		total_meetings = frappe.db.count(
			"Committee Meeting", {"meeting_date": ["between", [start_date, end_date]]}
		)

		if total_meetings > 0:
			transparency_score = (completed_meetings / total_meetings) * 100
			self.transparency_index = transparency_score / 100  # Convert to 0-1 scale

		# Placeholder values for complex compliance metrics
		self.regulatory_compliance_score = 92.0  # Placeholder
		self.legal_requirement_compliance = 95.0  # Placeholder
		self.audit_readiness_score = 88.0  # Placeholder
		self.policy_violations_trend = "Estable"  # Placeholder

	def calculate_community_engagement_score(self):
		"""Calculate composite community engagement score"""
		scores = []

		if self.assembly_participation_rate:
			scores.append(self.assembly_participation_rate / 100)

		if self.poll_participation_rate:
			scores.append(self.poll_participation_rate / 100)

		if self.voting_participation_rate:
			scores.append(self.voting_participation_rate / 100)

		if self.community_event_participation:
			scores.append(self.community_event_participation / 100)

		if scores:
			self.community_engagement_score = sum(scores) / len(scores)

	def get_data_sources_text(self):
		"""Get text describing data sources used"""
		sources = [
			"Assembly Management - Participación en asambleas y quórum",
			"Committee Meeting - Asistencia a reuniones del comité",
			"Agreement Tracking - Cumplimiento de acuerdos",
			"Committee Poll - Participación en encuestas",
			"Voting System - Participación en votaciones",
			"Community Event - Participación en eventos comunitarios",
			"Physical Space - Utilización de espacios",
		]

		return "\n".join(sources)

	def get_kpi_summary(self):
		"""Get KPI summary for dashboard"""
		return {
			"period": f"{self.period_year}-{str(self.period_month).zfill(2)}",
			"status": self.status,
			"governance": {
				"assembly_participation": self.assembly_participation_rate,
				"agreement_completion": self.agreement_completion_rate,
				"meeting_attendance": self.meeting_attendance_rate,
				"community_engagement": self.community_engagement_score,
			},
			"financial": {
				"collection_efficiency": self.collection_efficiency,
				"budget_variance": self.budget_variance,
				"event_budget_efficiency": self.event_budget_efficiency,
			},
			"operational": {
				"event_participation": self.community_event_participation,
				"space_utilization": self.space_utilization_rate,
				"agreement_fulfillment": self.agreement_fulfillment_rate,
			},
			"compliance": {
				"regulatory_compliance": self.regulatory_compliance_score,
				"document_update": self.document_update_status,
				"transparency_index": self.transparency_index,
			},
		}

	def get_performance_trends(self, months_back=6):
		"""Get performance trends for the last N months"""
		trends = {}

		for i in range(months_back):
			period_date = add_months(getdate(f"{self.period_year}-{self.period_month}-01"), -i)

			kpi_record = frappe.get_value(
				"Committee KPI",
				{"period_year": period_date.year, "period_month": period_date.month},
				[
					"assembly_participation_rate",
					"agreement_completion_rate",
					"community_engagement_score",
					"event_budget_efficiency",
				],
				as_dict=True,
			)

			if kpi_record:
				period_key = f"{period_date.year}-{str(period_date.month).zfill(2)}"
				trends[period_key] = kpi_record

		return trends

	@staticmethod
	def generate_monthly_kpis(year, month):
		"""Generate KPIs for a specific month"""
		# Check if KPIs already exist for this period
		existing_kpi = frappe.get_value("Committee KPI", {"period_year": year, "period_month": month}, "name")

		if existing_kpi:
			kpi_doc = frappe.get_doc("Committee KPI", existing_kpi)
		else:
			kpi_doc = frappe.get_doc({"doctype": "Committee KPI", "period_year": year, "period_month": month})
			kpi_doc.insert()

		# Calculate all KPIs
		kpi_doc.calculate_all_kpis()

		return kpi_doc

	@staticmethod
	def get_latest_kpis(limit=12):
		"""Get latest KPI records"""
		return frappe.get_all(
			"Committee KPI",
			fields=[
				"name",
				"period_year",
				"period_month",
				"status",
				"community_engagement_score",
				"assembly_participation_rate",
			],
			order_by="period_year desc, period_month desc",
			limit=limit,
		)

	@staticmethod
	def get_kpi_dashboard_data():
		"""Get KPI data for executive dashboard"""
		# Get latest completed KPI
		latest_kpi = frappe.get_all(
			"Committee KPI",
			filters={"status": ["in", ["Calculado", "Aprobado", "Publicado"]]},
			fields=["name"],
			order_by="period_year desc, period_month desc",
			limit=1,
		)

		if not latest_kpi:
			return None

		kpi_doc = frappe.get_doc("Committee KPI", latest_kpi[0].name)
		return kpi_doc.get_kpi_summary()
