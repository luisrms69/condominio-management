# Hallazgo: Contaminación de Fixtures en bench export-fixtures

**Fecha:** 2026-05-21
**Detectado durante:** Validación del fixture de Role (PR de migración v15→v16)
**Estado:** Documentado — pendiente corrección en trabajo separado

---

## Contexto

Durante la validación del nuevo fixture de `Role` (22 roles custom requeridos por permisos
de DocTypes), se verificó que ejecutar `bench --site admin1.dev export-fixtures --app
condominium_management` modifica fixtures existentes ajenos al scope del cambio.

El fixture de `Role` sí es estable: checksum idéntico en dos exports consecutivos.

---

## Fixtures afectados

| Fixture | Causa probable |
|---------|---------------|
| `contribution_category.json` | BD de `admin1.dev` tiene registros de test generados por la suite de tests (nombres como `Test Infrastructure 20251026195417940`). No fueron exportados en su momento y quedaron en la BD sin contrapartida en código. |
| `entity_type_configuration.json` | BD tiene un registro para entidad `User` que no estaba en el fixture comprometido. Fue creado probablemente durante pruebas o configuración manual. |
| `master_template_registry.json` | Campo `last_update` en BD tiene timestamp más reciente que el comprometido (`2026-01-24` vs `2025-10-07`). Se actualiza automáticamente al usar el sistema. |

---

## Impacto operativo

- Cualquier ejecución de `bench export-fixtures` genera un diff sucio en esos 3 archivos.
- Riesgo de que esos cambios se commiteen accidentalmente junto con cambios legítimos.
- La contaminación de `contribution_category` incluye datos de test que no deben estar en fixtures de producción.

---

## Decisión

**No se corrige en este PR.** La corrección requiere trabajo específico:

1. Limpiar registros de test de `contribution_category` en `admin1.dev`.
2. Evaluar si el registro `User` en `entity_type_configuration` debe exportarse o eliminarse.
3. Decidir si el timestamp de `master_template_registry.last_update` debe congelarse en el fixture o excluirse del export.

---

## Regla operativa hasta que se corrija

- **No commitear** cambios en `contribution_category.json`, `entity_type_configuration.json`
  ni `master_template_registry.json` sin revisión específica de su contenido.
- Después de cada `bench export-fixtures`, verificar `git diff --stat` y revertir
  cualquier cambio en esos 3 archivos que no sea intencional.
- Ver también: `docs/development/REPORTE-FIXTURES-SOBRESCRITURA.md`

---

## Análisis detallado por fixture (2026-05-21)

### contribution_category.json

- **Registros versionados:** 6 (legítimos, nombres tipo `Document Generation-Infrastructure Template`)
- **Registros en admin1.dev:** 61 = 6 reales + 55 de test
- **Registros de test:** `contribution_type = "Test Infrastructure 202510XXXXXXXXX"`, names tipo hash aleatorio (`3l37m8vi14`, etc.)
- **Causa:** Tests L4 crean registros con `frappe.get_doc(...).insert()` sin limpiarlos en `tearDown`. Acumulados desde oct 2025.
- **Fix en hooks.py:** Agregar filtro explícito por los 6 nombres reales.
- **Fix en BD:** Pendiente de autorización y backup previo — no ejecutar sin aprobación.

### entity_type_configuration.json

- **Registros versionados:** 1 (`Service Management Contract`)
- **Registros en admin1.dev:** 2 = 1 versionado + 1 nuevo (`User`, `entity_name=Usuario`, `auto_detect_on_create=1`, creado 2025-10-26)
- **Estado del registro `User`:** Requiere decisión humana:
  - Si es configuración funcional → incluir en fixture con filtro explícito
  - Si es artefacto de test/desarrollo → eliminar de BD solo después de backup y autorización
- **Fix en hooks.py:** Filtro explícito por `Service Management Contract` mientras se resuelve `User`.

### master_template_registry.json

- **Tipo:** Single DocType (1 único registro)
- **Diferencia:** Solo el campo `last_update` cambia (`2025-10-07` → `2026-01-24`)
- **Causa:** `last_update` es campo volátil — se actualiza automáticamente en cada propagación de templates. No es dato de configuración.
- **Fix limpio no disponible en v15:** Frappe no permite excluir campos individuales del export de fixtures.
- **Workaround:** Revertir `master_template_registry.json` después de cada `bench export-fixtures` hasta diseñar solución mejor.

---

## Reglas no negociables para cambios de BD

1. **Ningún cambio en BD se ejecuta sin autorización humana explícita** en ese turno de trabajo.
2. **Antes de cualquier cambio en BD se debe correr backup completo** del sitio afectado:
   ```bash
   bench --site admin1.dev backup --with-files
   ```
3. **Si un dato es funcional para la app**, debe quedar versionado como fixture, patch o setup
   controlado. No se acepta depender de cambios manuales en BD.
4. **No se permite resolver contaminación de fixtures borrando datos sin análisis previo.**
   Los datos de test acumulados en BD son candidatos a limpieza, no basura eliminable automáticamente.
5. **El registro `User` en Entity Type Configuration no se toca** hasta decisión humana explícita
   sobre si es configuración real o artefacto de desarrollo.
6. **Los 55 registros de test en Contribution Category no se borran** en este PR.
   Se resuelven añadiendo filtros en hooks.py para que no contaminen el export.

---

## Plan de corrección propuesto (este PR)

**Cambios en hooks.py únicamente — sin tocar BD:**

1. Filtro explícito para `Contribution Category`: exportar solo los 6 nombres reales versionados.
2. Filtro explícito para `Entity Type Configuration`: exportar solo `Service Management Contract`
   mientras se decide sobre el registro `User`.
3. `Master Template Registry`: sin cambio de filtro. Documentar workaround de revertir post-export.

**Pendiente de PR/trabajo separado:**
- Decisión sobre `User` en Entity Type Configuration
- Limpieza de 55 registros test en Contribution Category (requiere backup + autorización)
- Solución de largo plazo para `last_update` volátil en Master Template Registry
