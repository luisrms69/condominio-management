// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

frappe.ui.form.on("Committee Poll", {
	refresh: function (frm) {
		if (frm.is_new()) return;

		const open = frm.doc.status === "Abierta";

		if (open) {
			frm.add_custom_button(__("Cerrar Encuesta"), function () {
				frappe.confirm(
					__("¿Cerrar esta encuesta? No se podrán registrar más respuestas."),
					function () {
						frm.set_value("status", "Cerrada");
						frm.set_value("closed_date", frappe.datetime.now_datetime());
						frm.set_value("closed_by", frm.doc.created_by || "");
						frm.save();
					}
				);
			}).addClass("btn-danger");
		}

		render_results_chart(frm);
	},
});

function render_results_chart(frm) {
	const wrapper = frm.fields_dict.poll_description?.$wrapper?.closest(".form-column");
	if (!wrapper) return;

	const options = frm.doc.poll_options || [];
	const total = frm.doc.total_responses || 0;
	if (!options.length || !total) return;

	// Remove previous chart if any
	frm.$wrapper.find(".poll-results-chart").remove();

	let bars = options
		.slice()
		.sort((a, b) => (b.response_count || 0) - (a.response_count || 0))
		.map(function (opt) {
			const pct = Math.round(((opt.response_count || 0) / total) * 100);
			return `
			<div style="margin-bottom:10px;">
				<div style="display:flex;justify-content:space-between;margin-bottom:3px;">
					<span style="font-weight:500;">${frappe.utils.escape_html(opt.option_text)}</span>
					<span style="color:#666;">${opt.response_count || 0} (${pct}%)</span>
				</div>
				<div style="background:#f0f0f0;border-radius:4px;height:20px;overflow:hidden;">
					<div style="background:var(--primary);height:100%;width:${pct}%;transition:width 0.4s;"></div>
				</div>
			</div>`;
		})
		.join("");

	const chart = $(`
		<div class="poll-results-chart" style="margin:16px 0;padding:16px;background:var(--subtle-fg);border-radius:6px;">
			<div style="font-weight:600;margin-bottom:12px;">${__("Resultados")} — ${total} ${__(
		"respuestas"
	)}</div>
			${bars}
		</div>
	`);

	frm.fields_dict.results_section?.$wrapper
		? frm.fields_dict.results_section.$wrapper.before(chart)
		: frm.$wrapper.find(".form-layout").append(chart);
}
