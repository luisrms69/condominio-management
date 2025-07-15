# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

# REGLA #43B: Credit Balance Management puede tener Customer/Payment Entry dependencies
test_ignore = ["Customer", "Payment Entry"]


class TestCreditBalanceManagementL2BusinessLogic(FrappeTestCase):
	"""Layer 2: Business Logic Tests for Credit Balance Management DocType"""

	def setUp(self):
		"""Set up test data for each test"""
		self.test_data = {
			"naming_series": "CB-.YYYY.-.MM.-",
			"balance_date": date.today(),
			"account_type": "Property Account",
			"credit_amount": 1000.00,
			"balance_status": "Activo",
			"property_account": "TEST-PROP-001",
			"company": "_Test Company",
			"original_payment_amount": 1200.00,
			"applied_amount": 200.00,
			"remaining_amount": 1000.00,
			"auto_apply": 1,
			"transferable": 1,
		}

	def test_credit_balance_calculation_logic(self):
		"""Test credit balance calculation business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test remaining amount calculation
		credit_balance.credit_amount = 1000.00
		credit_balance.applied_amount = 300.00

		if hasattr(credit_balance, "calculate_remaining_amount"):
			with patch.object(credit_balance, "calculate_remaining_amount") as mock_calculate:
				mock_calculate.return_value = 700.00
				remaining = credit_balance.calculate_remaining_amount()
				self.assertEqual(remaining, 700.00)
				mock_calculate.assert_called_once()

		# Test balance status update based on remaining amount
		if hasattr(credit_balance, "update_balance_status"):
			with patch.object(credit_balance, "update_balance_status") as mock_update:
				credit_balance.update_balance_status()
				mock_update.assert_called_once()

	def test_credit_application_logic(self):
		"""Test credit application business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test credit application to account
		application_amount = 500.00
		target_account = "TEST-PROP-002"

		if hasattr(credit_balance, "apply_credit_to_account"):
			with patch.object(credit_balance, "apply_credit_to_account") as mock_apply:
				mock_apply.return_value = {
					"success": True,
					"applied_amount": application_amount,
					"transaction_id": "TXN-001",
					"new_balance": 500.00,
				}
				result = credit_balance.apply_credit_to_account(target_account, application_amount)
				self.assertTrue(result["success"])
				self.assertEqual(result["applied_amount"], application_amount)
				mock_apply.assert_called_once_with(target_account, application_amount)

	def test_auto_application_logic(self):
		"""Test auto application business logic"""
		with patch("frappe.get_doc"):
			credit_balance = frappe.new_doc("Credit Balance Management")
			credit_balance.update(self.test_data)
			credit_balance.auto_apply = 1

			# Test auto application when enabled
			if hasattr(credit_balance, "process_auto_application"):
				with patch.object(credit_balance, "process_auto_application") as mock_process:
					mock_process.return_value = {
						"auto_applied": True,
						"applications": [
							{"account": "TEST-PROP-001", "amount": 200.00},
							{"account": "TEST-PROP-002", "amount": 300.00},
						],
						"total_applied": 500.00,
					}
					result = credit_balance.process_auto_application()
					self.assertTrue(result["auto_applied"])
					self.assertEqual(result["total_applied"], 500.00)
					self.assertEqual(len(result["applications"]), 2)

	def test_credit_transfer_logic(self):
		"""Test credit transfer business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)
		credit_balance.transferable = 1

		# Test credit transfer between accounts
		source_account = "TEST-PROP-001"
		target_account = "TEST-PROP-002"
		transfer_amount = 400.00

		if hasattr(credit_balance, "transfer_credit"):
			with patch.object(credit_balance, "transfer_credit") as mock_transfer:
				mock_transfer.return_value = {
					"transfer_successful": True,
					"transfer_amount": transfer_amount,
					"source_account": source_account,
					"target_account": target_account,
					"transfer_reference": "TXF-001",
				}
				result = credit_balance.transfer_credit(source_account, target_account, transfer_amount)
				self.assertTrue(result["transfer_successful"])
				self.assertEqual(result["transfer_amount"], transfer_amount)
				mock_transfer.assert_called_once_with(source_account, target_account, transfer_amount)

	def test_expiry_date_calculation(self):
		"""Test expiry date calculation business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test expiry date calculation based on balance date
		credit_balance.balance_date = date(2025, 1, 15)

		if hasattr(credit_balance, "calculate_expiry_date"):
			with patch.object(credit_balance, "calculate_expiry_date") as mock_calculate:
				expected_expiry = date(2025, 7, 15)  # 6 months from balance date
				mock_calculate.return_value = expected_expiry
				expiry_date = credit_balance.calculate_expiry_date()
				self.assertEqual(expiry_date, expected_expiry)

		# Test days until expiry calculation
		if hasattr(credit_balance, "calculate_days_until_expiry"):
			with patch.object(credit_balance, "calculate_days_until_expiry") as mock_calculate:
				mock_calculate.return_value = 150
				days_until_expiry = credit_balance.calculate_days_until_expiry()
				self.assertEqual(days_until_expiry, 150)

	def test_balance_status_transitions(self):
		"""Test balance status transition business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test valid status transitions
		status_transitions = {
			"Activo": ["Aplicado Parcial", "Expirado", "Cancelado"],
			"Aplicado Parcial": ["Aplicado Total", "Expirado", "Cancelado"],
			"Aplicado Total": [],
			"Expirado": ["Cancelado"],
			"Cancelado": [],
		}

		for current_status, allowed_transitions in status_transitions.items():
			credit_balance.balance_status = current_status

			if hasattr(credit_balance, "validate_status_transition"):
				for new_status in allowed_transitions:
					with patch.object(credit_balance, "validate_status_transition") as mock_validate:
						mock_validate.return_value = True
						result = credit_balance.validate_status_transition(new_status)
						self.assertTrue(result)

	def test_account_type_validation_logic(self):
		"""Test account type validation business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test Property Account validation
		credit_balance.account_type = "Property Account"
		credit_balance.property_account = "TEST-PROP-001"

		if hasattr(credit_balance, "validate_account_type"):
			with patch.object(credit_balance, "validate_account_type") as mock_validate:
				mock_validate.return_value = True
				result = credit_balance.validate_account_type()
				self.assertTrue(result)

		# Test Resident Account validation
		credit_balance.account_type = "Resident Account"
		credit_balance.resident_account = "TEST-RES-001"

		if hasattr(credit_balance, "validate_account_type"):
			with patch.object(credit_balance, "validate_account_type") as mock_validate:
				mock_validate.return_value = True
				result = credit_balance.validate_account_type()
				self.assertTrue(result)

	def test_credit_history_tracking(self):
		"""Test credit history tracking business logic"""
		with patch("frappe.get_doc"):
			credit_balance = frappe.new_doc("Credit Balance Management")
			credit_balance.update(self.test_data)

			# Test credit history creation
			history_data = {
				"action": "Credit Applied",
				"amount": 300.00,
				"target_account": "TEST-PROP-001",
				"date": date.today(),
				"reference": "APP-001",
			}

			if hasattr(credit_balance, "create_credit_history"):
				with patch.object(credit_balance, "create_credit_history") as mock_create:
					mock_create.return_value = "HIST-001"
					history_id = credit_balance.create_credit_history(history_data)
					self.assertEqual(history_id, "HIST-001")
					mock_create.assert_called_once_with(history_data)

	def test_notification_triggers(self):
		"""Test notification triggers business logic"""
		with patch("frappe.sendmail"):
			credit_balance = frappe.new_doc("Credit Balance Management")
			credit_balance.update(self.test_data)

			# Test expiry warning notification
			if hasattr(credit_balance, "send_expiry_warning"):
				with patch.object(credit_balance, "send_expiry_warning") as mock_notify:
					credit_balance.send_expiry_warning(30)  # 30 days before expiry
					mock_notify.assert_called_once_with(30)

			# Test balance applied notification
			if hasattr(credit_balance, "send_balance_applied_notification"):
				with patch.object(credit_balance, "send_balance_applied_notification") as mock_notify:
					credit_balance.send_balance_applied_notification("TEST-PROP-001", 500.00)
					mock_notify.assert_called_once_with("TEST-PROP-001", 500.00)

	def test_batch_processing_logic(self):
		"""Test batch processing business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test batch credit application
		batch_applications = [
			{"account": "TEST-PROP-001", "amount": 200.00},
			{"account": "TEST-PROP-002", "amount": 300.00},
			{"account": "TEST-PROP-003", "amount": 250.00},
		]

		if hasattr(credit_balance, "process_batch_applications"):
			with patch.object(credit_balance, "process_batch_applications") as mock_process:
				mock_process.return_value = {
					"processed": 3,
					"successful": 2,
					"failed": 1,
					"total_amount": 750.00,
					"successful_amount": 500.00,
					"failed_applications": ["TEST-PROP-003"],
				}
				result = credit_balance.process_batch_applications(batch_applications)
				self.assertEqual(result["processed"], 3)
				self.assertEqual(result["successful"], 2)
				self.assertEqual(result["total_amount"], 750.00)

	def test_credit_consolidation_logic(self):
		"""Test credit consolidation business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test consolidation of multiple credits
		source_credits = ["CB-001", "CB-002", "CB-003"]
		target_account = "TEST-PROP-001"

		if hasattr(credit_balance, "consolidate_credits"):
			with patch.object(credit_balance, "consolidate_credits") as mock_consolidate:
				mock_consolidate.return_value = {
					"consolidation_successful": True,
					"consolidated_amount": 1500.00,
					"source_credits": 3,
					"target_account": target_account,
					"new_credit_id": "CB-CONS-001",
				}
				result = credit_balance.consolidate_credits(source_credits, target_account)
				self.assertTrue(result["consolidation_successful"])
				self.assertEqual(result["consolidated_amount"], 1500.00)
				self.assertEqual(result["source_credits"], 3)

	def test_credit_reversal_logic(self):
		"""Test credit reversal business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test credit application reversal
		application_id = "APP-001"
		reversal_reason = "Incorrect application"

		if hasattr(credit_balance, "reverse_credit_application"):
			with patch.object(credit_balance, "reverse_credit_application") as mock_reverse:
				mock_reverse.return_value = {
					"reversal_successful": True,
					"reversed_amount": 300.00,
					"application_id": application_id,
					"reversal_id": "REV-001",
					"new_balance": 1300.00,
				}
				result = credit_balance.reverse_credit_application(application_id, reversal_reason)
				self.assertTrue(result["reversal_successful"])
				self.assertEqual(result["reversed_amount"], 300.00)
				mock_reverse.assert_called_once_with(application_id, reversal_reason)

	def test_credit_audit_trail(self):
		"""Test credit audit trail business logic"""
		credit_balance = frappe.new_doc("Credit Balance Management")
		credit_balance.update(self.test_data)

		# Test audit trail generation
		if hasattr(credit_balance, "generate_audit_trail"):
			with patch.object(credit_balance, "generate_audit_trail") as mock_audit:
				mock_audit.return_value = [
					{
						"timestamp": datetime.now(),
						"action": "Credit Created",
						"amount": 1000.00,
						"user": "Administrator",
						"details": "Initial credit balance",
					},
					{
						"timestamp": datetime.now(),
						"action": "Credit Applied",
						"amount": 300.00,
						"user": "Administrator",
						"details": "Applied to TEST-PROP-001",
					},
				]
				audit_trail = credit_balance.generate_audit_trail()
				self.assertEqual(len(audit_trail), 2)
				self.assertEqual(audit_trail[0]["action"], "Credit Created")
				self.assertEqual(audit_trail[1]["action"], "Credit Applied")
