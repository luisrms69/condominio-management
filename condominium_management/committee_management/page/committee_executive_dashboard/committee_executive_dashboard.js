// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

frappe.pages["committee-executive-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Panel Ejecutivo del Comité"),
		single_column: true,
	});

	// Initialize dashboard
	new CommitteeExecutiveDashboard(page);
};

class CommitteeExecutiveDashboard {
	constructor(page) {
		this.page = page;
		this.dashboard_data = {};
		this.init();
	}

	init() {
		this.setup_page();
		this.load_dashboard_data();
		this.setup_refresh_interval();
	}

	setup_page() {
		// Add custom CSS
		this.add_custom_styles();

		// Set page content
		this.page.main.html(frappe.render_template("committee_executive_dashboard"));

		// Setup event handlers
		this.setup_event_handlers();

		// Make dashboard globally accessible for refresh
		window.dashboard = this;
	}

	add_custom_styles() {
		const style = `
            <style>
                .committee-dashboard {
                    padding: 15px;
                }

                .dashboard-header {
                    margin-bottom: 25px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #eee;
                }

                .dashboard-metrics {
                    margin-bottom: 25px;
                }

                .metric-card {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #007bff;
                    display: flex;
                    align-items: center;
                    transition: transform 0.2s ease;
                }

                .metric-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }

                .metric-card-primary { border-left-color: #007bff; }
                .metric-card-success { border-left-color: #28a745; }
                .metric-card-warning { border-left-color: #ffc107; }
                .metric-card-info { border-left-color: #17a2b8; }
                .metric-card-purple { border-left-color: #6f42c1; }
                .metric-card-orange { border-left-color: #fd7e14; }

                .metric-icon {
                    font-size: 24px;
                    margin-right: 15px;
                    opacity: 0.7;
                }

                .metric-number {
                    font-size: 28px;
                    font-weight: bold;
                    line-height: 1;
                    margin-bottom: 5px;
                }

                .metric-label {
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .dashboard-section {
                    background: white;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .section-header {
                    padding: 15px 20px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .section-header h4 {
                    margin: 0;
                    color: #333;
                }

                .section-content {
                    padding: 20px;
                }

                .loading-indicator {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                }

                .meeting-item, .agreement-item, .poll-item, .event-item {
                    padding: 12px;
                    border-bottom: 1px solid #f0f0f0;
                    transition: background-color 0.2s ease;
                }

                .meeting-item:hover, .agreement-item:hover, .poll-item:hover, .event-item:hover {
                    background-color: #f8f9fa;
                }

                .meeting-item:last-child, .agreement-item:last-child, .poll-item:last-child, .event-item:last-child {
                    border-bottom: none;
                }

                .item-title {
                    font-weight: 500;
                    margin-bottom: 5px;
                }

                .item-meta {
                    font-size: 12px;
                    color: #666;
                }

                .status-badge {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 500;
                    text-transform: uppercase;
                }

                .status-pending { background: #fff3cd; color: #856404; }
                .status-progress { background: #cce5ff; color: #0066cc; }
                .status-completed { background: #d4edda; color: #155724; }
                .status-overdue { background: #f8d7da; color: #721c24; }

                .quick-action-btn {
                    display: block;
                    width: 100%;
                    margin-bottom: 8px;
                    text-align: left;
                    padding: 10px 15px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    background: white;
                    transition: all 0.2s ease;
                }

                .quick-action-btn:hover {
                    background: #f8f9fa;
                    border-color: #007bff;
                    color: #007bff;
                }

                .quick-action-btn i {
                    margin-right: 8px;
                }

                .performance-metric {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 0;
                    border-bottom: 1px solid #f0f0f0;
                }

                .performance-metric:last-child {
                    border-bottom: none;
                }

                .progress-bar-container {
                    width: 60%;
                    height: 6px;
                    background: #f0f0f0;
                    border-radius: 3px;
                    overflow: hidden;
                }

                .progress-bar {
                    height: 100%;
                    background: #28a745;
                    transition: width 0.3s ease;
                }

                .dashboard-alerts {
                    margin-bottom: 20px;
                }

                .alert-item {
                    padding: 12px 15px;
                    margin-bottom: 10px;
                    border-radius: 6px;
                    border-left: 4px solid;
                }

                .alert-danger {
                    background: #f8d7da;
                    border-left-color: #dc3545;
                    color: #721c24;
                }

                .alert-warning {
                    background: #fff3cd;
                    border-left-color: #ffc107;
                    color: #856404;
                }

                .alert-info {
                    background: #d1ecf1;
                    border-left-color: #17a2b8;
                    color: #0c5460;
                }

                .alert-success {
                    background: #d4edda;
                    border-left-color: #28a745;
                    color: #155724;
                }

                @media (max-width: 768px) {
                    .committee-dashboard {
                        padding: 10px;
                    }

                    .metric-card {
                        margin-bottom: 10px;
                    }

                    .dashboard-section {
                        margin-bottom: 15px;
                    }

                    .section-content {
                        padding: 15px;
                    }
                }
            </style>
        `;

		$("head").append(style);
	}

