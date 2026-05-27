# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-27
**Rama activa:** `feature/docs-new-workflow`
**Tarea actual:** Configuración inicial de condo-v16.dev — Company CONDOV16 como CONDO

---

## Recuperación rápida

Estoy trabajando en:
Configurar condo-v16.dev como primer entorno funcional de condominium_management v16.
El setup wizard está completo. El bug de Company Type IDs fue corregido y commiteado.
El formulario de Company ya muestra Tipo de Empresa y secciones condicionales correctamente.

Plan que estoy siguiendo:
CONTINUITY.md sección "Próximos pasos post-migración" → ítem 1 en progreso.

Objetivo inmediato:
Abrir PR de `feature/docs-new-workflow` → `main`.

Criterio de avance:
PR mergeado, condo-v16.dev con migrate limpio post-merge.

---

## Estado actual

### Ya cerrado
- Setup wizard condo-v16.dev ✅ (CONDOV16/CV16, MXN, Mexico)
- Bug Company Type IDs corregido: `'Condominio'`→`'CONDO'`, `'Administradora'`→`'ADMIN'` en fixtures, hooks y tests
- insert_after de custom_field.json corregido — company_type visible en form
- docs_new/ creado con workflow documental, instalacion-y-configuracion.md, tecnico/hooks.md
- Commit `ec362de` en `feature/docs-new-workflow`, sin push

### En progreso
- PR de `feature/docs-new-workflow` → pendiente de autorización para push + PR

### Pendiente inmediato
1. Push + PR de `feature/docs-new-workflow`
2. Guardar CONDOV16 con `company_type = CONDO` desde la UI (no por consola)
3. Datos mínimos de referencia: Space Categories, Component Types

### No repetir
- No mover `insert_after` de `company_type` — ya está en `"reporting_currency"` y funciona
- No intentar diagnosticar con `site_config.json` ni SQL directo — usar `bench execute` con expresiones simples
- No crear sección nueva para company_type — el campo ya es visible sin sección propia

---

## Decisiones vigentes
- `company_type.insert_after = "reporting_currency"` — último campo de la sección `details` (siempre visible, sin depends_on). No cambiar.
- `docs_new/` se construye progresivamente tarea por tarea — no hacer movimientos masivos de `docs/`
- `one_offs/` nunca se commitea (CLAUDE.md global)
- Branch única `feature/docs-new-workflow` cubre docs + fix Company Type IDs — son parte del mismo arranque

---

## Archivos relevantes ahora

### Leer primero
- `condominium_management/fixtures/custom_field.json` — cadena insert_after corregida
- `condominium_management/fixtures/company_type.json` — IDs reales: CONDO, ADMIN, PROV, CONTR

### Probablemente editar
- `CONTINUITY.md` — actualizar tras merge del PR

### No tocar
- `hooks.py` líneas ~190-198 — hooks universales comentados (ISSUE #7)
- Sites v15 (`admin1.dev`, etc.)
- `test-condominium.localhost` — solo para tests

---

## Riesgos / cuidados
- `bench migrate` aplica custom_field.json al site — si se revierte el fixture sin migrate, la BD queda desincronizada
- ISSUE #7 (hooks universales) sigue sin resolver — Document Generation no detecta entidades automáticamente
- 72 de 85 DocTypes sin fixtures — instalación nueva queda incompleta

---

## Información faltante
- Validación pendiente: confirmar que CONDOV16 guardado con company_type=CONDO no dispara errores de validación en company_hooks.py (property_usage_type requerido)
