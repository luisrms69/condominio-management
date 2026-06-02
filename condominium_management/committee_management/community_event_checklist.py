# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Default Event Checklist Items — created on migrate if they don't exist.

Rule: NEVER overwrite existing records. Only insert new ones.
Each installation manages its own is_enabled state.
"""

import frappe

_DEFAULT_ITEMS = [
	{
		"item_name": "Venue confirmado",
		"applies_to_all": 1,
		"applies_to_types": "",
		"requires_outdoor": 0,
		"sort_order": 1,
	},
	{
		"item_name": "Logística y catering confirmado",
		"applies_to_all": 0,
		"applies_to_types": "Social,Infantil,Cultural",
		"requires_outdoor": 0,
		"sort_order": 2,
	},
	{
		"item_name": "Comunicaciones enviadas a condóminos",
		"applies_to_all": 1,
		"applies_to_types": "",
		"requires_outdoor": 0,
		"sort_order": 3,
	},
	{
		"item_name": "Materiales y decoración listos",
		"applies_to_all": 0,
		"applies_to_types": "Social,Infantil,Cultural",
		"requires_outdoor": 0,
		"sort_order": 4,
	},
	{
		"item_name": "Equipo deportivo y árbitros confirmados",
		"applies_to_all": 0,
		"applies_to_types": "Deportivo",
		"requires_outdoor": 0,
		"sort_order": 5,
	},
	{
		"item_name": "Verificación del clima",
		"applies_to_all": 1,
		"applies_to_types": "",
		"requires_outdoor": 1,
		"sort_order": 6,
	},
]


def setup_event_checklist_items():
	"""Create default checklist items if they do not exist. Never overwrites."""
	created = []
	for item in _DEFAULT_ITEMS:
		if frappe.db.exists("Event Checklist Item", {"item_name": item["item_name"]}):
			continue
		frappe.get_doc(
			{
				"doctype": "Event Checklist Item",
				"is_enabled": 1,
				**item,
			}
		).insert(ignore_permissions=True)
		created.append(item["item_name"])

	if created:
		frappe.db.commit()

	return created
