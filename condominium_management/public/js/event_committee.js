// Copyright (c) 2025, Buzola and contributors
// Committee Meeting functionality on native Frappe Event

frappe.ui.form.on("Event", {
	event_category: function (frm) {
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
									allocated_to: values.assigned_to || frappe.session.user,
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
									load_agreements_widget(frm);
								}
							},
						});
					},
					__("Nuevo Acuerdo"),
					__("Crear")
				);
			});
		}

		load_agreements_widget(frm);
	},
});

function load_agreements_widget(frm) {
	const wrapper = frm.fields_dict.committee_agreements_widget?.$wrapper;
	if (!wrapper) return;

	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "ToDo",
			filters: { reference_type: "Event", reference_name: frm.doc.name },
			fields: ["name", "description", "status", "date", "allocated_to"],
			order_by: "creation desc",
			limit: 50,
		},
		callback: function (r) {
			const todos = r.message || [];
			let html = "";

			if (!todos.length) {
				html =
					'<p class="text-muted" style="padding:8px 0;">' +
					__("Sin acuerdos registrados.") +
					"</p>";
			} else {
				const colors = { Open: "orange", Closed: "green", Cancelled: "red" };
				html =
					'<table class="table table-bordered table-sm" style="margin-bottom:0;"><thead><tr>' +
					"<th>" +
					__("Acuerdo") +
					"</th>" +
					"<th style='width:130px'>" +
					__("Asignado a") +
					"</th>" +
					"<th style='width:100px'>" +
					__("Fecha límite") +
					"</th>" +
					"<th style='width:90px'>" +
					__("Estado") +
					"</th>" +
					"</tr></thead><tbody>";

				todos.forEach(function (t) {
					const desc = (t.description || "").split("\n")[1] || t.description || "";
					const color = colors[t.status] || "gray";
					const date_str = t.date ? frappe.datetime.str_to_user(t.date) : "—";
					html +=
						"<tr>" +
						'<td><a href="/app/todo/' +
						t.name +
						'" target="_blank">' +
						frappe.utils.escape_html(desc.substring(0, 80)) +
						(desc.length > 80 ? "…" : "") +
						"</a></td>" +
						"<td>" +
						frappe.utils.escape_html(t.allocated_to || "—") +
						"</td>" +
						"<td>" +
						date_str +
						"</td>" +
						'<td><span class="indicator-pill ' +
						color +
						'">' +
						__(t.status) +
						"</span></td>" +
						"</tr>";
				});

				html += "</tbody></table>";
			}

			wrapper.html(html);
		},
	});
}
