# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Default Property Relationship Types — created on migrate if they don't exist.

Rule: NEVER overwrite existing records. Each installation manages its own defaults.
"""

import frappe

_DEFAULT_TYPES = [
	{
		"relationship_name": "Propietario",
		"default_can_vote": 1,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 1,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Copropietario",
		"default_can_vote": 1,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 1,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Residente",
		"default_can_vote": 0,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 0,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Arrendatario",
		"default_can_vote": 0,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 0,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Familiar",
		"default_can_vote": 0,
		"default_can_respond_polls": 0,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 0,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Apoderado",
		"default_can_vote": 1,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 1,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Administrador",
		"default_can_vote": 1,
		"default_can_respond_polls": 1,
		"default_can_rsvp_events": 1,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 1,
		"default_can_view_statement": 1,
		"default_can_receive_portal_communications": 1,
	},
	{
		"relationship_name": "Staff",
		"default_can_vote": 0,
		"default_can_respond_polls": 0,
		"default_can_rsvp_events": 0,
		"default_can_create_tickets": 1,
		"default_can_reserve_amenities": 0,
		"default_can_view_statement": 0,
		"default_can_receive_portal_communications": 0,
	},
]


def setup_property_relationship_types():
	"""Create default relationship types if they do not exist. Never overwrites."""
	created = []
	for rt in _DEFAULT_TYPES:
		if frappe.db.exists("Property Relationship Type", {"relationship_name": rt["relationship_name"]}):
			continue
		frappe.get_doc(
			{
				"doctype": "Property Relationship Type",
				"is_active": 1,
				**rt,
			}
		).insert(ignore_permissions=True)
		created.append(rt["relationship_name"])

	if created:
		frappe.db.commit()

	return created
