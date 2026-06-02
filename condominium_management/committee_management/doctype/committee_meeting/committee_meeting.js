// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

frappe.ui.form.on("Committee Meeting", {
	refresh: function (frm) {
		if (frm.is_new()) return;

		// Agendar en Calendario — siempre disponible
		frm.add_custom_button(__("Agendar en Calendario"), function () {
			frappe.call({
				method: "create_event",
				doc: frm.doc,
				callback: function (r) {
					if (r.message) {
						frappe.show_alert({ message: __("Evento creado"), indicator: "green" });
						frappe.set_route("Form", "Event", r.message);
					}
				},
			});
		});

		// Crear Acuerdo — solo si la reunión no está terminada
		if (frm.doc.status !== "Terminada") {
			frm.add_custom_button(__("Crear Acuerdo"), function () {
				frappe.prompt(
					[
						{
							fieldname: "subject",
							fieldtype: "Data",
							label: __("Acuerdo / Tarea"),
							reqd: 1,
						},
						{
							fieldname: "description",
							fieldtype: "Small Text",
							label: __("Descripción"),
						},
						{
							fieldname: "assigned_to",
							fieldtype: "Link",
							options: "User",
							label: __("Asignado a"),
						},
						{ fieldname: "due_date", fieldtype: "Date", label: __("Fecha Límite") },
					],
					function (values) {
						frappe.call({
							method: "create_task",
							doc: frm.doc,
							args: {
								subject: values.subject,
								description: values.description || "",
								assigned_to: values.assigned_to || "",
								due_date: values.due_date || "",
							},
							callback: function (r) {
								if (r.message) {
									frappe.show_alert({
										message: __("Acuerdo creado: {0}", [r.message]),
										indicator: "green",
									});
								}
							},
						});
					},
					__("Nuevo Acuerdo"),
					__("Crear")
				);
			});
		}
	},
});

// Auto-fill person_name desde committee_member en la tabla de asistentes
frappe.ui.form.on("Meeting Attendee", {
	committee_member: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.committee_member) {
			frappe.db.get_value(
				"Committee Member",
				row.committee_member,
				"full_name",
				function (r) {
					if (r && r.full_name) {
						frappe.model.set_value(cdt, cdn, "person_name", r.full_name);
						frappe.model.set_value(cdt, cdn, "person_type", "Miembro del Comité");
					}
				}
			);
		}
	},
});
