# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class PropertyUsageType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.TextEditor | None
		is_active: DF.Check
		type_name: DF.Data
		usage_category: DF.Select
	# end: auto-generated types

	pass
