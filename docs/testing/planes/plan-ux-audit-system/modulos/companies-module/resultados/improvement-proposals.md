# Companies – Improvement Proposals

**Módulo:** Companies
**Fecha:** 2025-10-18 (Día 1)
**Estado:** Propuestas preliminares basadas en friction points identificados

---

## Propuestas de Mejora

| ID | Problema Identificado | Propuesta de Solución | Costo/Complejidad | Beneficio | Prioridad | Esfuerzo Estimado |
|----|----------------------|----------------------|-------------------|-----------|-----------|-------------------|
| CM-UX-001 | Sin wizard de setup inicial - usuario no sabe por dónde empezar | Implementar Setup Wizard que guíe: 1) Crear Company → 2) Crear Condominium Information → 3) Crear Service Management Contract → 4) Configurar Physical Spaces | L (Large) | L (Large) | 🔴 Alta | 3-5 días |
| CM-UX-002 | No claro qué crear primero (Company vs Condominium Information) | Agregar banner informativo en Condominium Information form: "⚠️ Primero debe crear una Company. [Ver guía]" + deshabilitar guardado si no hay Company seleccionada | S (Small) | M (Medium) | 🔴 Alta | 4-6 horas |
| CM-UX-003 | Relación Company ↔ Condominium Information no obvia | 1) Help text visible con diagrama, 2) Link directo "Crear Company" desde Condominium form, 3) Validación que muestre Companies disponibles | M (Medium) | M (Medium) | 🟡 Media | 1-2 días |
| CM-UX-004 | Campos obligatorios poco visibles en Company form | 1) Asteriscos rojos más grandes, 2) Resumen "X campos obligatorios faltantes" arriba del form, 3) Highlight campos faltantes al intentar guardar | S (Small) | M (Medium) | 🟡 Media | 4-6 horas |
| CM-UX-005 | Campos custom (cm_*) mezclados con estándar ERPNext | Agrupar campos custom en sección colapsable "Configuración Específica Condominios" con descripción clara | S (Small) | S (Small) | 🟢 Baja | 2-4 horas |

---

## Propuestas Detalladas

### 🔴 CM-UX-001: Setup Wizard

**Problema:** Sin guía para configuración inicial, usuario pierde 20-30 min en setup que debería tomar 5-10 min.

**Solución propuesta:**

```python
# Wizard de 4 pasos estilo ERPNext
Step 1: Crear Company
  - Form simplificado (solo campos esenciales)
  - Ayuda contextual visible
  - Valores default inteligentes (Country=Mexico, Currency=MXN)

Step 2: Crear Condominium Information
  - Auto-enlazado a Company del Step 1
  - Campos organizados por secciones lógicas
  - Validaciones en tiempo real

Step 3: Crear Service Management Contract
  - Relación Company ↔ Condominium pre-poblada
  - Template de contrato default

Step 4: Configuración Physical Spaces (opcional)
  - Link a siguiente módulo
  - Opción "Configurar después"
```

**Beneficios:**
- ✅ Reduce tiempo setup de 20-30 min → 5-10 min (60% reducción)
- ✅ Elimina 90% de errores configuración inicial
- ✅ Usuario entiende arquitectura del sistema
- ✅ Experiencia profesional desde primer contacto

**Complejidad:**
- Crear nuevo DocType "Condominium Setup Wizard"
- 4 vistas/steps con navegación
- Lógica validación entre steps
- Integración con DocTypes existentes
- Tests completos del wizard

**Estimación:** 3-5 días (con tests)

---

### 🔴 CM-UX-002: Banner Informativo Order de Creación

**Problema:** Usuario intenta crear Condominium Information antes de Company.

**Solución propuesta:**

```javascript
// client script para Condominium Information
frappe.ui.form.on('Condominium Information', {
    onload: function(frm) {
        if (frm.is_new()) {
            // Verificar si existen Companies
            frappe.call({
                method: 'frappe.client.get_count',
                args: { doctype: 'Company' },
                callback: function(r) {
                    if (r.message === 0) {
                        // Mostrar banner grande
                        frm.dashboard.add_comment(
                            `⚠️ <b>Primero debe crear una Company</b><br>
                            Los condominios deben estar asociados a una Company en ERPNext.
                            <a href="/app/company/new">Crear Company ahora</a> |
                            <a href="/docs/user-guide/companies">Ver guía</a>`,
                            'red', true
                        );
                        // Deshabilitar guardado
                        frm.disable_save();
                    }
                }
            });
        }
    }
});
```

