# Financial Management – Improvement Proposals

**Módulo:** Financial Management
**Fecha:** 2025-10-18 (Día 1 - Template)
**Estado:** Propuestas preliminares basadas en friction points anticipados

---

## Propuestas de Mejora

| ID | Problema Identificado | Propuesta de Solución | Costo/Complejidad | Beneficio | Prioridad | Esfuerzo Estimado |
|----|----------------------|----------------------|-------------------|-----------|-----------|-------------------|
| FM-UX-001 | Sin preview antes de generar 30+ invoices bulk - riesgo errores masivos | Modal preview con tabla resumen: departamentos, montos, conceptos. Confirmación explícita antes de generar | M (Medium) | L (Large) | 🔴 Alta | 2 días |
| FM-UX-002 | Envío emails manual uno por uno - inviable para 30+ propietarios | Acción bulk "Enviar Invoices" con selección múltiple + template email configurable | M (Medium) | L (Large) | 🔴 Alta | 2-3 días |
| FM-UX-003 | Dashboard sin KPIs financieros críticos (saldo, pagos vencidos, proyección) | Dashboard Financiero con cards: Saldo Actual, Pagos Pendientes, Pagos Vencidos, Proyección Mes + gráficas tendencias | L (Large) | L (Large) | 🔴 Alta | 3-4 días |
| FM-UX-004 | Sin vista consolidada invoices del Billing Cycle | Vista "Invoices del Ciclo" con tabla: propietario, monto, estado pago, acciones bulk | S (Small) | M (Medium) | 🟡 Media | 1 día |
| FM-UX-005 | No claro alcance conceptos facturación (¿aplican a todos los deptos?) | Preview dinámico: "Este concepto aplicará a X departamentos" + opción filtrar por criterios | M (Medium) | M (Medium) | 🟡 Media | 1-2 días |

---

## Propuestas Detalladas

### 🔴 FM-UX-001: Preview Generación Bulk Invoices

**Problema:** Generar 30+ invoices sin preview - si hay error configuración, corrección manual de todos los invoices.

**Solución propuesta:**

```python
# En Billing Cycle, botón "Generar Facturas"
frappe.ui.form.on('Billing Cycle', {
    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Preview Generación'), function() {
                // API calcula preview sin crear docs
                frappe.call({
                    method: 'condominium_management.financial_management.api.preview_invoice_generation',
                    args: { billing_cycle: frm.doc.name },
                    callback: function(r) {
                        // Modal con tabla resumen
                        let d = new frappe.ui.Dialog({
                            title: 'Preview Generación de Facturas',
                            fields: [
                                {
                                    fieldtype: 'HTML',
                                    fieldname: 'preview_html',
                                    options: `
                                        <h4>Resumen</h4>
                                        <p>Total invoices: ${r.message.total_count}</p>
                                        <p>Monto total: $${r.message.total_amount} MXN</p>

                                        <table class="table table-bordered">
                                            <tr>
                                                <th>Departamento</th>
                                                <th>Propietario</th>
                                                <th>Conceptos</th>
                                                <th>Monto Total</th>
                                            </tr>
                                            ${r.message.invoices.map(inv => `
                                                <tr>
                                                    <td>${inv.property}</td>
                                                    <td>${inv.customer}</td>
                                                    <td>${inv.items.join(', ')}</td>
                                                    <td>$${inv.total}</td>
                                                </tr>
                                            `).join('')}
                                        </table>
                                    `
                                }
                            ],
                            primary_action_label: 'Generar Facturas',
                            primary_action(values) {
                                // Generar con confirmación
                                frappe.confirm(
                                    `¿Generar ${r.message.total_count} facturas?`,
                                    function() {
                                        frm.call('generate_invoices').then(() => {
                                            frappe.msgprint('Facturas generadas exitosamente');
                                            frm.reload_doc();
                                        });
                                    }
                                );
                                d.hide();
                            }
                        });
                        d.show();
                    }
                });
            }, __('Acciones'));
        }
    }
});
```

