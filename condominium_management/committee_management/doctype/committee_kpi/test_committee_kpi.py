# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCommitteeKPI(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-KPI-%"')
		frappe.db.sql('DELETE FROM `tabCommittee KPI` WHERE committee_member LIKE "%TEST-MEMBER-KPI%"')
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-KPI-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test KPI Company"')

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code LIKE "TEST-PROP-KPI-%"')
		frappe.db.sql('DELETE FROM `tabCommittee KPI` WHERE committee_member LIKE "%TEST-MEMBER-KPI%"')
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "TEST-PROP-KPI-%"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test KPI Company"')

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for committee KPI tests"""
		# Create test company
		if not frappe.db.exists("Company", "Test KPI Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test KPI Company', 'Test KPI Company', 'TKC', 'USD')"
			)
			frappe.db.commit()

		# Create test properties
		cls.test_properties = []
		for i in range(2):
			prop_code = f"TEST-PROP-KPI-{i+1:03d}"
			if not frappe.db.exists("Property Registry", prop_code):
				property_doc = frappe.get_doc(
					{
						"doctype": "Property Registry",
						"property_code": prop_code,
						"property_name": f"Test KPI Property {i+1}",
						"naming_series": "PROP-.YYYY.-",
						"company": "Test KPI Company",
						"property_usage_type": "Residencial",
						"acquisition_type": "Compra",
						"property_status_type": "Activo",
						"registration_date": nowdate(),
					}
				)
				property_doc.insert(ignore_permissions=True)
				cls.test_properties.append(prop_code)

		# Create test committee members
		cls.test_members = []
		for i, prop_code in enumerate(cls.test_properties):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"property_registry": prop_code,
					"role_in_committee": "Presidente" if i == 0 else "Miembro",
					"start_date": nowdate(),
					"end_date": add_days(nowdate(), 365),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			cls.test_members.append(member.name)

	def test_committee_kpi_creation(self):
		"""Test basic committee KPI creation"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Mensual",
				"kpi_month": "01",
				"meetings_attended": 5,
				"meetings_organized": 2,
				"agreements_fulfilled": 3,
				"performance_score": 85.5,
			}
		)

		kpi.insert()

		# Verify the document was created
		self.assertTrue(kpi.name)
		self.assertEqual(kpi.committee_member, self.__class__.test_members[0])
		self.assertEqual(kpi.period_year, 2025)
		self.assertEqual(kpi.meetings_attended, 5)
		self.assertEqual(kpi.performance_score, 85.5)

		# Clean up
		kpi.delete()

	def test_kpi_calculation(self):
		"""Test KPI calculation functionality"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Mensual",
				"kpi_month": "02",
				"meetings_attended": 8,
				"meetings_organized": 3,
				"agreements_fulfilled": 5,
				"agreements_overdue": 1,
				"community_events_organized": 2,
			}
		)

		kpi.insert()

		# Calculate performance score
		kpi.calculate_performance_score()

		# Verify calculation (should be based on weighted metrics)
		self.assertGreater(kpi.performance_score, 0)
		self.assertLessEqual(kpi.performance_score, 100)

		# Clean up
		kpi.delete()

	def test_monthly_kpi_aggregation(self):
		"""Test aggregating monthly KPIs"""
		# Create monthly KPIs for a member
		months = ["01", "02", "03"]
		kpi_docs = []

		for month in months:
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": self.__class__.test_members[0],
					"period_year": 2025,
					"kpi_period": "Mensual",
					"kpi_month": month,
					"meetings_attended": 4,
					"meetings_organized": 1,
					"agreements_fulfilled": 2,
					"performance_score": 75.0,
				}
			)
			kpi.insert()
			kpi_docs.append(kpi)

		# Create quarterly aggregation
		quarterly_kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Trimestral",
				"kpi_quarter": "Q1",
			}
		)
		quarterly_kpi.insert()

		# Aggregate monthly data
		quarterly_kpi.aggregate_monthly_data()

		# Verify aggregation
		self.assertEqual(quarterly_kpi.meetings_attended, 12)  # 4 * 3 months
		self.assertEqual(quarterly_kpi.meetings_organized, 3)  # 1 * 3 months
		self.assertEqual(quarterly_kpi.agreements_fulfilled, 6)  # 2 * 3 months

		# Clean up
		quarterly_kpi.delete()
		for kpi in kpi_docs:
			kpi.delete()

	def test_annual_kpi_summary(self):
		"""Test creating annual KPI summary"""
		# Create quarterly KPIs
		quarters = ["Q1", "Q2", "Q3", "Q4"]
		quarterly_kpis = []

		for quarter in quarters:
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": self.__class__.test_members[0],
					"period_year": 2025,
					"kpi_period": "Trimestral",
					"kpi_quarter": quarter,
					"meetings_attended": 12,
					"meetings_organized": 3,
					"agreements_fulfilled": 6,
					"performance_score": 80.0,
				}
			)
			kpi.insert()
			quarterly_kpis.append(kpi)

		# Create annual summary
		annual_kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Anual",
			}
		)
		annual_kpi.insert()

		# Aggregate quarterly data
		annual_kpi.aggregate_quarterly_data()

		# Verify aggregation
		self.assertEqual(annual_kpi.meetings_attended, 48)  # 12 * 4 quarters
		self.assertEqual(annual_kpi.meetings_organized, 12)  # 3 * 4 quarters
		self.assertEqual(annual_kpi.agreements_fulfilled, 24)  # 6 * 4 quarters

		# Clean up
		annual_kpi.delete()
		for kpi in quarterly_kpis:
			kpi.delete()

	def test_kpi_comparison(self):
		"""Test KPI comparison between members"""
		# Create KPIs for different members
		kpis = []
		for i, member in enumerate(self.__class__.test_members):
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": member,
					"period_year": 2025,
					"kpi_period": "Mensual",
					"kpi_month": "03",
					"meetings_attended": 5 + i,
					"meetings_organized": 2 + i,
					"agreements_fulfilled": 3 + i,
					"performance_score": 75.0 + (i * 5),
				}
			)
			kpi.insert()
			kpis.append(kpi)

		# Compare KPIs
		comparison_data = kpis[0].compare_with_peers(2025, "Mensual", "03")

		# Verify comparison data
		self.assertIsNotNone(comparison_data)
		self.assertIn("average_performance", comparison_data)
		self.assertIn("ranking", comparison_data)

		# Clean up
		for kpi in kpis:
			kpi.delete()

	def test_kpi_trend_analysis(self):
		"""Test KPI trend analysis"""
		# Create KPIs for multiple months
		months = ["01", "02", "03", "04"]
		kpi_docs = []

		for i, month in enumerate(months):
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": self.__class__.test_members[0],
					"period_year": 2025,
					"kpi_period": "Mensual",
					"kpi_month": month,
					"meetings_attended": 4 + i,  # Increasing trend
					"meetings_organized": 2,
					"agreements_fulfilled": 3 - i if i < 3 else 0,  # Decreasing trend
					"performance_score": 70.0 + (i * 5),  # Increasing trend
				}
			)
			kpi.insert()
			kpi_docs.append(kpi)

		# Analyze trends
		trend_data = kpi_docs[-1].analyze_trends(2025)

		# Verify trend analysis
		self.assertIsNotNone(trend_data)
		self.assertIn("meetings_attended_trend", trend_data)
		self.assertIn("performance_trend", trend_data)

		# Clean up
		for kpi in kpi_docs:
			kpi.delete()

	def test_kpi_alerts(self):
		"""Test KPI alert generation"""
		# Create KPI with poor performance
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Mensual",
				"kpi_month": "05",
				"meetings_attended": 1,  # Low attendance
				"meetings_organized": 0,
				"agreements_fulfilled": 0,
				"agreements_overdue": 3,  # High overdue
				"performance_score": 35.0,  # Low performance
			}
		)

		kpi.insert()

		# Generate alerts
		alerts = kpi.generate_performance_alerts()

		# Verify alerts
		self.assertIsNotNone(alerts)
		self.assertGreater(len(alerts), 0)

		# Clean up
		kpi.delete()

	def test_kpi_export(self):
		"""Test KPI data export"""
		# Create sample KPIs
		kpi_docs = []
		for i in range(3):
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": self.__class__.test_members[0],
					"period_year": 2025,
					"kpi_period": "Mensual",
					"kpi_month": f"{i+1:02d}",
					"meetings_attended": 4 + i,
					"meetings_organized": 1,
					"agreements_fulfilled": 2 + i,
					"performance_score": 75.0 + (i * 5),
				}
			)
			kpi.insert()
			kpi_docs.append(kpi)

		# Export KPI data
		export_data = kpi_docs[0].export_kpi_data(2025, "Mensual")

		# Verify export
		self.assertIsNotNone(export_data)
		self.assertGreater(len(export_data), 0)

		# Clean up
		for kpi in kpi_docs:
			kpi.delete()

	def test_unique_kpi_constraint(self):
		"""Test unique constraint for KPI records"""
		# Create first KPI
		kpi1 = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Mensual",
				"kpi_month": "06",
				"meetings_attended": 5,
				"performance_score": 80.0,
			}
		)
		kpi1.insert()

		# Try to create duplicate KPI
		kpi2 = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.__class__.test_members[0],
				"period_year": 2025,
				"kpi_period": "Mensual",
				"kpi_month": "06",  # Same period
				"meetings_attended": 3,
				"performance_score": 70.0,
			}
		)

		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			kpi2.insert()

		# Clean up
		kpi1.delete()

	# tearDown removed - using tearDownClass pattern from REGLA #29


if __name__ == "__main__":
	unittest.main()
