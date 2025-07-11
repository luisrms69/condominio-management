# Frappe Test Auto-Generation Template

## Instructions for Continue.dev

Generate a complete, corrected FrappeTestCase for the given DocType following these specifications:

### Required Analysis Steps:
1. **Read DocType JSON** - Analyze the complete JSON structure
2. **Identify Required Fields** - Find all fields with `"reqd": 1`
3. **Identify Link Dependencies** - Find all Link fields and their target DocTypes
4. **Check Field Names** - Ensure exact match with JSON field names
5. **Create Master Data Setup** - Generate required masters (Company, Property Types, etc.)

### Test File Structure Required:
```python
# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate

class Test{DocTypeName}(FrappeTestCase):
    def setUp(self):
        """Set up test data"""
        self.setup_test_data()

    def setup_test_data(self):
        """Create all required master data and dependencies"""
        # CREATE ALL REQUIRED MASTERS FIRST
        self.create_test_masters()
        
        # CREATE DEPENDENCIES IN CORRECT ORDER
        # Example: Company -> Property Registry -> Committee Member
        
    def create_test_masters(self):
        """Create all required master DocTypes"""
        # Auto-detect and create based on Link field dependencies
        
    def test_{doctype_name}_creation(self):
        """Test basic {doctype_name} creation"""
        {doctype_var} = frappe.get_doc({
            "doctype": "{DocType Name}",
            # INCLUDE ALL REQUIRED FIELDS FROM JSON
            # USE EXACT FIELD NAMES FROM JSON
        })
        {doctype_var}.insert()
        self.assertTrue({doctype_var}.name)
        
    # ADDITIONAL TEST METHODS FOR VALIDATIONS
    # EDGE CASES AND BUSINESS LOGIC
```

### Critical Requirements:
- **EXACT FIELD NAMES**: Use only field names that exist in the DocType JSON
- **ALL REQUIRED FIELDS**: Include every field with `"reqd": 1`
- **MASTER DATA**: Create complete dependency chain
- **NO ASSUMPTIONS**: Don't guess field names or structures
- **PROPER CLEANUP**: Use appropriate tearDown methods

### Example Input/Output:
**Input:** `committee_member.json`
**Output:** Complete `test_committee_member.py` with all required fields properly populated

### Validation Checklist:
- [ ] All `"reqd": 1` fields included
- [ ] All Link fields have target DocType creation
- [ ] Field names match JSON exactly
- [ ] Master data created in correct order
- [ ] Test methods cover main functionality
- [ ] Validation tests for business rules
- [ ] Proper error handling tests

Use this template for generating corrected tests for all Committee Management DocTypes.