**Beneficios:**
- ✅ Usuario ve exactamente qué se generará antes de ejecutar
- ✅ Detecta errores configuración antes de crear 30+ docs
- ✅ Reduce re-trabajo de 100% errores → <5%
- ✅ Confianza en operación masiva

**Complejidad:** Media (API preview + UI modal con tabla)

**Estimación:** 2 días

---

### 🔴 FM-UX-002: Envío Bulk Emails Invoices

**Problema:** Enviar 30 emails manualmente toma 30-60 minutos (inviable).

**Solución propuesta:**

```python
# En vista consolidada invoices del ciclo
# Checkbox selección múltiple + botón "Enviar Emails"

@frappe.whitelist()
def send_bulk_invoices(billing_cycle, invoice_list=None):
    """
    Envía emails bulk con invoices adjuntos.

    Args:
        billing_cycle: Nombre del Billing Cycle
        invoice_list: Lista de Sales Invoice names (opcional, default: todos del ciclo)

    Returns:
        {
            'sent': 28,
            'failed': 2,
            'errors': [{'invoice': 'SI-001', 'error': 'Email inválido'}]
        }
    """
    # Template email configurable
    template = frappe.get_doc('Email Template', 'Invoice Notification Condominium')

    invoices = invoice_list or get_cycle_invoices(billing_cycle)
    results = {'sent': 0, 'failed': 0, 'errors': []}

    for invoice_name in invoices:
        try:
            invoice = frappe.get_doc('Sales Invoice', invoice_name)
            # Adjuntar PDF invoice
            attachments = [frappe.attach_print('Sales Invoice', invoice_name, file_name=f'{invoice_name}.pdf')]

            # Enviar email
            frappe.sendmail(
                recipients=[invoice.customer_email],
                subject=template.subject,
                message=frappe.render_template(template.response, {'doc': invoice}),
                attachments=attachments
            )
            results['sent'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({'invoice': invoice_name, 'error': str(e)})

    return results
```

**Beneficios:**
- ✅ 30 emails enviados en 1-2 min vs 30-60 min manual
- ✅ Template configurable (personalizar mensaje)
- ✅ Reporte errores específicos (emails inválidos)
- ✅ Permite envío selectivo (filtrar por estado pago)

**Complejidad:** Media (backend bulk + UI selección + template)

**Estimación:** 2-3 días

---

### 🔴 FM-UX-003: Dashboard Financiero KPIs

**Problema:** Dashboard no muestra información financiera crítica - usuario debe navegar múltiples pantallas.

**Solución propuesta:**

```python
# Dashboard cards en Financial Management workspace

[Card 1: Saldo Actual]
- Monto: $XXX,XXX MXN
- Tendencia: +5% vs mes anterior
- Icon: 💰

[Card 2: Pagos Pendientes]
- Cantidad: 12 invoices
- Monto: $XX,XXX MXN
- Icon: ⏳

[Card 3: Pagos Vencidos]
- Cantidad: 3 invoices
- Monto: $X,XXX MXN (ALERTA ROJA)
- Icon: ⚠️

[Card 4: Proyección Mes]
- Ingresos esperados: $XXX,XXX
- Egresos programados: $XX,XXX
- Balance proyectado: $XX,XXX
- Icon: 📊

[Gráfica 1: Ingresos vs Egresos (12 meses)]
[Gráfica 2: Tasa Cobranza Mensual]
[Gráfica 3: Top 5 Conceptos Facturación]
```

**Implementación:**
- Frappe Workspace con Number Cards
- Chart widgets (bar, line, pie)
- Auto-refresh cada 5 min
- Drill-down: click card → listado detallado

**Beneficios:**
- ✅ Visibilidad inmediata salud financiera
- ✅ Alertas proactivas (pagos vencidos)
- ✅ Decisiones informadas (proyecciones)
- ✅ Reduce tiempo revisar estado de 30 min → 2 min

**Complejidad:** Large (múltiples cards + gráficas + queries optimizadas)

**Estimación:** 3-4 días

---

