# Physical Spaces – Friction Points

**Módulo:** Physical Spaces
**Fecha evaluación:** 2025-10-18 (Día 1 - Template)
**Estado:** Template preparado - Pendiente evaluación real

---

## Friction Points Identificados (Preliminar)

| Paso Journey | Descripción Fricción | Impacto Usuario | Severidad | Evidencia | Sugerencia Rápida |
|--------------|---------------------|----------------|-----------|-----------|-------------------|
| 2 | No obvio cómo iniciar estructura jerárquica (crear raíz primero) | Usuario pierde 5-10 min o crea estructura incorrecta | Media | (TBD - capturar Día 2+) | Wizard inicial "Configurar Estructura" |
| 3 | Concepto técnico "parent_physical_space=None" poco user-friendly | Confusión sobre qué significa "None" en contexto negocio | Media | (TBD) | Help text: "Dejar vacío para crear nivel raíz" |
| 6-8 | Sin bulk create - creación manual uno por uno | Setup de 30+ espacios toma 60-90 min vs 15-20 esperado | Alta | (TBD) | Implementar bulk import desde Excel/CSV |
| 8 | Sin templates para estructuras comunes | Re-trabajo manual para cada torre similar | Alta | (TBD) | Templates: "Torre N pisos M deptos" |
| 9 | Asignación Space Category individual vs bulk | Clicks innecesarios para categorizar múltiples espacios | Media | (TBD) | Bulk update categorías |

---

## Categorización por Tipo

### Onboarding / Primera Configuración
- ⚠️ No claro cómo iniciar estructura jerárquica
- ⚠️ Terminología técnica (parent=None, Nested Set)
- ❌ Sin wizard de configuración inicial

### Operaciones Masivas
- ❌ Sin bulk create (problema crítico para 30+ espacios)
- ❌ Sin templates para estructuras repetitivas
- ⚠️ Sin bulk update para categorías

### Navegación / Visualización
- ❓ Tree view usabilidad (TBD - evaluar en Día 2+)
- ❓ Search/filtros en tree (TBD)
- ❓ Breadcrumbs claridad (TBD)

### Validaciones / Errores
- ❓ Mensajes Nested Set constraints claros (TBD)
- ❓ Prevención errores estructura inválida (TBD)

---

## Métricas Estimadas

| Métrica | Valor Actual (estimado) | Valor Ideal | Gap |
|---------|------------------------|-------------|-----|
| Tiempo configuración estructura 30 espacios | 60-90 min | 10-15 min | ~75 min |
| Errores estructura jerárquica | 30-40% | <5% | ~35% |
| Clicks totales setup 30 espacios | 200-300 | 20-30 | ~270 |
| Re-trabajo (corregir después) | 20-30% | <5% | ~25% |

> **Nota:** Métricas estimadas - validar con observación real en Día 2+

---

## Priorización Preliminar

### 🔴 Alta Prioridad (Bloqueantes para uso real)
1. Bulk create espacios (crítico para condominios 20+ unidades)
2. Templates estructuras comunes (Torres, Edificios)

### 🟡 Media Prioridad (Impacto significativo)
3. Wizard configuración inicial
4. Terminología user-friendly (vs técnica Nested Set)
5. Bulk update categorías

### 🟢 Baja Prioridad (Mejora incremental)
6. Mejoras tree view (iconos, colores)
7. Shortcuts teclado

---

**Próximos pasos:**
- Ejecutar journey completo en admin1.dev (Día 2+)
- Validar si existe bulk import (puede estar no documentado)
- Capturar evidencias friction points
- Medir métricas reales
- Actualizar severidades y prioridades

---

**Actualizado:** 2025-10-18
**Estado:** Template - Pendiente validación con usuarios reales
