# Companies – Evaluación Heurística (Nielsen)

**Módulo:** Companies
**Evaluador:** Claude Code
**Fecha:** 2025-10-18 (Día 1)
**Estado:** Evaluación inicial - 2 heurísticas completadas

---

## 1. Visibilidad del estado del sistema

**Observación:**
El usuario necesita saber en todo momento si está trabajando con el DocType correcto (Company vs Condominium Information vs Service Management Contract), ya que Companies integra con ERPNext Company core.

**Evaluación preliminar:**
- ✅ Breadcrumbs presentes en formularios
- ⚠️ No hay indicador claro de qué DocType estás editando cuando hay múltiples tabs abiertos
- ❌ Sin feedback visual claro cuando se guarda un registro

**Severidad:** Media

**Evidencia:** `evidencias/screenshots/` (pendiente captura Día 2)

**Acciones sugeridas:**
- Agregar badge/indicador de tipo de documento en header
- Mejorar feedback de guardado (toast notification más visible)

---

## 2. Correspondencia sistema-mundo real

**Observación:**
El módulo usa terminología del dominio de gestión de condominios, pero mezcla conceptos ERPNext (Company) con conceptos específicos (Condominium Information).

**Evaluación preliminar:**
- ✅ Labels en español según RG-001
- ✅ Términos del dominio (Condominio, Contrato de Gestión) familiares para usuarios
- ⚠️ Integración con ERPNext Company puede confundir (¿cuándo uso Company vs Condominium Information?)
- ⚠️ Campos con prefijo cm_* pueden no ser obvios para usuario final

**Severidad:** Media

**Evidencia:** Requiere recreación de journey de creación de primer condominio

**Acciones sugeridas:**
- Wizard de setup inicial que guíe: "Crear Company → Crear Condominium Information → Crear Contrato"
- Help text explicando relación Company ↔ Condominium Information
- Ocultar o agrupar campos técnicos (cm_*)

---

## 3. Control y libertad del usuario

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 4. Consistencia y estándares

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 5. Prevención de errores

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 6. Reconocimiento antes que recuerdo

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 7. Flexibilidad y eficiencia de uso

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 8. Diseño estético y minimalista

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 9. Ayuda a reconocer, diagnosticar y recuperarse de errores

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## 10. Ayuda y documentación

**Observación:** (Pendiente evaluación Día 2)

**Severidad:** TBD

**Evidencia:** TBD

---

## Hallazgos Críticos (Preliminar)

### Alta Prioridad
1. **Falta wizard de setup inicial** - Usuario nuevo no sabe por dónde empezar
2. **Confusión Company vs Condominium Information** - Dos conceptos similares sin relación clara

### Media Prioridad
3. **Feedback de guardado poco visible** - Usuario no está seguro si cambios se guardaron
4. **Campos técnicos (cm_*) visibles** - Añaden complejidad innecesaria

### Baja Prioridad
5. (Pendiente identificar en evaluación completa)

---

**Próximos pasos:**
- Completar heurísticas 3-10 con observaciones reales (Día 2)
- Capturar screenshots de cada hallazgo
- Ejecutar user journey completo de creación de condominio
- Priorizar mejoras con matriz impacto/esfuerzo

---

**Actualizado:** 2025-10-18
**Completado:** 20% (2/10 heurísticas)