	setup_event_handlers() {
		// Setup quick action handlers
		$(document).on("click", ".quick-action-btn", (e) => {
			const action = $(e.currentTarget).data("action");
			this.handle_quick_action(action);
		});

		// Setup metric card click handlers
		$(document).on("click", ".metric-card", (e) => {
			const metric = $(e.currentTarget).find(".metric-number").data("metric");
			this.handle_metric_click(metric);
		});

		// Setup alert action handlers
		$(document).on("click", "[data-alert-action]", (e) => {
			const action = $(e.currentTarget).data("alert-action");
			this.handle_alert_action(action);
		});
	}

	load_dashboard_data() {
		frappe.call({
			method: "condominium_management.committee_management.page.committee_executive_dashboard.committee_executive_dashboard.get_committee_dashboard_data",
			callback: (r) => {
				if (r.message) {
					this.dashboard_data = r.message;
					this.render_dashboard();
				}
			},
		});

		// Load member profile separately
		frappe.call({
			method: "condominium_management.committee_management.page.committee_executive_dashboard.committee_executive_dashboard.get_committee_member_profile",
			callback: (r) => {
				if (r.message) {
					this.render_member_profile(r.message);
				}
			},
		});
	}

	render_dashboard() {
		this.render_metrics();
		this.render_alerts();
		this.render_meetings();
		this.render_agreements();
		this.render_polls();
		this.render_events();
		this.render_assembly_insights();
		this.render_performance();
		this.render_quick_actions();
	}

	render_metrics() {
		const metrics = this.dashboard_data.overview_metrics || {};

		Object.keys(metrics).forEach((key) => {
			const element = $(`.metric-number[data-metric="${key}"]`);
			if (element.length) {
				this.animate_number(element, metrics[key]);
			}
		});
	}

	animate_number(element, target_value) {
		const start_value = 0;
		const duration = 1000;
		const increment = target_value / (duration / 16);
		let current_value = start_value;

		const timer = setInterval(() => {
			current_value += increment;
			if (current_value >= target_value) {
				current_value = target_value;
				clearInterval(timer);
			}
			element.text(Math.floor(current_value));
		}, 16);
	}

	render_alerts() {
		const alerts = this.dashboard_data.alerts_notifications || [];
		const container = $("#alert-container");

		if (alerts.length > 0) {
			$("#dashboard-alerts").show();

			const alertsHtml = alerts
				.map(
					(alert) => `
                <div class="alert-item alert-${alert.type}">
                    <strong>${alert.title}</strong><br>
                    ${alert.message}
                    ${
						alert.action
							? `<br><a href="#" data-alert-action="${alert.action}" class="btn btn-xs btn-outline-primary mt-2">Ver Detalles</a>`
							: ""
					}
                </div>
            `
				)
				.join("");

			container.html(alertsHtml);
		} else {
			$("#dashboard-alerts").hide();
		}
	}

