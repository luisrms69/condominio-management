# document_generation/scheduled.py
# Tareas programadas para monitoreo y mantenimiento

import json

import frappe
from frappe.utils import add_months, now_datetime


def performance_monitoring():
	"""
	Monitoreo mensual de performance del Document Generation Framework.

	Basado en: REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md
	Ejecuta: Primer día de cada mes
	"""
	try:
		# Obtener Master Template Registry
		registry_name = frappe.db.get_value("Master Template Registry", {}, "name")
		if not registry_name:
			frappe.log_error("Master Template Registry no encontrado", "Performance Monitoring")
			return

		registry = frappe.get_doc("Master Template Registry", registry_name)

		# Métricas de crecimiento
		metrics = {
			"timestamp": now_datetime().isoformat(),
			"infrastructure_templates_count": len(registry.infrastructure_templates or []),
			"auto_assignment_rules_count": len(registry.auto_assignment_rules or []),
			"template_version": registry.template_version,
			"json_size_bytes": len(json.dumps(registry.as_dict())),
			"json_size_kb": round(len(json.dumps(registry.as_dict())) / 1024, 2),
		}

		# Thresholds de alerta (basados en análisis)
		thresholds = {
			"templates_warning": 100,  # Amarillo
			"templates_critical": 300,  # Rojo - requiere migración
			"json_size_warning": 1024,  # 1 MB
			"json_size_critical": 10240,  # 10 MB
		}

		# Evaluación de estado
		status = "green"
		alerts = []

		if metrics["infrastructure_templates_count"] >= thresholds["templates_critical"]:
			status = "red"
			alerts.append(
				f"🚨 CRÍTICO: {metrics['infrastructure_templates_count']} templates (>= {thresholds['templates_critical']}). Migración a DocTypes separados REQUERIDA."
			)
		elif metrics["infrastructure_templates_count"] >= thresholds["templates_warning"]:
			status = "yellow"
			alerts.append(
				f"⚠️ ADVERTENCIA: {metrics['infrastructure_templates_count']} templates (>= {thresholds['templates_warning']}). Considerar optimizaciones."
			)

		if metrics["json_size_bytes"] >= thresholds["json_size_critical"]:
			status = "red"
			alerts.append(
				f"🚨 CRÍTICO: JSON size {metrics['json_size_kb']} KB (>= {thresholds['json_size_critical'] / 1024} MB). Migración REQUERIDA."
			)
		elif metrics["json_size_bytes"] >= thresholds["json_size_warning"]:
			status = "yellow" if status != "red" else status
			alerts.append(
				f"⚠️ ADVERTENCIA: JSON size {metrics['json_size_kb']} KB (>= {thresholds['json_size_warning'] / 1024} MB). Monitorear de cerca."
			)

		# Crear reporte
		report = {
			"status": status,
			"metrics": metrics,
			"alerts": alerts,
			"next_review": add_months(now_datetime(), 1).isoformat(),
			"recommendations": get_recommendations(metrics, status),
		}

		# Log reporte completo
		frappe.log_error(json.dumps(report, indent=2), f"Performance Monitoring - {status.upper()}")

		# Notificaciones según severidad
		if status == "red":
			# Notificación crítica a administradores
			send_critical_alert(report)
		elif status == "yellow":
			# Notificación de advertencia
			send_warning_alert(report)
		else:
			# Log normal - todo OK
			frappe.logger().info(
				f"Performance monitoring OK: {metrics['infrastructure_templates_count']} templates, {metrics['json_size_kb']} KB"
			)

		# Actualizar última revisión en registry
		registry.db_set("last_performance_review", now_datetime(), update_modified=False)

	except Exception as e:
		frappe.log_error(f"Error en performance monitoring: {e!s}", "Performance Monitoring Error")