### 🟡 FM-UX-004: Vista Consolidada Invoices del Ciclo

**Problema:** Revisar invoices requiere búsqueda individual - sin vista consolidada.

**Solución propuesta:**

```python
# En Billing Cycle, tab "Invoices Generados"
# Child table o linked list view

[Vista Tabla]
Columnas:
- Checkbox (selección bulk)
- Departamento (link a Physical Space)
- Propietario (link a Customer)
- Invoice # (link a Sales Invoice)
- Monto
- Estado Pago (Draft/Outstanding/Paid/Cancelled)
- Fecha Vencimiento
- Acciones (Ver, Enviar Email, Registrar Pago)

[Filtros rápidos]
- Estado: Todos | Pendientes | Pagados | Vencidos
- Búsqueda por propietario/departamento

[Acciones Bulk]
- Enviar emails seleccionados
- Exportar a Excel
- Imprimir seleccionados
```

**Beneficios:**
- ✅ Vista consolidada todo el ciclo en una pantalla
- ✅ Filtros rápidos por estado
- ✅ Acciones bulk accesibles
- ✅ Exportación para reportes externos

**Complejidad:** Small (linked list view + filtros)

**Estimación:** 1 día

---

## Matriz Impacto vs Esfuerzo

```
Alta Prioridad (Hacer primero)     │ Evaluación Posterior
─────────────────────────────────────┼─────────────────────────────────
FM-UX-004 (Vista consolidada)        │ FM-UX-003 (Dashboard KPIs)
  - Impacto: MEDIO                   │   - Impacto: MUY ALTO
  - Esfuerzo: BAJO                   │   - Esfuerzo: ALTO
  ✅ QUICK WIN                        │   🔴 PROYECTO ESTRATÉGICO
                                     │
                                     │ FM-UX-002 (Bulk emails)
                                     │   - Impacto: MUY ALTO
                                     │   - Esfuerzo: MEDIO
                                     │   🔴 PROYECTO PRIORITARIO
─────────────────────────────────────┼─────────────────────────────────
FM-UX-005 (Preview conceptos)        │ FM-UX-001 (Preview bulk gen)
  - Impacto: MEDIO                   │   - Impacto: ALTO
  - Esfuerzo: BAJO-MEDIO             │   - Esfuerzo: MEDIO
  🟡 SIGUIENTE ITERACIÓN              │   🔴 PROYECTO PRIORITARIO
```

---

## Roadmap Sugerido

### Sprint 1 (Semana 1) - Quick Wins
1. ✅ FM-UX-004: Vista consolidada invoices (1 día)
2. ✅ FM-UX-005: Preview aplicación conceptos (2 días)

**Total:** ~3 días → Mejora inmediata visibilidad

### Sprint 2 (Semanas 2-3) - Proyectos Prioritarios
3. ✅ FM-UX-001: Preview generación bulk (2 días)
4. ✅ FM-UX-002: Envío bulk emails (3 días)

**Total:** ~5 días → Operación masiva eficiente

### Sprint 3 (Semanas 4-5) - Proyecto Estratégico
5. ✅ FM-UX-003: Dashboard KPIs completo (4 días)

**Total proyecto:** ~4-5 semanas para todas las mejoras

---

## Criterios de Éxito

### Métricas objetivo post-implementación:

| Métrica | Antes | Después (Target) |
|---------|-------|------------------|
| Tiempo facturación 30 deptos | 90-120 min | 15-20 min |
| Tiempo envío 30 emails | 30-60 min | 1-2 min |
| Errores facturación masiva | 20-30% | <5% |
| Tiempo revisar estado financiero | 30 min | 2 min |
| Satisfacción usuario (1-5) | 2.5 | 4.5+ |

---

**Próximos pasos:**
- Validar propuestas con contadores/administradores reales
- Verificar funcionalidad bulk existente
- Priorizar según feedback usuarios
- Crear issues GitHub para cada propuesta
- Asignar a sprints según roadmap

---

**Actualizado:** 2025-10-18
**Estado:** Propuestas preliminares - Pendiente validación real
