// Copyright (c) 2025, Buzola and contributors
// For license information, please see license.txt

/**
 * Dashboard Ejecutivo - Centro de Control Multi-Módulo
 * ===================================================
 *
 * SPA para dashboard ejecutivo con widgets configurables,
 * KPIs en tiempo real y vista consolidada de todos los módulos.
 */

frappe.pages["dashboard-ejecutivo"].on_page_load = function (wrapper) {
	new DashboardEjecutivo(wrapper);
};

class DashboardEjecutivo {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: "Dashboard Ejecutivo - Centro de Control",
			single_column: false,
		});

		this.current_dashboard = null;
		this.widgets = [];
		this.refresh_interval = 30000; // 30 segundos por defecto
		this.refresh_timer = null;
		this.grid = null;

		this.init();
	}

	init() {
		this.setup_page();
		this.load_dashboard_config();
		this.setup_auto_refresh();
	}

	setup_page() {
		// Configurar toolbar
		this.page.set_primary_action("Actualizar", () => this.refresh_dashboard(), "refresh");

		this.page.add_menu_item("Configurar Dashboard", () => this.open_dashboard_config());
		this.page.add_menu_item("Crear Snapshot", () => this.create_snapshot());
		this.page.add_menu_item("Ver Histórico", () => this.view_snapshots());

		// Selector de dashboard
		this.dashboard_selector = this.page.add_field({
			fieldtype: "Select",
			label: "Dashboard",
			fieldname: "dashboard_selector",
			options: [],
			change: () => this.on_dashboard_change(),
		});

		// Selector de empresa
		this.company_selector = this.page.add_field({
			fieldtype: "Link",
			label: "Empresa",
			fieldname: "company_selector",
			options: "Company",
			change: () => this.refresh_dashboard(),
		});

		// Crear contenedor principal
		this.setup_layout();
	}

	setup_layout() {
		this.page.main.html(`
			<div class="dashboard-container">
				<!-- Header con métricas principales -->
				<div class="dashboard-header">
					<div class="row">
						<div class="col-md-3">
							<div class="metric-card" id="total-modules">
								<div class="metric-icon">
									<i class="fa fa-cubes"></i>
								</div>
								<div class="metric-content">
									<div class="metric-value">6</div>
									<div class="metric-label">Módulos Activos</div>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="metric-card" id="system-health">
								<div class="metric-icon">
									<i class="fa fa-heartbeat"></i>
								</div>
								<div class="metric-content">
									<div class="metric-value">98.5%</div>
									<div class="metric-label">Salud del Sistema</div>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="metric-card" id="active-alerts">
								<div class="metric-icon">
									<i class="fa fa-exclamation-triangle"></i>
								</div>
								<div class="metric-content">
									<div class="metric-value">0</div>
									<div class="metric-label">Alertas Activas</div>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="metric-card" id="last-update">
								<div class="metric-icon">
									<i class="fa fa-clock-o"></i>
								</div>
								<div class="metric-content">
									<div class="metric-value">--:--</div>
									<div class="metric-label">Última Actualización</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Grid de widgets configurables -->
				<div class="dashboard-grid" id="dashboard-grid">
					<!-- Los widgets se cargarán dinámicamente aquí -->
				</div>

				<!-- Loading overlay -->
				<div class="dashboard-loading" id="dashboard-loading" style="display: none;">
					<div class="loading-content">
						<i class="fa fa-spinner fa-spin fa-3x"></i>
						<p>Cargando datos del dashboard...</p>
					</div>
				</div>
			</div>
		`);

		this.apply_dashboard_styles();
	}

	apply_dashboard_styles() {
		$("<style>")
			.prop("type", "text/css")
			.html(
				`
				.dashboard-container {
					padding: 15px;
					background: #f8f9fa;
					min-height: calc(100vh - 140px);
				}

				.dashboard-header {
					margin-bottom: 20px;
				}

				.metric-card {
					background: white;
					border-radius: 8px;
					padding: 20px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
					display: flex;
					align-items: center;
					transition: transform 0.2s ease;
				}

				.metric-card:hover {
					transform: translateY(-2px);
					box-shadow: 0 4px 8px rgba(0,0,0,0.15);
				}

				.metric-icon {
					font-size: 2.5em;
					color: #007bff;
					margin-right: 15px;
				}

				.metric-value {
					font-size: 2em;
					font-weight: bold;
					color: #333;
					line-height: 1;
				}

				.metric-label {
					font-size: 0.9em;
					color: #666;
					margin-top: 5px;
				}

				.dashboard-grid {
					min-height: 400px;
					background: white;
					border-radius: 8px;
					padding: 20px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.1);
				}

				.widget-container {
					background: #fff;
					border: 1px solid #e3e6f0;
					border-radius: 8px;
					padding: 15px;
					margin: 10px;
					box-shadow: 0 2px 4px rgba(0,0,0,0.05);
					transition: all 0.3s ease;
				}

				.widget-container:hover {
					box-shadow: 0 4px 8px rgba(0,0,0,0.1);
					transform: translateY(-1px);
				}

				.widget-header {
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 15px;
					padding-bottom: 10px;
					border-bottom: 1px solid #eee;
				}

				.widget-title {
					font-size: 1.1em;
					font-weight: 600;
					color: #333;
				}

				.widget-refresh {
					cursor: pointer;
					color: #007bff;
					font-size: 0.9em;
				}

				.widget-content {
					min-height: 100px;
				}

				.kpi-card {
					text-align: center;
					padding: 20px;
				}

				.kpi-value {
					font-size: 2.5em;
					font-weight: bold;
					color: #007bff;
				}

				.kpi-trend {
					margin-top: 10px;
					font-size: 0.9em;
				}

				.kpi-trend.up {
					color: #28a745;
				}

				.kpi-trend.down {
					color: #dc3545;
				}

				.kpi-trend.neutral {
					color: #6c757d;
				}

				.dashboard-loading {
					position: absolute;
					top: 0;
					left: 0;
					right: 0;
					bottom: 0;
					background: rgba(255,255,255,0.8);
					display: flex;
					align-items: center;
					justify-content: center;
					z-index: 1000;
				}

				.loading-content {
					text-align: center;
					color: #666;
				}

				.loading-content i {
					margin-bottom: 15px;
				}

				.alert-item {
					background: #fff3cd;
					border: 1px solid #ffeaa7;
					border-radius: 4px;
					padding: 10px;
					margin: 5px 0;
				}

				.alert-item.critical {
					background: #f8d7da;
					border-color: #f5c6cb;
				}

				.alert-item.warning {
					background: #fff3cd;
					border-color: #ffeaa7;
				}

				.alert-item.info {
					background: #d1ecf1;
					border-color: #bee5eb;
				}

				@media (max-width: 768px) {
					.dashboard-container {
						padding: 10px;
					}

					.metric-card {
						margin-bottom: 15px;
					}

					.metric-icon {
						font-size: 2em;
					}

					.metric-value {
						font-size: 1.5em;
					}
				}
			`
			)
			.appendTo("head");
	}

	async load_dashboard_config() {
		try {
			this.show_loading(true);

			// Cargar dashboards disponibles
			const dashboards = await frappe.call({
				method: "condominium_management.dashboard_consolidado.page.dashboard_ejecutivo.dashboard_ejecutivo.get_user_dashboards",
			});

			if (dashboards.message && dashboards.message.length > 0) {
				// Actualizar selector de dashboard
				const options = dashboards.message.map((d) => ({
					value: d.name,
					label: `${d.dashboard_name} (${d.dashboard_type})`,
				}));

				this.dashboard_selector.df.options = options;
				this.dashboard_selector.refresh();

				// Seleccionar dashboard por defecto
				const default_dashboard =
					dashboards.message.find((d) => d.is_default) || dashboards.message[0];
				this.dashboard_selector.set_value(default_dashboard.name);

				await this.load_dashboard_data(default_dashboard.name);
			} else {
				this.show_no_dashboard_message();
			}
		} catch (error) {
			console.error("Error cargando configuración del dashboard:", error);
			this.show_error_message("Error cargando configuración del dashboard");
		} finally {
			this.show_loading(false);
		}
	}

	async load_dashboard_data(dashboard_config_name) {
		try {
			this.current_dashboard = dashboard_config_name;

			// Cargar configuración del dashboard
			const config = await frappe.call({
				method: "condominium_management.dashboard_consolidado.page.dashboard_ejecutivo.dashboard_ejecutivo.get_default_dashboard_config",
			});

			if (config.message) {
				this.refresh_interval = (config.message.refresh_interval || 30) * 1000;
				this.setup_auto_refresh();
			}

			// Cargar widgets del dashboard
			const widgets = await frappe.call({
				method: "condominium_management.dashboard_consolidado.page.dashboard_ejecutivo.dashboard_ejecutivo.get_dashboard_widgets",
				args: { dashboard_config_name: dashboard_config_name },
			});

			this.widgets = widgets.message || [];

			// Cargar datos del dashboard
			await this.refresh_dashboard();
		} catch (error) {
			console.error("Error cargando datos del dashboard:", error);
			this.show_error_message("Error cargando datos del dashboard");
		}
	}

	async refresh_dashboard() {
		try {
			this.show_loading(true);

			const company_filter = this.company_selector.get_value();

			// Obtener overview general
			const overview = await frappe.call({
				method: "condominium_management.dashboard_consolidado.api.get_dashboard_overview",
				args: {
					dashboard_config: this.current_dashboard,
					company: company_filter,
				},
			});

			if (overview.message && overview.message.success) {
				this.update_header_metrics(overview.message.data);
				await this.render_widgets(overview.message.data);
			} else {
				this.show_error_message(
					overview.message?.error || "Error obteniendo datos del dashboard"
				);
			}
		} catch (error) {
			console.error("Error actualizando dashboard:", error);
			this.show_error_message("Error actualizando dashboard");
		} finally {
			this.show_loading(false);
		}
	}

	update_header_metrics(data) {
		// Actualizar métricas del header
		const moduleCount = Object.keys(data.modules || {}).length;
		$("#total-modules .metric-value").text(moduleCount);

		const alertCount = (data.active_alerts || []).length;
		$("#active-alerts .metric-value").text(alertCount);

		// Actualizar color del icono de alertas
		const alertIcon = $("#active-alerts .metric-icon i");
		if (alertCount > 0) {
			alertIcon
				.removeClass("fa-exclamation-triangle")
				.addClass("fa-exclamation-circle")
				.css("color", "#dc3545");
		} else {
			alertIcon
				.removeClass("fa-exclamation-circle")
				.addClass("fa-exclamation-triangle")
				.css("color", "#28a745");
		}

		// Actualizar timestamp
		const lastUpdate = new Date(data.timestamp);
		$("#last-update .metric-value").text(lastUpdate.toLocaleTimeString());

		// Salud del sistema
		const systemHealth = data.system_health || {};
		const healthValue = systemHealth.status === "healthy" ? "98.5%" : "85.0%";
		$("#system-health .metric-value").text(healthValue);
	}

	async render_widgets(data) {
		const gridContainer = $("#dashboard-grid");

		if (this.widgets.length === 0) {
			gridContainer.html(`
				<div class="text-center" style="padding: 50px;">
					<i class="fa fa-puzzle-piece fa-3x text-muted"></i>
					<h4 class="text-muted mt-3">No hay widgets configurados</h4>
					<p class="text-muted">Configure widgets en la configuración del dashboard</p>
					<button class="btn btn-primary" onclick="dashboard_ejecutivo.open_dashboard_config()">
						Configurar Dashboard
					</button>
				</div>
			`);
			return;
		}

		// Render widgets en grid simple por ahora
		let widgetHtml = '<div class="row">';

		for (let i = 0; i < this.widgets.length; i++) {
			const widget = this.widgets[i];
			const colClass = this.get_column_class(widget.width || 4);

			widgetHtml += `
				<div class="${colClass}">
					<div class="widget-container" data-widget-index="${i}">
						<div class="widget-header">
							<div class="widget-title">${widget.widget_name}</div>
							<div class="widget-refresh" onclick="dashboard_ejecutivo.refresh_widget(${i})">
								<i class="fa fa-refresh"></i>
							</div>
						</div>
						<div class="widget-content" id="widget-content-${i}">
							${await this.render_widget_content(widget, data)}
						</div>
					</div>
				</div>
			`;
		}

		widgetHtml += "</div>";
		gridContainer.html(widgetHtml);
	}

	async render_widget_content(widget, data) {
		const widgetType = widget.widget_type;
		const dataSource = widget.data_source;

		if (widgetType === "Tarjeta KPI") {
			return this.render_kpi_card(widget, data);
		} else if (widgetType === "Tabla") {
			return this.render_table_widget(widget, data);
		} else if (widgetType === "Gráfico") {
			return this.render_chart_widget(widget, data);
		} else if (widgetType === "Alerta") {
			return this.render_alert_widget(widget, data);
		} else {
			return `
				<div class="text-center text-muted">
					<i class="fa fa-cog fa-2x"></i>
					<p>Widget ${widgetType} en desarrollo</p>
				</div>
			`;
		}
	}

	render_kpi_card(widget, data) {
		const moduleData = data.modules;
		const dataSource = widget.data_source.toLowerCase().replace(" ", "_");
		const sourceData = moduleData[dataSource] || {};

		// Obtener primer valor numérico disponible
		let value = 0;
		let label = "Sin datos";

		for (const [key, val] of Object.entries(sourceData)) {
			if (typeof val === "number") {
				value = val;
				label = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
				break;
			}
		}

		return `
			<div class="kpi-card">
				<div class="kpi-value">${value}</div>
				<div class="kpi-label">${label}</div>
				<div class="kpi-trend neutral">
					<i class="fa fa-minus"></i> Sin tendencia
				</div>
			</div>
		`;
	}

	render_table_widget(widget, data) {
		const moduleData = data.modules;
		const dataSource = widget.data_source.toLowerCase().replace(" ", "_");
		const sourceData = moduleData[dataSource] || {};

		let tableHtml = `
			<table class="table table-striped table-sm">
				<thead>
					<tr>
						<th>Métrica</th>
						<th>Valor</th>
					</tr>
				</thead>
				<tbody>
		`;

		for (const [key, value] of Object.entries(sourceData)) {
			if (typeof value === "number" || typeof value === "string") {
				const label = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
				tableHtml += `
					<tr>
						<td>${label}</td>
						<td>${value}</td>
					</tr>
				`;
			}
		}

		tableHtml += "</tbody></table>";
		return tableHtml;
	}

	render_chart_widget(widget, data) {
		return `
			<div class="text-center text-muted" style="padding: 40px;">
				<i class="fa fa-bar-chart fa-2x"></i>
				<p>Gráficos en desarrollo</p>
				<small>Próximamente con Chart.js</small>
			</div>
		`;
	}

	render_alert_widget(widget, data) {
		const alerts = data.active_alerts || [];

		if (alerts.length === 0) {
			return `
				<div class="text-center text-success">
					<i class="fa fa-check-circle fa-2x"></i>
					<p>No hay alertas activas</p>
				</div>
			`;
		}

		let alertsHtml = "";
		alerts.forEach((alert) => {
			alertsHtml += `
				<div class="alert-item ${alert.priority || "info"}">
					<strong>${alert.title}</strong><br>
					<small>${alert.message}</small>
				</div>
			`;
		});

		return alertsHtml;
	}

	get_column_class(width) {
		// Convertir ancho de grid a clases Bootstrap
		if (width <= 3) return "col-md-3";
		if (width <= 6) return "col-md-6";
		if (width <= 9) return "col-md-9";
		return "col-md-12";
	}

	setup_auto_refresh() {
		if (this.refresh_timer) {
			clearInterval(this.refresh_timer);
		}

		this.refresh_timer = setInterval(() => {
			this.refresh_dashboard();
		}, this.refresh_interval);
	}

	async refresh_widget(widgetIndex) {
		try {
			const widget = this.widgets[widgetIndex];
			if (!widget) return;

			// Mostrar loading en el widget específico
			$(`#widget-content-${widgetIndex}`).html(`
				<div class="text-center">
					<i class="fa fa-spinner fa-spin"></i>
					<p>Actualizando...</p>
				</div>
			`);

			// Obtener datos actualizados
			const company_filter = this.company_selector.get_value();
			const overview = await frappe.call({
				method: "condominium_management.dashboard_consolidado.api.get_dashboard_overview",
				args: {
					dashboard_config: this.current_dashboard,
					company: company_filter,
				},
			});

			if (overview.message && overview.message.success) {
				const content = await this.render_widget_content(widget, overview.message.data);
				$(`#widget-content-${widgetIndex}`).html(content);
			}
		} catch (error) {
			console.error("Error actualizando widget:", error);
			$(`#widget-content-${widgetIndex}`).html(
				'<div class="text-danger">Error actualizando widget</div>'
			);
		}
	}

	on_dashboard_change() {
		const selectedDashboard = this.dashboard_selector.get_value();
		if (selectedDashboard && selectedDashboard !== this.current_dashboard) {
			this.load_dashboard_data(selectedDashboard);
		}
	}

	open_dashboard_config() {
		frappe.set_route("List", "Dashboard Configuration");
	}

	async create_snapshot() {
		try {
			const company_filter = this.company_selector.get_value();
			const notes = await frappe.prompt({
				label: "Notas del Snapshot",
				fieldtype: "Text",
				reqd: false,
			});

			if (notes !== null) {
				const result = await frappe.call({
					method: "condominium_management.dashboard_consolidado.api.create_dashboard_snapshot",
					args: {
						dashboard_config: this.current_dashboard,
						company: company_filter,
						notes: notes,
					},
				});

				if (result.message && result.message.success) {
					frappe.show_alert({
						message: "Snapshot creado exitosamente",
						indicator: "green",
					});
				} else {
					frappe.show_alert({
						message: result.message?.error || "Error creando snapshot",
						indicator: "red",
					});
				}
			}
		} catch (error) {
			console.error("Error creando snapshot:", error);
			frappe.show_alert({
				message: "Error creando snapshot",
				indicator: "red",
			});
		}
	}

	view_snapshots() {
		frappe.set_route("List", "Dashboard Snapshot");
	}

	show_loading(show) {
		if (show) {
			$("#dashboard-loading").show();
		} else {
			$("#dashboard-loading").hide();
		}
	}

	show_error_message(message) {
		$("#dashboard-grid").html(`
			<div class="text-center" style="padding: 50px;">
				<i class="fa fa-exclamation-triangle fa-3x text-danger"></i>
				<h4 class="text-danger mt-3">Error</h4>
				<p class="text-muted">${message}</p>
				<button class="btn btn-primary" onclick="dashboard_ejecutivo.refresh_dashboard()">
					Reintentar
				</button>
			</div>
		`);
	}

	show_no_dashboard_message() {
		$("#dashboard-grid").html(`
			<div class="text-center" style="padding: 50px;">
				<i class="fa fa-dashboard fa-3x text-muted"></i>
				<h4 class="text-muted mt-3">No hay dashboards configurados</h4>
				<p class="text-muted">Cree una configuración de dashboard para comenzar</p>
				<button class="btn btn-primary" onclick="dashboard_ejecutivo.open_dashboard_config()">
					Crear Dashboard
				</button>
			</div>
		`);
	}
}

// Exponer instancia global para callbacks
let dashboard_ejecutivo;
