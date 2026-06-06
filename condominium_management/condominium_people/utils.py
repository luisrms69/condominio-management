# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Condominium People — helpers for User ↔ Property Registry authorization.

Rule: modules must import and call these helpers instead of reimplementing
authorization logic.

Rule: System Manager always returns True (administrative bypass).
"""

import frappe
from frappe.utils import getdate, nowdate

_PERMISSION_FIELDS = (
	"can_vote",
	"can_respond_polls",
	"can_rsvp_events",
	"can_create_tickets",
	"can_reserve_amenities",
	"can_view_statement",
	"can_receive_portal_communications",
)


def _is_system_manager(user):
	return "System Manager" in frappe.get_roles(user)


def _active_pua_filters(user, property_registry):
	today = nowdate()
	return {
		"user": user,
		"property_registry": property_registry,
		"is_active": 1,
		"valid_from": ["in", [None, ""], ["<=", today]],
	}


def get_active_authorization(user, property_registry):
	"""Return the active, valid PUA for user + property, or None."""
	today = nowdate()
	results = frappe.get_all(
		"Property User Authorization",
		filters={
			"user": user,
			"property_registry": property_registry,
			"is_active": 1,
		},
		fields=["name", *_PERMISSION_FIELDS, "valid_from", "valid_until", "relationship_type", "company"],
		limit=1,
	)
	if not results:
		return None
	pua = results[0]
	if pua.valid_from and getdate(pua.valid_from) > getdate(today):
		return None
	if pua.valid_until and getdate(pua.valid_until) < getdate(today):
		return None
	return pua


def get_effective_permissions(user, property_registry):
	"""Return dict of effective permissions, or None if no active authorization."""
	pua = get_active_authorization(user, property_registry)
	if not pua:
		return None
	return {field: bool(pua.get(field)) for field in _PERMISSION_FIELDS}


def can_user_act_for_property(user, property_registry, action):
	"""
	Single entry point for condominial permission checks.

	action: one of can_vote, can_respond_polls, can_rsvp_events,
	        can_create_tickets, can_reserve_amenities,
	        can_view_statement, can_receive_portal_communications

	Returns True for System Manager (administrative bypass).
	"""
	if action not in _PERMISSION_FIELDS:
		frappe.throw(f"Permiso desconocido: {action}")
	if _is_system_manager(user):
		return True
	pua = get_active_authorization(user, property_registry)
	if not pua:
		return False
	return bool(pua.get(action))


def get_authorized_properties(user, permission=None, company=None):
	"""
	List of property_registry where user has active, valid authorization.

	permission: optional can_* field to filter by.
	company: optional company filter.
	"""
	today = nowdate()
	filters = {"user": user, "is_active": 1}
	if permission:
		if permission not in _PERMISSION_FIELDS:
			frappe.throw(f"Permiso desconocido: {permission}")
		filters[permission] = 1
	if company:
		filters["company"] = company

	results = frappe.get_all(
		"Property User Authorization",
		filters=filters,
		fields=["property_registry", "valid_from", "valid_until"],
	)

	today_date = getdate(today)
	return [
		r.property_registry
		for r in results
		if (not r.valid_from or getdate(r.valid_from) <= today_date)
		and (not r.valid_until or getdate(r.valid_until) >= today_date)
	]


def get_authorized_users_for_property(property_registry, permission=None):
	"""
	List of users with active authorization over a property.
	permission: optional filter by specific can_* field.
	"""
	today = nowdate()
	filters = {"property_registry": property_registry, "is_active": 1}
	if permission:
		if permission not in _PERMISSION_FIELDS:
			frappe.throw(f"Permiso desconocido: {permission}")
		filters[permission] = 1

	results = frappe.get_all(
		"Property User Authorization",
		filters=filters,
		fields=["user", "valid_from", "valid_until"],
	)
	today_date = getdate(today)
	return [
		r.user
		for r in results
		if (not r.valid_from or getdate(r.valid_from) <= today_date)
		and (not r.valid_until or getdate(r.valid_until) >= today_date)
	]


# ── Convenience aliases ────────────────────────────────────────────────────────


def can_user_vote_for_property(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_vote")


def can_user_respond_poll_for_property(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_respond_polls")


def can_user_rsvp_for_property(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_rsvp_events")


def can_user_create_ticket_for_property(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_create_tickets")


def can_user_reserve_amenity_for_property(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_reserve_amenities")


def can_user_view_statement(user, property_registry):
	return can_user_act_for_property(user, property_registry, "can_view_statement")
