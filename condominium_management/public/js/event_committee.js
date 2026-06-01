// Copyright (c) 2025, Buzola and contributors
// Committee Meeting + Assembly functionality on native Frappe Event

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

	// ── Assembly: snapshot quorum on close ────────────────────────────────────
	asm_status: function (frm) {
		if (frm.doc.condominium_meeting_type !== "Assembly") return;
		if (frm.doc.asm_status === "Cerrada") {
			snapshot_quorum(frm);
		}
	},

	refresh: function (frm) {
		if (frm.is_new()) return;

		// ── Assembly UI ─────────────────────────────────────────────────────────
		if (frm.doc.condominium_meeting_type === "Assembly") {
			const published = !!frm.doc.asm_convocation_published;
			const closed = frm.doc.asm_status === "Cerrada";

			// asm_type: frozen after first save
			frm.set_df_property("asm_type", "read_only", 1);

			// Quorum result fields: always read-only
			frm.set_df_property("asm_quorum_current", "read_only", 1);
			frm.set_df_property("asm_quorum_reached", "read_only", 1);

			if (published) {
				// Freeze all convocation fields
				const FROZEN_ON_PUBLISH = [
					"asm_convocation_date",
					"asm_convener",
					"asm_first_call",
					"asm_second_call",
					"asm_quorum_first",
					"asm_quorum_second",
					"asm_notif_email",
					"asm_notif_fisico",
					"asm_notif_portal",
					"asm_notif_publicacion",
					"asm_notif_otro",
					"asm_convocation_document",
				];
				FROZEN_ON_PUBLISH.forEach(function (f) {
					frm.set_df_property(f, "read_only", 1);
				});

				// Freeze announcement columns in agenda table
				const FROZEN_AGENDA = [
					"item_number",
					"agenda_topic",
					"topic_description",
					"presenter",
					"requires_vote",
					"vote_type",
					"required_percentage",
					"supporting_documents",
				];
				FROZEN_AGENDA.forEach(function (f) {
					frm.fields_dict.asm_formal_agenda?.grid?.update_docfield_property(
						f,
						"read_only",
						1
					);
				});

				const pub_on = frm.doc.asm_convocation_published_on
					? frappe.datetime.str_to_user(frm.doc.asm_convocation_published_on)
					: "";
				frm.set_intro(
					__("Convocatoria publicada{0}", [pub_on ? " el " + pub_on : ""]),
					"green"
				);
			}

			if (closed) {
				frm.set_df_property("asm_quorum_registration", "read_only", 1);
			}

			// Botón Publicar Convocatoria — solo si no publicada y no cerrada
			if (!published && !closed) {
				frm.add_custom_button(__("Publicar Convocatoria"), function () {
					publish_convocatoria(frm);
				}).addClass("btn-primary");
			}

			// Botón Crear Acuerdo — disponible solo después de publicada y antes de cerrar
			if (published && !closed) {
				frm.add_custom_button(__("Crear Acuerdo"), function () {
					create_agreement(frm, "asm_agreements_widget");
				});
			}

			load_agreements_widget(frm, "asm_agreements_widget");
			return;
		}

		// ── Committee Meeting UI ────────────────────────────────────────────────
		if (
			frm.doc.event_category !== "Meeting" ||
			frm.doc.condominium_meeting_type !== "Committee Meeting"
		)
			return;

		const ended =
			frm.doc.status === "Closed" ||
			(frm.doc.ends_on && frappe.datetime.now_datetime() > frm.doc.ends_on);

		if (!ended) {
			frm.add_custom_button(__("Crear Acuerdo"), function () {
				create_agreement(frm, "committee_agreements_widget");
			});
		}

		load_agreements_widget(frm, "committee_agreements_widget");
	},
});

// ── Quorum Record: proxy obligatorio si Representado ──────────────────────────
frappe.ui.form.on("Quorum Record", {
	attendance_status: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const is_proxy = row.attendance_status === "Representado";

		const proxy_doc_field = frappe.meta.get_docfield(
			"Quorum Record",
			"proxy_document",
			frm.doc.name
		);
		const proxy_holder_field = frappe.meta.get_docfield(
			"Quorum Record",
			"proxy_holder",
			frm.doc.name
		);

		if (proxy_doc_field) proxy_doc_field.reqd = is_proxy ? 1 : 0;
		if (proxy_holder_field) proxy_holder_field.reqd = is_proxy ? 1 : 0;

		frm.refresh_field("asm_quorum_registration");

		if (is_proxy && !row.proxy_document) {
			frappe.show_alert({
				message: __("Asistencia como Representado requiere documento de representación."),
				indicator: "orange",
			});
		}
	},
});

