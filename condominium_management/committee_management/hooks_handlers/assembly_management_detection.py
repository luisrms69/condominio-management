# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_submit(doc, method):
	"""Assembly Management on submit hook"""
	if doc.doctype != "Assembly Management":
		return

	# Create voting systems for agenda items that require voting
	create_voting_systems(doc)

	# Create agreement tracking for approved motions
	create_agreement_tracking(doc)

	# Update assembly KPIs
	update_assembly_kpis(doc)


def on_update(doc, method):
	"""Assembly Management on update hook"""
	if doc.doctype != "Assembly Management":
		return

	# Update quorum percentage when quorum records change
	if doc.has_value_changed("quorum_records"):
		doc.calculate_quorum_percentage()

	# Sync quorum records with all active properties
	if not doc.quorum_records:
		load_all_properties_to_quorum(doc)


def create_voting_systems(doc):
	"""Create voting systems for agenda items requiring votes"""
	try:
		for item in doc.agenda_items:
			if item.requires_voting and not item.voting_system:
				voting_doc = frappe.get_doc(
					{
						"doctype": "Voting System",
						"voting_title": f"Votación: {item.topic_title}",
						"voting_type": item.voting_type,
						"assembly_management": doc.name,
						"agenda_item": item.name,
						"voting_start_date": doc.assembly_date,
						"voting_end_date": doc.assembly_date,
						"required_percentage": get_required_percentage(item.voting_type),
						"allows_anonymous": 0,
						"status": "Activa",
					}
				)
				voting_doc.insert()

				# Link back to agenda item
				item.voting_system = voting_doc.name

	except Exception as e:
		frappe.log_error(f"Error creating voting systems: {e!s}")


def create_agreement_tracking(doc):
	"""Create agreement tracking for approved motions"""
	try:
		for item in doc.agenda_items:
			if item.requires_voting and item.voting_result == "Aprobado":
				agreement_doc = frappe.get_doc(
					{
						"doctype": "Agreement Tracking",
						"agreement_title": f"Acuerdo: {item.topic_title}",
						"agreement_type": "Resolución de Asamblea",
						"assembly_management": doc.name,
						"agenda_item": item.name,
						"agreement_date": doc.assembly_date,
						"due_date": frappe.utils.add_days(doc.assembly_date, 30),
						"status": "Pendiente",
						"priority": "Alta" if item.voting_type == "Mayoría Calificada" else "Media",
						"description": item.description or item.topic_title,
					}
				)
				agreement_doc.insert()

	except Exception as e:
		frappe.log_error(f"Error creating agreement tracking: {e!s}")


def load_all_properties_to_quorum(doc):
	"""Load all active properties to quorum registration"""
	try:
		properties = frappe.get_all(
			"Property Registry",
			filters={"status": "Activo"},
			fields=["name", "property_number", "owner_name", "unit_area"],
		)

		for prop in properties:
			doc.append(
				"quorum_records",
				{
					"property_registry": prop.name,
					"owner_name": prop.owner_name,
					"property_number": prop.property_number,
					"unit_area": prop.unit_area,
					"attendance_status": "Pendiente",
					"participation_type": "Directo",
					"proxy_holder": None,
				},
			)

		doc.save()

	except Exception as e:
		frappe.log_error(f"Error loading properties to quorum: {e!s}")


def get_required_percentage(voting_type):
	"""Get required percentage based on voting type"""
	percentages = {"Mayoría Simple": 51, "Mayoría Calificada": 67, "Unanimidad": 100, "Mayoría Absoluta": 51}
	return percentages.get(voting_type, 51)


def update_assembly_kpis(doc):
	"""Update KPI records for assembly organizer"""
	try:
		if doc.assembly_organizer:
			update_member_kpis(doc.assembly_organizer, "assemblies_organized", 1)

		# Update KPIs for committee members who participated
		for quorum in doc.quorum_records:
			if quorum.attendance_status == "Presente":
				# Find committee member for this property
				committee_member = frappe.db.get_value(
					"Committee Member",
					{"property_registry": quorum.property_registry, "is_active": 1},
					"name",
				)
				if committee_member:
					update_member_kpis(committee_member, "assemblies_attended", 1)

	except Exception as e:
		frappe.log_error(f"Error updating assembly KPIs: {e!s}")


def update_member_kpis(committee_member, field, increment):
	"""Update specific KPI field for committee member"""
	try:
		current_month = frappe.utils.nowdate()[5:7]
		current_year = frappe.utils.nowdate()[:4]

		kpi_record = frappe.db.get_value(
			"Committee KPI",
			{
				"committee_member": committee_member,
				"kpi_period": "Mensual",
				"kpi_year": current_year,
				"kpi_month": current_month,
			},
			"name",
		)

		if kpi_record:
			kpi_doc = frappe.get_doc("Committee KPI", kpi_record)
			current_value = getattr(kpi_doc, field) or 0
			setattr(kpi_doc, field, current_value + increment)
			kpi_doc.save()

	except Exception as e:
		frappe.log_error(f"Error updating member KPIs: {e!s}")
