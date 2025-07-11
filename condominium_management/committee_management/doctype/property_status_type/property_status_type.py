# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class PropertyStatusType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.TextEditor | None
		is_active: DF.Check
		status_name: DF.Data
	# end: auto-generated types

	pass