// ── Quorum snapshot on assembly close ────────────────────────────────────────
function snapshot_quorum(frm) {
	const attended = ["Presente", "Virtual", "Representado"];
	let total = 0;

	(frm.doc.asm_quorum_registration || []).forEach(function (row) {
		if (attended.includes(row.attendance_status)) {
			total += row.ownership_percentage || 0;
		}
	});

	const required =
		frm.doc.asm_opened_in_call === "Primera Convocatoria"
			? frm.doc.asm_quorum_first || 0
			: frm.doc.asm_quorum_second || 0;

	const reached = total >= required;

	frm.set_value("asm_quorum_current", Math.round(total * 100) / 100);
	frm.set_value("asm_quorum_reached", reached ? 1 : 0);

	frappe.show_alert({
		message: __("Quórum registrado: {0}% — {1}", [
			Math.round(total * 100) / 100,
			reached ? __("Alcanzado ✓") : __("No alcanzado ✗"),
		]),
		indicator: reached ? "green" : "red",
	});
}

// ── Publicar Convocatoria ─────────────────────────────────────────────────────
function publish_convocatoria(frm) {
	// Validate minimum required fields before publishing
	const required_asm = [
		{ field: "asm_type", label: __("Tipo de Asamblea") },
		{ field: "asm_convocation_date", label: __("Fecha de Convocatoria") },
		{ field: "asm_convener", label: __("Convocante") },
		{ field: "asm_first_call", label: __("Hora Primera Convocatoria") },
		{ field: "asm_second_call", label: __("Hora Segunda Convocatoria") },
		{ field: "asm_quorum_first", label: __("Quórum Mínimo Primera Convocatoria") },
		{ field: "asm_quorum_second", label: __("Quórum Mínimo Segunda Convocatoria") },
	];
	const missing = required_asm.filter((r) => !frm.doc[r.field]).map((r) => r.label);
	if (missing.length) {
		frappe.msgprint({
			title: __("Campos requeridos"),
			message: __("Completa antes de publicar:<br><ul><li>{0}</li></ul>", [
				missing.join("</li><li>"),
			]),
			indicator: "red",
		});
		return;
	}

	if (!frm.doc.asm_formal_agenda || !frm.doc.asm_formal_agenda.length) {
		frappe.msgprint({
			title: __("Agenda requerida"),
			message: __("Agrega al menos un punto de agenda antes de publicar."),
			indicator: "red",
		});
		return;
	}

	// Check native Event fields used in the print format
	const required_event = [
		{ field: "subject", label: __("Título del evento") },
		{ field: "starts_on", label: __("Fecha y hora de la asamblea") },
	];
	const missing_event = required_event.filter((r) => !frm.doc[r.field]).map((r) => r.label);
	if (missing_event.length) {
		frappe.msgprint({
			title: __("Campos del evento requeridos"),
			message: __("Completa antes de publicar:<br><ul><li>{0}</li></ul>", [
				missing_event.join("</li><li>"),
			]),
			indicator: "orange",
		});
		return;
	}

	frappe.confirm(
		__(
			"¿Confirmas que la convocatoria fue enviada a los condóminos?<br><br>" +
				"<strong>Esta acción es irreversible.</strong><br>" +
				"Los campos de convocatoria y la agenda quedarán congelados."
		),
		function () {
			frm.set_value("asm_convocation_published", 1);
			frm.set_value("asm_convocation_published_on", frappe.datetime.now_datetime());
			frm.set_value("asm_status", "Convocada");
			frm.save();
		}
	);
}

// ── Crear Acuerdo (shared by Committee Meeting and Assembly) ──────────────────
function create_agreement(frm, widget_fieldname) {
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
						load_agreements_widget(frm, widget_fieldname);
					}
				},
			});
		},
		__("Nuevo Acuerdo"),
		__("Crear")
	);
}

// ── Agreements widget ─────────────────────────────────────────────────────────
function load_agreements_widget(frm, widget_fieldname) {
	const wrapper = frm.fields_dict[widget_fieldname]?.$wrapper;
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
