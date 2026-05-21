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
