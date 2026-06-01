// Copyright (c) 2025, Buzola and contributors
// Committee Meeting functionality on native Frappe Event

frappe.ui.form.on("Event", {
	event_category: function (frm) {
		// Limpiar tipo de reunión al cambiar categoría
		if (frm.doc.event_category !== "Meeting") {
			frm.set_value("condominium_meeting_type", "");
		}
	},

	condominium_meeting_type: function (frm) {
		if (frm.doc.condominium_meeting_type !== "Committee Meeting") {
			frm.set_value("committee_meeting_type", "");
		}
	},

	refresh: function (frm) {
		if (frm.is_new()) return;
		if (
			frm.doc.event_category !== "Meeting" ||
			frm.doc.condominium_meeting_type !== "Committee Meeting"
		)
			return;

		// Crear Acuerdo — solo disponible antes de que el evento termine
		const ended =
			frm.doc.status === "Closed" ||
			(frm.doc.ends_on && frappe.datetime.now_datetime() > frm.doc.ends_on);

		if (!ended) {
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
							method: "frappe.client.insert",
							args: {
								doc: {
									doctype: "ToDo",
									description:
										"[" +
										frm.doc.subject +
										"]\n" +
										values.subject +
										(values.description ? "\n\n" + values.description : ""),
									owner: values.assigned_to || frappe.session.user,
									reference_type: "Event",
									reference_name: frm.doc.name,
									date: values.due_date || null,
									status: "Open",
								},
							},
							callback: function (r) {
								if (r.message) {
									frappe.show_alert({
										message: __("Acuerdo creado: {0}", [r.message.name]),
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