**Beneficios:**
- ✅ Previene error común
- ✅ Guía al usuario al siguiente paso correcto
- ✅ Reduce frustración y re-trabajo

**Complejidad:** Baja (solo client script + validation)

**Estimación:** 4-6 horas (con tests)

---

### 🟡 CM-UX-003: Diagrama Relación Company ↔ Condominium

**Problema:** Relación entre DocTypes no es obvia.

**Solución propuesta:**

```python
# En Condominium Information doctype:
# 1. Help text campo 'company':
"Seleccione la Company (entidad legal) a la que pertenece este condominio.
Una Company puede gestionar múltiples condominios.

Company → 1:N → Condominiums"

# 2. Botón quick-create:
# client script
frappe.ui.form.on('Condominium Information', {
    refresh: function(frm) {
        if (!frm.doc.company) {
            frm.add_custom_button(__('Crear Nueva Company'), function() {
                frappe.new_doc('Company', {
                    onload: function(new_company_frm) {
                        // Al guardar, auto-select en Condominium
                        new_company_frm.on_submit = function() {
                            frm.set_value('company', new_company_frm.doc.name);
                        };
                    }
                });
            }, __('Acciones'));
        }
    }
});
```

**Beneficios:**
- ✅ Usuario entiende relación 1:N
- ✅ Reduce consultas a documentación
- ✅ Flujo más rápido (crear Company sin salir del form)

**Complejidad:** Media (client script + help text + diagram)

**Estimación:** 1-2 días

---

## Matriz Impacto vs Esfuerzo

```
Alta Prioridad (Hacer primero)     │ Evaluación Posterior
─────────────────────────────────────┼─────────────────────────────────
CM-UX-002 (Banner)                   │
  - Impacto: ALTO                    │ CM-UX-001 (Wizard)
  - Esfuerzo: BAJO                   │   - Impacto: MUY ALTO
  ✅ QUICK WIN                        │   - Esfuerzo: ALTO
                                     │   ⏳ PROYECTO MAYOR
─────────────────────────────────────┼─────────────────────────────────
CM-UX-004 (Campos obligatorios)      │ CM-UX-005 (Agrupar campos)
CM-UX-003 (Diagrama relación)        │   - Impacto: BAJO
  - Impacto: MEDIO                   │   - Esfuerzo: BAJO
  - Esfuerzo: BAJO-MEDIO             │   🟢 NICE TO HAVE
  🟡 SIGUIENTE ITERACIÓN              │
```

---

## Roadmap Sugerido

### Sprint 1 (Semana 1) - Quick Wins
1. ✅ CM-UX-002: Banner informativo (6h)
2. ✅ CM-UX-004: Campos obligatorios visibles (6h)
3. ✅ CM-UX-005: Agrupar campos custom (4h)

**Total:** ~2 días → Mejora inmediata experiencia

### Sprint 2 (Semana 2) - Mejoras Medias
4. ✅ CM-UX-003: Diagrama + help text relación (2 días)

### Sprint 3 (Semana 3-4) - Proyecto Mayor
5. ✅ CM-UX-001: Setup Wizard completo (5 días)

**Total proyecto:** ~2-3 semanas para todas las mejoras

---

## Criterios de Éxito

### Métricas objetivo post-implementación:

| Métrica | Antes | Después (Target) |
|---------|-------|------------------|
| Tiempo setup primer condominio | 20-30 min | 5-10 min |
| Tasa error configuración inicial | 60-70% | <10% |
| Consultas documentación | 3-5 | 0-1 |
| Satisfacción usuario (1-5) | 2.5 | 4.5+ |

---

**Próximos pasos:**
- Validar propuestas con stakeholders
- Priorizar según recursos disponibles
- Crear issues GitHub para cada propuesta
- Asignar a sprints según roadmap

---

**Actualizado:** 2025-10-18
**Estado:** Propuestas preliminares - Pendiente aprobación
