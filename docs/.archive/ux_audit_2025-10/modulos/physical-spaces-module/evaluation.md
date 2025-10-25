# Physical Spaces – Evaluación Heurística (Nielsen)

**Módulo:** Physical Spaces
**Evaluador:** Claude Code
**Fecha:** 2025-10-18 (Día 1 - Template)
**Estado:** Pendiente evaluación - Template preparado

---

## 1. Visibilidad del estado del sistema

**Observación:** (Pendiente evaluación Día 2+)

El módulo Physical Spaces maneja estructura jerárquica (Nested Set) con niveles: Condominio → Torre/Edificio → Piso → Departamento/Local. Usuario debe visualizar claramente:
- Nivel actual en jerarquía
- Relación padre-hijo
- Estado del espacio (ocupado/disponible/en mantenimiento)

**Evaluación preliminar:**
- ⚠️ Tree view disponible pero puede no ser obvia para usuario nuevo
- ❓ ¿Breadcrumbs muestran path completo en jerarquía?
- ❓ ¿Indicadores visuales de nivel (iconos, colores)?

**Severidad:** TBD

**Evidencia:** `evidencias/screenshots/` (pendiente captura)

**Acciones sugeridas:**
- (TBD después de evaluación real)

---

## 2. Correspondencia sistema-mundo real

**Observación:** (Pendiente evaluación Día 2+)

Terminología debe corresponder al dominio inmobiliario/condominios:
- "Physical Space" vs "Espacio Físico" vs "Propiedad"
- "Space Category" - ¿obvio para usuario?
- "Space Component" - ¿claro su propósito?

**Evaluación preliminar:**
- ✅ Labels en español (RG-001)
- ❓ ¿Términos familiares para administradores?
- ❓ ¿Documentación contextual visible?

**Severidad:** TBD

**Evidencia:** TBD

**Acciones sugeridas:**
- (TBD después de evaluación real)

---

## 3. Control y libertad del usuario

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Usuario puede mover espacios en jerarquía fácilmente?
- ¿Puede deshacer cambios en estructura jerárquica?
- ¿Qué pasa si elimina nodo con hijos?

**Severidad:** TBD

**Evidencia:** TBD

---

## 4. Consistencia y estándares

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Navegación consistente con otros módulos?
- ¿Íconos y colores consistentes?
- ¿Patrones de formularios similares a Companies?

**Severidad:** TBD

**Evidencia:** TBD

---

## 5. Prevención de errores

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Validaciones evitan crear estructura inconsistente?
- ¿Previene eliminar espacio con datos dependientes?
- ¿Confirmación para acciones destructivas?

**Severidad:** TBD

**Evidencia:** TBD

---

## 6. Reconocimiento antes que recuerdo

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Opciones visibles vs. requieren memorizar comandos?
- ¿Tree view muestra información suficiente sin abrir nodo?
- ¿Shortcuts visibles para usuarios avanzados?

**Severidad:** TBD

**Evidencia:** TBD

---

## 7. Flexibilidad y eficiencia de uso

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Bulk operations para crear múltiples espacios?
- ¿Templates para espacios comunes?
- ¿Atajos teclado disponibles?

**Severidad:** TBD

**Evidencia:** TBD

---

## 8. Diseño estético y minimalista

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Tree view muestra solo info relevante?
- ¿Formularios organizados lógicamente?
- ¿Sin campos innecesarios visibles?

**Severidad:** TBD

**Evidencia:** TBD

---

## 9. Ayuda a reconocer, diagnosticar y recuperarse de errores

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Mensajes error claros al violar Nested Set constraints?
- ¿Errores indican cómo corregir?
- ¿Puede recuperarse de operaciones incorrectas?

**Severidad:** TBD

**Evidencia:** TBD

---

## 10. Ayuda y documentación

**Observación:** (Pendiente evaluación Día 2+)

**Hipótesis a validar:**
- ¿Link a documentación visible en formulario?
- ¿Ayuda contextual para Nested Set?
- ¿Ejemplos visuales de estructura jerárquica?

**Severidad:** TBD

**Evidencia:** TBD

---

## Hallazgos Críticos (Preliminar)

### Alta Prioridad
1. (TBD - evaluar en ejecución real)

### Media Prioridad
2. (TBD - evaluar en ejecución real)

### Baja Prioridad
3. (TBD - evaluar en ejecución real)

---

**Próximos pasos:**
- Ejecutar evaluación completa en admin1.dev
- Capturar evidencias (screenshots/videos)
- Completar las 10 heurísticas con observaciones reales
- Identificar friction points específicos

---

**Actualizado:** 2025-10-18
**Completado:** 0% (Template preparado)
