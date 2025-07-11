# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCommitteeKPI(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		self.setup_test_data()

	def setup_test_data(self):
		"""Create test data for committee KPI tests"""
		# Create test committee member
		if not frappe.db.exists("Committee Member", {"member_name": "Test KPI Member"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"member_name": "Test KPI Member",
					"role": "Secretario",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			self.test_committee_member = member.name
		else:
			self.test_committee_member = frappe.get_value(
				"Committee Member", {"member_name": "Test KPI Member"}, "name"
			)

	def test_committee_kpi_creation(self):
		"""Test basic committee KPI creation"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": 5,
				"meetings_organized": 2,
				"agreements_created": 3,
				"agreements_completed": 2,
				"polls_created": 1,
				"events_organized": 1,
			}
		)

		kpi.insert()

		# Verify the document was created
		self.assertTrue(kpi.name)
		self.assertEqual(kpi.committee_member, self.test_committee_member)
		self.assertEqual(kpi.kpi_period, "Mensual")
		self.assertEqual(kpi.meetings_attended, 5)

		# Clean up
		kpi.delete()

	def test_negative_values_validation(self):
		"""Test that KPI values cannot be negative"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": -1,  # Negative value
			}
		)

		with self.assertRaises(frappe.ValidationError):
			kpi.insert()

	def test_percentage_validation(self):
		"""Test that percentage fields must be between 0 and 100"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"attendance_rate": 150,  # Invalid percentage
			}
		)

		with self.assertRaises(frappe.ValidationError):
			kpi.insert()

	def test_monthly_period_validation(self):
		"""Test that monthly KPIs must specify month"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				# No kpi_month specified
			}
		)

		with self.assertRaises(frappe.ValidationError):
			kpi.insert()

	def test_calculate_performance_metrics(self):
		"""Test performance metrics calculation"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": 8,
				"meetings_organized": 2,
				"agreements_created": 5,
				"agreements_completed": 4,
				"polls_created": 3,
				"events_organized": 1,
			}
		)

		kpi.insert()

		# Calculate performance metrics
		kpi.calculate_performance_metrics()

		# Verify calculations
		# Completion rate: agreements_completed / agreements_created = 4/5 = 80%
		self.assertEqual(kpi.completion_rate, 80)

		# Performance score should be calculated based on weighted activities
		self.assertGreater(kpi.performance_score, 0)
		self.assertLessEqual(kpi.performance_score, 100)

		# Clean up
		kpi.delete()

	def test_update_meeting_attendance(self):
		"""Test updating meeting attendance KPI"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": 3,
			}
		)

		kpi.insert()

		# Update meeting attendance
		kpi.update_meeting_attendance(2)  # Add 2 more meetings

		# Verify update
		self.assertEqual(kpi.meetings_attended, 5)

		# Clean up
		kpi.delete()

	def test_update_agreement_metrics(self):
		"""Test updating agreement-related metrics"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"agreements_created": 2,
				"agreements_completed": 1,
			}
		)

		kpi.insert()

		# Update agreement metrics
		kpi.update_agreement_metrics(1, 1)  # Add 1 created, 1 completed

		# Verify updates
		self.assertEqual(kpi.agreements_created, 3)
		self.assertEqual(kpi.agreements_completed, 2)

		# Clean up
		kpi.delete()

	def test_get_monthly_kpi(self):
		"""Test getting monthly KPI for a committee member"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": 4,
			}
		)

		kpi.insert()

		# Get monthly KPI
		monthly_kpi = kpi.get_monthly_kpi(self.test_committee_member, "2025", "01")

		# Verify result
		self.assertIsNotNone(monthly_kpi)
		self.assertEqual(monthly_kpi["meetings_attended"], 4)

		# Clean up
		kpi.delete()

	def test_get_member_performance_trend(self):
		"""Test getting performance trend for a member"""
		# Create KPIs for multiple months
		months = ["01", "02", "03"]
		scores = [75, 80, 85]

		kpi_records = []
		for i, month in enumerate(months):
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": self.test_committee_member,
					"kpi_period": "Mensual",
					"kpi_year": "2025",
					"kpi_month": month,
					"performance_score": scores[i],
				}
			)
			kpi.insert()
			kpi_records.append(kpi)

		# Get performance trend
		trend = kpi_records[0].get_member_performance_trend(self.test_committee_member, "2025")

		# Verify trend
		self.assertEqual(len(trend), 3)
		self.assertEqual(trend[0]["performance_score"], 75)
		self.assertEqual(trend[-1]["performance_score"], 85)

		# Clean up
		for kpi in kpi_records:
			kpi.delete()

	def test_get_top_performers(self):
		"""Test getting top performing committee members"""
		# Create KPIs for multiple members
		members_data = [
			{"name": "Member A", "score": 90},
			{"name": "Member B", "score": 85},
			{"name": "Member C", "score": 95},
		]

		kpi_records = []
		for member_data in members_data:
			# Create committee member
			if not frappe.db.exists("Committee Member", {"member_name": member_data["name"]}):
				member = frappe.get_doc(
					{
						"doctype": "Committee Member",
						"member_name": member_data["name"],
						"role": "Vocal",
						"start_date": nowdate(),
						"is_active": 1,
					}
				)
				member.insert(ignore_permissions=True)

			member_name = frappe.get_value("Committee Member", {"member_name": member_data["name"]}, "name")

			# Create KPI
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": member_name,
					"kpi_period": "Mensual",
					"kpi_year": "2025",
					"kpi_month": "01",
					"performance_score": member_data["score"],
				}
			)
			kpi.insert()
			kpi_records.append(kpi)

		# Get top performers
		top_performers = kpi_records[0].get_top_performers("2025", "01", 2)

		# Verify results (should be Member C and Member A)
		self.assertEqual(len(top_performers), 2)
		self.assertEqual(top_performers[0]["performance_score"], 95)  # Member C
		self.assertEqual(top_performers[1]["performance_score"], 90)  # Member A

		# Clean up
		for kpi in kpi_records:
			kpi.delete()

	def test_calculate_committee_average(self):
		"""Test calculating committee average performance"""
		# Create multiple KPI records
		scores = [80, 85, 90, 75]
		kpi_records = []

		for i, score in enumerate(scores):
			# Create committee member
			member_name = f"Avg Test Member {i+1}"
			if not frappe.db.exists("Committee Member", {"member_name": member_name}):
				member = frappe.get_doc(
					{
						"doctype": "Committee Member",
						"member_name": member_name,
						"role": "Vocal",
						"start_date": nowdate(),
						"is_active": 1,
					}
				)
				member.insert(ignore_permissions=True)

			member_id = frappe.get_value("Committee Member", {"member_name": member_name}, "name")

			# Create KPI
			kpi = frappe.get_doc(
				{
					"doctype": "Committee KPI",
					"committee_member": member_id,
					"kpi_period": "Mensual",
					"kpi_year": "2025",
					"kpi_month": "01",
					"performance_score": score,
				}
			)
			kpi.insert()
			kpi_records.append(kpi)

		# Calculate committee average
		average = kpi_records[0].calculate_committee_average("2025", "01")

		# Verify average (80+85+90+75)/4 = 82.5
		expected_average = sum(scores) / len(scores)
		self.assertEqual(average, expected_average)

		# Clean up
		for kpi in kpi_records:
			kpi.delete()

	def test_generate_monthly_report(self):
		"""Test generating monthly KPI report"""
		kpi = frappe.get_doc(
			{
				"doctype": "Committee KPI",
				"committee_member": self.test_committee_member,
				"kpi_period": "Mensual",
				"kpi_year": "2025",
				"kpi_month": "01",
				"meetings_attended": 6,
				"meetings_organized": 2,
				"agreements_created": 4,
				"agreements_completed": 3,
				"performance_score": 85,
			}
		)

		kpi.insert()

		# Generate monthly report
		report = kpi.generate_monthly_report(self.test_committee_member, "2025", "01")

		# Verify report structure
		self.assertIn("member_info", report)
		self.assertIn("kpi_summary", report)
		self.assertIn("performance_analysis", report)
		self.assertEqual(report["kpi_summary"]["meetings_attended"], 6)
		self.assertEqual(report["kpi_summary"]["performance_score"], 85)

		# Clean up
		kpi.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up test KPIs
		frappe.db.delete("Committee KPI", {"committee_member": self.test_committee_member})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
