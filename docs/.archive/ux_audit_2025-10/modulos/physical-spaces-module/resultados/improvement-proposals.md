# Physical Spaces – Improvement Proposals

**Módulo:** Physical Spaces
**Fecha:** 2025-10-18 (Día 1 - Template)
**Estado:** Propuestas preliminares basadas en friction points anticipados

---

## Propuestas de Mejora

| ID | Problema Identificado | Propuesta de Solución | Costo/Complejidad | Beneficio | Prioridad | Esfuerzo Estimado |
|----|----------------------|----------------------|-------------------|-----------|-----------|-------------------|
| PS-UX-001 | Sin bulk create - setup manual 30+ espacios toma 60-90 min | Bulk Import desde Excel/CSV con template predefinido + validaciones Nested Set | M (Medium) | L (Large) | 🔴 Alta | 2-3 días |
| PS-UX-002 | Sin templates para estructuras comunes (Torres con N pisos) | Wizard "Crear Torre" que genera estructura completa: Torre → Pisos → Departamentos automáticamente | M (Medium) | L (Large) | 🔴 Alta | 2-3 días |
| PS-UX-003 | No claro cómo iniciar estructura jerárquica | Wizard setup inicial "Configurar Estructura Física" con guía paso a paso | M (Medium) | M (Medium) | 🟡 Media | 1-2 días |
| PS-UX-004 | Terminología técnica (parent_physical_space=None) confunde usuario | Simplificar labels: "Espacio Padre" + help text: "Dejar vacío para nivel raíz del condominio" | S (Small) | S (Small) | 🟡 Media | 2-4 horas |
| PS-UX-005 | Sin bulk update para Space Category | Acción masiva "Asignar Categoría" para selección múltiple en tree view | S (Small) | M (Medium) | 🟡 Media | 1 día |

---

## Propuestas Detalladas

### 🔴 PS-UX-001: Bulk Import Espacios desde Excel

**Problema:** Setup manual de 30+ espacios toma 60-90 minutos (inviable para condominios grandes).

**Solución propuesta:**

```python
# Template Excel estandarizado:
# Columna A: Nombre Espacio
# Columna B: Parent (nombre o código)
# Columna C: Space Category
# Columna D: Nivel (auto-calculado)
# Columna E: Código único

Ejemplo:
Torres del Sol    |              | Condominio      | 0 | ROOT
Torre A          | Torres del Sol| Torre          | 1 | TORRE-A
Piso 1           | Torre A       | Piso           | 2 | A-P1
Depto A-101      | Piso 1        | Departamento   | 3 | A-101
Depto A-102      | Piso 1        | Departamento   | 3 | A-102

# Funcionalidad import:
1. Validar estructura (parent existe, no ciclos)
2. Calcular lft/rgt Nested Set automáticamente
3. Batch insert optimizado
4. Reporte errores específicos (línea Excel con problema)
5. Preview antes de import final
```

**Beneficios:**
- ✅ Reduce tiempo setup de 90 min → 10 min (90% reducción)
- ✅ Elimina errores estructura manual
- ✅ Permite duplicar/modificar templates fácilmente
- ✅ Facilita migraciones desde otros sistemas

**Complejidad:**
- Parser Excel con validaciones
- Cálculo Nested Set lft/rgt para múltiples nodos
- Transacción atómica (todo o nada)
- UI preview con errores resaltados
- Tests Nested Set integrity

**Estimación:** 2-3 días (con tests completos)

---

### 🔴 PS-UX-002: Wizard "Crear Torre"

**Problema:** Crear estructuras repetitivas (Torre → Pisos → Deptos) es tedioso y propenso a errores.

**Solución propuesta:**

```python
# Wizard interactivo
frappe.ui.form.on('Physical Space', {
    refresh: function(frm) {
        frm.add_custom_button(__('Crear Torre Completa'), function() {
            let d = new frappe.ui.Dialog({
                title: 'Crear Estructura Torre',
                fields: [
                    {
                        label: 'Nombre Torre',
                        fieldname: 'tower_name',
                        fieldtype: 'Data',
                        reqd: 1
                    },
                    {
                        label: 'Número de Pisos',
                        fieldname: 'num_floors',
                        fieldtype: 'Int',
                        reqd: 1,
                        default: 5
                    },
                    {
                        label: 'Departamentos por Piso',
                        fieldname: 'units_per_floor',
                        fieldtype: 'Int',
                        reqd: 1,
                        default: 4
                    },
                    {
                        label: 'Patrón Nomenclatura',
                        fieldname: 'naming_pattern',
                        fieldtype: 'Select',
                        options: 'A-101\nTorre-Piso-Depto\nNúmero Secuencial',
                        default: 'A-101'
                    },
                    {
                        label: 'Preview',
                        fieldname: 'preview',
                        fieldtype: 'HTML',
                        read_only: 1
                    }
                ],
                primary_action_label: 'Crear Estructura',
                primary_action(values) {
                    // Backend crea:
                    // 1. Torre
                    // 2. N Pisos
                    // 3. M Deptos por piso
                    // 4. Calcula Nested Set
                    // 5. Asigna categorías automáticamente
                    frappe.call({
                        method: 'condominium_management.api.create_tower_structure',
                        args: values,
                        callback: function(r) {
                            frappe.msgprint(`Torre creada: ${r.message.spaces_created} espacios`);
                            frm.reload_doc();
                        }
                    });
                    d.hide();
                }
            });

            // Preview dinámico al cambiar valores
            d.fields_dict.num_floors.$input.on('change', function() {
                update_preview(d);
            });

            d.show();
        }, __('Acciones'));
    }
});
```

