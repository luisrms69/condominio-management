# Companies – Friction Points

**Módulo:** Companies
**Fecha evaluación:** 2025-10-18 (Día 1 - Planificación)
**Estado:** Puntos de fricción preliminares identificados

---

## Friction Points Identificados

| Paso Journey | Descripción Fricción | Impacto Usuario | Severidad | Evidencia | Sugerencia Rápida |
|--------------|---------------------|----------------|-----------|-----------|-------------------|
| 3 | No está claro qué DocType crear primero (Company vs Condominium Information) | Usuario pierde 5-10 min buscando documentación o prueba/error | Alta | `evidencias/screenshots/step3-confusion.png` (Día 2) | Wizard de setup inicial que guíe el orden |
| 6 | Relación Company ↔ Condominium Information no es obvia en el formulario | Usuario puede crear Condominium sin enlazar correctamente a Company | Media | `evidencias/screenshots/step6-no-link.png` (Día 2) | Help text visible con diagrama de relación |
| - | Sin wizard de configuración inicial | Setup completo requiere conocer arquitectura del sistema | Alta | `evidencias/videos/journey1-full-confusion.mp4` (Día 2) | Implementar Setup Wizard estilo ERPNext |
| 4 | Campos obligatorios no claramente marcados en Company form | Usuario intenta guardar y recibe error sin saber qué falta | Media | (TBD - capturar Día 2) | Asteriscos rojos más visibles, resumen campos faltantes |
| 7 | Campos custom (cm_*) mezclados con campos estándar ERPNext | Usuario confundido sobre qué campos son específicos de condominios | Baja | (TBD - capturar Día 2) | Agrupar campos custom en sección dedicada |

---

## Categorización por Tipo

### Onboarding / Primera Experiencia
- ❌ Sin wizard de setup inicial
- ⚠️ No claro qué crear primero (Company vs Condominium)
- ⚠️ Relación entre DocTypes no explícita

### Formularios / Validaciones
- ⚠️ Campos obligatorios poco visibles
- ⚠️ Mensajes de error poco accionables (TBD - verificar)

### Organización Información
- ℹ️ Campos custom mezclados con estándar
- ℹ️ Sin ayuda contextual visible

---

## Métricas Estimadas

| Métrica | Valor Actual (estimado) | Valor Ideal | Gap |
|---------|------------------------|-------------|-----|
| Tiempo setup primer condominio | 20-30 min | 5-10 min | 15-20 min |
| Tasa de error configuración inicial | 60-70% | <10% | ~60% |
| Consultas a documentación | 3-5 por setup | 0-1 | 3-4 |
| Re-trabajo (editar después de crear) | 40-50% | <5% | ~45% |

> **Nota:** Métricas estimadas - validar con observación real en Día 2

---

## Priorización Preliminar

### 🔴 Alta Prioridad (Bloqueantes)
1. Wizard de setup inicial
2. Clarificar orden creación Company → Condominium Information

### 🟡 Media Prioridad (Impacto significativo)
3. Help text relación Company ↔ Condominium
4. Mejorar visibilidad campos obligatorios

### 🟢 Baja Prioridad (Mejora incremental)
5. Agrupar campos custom
6. Ayuda contextual en formularios

---

**Próximos pasos:**
- Validar friction points con ejecución real en admin1.dev (Día 2)
- Capturar evidencias (screenshots/videos)
- Medir métricas reales vs estimadas
- Actualizar severidades según observación

---

**Actualizado:** 2025-10-18
**Estado:** Preliminar - Pendiente validación con usuarios reales