	render_meetings() {
		const meetings = this.dashboard_data.recent_meetings || {};

		// Upcoming meetings
		const upcomingHtml =
			(meetings.upcoming || [])
				.map(
					(meeting) => `
            <div class="meeting-item" data-meeting="${meeting.name}">
                <div class="item-title">${meeting.meeting_title}</div>
                <div class="item-meta">
                    <i class="fa fa-calendar"></i> ${frappe.datetime.str_to_user(
						meeting.meeting_date
					)}
                    <span class="status-badge status-pending">${meeting.meeting_format}</span>
                </div>
            </div>
        `
				)
				.join("") ||
			'<div class="text-muted text-center">No hay reuniones programadas</div>';

		$("#upcoming-meetings").html(upcomingHtml);

		// Recent meetings
		const recentHtml =
			(meetings.recent_completed || [])
				.map(
					(meeting) => `
            <div class="meeting-item" data-meeting="${meeting.name}">
                <div class="item-title">${meeting.meeting_title}</div>
                <div class="item-meta">
                    <i class="fa fa-calendar"></i> ${frappe.datetime.str_to_user(
						meeting.meeting_date
					)}
                    <span class="status-badge status-completed">${
						meeting.completion_rate
					}% Completado</span>
                </div>
            </div>
        `
				)
				.join("") ||
			'<div class="text-muted text-center">No hay reuniones recientes</div>';

		$("#recent-meetings").html(recentHtml);
	}

	render_agreements() {
		const agreements = this.dashboard_data.pending_agreements || [];

		if (agreements.length > 0) {
			const tableHtml = `
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Acuerdo</th>
                            <th>Responsable</th>
                            <th>Vencimiento</th>
                            <th>Progreso</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${agreements
							.map(
								(agreement) => `
                            <tr data-agreement="${agreement.name}">
                                <td>${agreement.agreement_title}</td>
                                <td>${agreement.responsible_person || "-"}</td>
                                <td>
                                    ${frappe.datetime.str_to_user(agreement.due_date)}
                                    ${
										agreement.is_overdue
											? '<span class="text-danger"><i class="fa fa-exclamation-triangle"></i></span>'
											: ""
									}
                                </td>
                                <td>
                                    <div class="progress-bar-container">
                                        <div class="progress-bar" style="width: ${
											agreement.completion_percentage || 0
										}%"></div>
                                    </div>
                                    <small>${agreement.completion_percentage || 0}%</small>
                                </td>
                                <td>
                                    <span class="status-badge ${
										agreement.is_overdue ? "status-overdue" : "status-pending"
									}">
                                        ${
											agreement.is_overdue
												? "Vencido"
												: agreement.status || "Pendiente"
										}
                                    </span>
                                </td>
                            </tr>
                        `
							)
							.join("")}
                    </tbody>
                </table>
            `;

