// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

frappe.ui.form.on("Committee Member", {
	refresh: function (frm) {
		// Solo usuarios con rol Condómino
		frm.set_query("user", function () {
			return {
				query: "condominium_management.committee_management.doctype.committee_member.committee_member.get_condomino_users",
			};
		});

		// Propiedad filtrada por condominio
		frm.set_query("property_registry", function () {
			return { filters: { company: frm.doc.company, is_active: 1 } };
		});

		// Cargo filtrado por condominio
		frm.set_query("committee_position", function () {
			return { filters: { company: frm.doc.company, is_active: 1 } };
		});
	},

	company: function (frm) {
		frm.set_value("property_registry", "");
		frm.set_value("committee_position", "");
		frm.refresh_field("property_registry");
		frm.refresh_field("committee_position");
	},
});
