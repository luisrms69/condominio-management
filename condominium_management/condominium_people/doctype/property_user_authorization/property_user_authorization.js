// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property User Authorization", {
	property_registry: function (frm) {
		if (frm.doc.property_registry) {
			frappe.db.get_value("Property Registry", frm.doc.property_registry, "company", (r) => {
				if (r && r.company) frm.set_value("company", r.company);
			});
		}
	},

	relationship_type: function (frm) {
		if (!frm.doc.relationship_type) return;
		frappe.db.get_doc("Property Relationship Type", frm.doc.relationship_type).then((rt) => {
			const mapping = {
				can_vote: rt.default_can_vote,
				can_respond_polls: rt.default_can_respond_polls,
				can_rsvp_events: rt.default_can_rsvp_events,
				can_create_tickets: rt.default_can_create_tickets,
				can_reserve_amenities: rt.default_can_reserve_amenities,
				can_view_statement: rt.default_can_view_statement,
				can_receive_portal_communications: rt.default_can_receive_portal_communications,
			};
			Object.entries(mapping).forEach(([field, val]) => frm.set_value(field, val));
		});
	},
});
