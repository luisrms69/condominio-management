# Financial Management – Friction Points

**Módulo:** Financial Management
**Fecha evaluación:** 2025-10-18 (Día 1 - Template)
**Estado:** Template preparado - Pendiente evaluación real

---

## Friction Points Identificados (Preliminar)

| Paso Journey | Descripción Fricción | Impacto Usuario | Severidad | Evidencia | Sugerencia Rápida |
|--------------|---------------------|----------------|-----------|-----------|-------------------|
| 2 | Dashboard no muestra KPIs críticos (saldo, pagos vencidos, proyección) | Información clave dispersa, requiere navegar múltiples pantallas | Alta | (TBD - capturar Día 2+) | Dashboard Consolidado Financiero con métricas clave |
| 3 | Campos obligatorios Billing Cycle no claramente marcados | Usuario intenta guardar y recibe errores inesperados | Media | (TBD) | Asteriscos rojos + resumen campos faltantes |
| 5 | No claro si conceptos facturación aplican a todos los deptos automáticamente | Riesgo facturar incorrectamente (algunos deptos sin concepto) | Alta | (TBD) | Preview: "Aplicará a X departamentos" antes de guardar |
| 6 | Sin preview antes de generar 30+ invoices bulk | Si error configuración, debe corregir 30 invoices manualmente | Alta | (TBD) | Preview con tabla resumen antes de generar |
| 7 | Sin listado consolidado de invoices del Billing Cycle | Revisar invoices requiere búsqueda individual por propietario | Media | (TBD) | Vista "Invoices del Ciclo" con filtros |
| 8 | Envío emails manual uno por uno vs bulk | 30 emails manuales toma 30-60 min | Alta | (TBD) | Acción bulk "Enviar todos los invoices" |

---

## Categorización por Tipo

### Visibilidad / Dashboard
- ❌ Dashboard sin KPIs financieros críticos
- ❌ Sin visibilidad consolidada estado facturación
- ⚠️ Sin alertas pagos vencidos visibles

### Facturación Masiva
- ❌ Sin preview antes de generar invoices bulk (riesgo alto)
- ❌ Sin envío bulk emails (operación manual inviable para 30+)
- ⚠️ No claro alcance conceptos facturación

### Validaciones / Prevención Errores
- ⚠️ Campos obligatorios poco visibles
- ❓ Validaciones contables pre-generación (TBD)
- ❓ Prevención duplicados mismo período (TBD)

### Navegación / Reportes
- ⚠️ Sin vista consolidada invoices por ciclo
- ❓ Acceso reportes contables (TBD)
- ❓ Exportación Excel/PDF (TBD)

---

## Métricas Estimadas

| Métrica | Valor Actual (estimado) | Valor Ideal | Gap |
|---------|------------------------|-------------|-----|
| Tiempo facturación 30 deptos | 90-120 min | 15-20 min | ~100 min |
| Errores facturación masiva | 20-30% | <5% | ~25% |
| Tiempo envío 30 emails | 30-60 min | 1-2 min | ~50 min |
| Tiempo generar reportes mensual | 60-90 min | 10-15 min | ~70 min |
| Clicks totales workflow completo | 150-200 | 20-30 | ~170 |

> **Nota:** Métricas estimadas - validar con observación real en Día 2+

---

## Priorización Preliminar

### 🔴 Alta Prioridad (Bloqueantes operación real)
1. Generación bulk invoices con preview (crítico para 30+ deptos)
2. Envío bulk emails (inviable manual para escala)
3. Dashboard KPIs financieros (visibilidad operación diaria)

### 🟡 Media Prioridad (Impacto significativo)
4. Vista consolidada invoices por ciclo
5. Campos obligatorios visibles en Billing Cycle
6. Preview aplicación conceptos facturación

### 🟢 Baja Prioridad (Mejora incremental)
7. Reportes contables predefinidos
8. Alertas automáticas pagos vencidos

---

**Próximos pasos:**
- Ejecutar journey completo en admin1.dev (Día 2+)
- Validar si existe generación bulk (puede estar implementada)
- Capturar evidencias friction points
- Medir métricas reales workflow completo
- Actualizar severidades según observación

---

**Actualizado:** 2025-10-18
**Estado:** Template - Pendiente validación con usuarios reales