**Beneficios:**
- ✅ Torre 5 pisos × 4 deptos (20 espacios) creada en 1 minuto
- ✅ Nomenclatura consistente garantizada
- ✅ Nested Set correcto automáticamente
- ✅ Preview evita errores

**Complejidad:** Media (wizard UI + backend batch create)

**Estimación:** 2-3 días

---

### 🟡 PS-UX-003: Wizard Setup Inicial Estructura

**Problema:** Usuario nuevo no sabe por dónde empezar configuración física.

**Solución propuesta:**

```python
# Wizard 3 pasos
Step 1: Tipo de Estructura
  - Opción 1: Torre única
  - Opción 2: Múltiples torres
  - Opción 3: Edificio horizontal (casas)
  - Opción 4: Import desde Excel

Step 2: Configuración según tipo
  - Si Torres: cantidad, pisos, deptos
  - Si Horizontal: cantidad casas, nomenclatura
  - Si Import: upload Excel

Step 3: Confirmación y Creación
  - Preview estructura completa
  - Botón "Crear Estructura"
  - Barra progreso (creando 30+ espacios)
```

**Beneficios:**
- ✅ Usuario nuevo completa setup en 5-10 min
- ✅ Estructura correcta desde inicio
- ✅ Cubre casos comunes (Torres, Horizontal, Mixto)

**Complejidad:** Media (3 steps wizard + lógica creación)

**Estimación:** 1-2 días

---

### 🟡 PS-UX-005: Bulk Update Space Category

**Problema:** Asignar categoría a 20 departamentos requiere 20 clicks individuales.

**Solución propuesta:**

```python
# En tree view:
1. Checkbox para selección múltiple
2. Botón "Acciones Masivas" aparece al seleccionar ≥2
3. Opción "Asignar Categoría"
4. Dialog selecciona categoría
5. Batch update en backend
```

**Beneficios:**
- ✅ 20 espacios categorizados en 1 operación vs 20
- ✅ Reduce clicks ~95%
- ✅ Menos errores (categoría consistente)

**Complejidad:** Baja (UI + batch update simple)

**Estimación:** 1 día

---

## Matriz Impacto vs Esfuerzo

```
Alta Prioridad (Hacer primero)     │ Evaluación Posterior
─────────────────────────────────────┼─────────────────────────────────
PS-UX-005 (Bulk update categorías)   │ PS-UX-001 (Bulk Import Excel)
  - Impacto: MEDIO                   │   - Impacto: MUY ALTO
  - Esfuerzo: BAJO                   │   - Esfuerzo: MEDIO
  ✅ QUICK WIN                        │   🔴 PROYECTO PRIORITARIO
                                     │
                                     │ PS-UX-002 (Wizard Torre)
                                     │   - Impacto: MUY ALTO
                                     │   - Esfuerzo: MEDIO
                                     │   🔴 PROYECTO PRIORITARIO
─────────────────────────────────────┼─────────────────────────────────
PS-UX-004 (Terminología)             │ PS-UX-003 (Wizard setup)
  - Impacto: BAJO                    │   - Impacto: MEDIO
  - Esfuerzo: BAJO                   │   - Esfuerzo: MEDIO
  🟢 NICE TO HAVE                     │   🟡 SIGUIENTE ITERACIÓN
```

---

## Roadmap Sugerido

### Sprint 1 (Semana 1) - Quick Wins
1. ✅ PS-UX-004: Terminología user-friendly (4h)
2. ✅ PS-UX-005: Bulk update categorías (1 día)

**Total:** ~1.5 días → Mejora inmediata operación diaria

### Sprint 2 (Semanas 2-3) - Proyectos Mayores
3. ✅ PS-UX-001: Bulk Import Excel (3 días)
4. ✅ PS-UX-002: Wizard "Crear Torre" (3 días)

**Total:** ~6 días → Reducción dramática tiempo setup

### Sprint 3 (Semana 4) - Setup Experience
5. ✅ PS-UX-003: Wizard setup inicial (2 días)

**Total proyecto:** ~3-4 semanas para todas las mejoras

---

## Criterios de Éxito

### Métricas objetivo post-implementación:

| Métrica | Antes | Después (Target) |
|---------|-------|------------------|
| Tiempo setup 30 espacios | 60-90 min | 10-15 min |
| Errores estructura Nested Set | 30-40% | <5% |
| Clicks totales setup | 200-300 | 20-30 |
| Satisfacción usuario (1-5) | 2.0 | 4.5+ |

---

**Próximos pasos:**
- Validar propuestas con administradores reales
- Verificar si existe funcionalidad bulk (puede estar no documentada)
- Priorizar según feedback usuarios
- Crear issues GitHub para cada propuesta
- Asignar a sprints según roadmap

---

**Actualizado:** 2025-10-18
**Estado:** Propuestas preliminares - Pendiente validación real