def get_recommendations(metrics, status):
	"""
	Generar recomendaciones basadas en métricas actuales.

	Args:
	    metrics: Métricas calculadas
	    status: Estado actual (green/yellow/red)

	Returns:
	    list: Lista de recomendaciones
	"""
	recommendations = []

	if status == "red":
		recommendations.extend(
			[
				"🚨 ACCIÓN INMEDIATA: Implementar migración a DocTypes separados",
				"📊 Evaluar arquitectura actual vs DocTypes independientes",
				"🔧 Implementar lazy loading para optimizar memoria",
				"📋 Crear plan de migración de datos existentes",
			]
		)
	elif status == "yellow":
		recommendations.extend(
			[
				"🔍 Implementar template indexing para optimizar búsquedas",
				"📊 Considerar pagination en UI de administración",
				"🚀 Implementar background loading para templates grandes",
				"📅 Programar revisión de arquitectura en próximo sprint",
			]
		)
	else:
		recommendations.extend(
			[
				"✅ Performance actual excelente",
				"📈 Continuar monitoreo mensual",
				"🔄 Mantener estrategia actual de Single DocType",
			]
		)

	# Recomendaciones específicas por métrica
	if metrics["infrastructure_templates_count"] > 50:
		recommendations.append("💡 Considerar categorización de templates por tipo/módulo")

	if metrics["auto_assignment_rules_count"] > metrics["infrastructure_templates_count"] * 3:
		recommendations.append("⚖️ Evaluar si hay demasiadas reglas de auto-asignación")

	return recommendations


def send_critical_alert(report):
	"""
	Enviar alerta crítica a administradores.

	Args:
	    report: Reporte de performance completo
	"""
	try:
		# Obtener usuarios administradores
		admins = frappe.get_all(
			"User",
			filters={"role_profile_name": "System Manager", "enabled": 1},
			fields=["email", "full_name"],
		)

		subject = "🚨 ALERTA CRÍTICA: Document Generation Framework - Migración Requerida"

		message = f"""
        <h2>🚨 ALERTA CRÍTICA: Performance Document Generation Framework</h2>

        <p><strong>Estado:</strong> {report["status"].upper()}</p>
        <p><strong>Timestamp:</strong> {report["metrics"]["timestamp"]}</p>

        <h3>📊 Métricas Actuales:</h3>
        <ul>
            <li><strong>Templates:</strong> {report["metrics"]["infrastructure_templates_count"]}</li>
            <li><strong>Reglas auto-asignación:</strong> {report["metrics"]["auto_assignment_rules_count"]}</li>
            <li><strong>Tamaño JSON:</strong> {report["metrics"]["json_size_kb"]} KB</li>
            <li><strong>Versión:</strong> {report["metrics"]["template_version"]}</li>
        </ul>

        <h3>🚨 Alertas:</h3>
        <ul>
        {"".join([f"<li>{alert}</li>" for alert in report["alerts"]])}
        </ul>

        <h3>💡 Recomendaciones:</h3>
        <ul>
        {"".join([f"<li>{rec}</li>" for rec in report["recommendations"]])}
        </ul>

        <p><strong>Próxima revisión:</strong> {report["next_review"]}</p>

        <hr>
        <p><em>Generado automáticamente por el sistema de monitoreo mensual.</em></p>
        """

		for admin in admins:
			frappe.sendmail(
				recipients=[admin.email],
				subject=subject,
				message=message,
				header=["Document Generation Framework", "red"],
			)

	except Exception as e:
		frappe.log_error(f"Error enviando alerta crítica: {e!s}", "Critical Alert Error")


def send_warning_alert(report):
	"""
	Enviar alerta de advertencia a administradores.

	Args:
	    report: Reporte de performance completo
	"""
	try:
		# Log como advertencia (no email para yellow status)
		frappe.logger().warning(f"Performance monitoring WARNING: {report['alerts']}")

		# Crear notificación en sistema
		notification = frappe.get_doc(
			{
				"doctype": "Notification Log",
				"subject": "⚠️ Document Generation Framework - Advertencia de Performance",
				"type": "Alert",
				"document_type": "Master Template Registry",
				"email_content": f"Métricas: {report['metrics']['infrastructure_templates_count']} templates, {report['metrics']['json_size_kb']} KB. Alertas: {'; '.join(report['alerts'])}",
			}
		)
		notification.insert(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(f"Error enviando alerta de advertencia: {e!s}", "Warning Alert Error")
