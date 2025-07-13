/**
 * API Documentation Portal Frontend - Day 3 Portal Web
 * ===================================================
 *
 * Portal SPA para explorar, probar y documentar APIs del sistema.
 */

frappe.pages["api-documentation-portal"].on_page_load = function (wrapper) {
	// Initialize the portal
	window.apiPortal = new APIDocumentationPortal(wrapper);
};

class APIDocumentationPortal {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: "Portal de Documentación de APIs",
			single_column: true,
		});

		this.currentAPI = null;
		this.collections = [];
		this.init();
	}

	init() {
		// Add custom CSS
		this.addCustomCSS();

		// Set up the page content
		this.setupPage();

		// Load initial data
		this.loadPortalData();

		// Set up event listeners
		this.setupEventListeners();
	}

	addCustomCSS() {
		const css = `
			<style>
			.api-documentation-portal {
				background: #f8f9fa;
				min-height: 100vh;
			}

			.portal-header {
				background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
				color: white;
				padding: 2rem 0;
				margin-bottom: 2rem;
			}

			.portal-header h1 {
				font-size: 2.5rem;
				margin-bottom: 0.5rem;
			}

			.subtitle {
				font-size: 1.2rem;
				opacity: 0.9;
				margin-bottom: 1.5rem;
			}

			.portal-stats {
				display: flex;
				gap: 2rem;
				flex-wrap: wrap;
			}

			.stat-item {
				text-align: center;
			}

			.stat-number {
				font-size: 2rem;
				font-weight: bold;
				display: block;
			}

			.stat-label {
				font-size: 0.9rem;
				opacity: 0.8;
			}

			.search-section {
				background: white;
				padding: 1.5rem 0;
				margin-bottom: 2rem;
				box-shadow: 0 2px 4px rgba(0,0,0,0.1);
			}

			.search-box {
				max-width: 800px;
				margin: 0 auto;
			}

			.search-filters {
				display: flex;
				gap: 1rem;
				margin-top: 1rem;
			}

			.search-filters .form-control {
				flex: 1;
			}

			.api-collections-sidebar {
				background: white;
				border-radius: 8px;
				padding: 1.5rem;
				height: fit-content;
				box-shadow: 0 2px 4px rgba(0,0,0,0.1);
			}

			.collection-group {
				margin-bottom: 1rem;
			}

			.collection-header {
				cursor: pointer;
				padding: 0.75rem;
				background: #f8f9fa;
				border-radius: 4px;
				display: flex;
				align-items: center;
				gap: 0.5rem;
				transition: background-color 0.2s;
			}

			.collection-header:hover {
				background: #e9ecef;
			}

			.collection-name {
				flex: 1;
				font-weight: 500;
			}

			.api-count {
				color: #6c757d;
				font-size: 0.9rem;
			}

			.toggle-icon {
				transition: transform 0.2s;
			}

			.collection-group.expanded .toggle-icon {
				transform: rotate(180deg);
			}

			.collection-apis {
				display: none;
				padding-left: 1rem;
				margin-top: 0.5rem;
			}

			.collection-group.expanded .collection-apis {
				display: block;
			}

			.api-item {
				cursor: pointer;
				padding: 0.5rem;
				border-radius: 4px;
				display: flex;
				align-items: center;
				gap: 0.5rem;
				transition: background-color 0.2s;
				margin-bottom: 0.25rem;
			}

			.api-item:hover {
				background: #e3f2fd;
			}

			.api-item.active {
				background: #2196f3;
				color: white;
			}

			.method-badge {
				font-size: 0.7rem;
				padding: 0.2rem 0.5rem;
				border-radius: 3px;
				font-weight: bold;
				text-transform: uppercase;
				min-width: 45px;
				text-align: center;
			}

			.method-get { background: #4caf50; color: white; }
			.method-post { background: #ff9800; color: white; }
			.method-put { background: #2196f3; color: white; }
			.method-delete { background: #f44336; color: white; }
			.method-patch { background: #9c27b0; color: white; }

			.api-name {
				flex: 1;
				font-size: 0.9rem;
			}

			.auto-icon {
				color: #ff9800;
				font-size: 0.8rem;
			}

			.api-details-panel {
				background: white;
				border-radius: 8px;
				min-height: 600px;
				box-shadow: 0 2px 4px rgba(0,0,0,0.1);
			}

			.welcome-screen {
				padding: 3rem;
				text-align: center;
			}

			.welcome-content h2 {
				color: #333;
				margin-bottom: 1rem;
			}

			.feature-highlights {
				display: grid;
				grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
				gap: 2rem;
				margin-top: 3rem;
			}

			.feature {
				text-align: center;
			}

			.feature i {
				color: #2196f3;
				margin-bottom: 1rem;
			}

			.feature h4 {
				margin-bottom: 0.5rem;
			}

			.api-details {
				padding: 2rem;
			}

			.api-header {
				display: flex;
				justify-content: space-between;
				align-items: flex-start;
				margin-bottom: 2rem;
				padding-bottom: 1rem;
				border-bottom: 1px solid #eee;
			}

			.api-title h2 {
				margin: 0.5rem 0;
			}

			.api-path {
				display: flex;
				align-items: center;
				gap: 1rem;
				margin-top: 0.5rem;
			}

			.api-path code {
				background: #f8f9fa;
				padding: 0.5rem 1rem;
				border-radius: 4px;
				font-family: 'Monaco', 'Consolas', monospace;
			}

			.api-actions {
				display: flex;
				gap: 0.5rem;
			}

			.nav-tabs {
				border-bottom: 2px solid #e9ecef;
				margin-bottom: 1.5rem;
			}

			.nav-tabs .nav-link {
				border: none;
				color: #6c757d;
				font-weight: 500;
			}

			.nav-tabs .nav-link.active {
				color: #2196f3;
				border-bottom: 2px solid #2196f3;
				background: none;
			}

			.type-badge {
				background: #6c757d;
				color: white;
				padding: 0.2rem 0.5rem;
				border-radius: 3px;
				font-size: 0.8rem;
			}

			.status-code {
				display: inline-block;
				padding: 0.3rem 0.6rem;
				border-radius: 4px;
				font-weight: bold;
				margin-right: 1rem;
			}

			.status-2 { background: #4caf50; color: white; }
			.status-3 { background: #ff9800; color: white; }
			.status-4 { background: #f44336; color: white; }
			.status-5 { background: #9c27b0; color: white; }

			.response-code {
				margin-bottom: 1.5rem;
				border: 1px solid #e9ecef;
				border-radius: 4px;
				overflow: hidden;
			}

			.response-header {
				background: #f8f9fa;
				padding: 1rem;
				display: flex;
				align-items: center;
			}

			.response-example {
				padding: 1rem;
				background: white;
			}

			.code-example {
				margin-bottom: 2rem;
				border: 1px solid #e9ecef;
				border-radius: 4px;
				overflow: hidden;
			}

			.example-header {
				background: #f8f9fa;
				padding: 1rem;
				display: flex;
				align-items: center;
				justify-content: space-between;
			}

			.language-tag {
				background: #2196f3;
				color: white;
				padding: 0.2rem 0.5rem;
				border-radius: 3px;
				font-size: 0.8rem;
				font-weight: bold;
			}

			.code-example pre {
				margin: 0;
				background: #f8f9fa;
				border: none;
				border-radius: 0;
			}

			.loading-overlay {
				position: fixed;
				top: 0;
				left: 0;
				width: 100%;
				height: 100%;
				background: rgba(0,0,0,0.5);
				display: flex;
				align-items: center;
				justify-content: center;
				z-index: 9999;
			}

			.loading-spinner {
				background: white;
				padding: 2rem;
				border-radius: 8px;
				text-align: center;
			}

			.loading-spinner i {
				color: #2196f3;
				margin-bottom: 1rem;
			}

			.api-tester-content {
				padding: 2rem;
			}

			.tester-header {
				margin-bottom: 2rem;
				padding-bottom: 1rem;
				border-bottom: 1px solid #eee;
			}

			.tester-header h3 {
				margin-bottom: 1rem;
			}

			.api-info {
				display: flex;
				align-items: center;
				gap: 1rem;
			}

			.request-section, .response-section {
				background: #f8f9fa;
				padding: 1.5rem;
				border-radius: 8px;
				height: 100%;
			}

			.request-section h4, .response-section h4 {
				margin-bottom: 1rem;
				color: #333;
			}

			.test-response-container {
				background: white;
				border: 1px solid #dee2e6;
				border-radius: 4px;
				min-height: 300px;
				padding: 1rem;
			}

			.placeholder-response {
				text-align: center;
				color: #6c757d;
				padding: 2rem;
			}

			.placeholder-response i {
				font-size: 2rem;
				margin-bottom: 1rem;
				display: block;
			}

			.loading-response {
				text-align: center;
				color: #2196f3;
				padding: 2rem;
			}

			.loading-response i {
				font-size: 2rem;
				margin-bottom: 1rem;
				display: block;
			}

			.test-result {
				border-radius: 4px;
				overflow: hidden;
			}

			.test-success {
				border: 1px solid #28a745;
			}

			.test-danger {
				border: 1px solid #dc3545;
			}

			.test-error {
				border: 1px solid #dc3545;
				background: #f8d7da;
			}

			.result-header {
				background: #f8f9fa;
				padding: 1rem;
				display: flex;
				align-items: center;
				gap: 1rem;
				border-bottom: 1px solid #dee2e6;
			}

			.status-badge {
				padding: 0.4rem 0.8rem;
				border-radius: 4px;
				font-weight: bold;
				font-size: 0.9rem;
			}

			.status-error {
				background: #dc3545;
				color: white;
			}

			.response-time {
				margin-left: auto;
				background: #6c757d;
				color: white;
				padding: 0.2rem 0.5rem;
				border-radius: 3px;
				font-size: 0.8rem;
			}

			.result-tabs {
				padding: 1rem;
			}

			.result-tabs .nav-pills {
				margin-bottom: 1rem;
			}

			.result-tabs .tab-content {
				background: #f8f9fa;
				border-radius: 4px;
				padding: 1rem;
			}

			.result-tabs pre {
				margin: 0;
				background: white;
				border: 1px solid #dee2e6;
				max-height: 300px;
				overflow-y: auto;
			}

			.request-info p {
				margin-bottom: 0.5rem;
			}

			.parameters-help {
				margin-top: 2rem;
				padding-top: 2rem;
				border-top: 1px solid #dee2e6;
			}

			.parameters-help h5 {
				margin-bottom: 1rem;
				color: #333;
			}

			.tester-footer {
				margin-top: 2rem;
				padding-top: 1rem;
				border-top: 1px solid #eee;
				display: flex;
				gap: 1rem;
				justify-content: flex-end;
			}

			.error-message {
				padding: 1rem;
				color: #721c24;
			}

			@media (max-width: 768px) {
				.portal-header h1 {
					font-size: 2rem;
				}

				.portal-stats {
					justify-content: center;
				}

				.search-filters {
					flex-direction: column;
				}

				.api-header {
					flex-direction: column;
					gap: 1rem;
				}

				.api-actions {
					width: 100%;
					justify-content: center;
				}
			}
			</style>
		`;

		this.page.main.append(css);
	}

	setupPage() {
		// Set page content from HTML template
		this.page.main.html($(this.wrapper).find(".api-documentation-portal").html());
	}

	setupEventListeners() {
		const self = this;

		// Search functionality
		$("#api-search").on("keypress", function (e) {
			if (e.which === 13) {
				self.searchAPIs();
			}
		});

		// Filter changes
		$("#method-filter, #module-filter").on("change", function () {
			self.searchAPIs();
		});

		// Copy functionality
		$(document).on("click", ".copy-url, .copy-code", function () {
			const text = $(this).data("url") || decodeURIComponent($(this).data("code"));
			navigator.clipboard.writeText(text).then(function () {
				frappe.show_alert({ message: "Copiado al portapapeles", indicator: "green" });
			});
		});
	}

	async loadPortalData() {
		this.showLoading(true);

		try {
			// Load portal statistics
			await this.loadPortalStats();

			// Load API collections
			await this.loadAPICollections();
		} catch (error) {
			console.error("Error loading portal data:", error);
			frappe.show_alert({ message: "Error cargando datos del portal", indicator: "red" });
		} finally {
			this.showLoading(false);
		}
	}

	async loadPortalStats() {
		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.page.api_documentation_portal.api_documentation_portal.get_portal_stats",
			});

			if (response.message && response.message.success) {
				this.renderPortalStats(response.message.stats);
			}
		} catch (error) {
			console.error("Error loading portal stats:", error);
		}
	}

	renderPortalStats(stats) {
		const statsHTML = `
			<div class="stat-item">
				<span class="stat-number">${stats.total_apis}</span>
				<span class="stat-label">Total APIs</span>
			</div>
			<div class="stat-item">
				<span class="stat-number">${stats.auto_generated}</span>
				<span class="stat-label">Auto-generadas</span>
			</div>
			<div class="stat-item">
				<span class="stat-number">${stats.completion_rate}%</span>
				<span class="stat-label">Completitud</span>
			</div>
			<div class="stat-item">
				<span class="stat-number">${stats.modules.length}</span>
				<span class="stat-label">Módulos</span>
			</div>
		`;

		$("#portal-stats").html(statsHTML);

		// Populate module filter
		const moduleOptions = stats.modules
			.map(
				(m) =>
					`<option value="${m.module_name}">${m.module_name} (${m.api_count})</option>`
			)
			.join("");
		$("#module-filter").append(moduleOptions);
	}

	async loadAPICollections() {
		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.page.api_documentation_portal.api_documentation_portal.get_api_collections",
			});

			if (response.message && response.message.success) {
				this.collections = response.message.collections;
				this.renderCollections();
			}
		} catch (error) {
			console.error("Error loading API collections:", error);
		}
	}

	renderCollections() {
		const template = $("#collections-template").html();
		if (!template) return;

		// Use frappe's template function instead of underscore
		const html = frappe.render_template(template, { collections: this.collections });

		$("#api-collections").html(html);
	}

	toggleCollection(element) {
		const group = $(element).closest(".collection-group");
		group.toggleClass("expanded");
	}

	async loadAPIDetails(apiName) {
		if (this.currentAPI === apiName) return;

		this.showLoading(true);
		this.currentAPI = apiName;

		// Update active state
		$(".api-item").removeClass("active");
		$(`.api-item[onclick*="${apiName}"]`).addClass("active");

		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.page.api_documentation_portal.api_documentation_portal.get_api_details",
				args: { api_name: apiName },
			});

			if (response.message && response.message.success) {
				this.renderAPIDetails(response.message.api);
			}
		} catch (error) {
			console.error("Error loading API details:", error);
			frappe.show_alert({ message: "Error cargando detalles de la API", indicator: "red" });
		} finally {
			this.showLoading(false);
		}
	}

	renderAPIDetails(api) {
		const template = $("#api-details-template").html();
		if (!template) return;

		// Use frappe's template function instead of underscore
		const html = frappe.render_template(template, { api: api });

		$("#welcome-screen").hide();
		$("#api-tester").hide();
		$("#api-details").html(html).show();

		// Initialize syntax highlighting if available
		if (window.hljs) {
			$("#api-details pre code").each(function (i, block) {
				hljs.highlightBlock(block);
			});
		}
	}

	async searchAPIs() {
		const query = $("#api-search").val();
		const methodFilter = $("#method-filter").val();
		const moduleFilter = $("#module-filter").val();

		const filters = {};
		if (methodFilter) filters.http_method = methodFilter;
		if (moduleFilter) filters.module_path = moduleFilter;

		this.showLoading(true);

		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.page.api_documentation_portal.api_documentation_portal.search_apis",
				args: {
					query: query,
					filters: filters,
				},
			});

			if (response.message && response.message.success) {
				this.renderSearchResults(response.message.results);
			}
		} catch (error) {
			console.error("Error searching APIs:", error);
			frappe.show_alert({ message: "Error en la búsqueda", indicator: "red" });
		} finally {
			this.showLoading(false);
		}
	}

	renderSearchResults(results) {
		// TODO: PHASE2: PORTAL - Implementar vista de resultados de búsqueda
		console.log("Search results:", results);
		frappe.show_alert({ message: `${results.length} APIs encontradas`, indicator: "blue" });
	}

	async showTester(apiName) {
		if (!apiName) {
			frappe.show_alert({ message: "Error: API no especificada", indicator: "red" });
			return;
		}

		this.showLoading(true);

		try {
			// Obtener template de parámetros para la API
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.api_tester.get_api_test_template",
				args: { api_name: apiName },
			});

			if (response.message && response.message.success) {
				this.renderAPITester(response.message.template);
			} else {
				frappe.show_alert({
					message: "Error cargando template de test",
					indicator: "red",
				});
			}
		} catch (error) {
			console.error("Error loading API tester:", error);
			frappe.show_alert({ message: "Error cargando tester", indicator: "red" });
		} finally {
			this.showLoading(false);
		}
	}

	renderAPITester(template) {
		const testerHTML = `
			<div class="api-tester-content">
				<div class="tester-header">
					<h3>🧪 API Tester - ${template.api_name}</h3>
					<div class="api-info">
						<span class="method-badge method-${template.http_method.toLowerCase()}">${
			template.http_method
		}</span>
						<code>${template.api_path}</code>
					</div>
				</div>

				<div class="tester-body">
					<div class="row">
						<div class="col-md-6">
							<div class="request-section">
								<h4>📤 Request</h4>

								<!-- Method Override -->
								<div class="form-group">
									<label>Método HTTP:</label>
									<select id="test-method" class="form-control">
										<option value="${template.http_method}">${template.http_method} (default)</option>
										<option value="GET">GET</option>
										<option value="POST">POST</option>
										<option value="PUT">PUT</option>
										<option value="DELETE">DELETE</option>
										<option value="PATCH">PATCH</option>
									</select>
								</div>

								<!-- Headers -->
								<div class="form-group">
									<label>Headers:</label>
									<textarea id="test-headers" class="form-control" rows="3" placeholder="JSON format">${JSON.stringify(
										template.headers_template,
										null,
										2
									)}</textarea>
								</div>

								<!-- Parameters -->
								<div class="form-group">
									<label>Parámetros:</label>
									<textarea id="test-parameters" class="form-control" rows="8" placeholder="JSON format">${JSON.stringify(
										template.request_template,
										null,
										2
									)}</textarea>
								</div>

								<!-- Authentication Notice -->
								${
									template.authentication_required
										? '<div class="alert alert-info"><i class="fa fa-lock"></i> Esta API requiere autenticación (automática)</div>'
										: '<div class="alert alert-success"><i class="fa fa-unlock"></i> Esta API no requiere autenticación</div>'
								}

								<!-- Test Button -->
								<button class="btn btn-primary btn-lg btn-block" onclick="window.apiPortal.executeAPITest('${
									template.api_name
								}')">
									<i class="fa fa-play"></i> Ejecutar Test
								</button>
							</div>
						</div>

						<div class="col-md-6">
							<div class="response-section">
								<h4>📥 Response</h4>
								<div id="test-response" class="test-response-container">
									<div class="placeholder-response">
										<i class="fa fa-info-circle"></i>
										<p>La respuesta aparecerá aquí después de ejecutar el test.</p>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Parameters Help -->
					${
						template.parameters && template.parameters.length > 0
							? `
					<div class="parameters-help">
						<h5>📋 Parámetros Disponibles</h5>
						<div class="table-responsive">
							<table class="table table-sm">
								<thead>
									<tr>
										<th>Parámetro</th>
										<th>Tipo</th>
										<th>Requerido</th>
										<th>Default</th>
										<th>Descripción</th>
									</tr>
								</thead>
								<tbody>
									${template.parameters
										.map(
											(param) => `
									<tr>
										<td><code>${param.name}</code></td>
										<td><span class="badge badge-secondary">${param.type}</span></td>
										<td>${
											param.required
												? '<span class="badge badge-danger">Sí</span>'
												: '<span class="badge badge-success">No</span>'
										}</td>
										<td>${param.default || "-"}</td>
										<td>${param.description || "Sin descripción"}</td>
									</tr>
									`
										)
										.join("")}
								</tbody>
							</table>
						</div>
					</div>
					`
							: ""
					}
				</div>

				<div class="tester-footer">
					<button class="btn btn-secondary" onclick="window.apiPortal.closeTester()">
						<i class="fa fa-arrow-left"></i> Volver a Detalles
					</button>
					<button class="btn btn-info" onclick="window.apiPortal.clearTesterForm()">
						<i class="fa fa-refresh"></i> Limpiar Formulario
					</button>
				</div>
			</div>
		`;

		$("#welcome-screen").hide();
		$("#api-details").hide();
		$("#api-tester").html(testerHTML).show();
	}

	async executeAPITest(apiName) {
		const methodSelect = $("#test-method").val();
		const headersText = $("#test-headers").val();
		const parametersText = $("#test-parameters").val();

		// Validar JSON
		let headers = {};
		let parameters = {};

		try {
			if (headersText.trim()) {
				headers = JSON.parse(headersText);
			}
		} catch (e) {
			frappe.show_alert({ message: "Error en formato JSON de Headers", indicator: "red" });
			return;
		}

		try {
			if (parametersText.trim()) {
				parameters = JSON.parse(parametersText);
			}
		} catch (e) {
			frappe.show_alert({
				message: "Error en formato JSON de Parámetros",
				indicator: "red",
			});
			return;
		}

		// Mostrar loading en response
		$("#test-response").html(`
			<div class="loading-response">
				<i class="fa fa-spinner fa-spin"></i>
				<p>Ejecutando test...</p>
			</div>
		`);

		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.api_tester.test_api_endpoint",
				args: {
					api_name: apiName,
					method: methodSelect,
					parameters: parameters,
					headers: headers,
				},
			});

			this.renderTestResponse(response.message);
		} catch (error) {
			console.error("Error executing API test:", error);
			this.renderTestResponse({
				success: false,
				error: "Error ejecutando test: " + error.message,
				error_type: "execution_error",
			});
		}
	}

	renderTestResponse(result) {
		let responseHTML = "";

		if (result.success) {
			const testResult = result.test_result;
			const statusClass = testResult.status_code < 400 ? "success" : "danger";

			responseHTML = `
				<div class="test-result test-${statusClass}">
					<div class="result-header">
						<span class="status-badge status-${Math.floor(testResult.status_code / 100)}">${
				testResult.status_code
			}</span>
						<span class="status-text">${testResult.status_text}</span>
						<span class="response-time">${testResult.response_time_ms}ms</span>
					</div>

					<div class="result-tabs">
						<ul class="nav nav-pills nav-sm">
							<li class="nav-item">
								<a class="nav-link active" href="#test-response-body" data-toggle="tab">Response</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="#test-response-headers" data-toggle="tab">Headers</a>
							</li>
							<li class="nav-item">
								<a class="nav-link" href="#test-request-info" data-toggle="tab">Request Info</a>
							</li>
						</ul>

						<div class="tab-content">
							<div class="tab-pane active" id="test-response-body">
								<pre><code class="json">${JSON.stringify(testResult.response_body, null, 2)}</code></pre>
							</div>
							<div class="tab-pane" id="test-response-headers">
								<pre><code class="json">${JSON.stringify(testResult.response_headers, null, 2)}</code></pre>
							</div>
							<div class="tab-pane" id="test-request-info">
								<div class="request-info">
									<p><strong>URL:</strong> <code>${testResult.request_url}</code></p>
									<p><strong>Método:</strong> <span class="badge badge-primary">${
										testResult.request_method
									}</span></p>
									<p><strong>Headers:</strong></p>
									<pre><code class="json">${JSON.stringify(testResult.request_headers, null, 2)}</code></pre>
									<p><strong>Parámetros:</strong></p>
									<pre><code class="json">${JSON.stringify(testResult.request_params, null, 2)}</code></pre>
								</div>
							</div>
						</div>
					</div>
				</div>
			`;
		} else {
			responseHTML = `
				<div class="test-result test-error">
					<div class="result-header">
						<span class="status-badge status-error">ERROR</span>
						<span class="error-type">${result.error_type || "unknown"}</span>
					</div>
					<div class="error-message">
						<p><strong>Error:</strong> ${result.error}</p>
						${
							result.retry_after
								? `<p><strong>Reintentar en:</strong> ${result.retry_after} segundos</p>`
								: ""
						}
					</div>
				</div>
			`;
		}

		$("#test-response").html(responseHTML);

		// Aplicar syntax highlighting si está disponible
		if (window.hljs) {
			$("#test-response pre code").each(function (i, block) {
				hljs.highlightBlock(block);
			});
		}
	}

	closeTester() {
		$("#api-tester").hide();
		if (this.currentAPI) {
			// Volver a mostrar detalles de la API actual
			$("#api-details").show();
		} else {
			$("#welcome-screen").show();
		}
	}

	clearTesterForm() {
		$("#test-method").val($("#test-method option:first").val());
		$("#test-headers").val('{\n  "Content-Type": "application/json"\n}');
		$("#test-parameters").val("{}");
		$("#test-response").html(`
			<div class="placeholder-response">
				<i class="fa fa-info-circle"></i>
				<p>La respuesta aparecerá aquí después de ejecutar el test.</p>
			</div>
		`);
	}

	async generateCode(apiName) {
		if (!apiName) {
			frappe.show_alert({ message: "Error: API no especificada", indicator: "red" });
			return;
		}

		// Mostrar diálogo de selección de lenguaje
		const languages = [
			{ label: "Python", value: "python" },
			{ label: "JavaScript", value: "javascript" },
			{ label: "cURL", value: "curl" },
			{ label: "PHP", value: "php" },
			{ label: "Java", value: "java" },
			{ label: "Go", value: "go" },
		];

		const dialog = new frappe.ui.Dialog({
			title: "Generar Código de Ejemplo",
			fields: [
				{
					label: "Lenguaje de Programación",
					fieldname: "language",
					fieldtype: "Select",
					options: languages.map((l) => l.value).join("\n"),
					default: "python",
					reqd: 1,
				},
				{
					label: "Incluir Autenticación",
					fieldname: "include_auth",
					fieldtype: "Check",
					default: 1,
				},
			],
			primary_action_label: "Generar Código",
			primary_action: async (values) => {
				dialog.hide();
				await this.doGenerateCode(apiName, values.language, values.include_auth);
			},
		});

		dialog.show();
	}

	async doGenerateCode(apiName, language, includeAuth) {
		this.showLoading(true);

		try {
			const response = await frappe.call({
				method: "condominium_management.api_documentation_system.code_generator.generate_api_code",
				args: {
					api_name: apiName,
					language: language,
					include_auth: includeAuth,
				},
			});

			if (response.message && response.message.success) {
				this.showCodeGeneratorResult(response.message);
			} else {
				frappe.show_alert({
					message:
						"Error generando código: " +
						(response.message?.error || "Error desconocido"),
					indicator: "red",
				});
			}
		} catch (error) {
			console.error("Error generating code:", error);
			frappe.show_alert({ message: "Error generando código", indicator: "red" });
		} finally {
			this.showLoading(false);
		}
	}

	showCodeGeneratorResult(result) {
		const dialog = new frappe.ui.Dialog({
			title: `Código ${result.language.toUpperCase()} - ${result.api_name}`,
			size: "large",
			fields: [
				{
					fieldname: "code_display",
					fieldtype: "HTML",
					options: `
						<div class="code-generator-result">
							<div class="code-header">
								<div class="code-info">
									<span class="language-tag">${result.language.toUpperCase()}</span>
									<span class="api-name">${result.api_name}</span>
								</div>
								<button class="btn btn-sm btn-primary copy-generated-code" data-code="${encodeURIComponent(
									result.code
								)}">
									<i class="fa fa-copy"></i> Copiar Código
								</button>
							</div>
							<div class="code-description">
								<p>${result.description}</p>
							</div>
							<div class="generated-code">
								<pre><code class="${result.language}">${result.code}</code></pre>
							</div>
						</div>
						<style>
							.code-generator-result {
								margin: 1rem 0;
							}
							.code-header {
								display: flex;
								justify-content: space-between;
								align-items: center;
								margin-bottom: 1rem;
								padding: 0.75rem;
								background: #f8f9fa;
								border-radius: 4px;
							}
							.code-info {
								display: flex;
								align-items: center;
								gap: 1rem;
							}
							.language-tag {
								background: #2196f3;
								color: white;
								padding: 0.3rem 0.6rem;
								border-radius: 3px;
								font-size: 0.8rem;
								font-weight: bold;
							}
							.api-name {
								font-weight: 500;
								color: #333;
							}
							.code-description {
								margin-bottom: 1rem;
								color: #6c757d;
							}
							.generated-code pre {
								background: #f8f9fa;
								border: 1px solid #dee2e6;
								border-radius: 4px;
								padding: 1rem;
								max-height: 400px;
								overflow-y: auto;
								margin: 0;
							}
							.generated-code code {
								font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
								font-size: 0.9rem;
								line-height: 1.4;
							}
						</style>
					`,
				},
			],
			primary_action_label: "Cerrar",
			primary_action: () => dialog.hide(),
		});

		dialog.show();

		// Agregar event listener para copiar código
		dialog.$wrapper.find(".copy-generated-code").on("click", function () {
			const code = decodeURIComponent($(this).data("code"));
			navigator.clipboard.writeText(code).then(function () {
				frappe.show_alert({
					message: "Código copiado al portapapeles",
					indicator: "green",
				});
			});
		});

		// Aplicar syntax highlighting si está disponible
		if (window.hljs) {
			dialog.$wrapper.find("pre code").each(function (i, block) {
				hljs.highlightBlock(block);
			});
		}
	}

	showLoading(show) {
		if (show) {
			$("#loading-overlay").show();
		} else {
			$("#loading-overlay").hide();
		}
	}
}

// Global utility functions
window.apiPortal = null;