			$("#pending-agreements-table").html(tableHtml);
		} else {
			$("#pending-agreements-table").html(
				'<div class="text-muted text-center">No hay acuerdos pendientes</div>'
			);
		}
	}

	render_polls() {
		const polls = this.dashboard_data.active_polls || [];

		const pollsHtml =
			polls
				.map(
					(poll) => `
            <div class="poll-item" data-poll="${poll.name}">
                <div class="item-title">${poll.poll_title}</div>
                <div class="item-meta">
                    <i class="fa fa-clock-o"></i> Termina: ${frappe.datetime.str_to_user(
						poll.poll_end_date
					)}<br>
                    <small>Respuestas: ${poll.total_responses}/${
						poll.total_eligible_voters || "N/A"
					}</small>
                </div>
            </div>
        `
				)
				.join("") || '<div class="text-muted text-center">No hay encuestas activas</div>';

		$("#active-polls").html(pollsHtml);
	}

	render_events() {
		const events = this.dashboard_data.upcoming_events || [];

		const eventsHtml =
			events
				.map(
					(event) => `
            <div class="event-item" data-event="${event.name}">
                <div class="item-title">${event.event_name}</div>
                <div class="item-meta">
                    <i class="fa fa-calendar"></i> ${frappe.datetime.str_to_user(
						event.event_start_date
					)}<br>
                    <span class="status-badge status-pending">${event.event_type}</span>
                    <small>Registros: ${event.registered_attendees_count}/${
						event.capacity_maximum || "Sin límite"
					}</small>
                </div>
            </div>
        `
				)
				.join("") || '<div class="text-muted text-center">No hay eventos próximos</div>';

		$("#upcoming-events").html(eventsHtml);
	}

	render_assembly_insights() {
		const insights = this.dashboard_data.assembly_insights || {};

		const insightsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Próximas Asambleas</h6>
                    ${
						(insights.upcoming_assemblies || [])
							.map(
								(assembly) => `
                        <div class="meeting-item">
                            <div class="item-title">${assembly.assembly_title}</div>
                            <div class="item-meta">
                                <i class="fa fa-calendar"></i> ${frappe.datetime.str_to_user(
									assembly.assembly_date
								)}
                                <span class="status-badge status-pending">${
									assembly.assembly_type
								}</span>
                            </div>
                        </div>
                    `
							)
							.join("") ||
						'<div class="text-muted">No hay asambleas programadas</div>'
					}
                </div>
                <div class="col-md-6">
                    <h6>Estadísticas</h6>
                    <div class="performance-metric">
                        <span>Quórum Promedio</span>
                        <span><strong>${insights.average_quorum_percentage || 0}%</strong></span>
                    </div>
                    <div class="performance-metric">
                        <span>Asambleas Este Año</span>
                        <span><strong>${insights.total_assemblies_ytd || 0}</strong></span>
                    </div>
                </div>
            </div>
        `;

		$("#assembly-insights").html(insightsHtml);
	}

	render_performance() {
		const performance = this.dashboard_data.committee_performance || {};

		const performanceHtml = `
            <div class="performance-metric">
                <span>Puntuación Promedio</span>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${
						performance.average_performance_score || 0
					}%"></div>
                </div>
                <span><strong>${performance.average_performance_score || 0}%</strong></span>
            </div>
            <div class="performance-metric">
                <span>Asistencia Promedio</span>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${
						performance.average_attendance_rate || 0
					}%"></div>
                </div>
                <span><strong>${performance.average_attendance_rate || 0}%</strong></span>
            </div>
            <div class="performance-metric">
                <span>Tasa de Cumplimiento</span>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${
						performance.average_completion_rate || 0
					}%"></div>
                </div>
                <span><strong>${performance.average_completion_rate || 0}%</strong></span>
            </div>
            <div class="mt-3">
                <small class="text-muted">
                    Miembros evaluados: ${performance.total_members_evaluated || 0}
                </small>
            </div>
        `;

		$("#performance-summary").html(performanceHtml);
	}

	render_quick_actions() {
		const actions = this.dashboard_data.quick_actions || [];

		const actionsHtml =
			actions
				.map(
					(action) => `
            <button class="quick-action-btn" data-action="${action.action}">
                <i class="fa fa-${action.icon}"></i> ${action.label}
            </button>
        `
				)
				.join("") ||
			'<div class="text-muted text-center">No hay acciones disponibles</div>';

		$("#quick-actions").html(actionsHtml);
	}

	render_member_profile(profile) {
		if (!profile) {
			$("#member-profile").html(
				'<div class="text-muted text-center">Perfil no disponible</div>'
			);
			return;
		}

		const kpis = profile.current_kpis || {};

		const profileHtml = `
            <div class="member-info">
                <h5>${profile.member_name}</h5>
                <p class="text-muted">${profile.role}</p>
                <small>Miembro desde: ${frappe.datetime.str_to_user(profile.start_date)}</small>
            </div>

            <hr>

            <div class="member-kpis">
                <h6>KPIs del Mes</h6>
                <div class="performance-metric">
                    <span>Puntuación</span>
                    <span><strong>${kpis.performance_score || 0}%</strong></span>
                </div>
                <div class="performance-metric">
                    <span>Asistencia</span>
                    <span><strong>${kpis.attendance_rate || 0}%</strong></span>
                </div>
                <div class="performance-metric">
                    <span>Cumplimiento</span>
                    <span><strong>${kpis.completion_rate || 0}%</strong></span>
                </div>
            </div>

            ${
				profile.can_approve_expenses
					? `
                <hr>
                <div class="member-permissions">
                    <small class="text-success">
                        <i class="fa fa-check"></i>
                        Autorizado para aprobar gastos hasta $${
							profile.expense_approval_limit || 0
						}
                    </small>
                </div>
            `
					: ""
			}
        `;

		$("#member-profile").html(profileHtml);
	}

	handle_quick_action(action) {
		const actions_map = {
			new_assembly: () => frappe.new_doc("Assembly Management"),
			new_schedule: () => frappe.new_doc("Meeting Schedule"),
			view_kpis: () => frappe.set_route("List", "Committee KPI"),
			new_meeting: () => frappe.new_doc("Committee Meeting"),
			new_poll: () => frappe.new_doc("Committee Poll"),
			track_agreements: () => frappe.set_route("List", "Agreement Tracking"),
			new_event: () => frappe.new_doc("Community Event"),
			review_budgets: () => frappe.set_route("query-report", "Budget Analysis"),
			pending_meetings: () =>
				frappe.set_route("List", "Committee Meeting", { meeting_status: "Programada" }),
			update_progress: () =>
				frappe.set_route("List", "Agreement Tracking", {
					status: ["in", ["Pendiente", "En Progreso"]],
				}),
		};

		if (actions_map[action]) {
			actions_map[action]();
		}
	}

	handle_metric_click(metric) {
		const routes_map = {
			active_members: ["List", "Committee Member", { is_active: 1 }],
			scheduled_meetings: ["List", "Committee Meeting", { meeting_status: "Programada" }],
			overdue_agreements: ["List", "Agreement Tracking", { status: "Vencido" }],
			active_polls: ["List", "Committee Poll", { poll_status: "Activa" }],
			planned_events: ["List", "Community Event", { event_status: "Planificado" }],
			pending_agreements: [
				"List",
				"Agreement Tracking",
				{ status: ["in", ["Pendiente", "En Progreso"]] },
			],
		};

		if (routes_map[metric]) {
			frappe.set_route(...routes_map[metric]);
		}
	}

	handle_alert_action(action) {
		// Handle specific alert actions
		const alert_actions = {
			view_overdue_agreements: () =>
				frappe.set_route("List", "Agreement Tracking", { status: "Vencido" }),
			view_upcoming_meetings: () =>
				frappe.set_route("List", "Committee Meeting", { meeting_status: "Programada" }),
			view_ending_polls: () =>
				frappe.set_route("List", "Committee Poll", { poll_status: "Activa" }),
			view_upcoming_events: () =>
				frappe.set_route("List", "Community Event", {
					event_status: ["in", ["Planificado", "En Organización"]],
				}),
		};

		if (alert_actions[action]) {
			alert_actions[action]();
		}
	}

	refresh() {
		frappe.show_alert({ message: __("Actualizando panel..."), indicator: "blue" });
		this.load_dashboard_data();
	}

	setup_refresh_interval() {
		// Auto-refresh every 5 minutes
		setInterval(() => {
			this.load_dashboard_data();
		}, 300000);
	}
}
