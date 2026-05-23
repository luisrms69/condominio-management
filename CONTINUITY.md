# Documento de Continuidad — condominium_management

**Fecha:** 2026-05-22
**Para:** Nueva sesión Claude Code abriendo este app en VS Code
**Desde:** Sesión de migración v16 — infraestructura Claude cerrada

---

## Qué es este app

`condominium_management` es una app Frappe/ERPNext para administración de condominios.
Gestiona propiedades, finanzas (cuotas, facturación automática, multas), espacios físicos,
comités, asambleas y contribuciones entre sitios (arquitectura multi-site).

**Repositorio:** https://github.com/luisrms69/condominio-management
**Branch activo:** `main`
**Versión:** 0.0.1 — en desarrollo activo, no en producción

---

## Estado actual de migración

La app está instalada en bench v16 y funcional. La migración v15 → v16 está en curso.

| Ítem | Estado |
|---|---|
| Repo limpio en `main` | ✅ commit 220f7f5 |
| Tag v15 preservado | ✅ `v15-last-before-v16-migration` |
| `condo-v16.dev` | ✅ frappe 16.18.2 + erpnext 16.18.3 + condominium_management 0.0.1 |
| `bench migrate` en condo-v16.dev | ✅ Limpio, sin errores |
| 85 DocTypes instalados | ✅ Verificado post-install |
| 27 Custom Fields en Company | ✅ Verificado |
| 22 Roles custom | ✅ Verificados |
| `test-condominium.localhost` | ⏳ Pendiente de crear |
| Setup wizard / Company base | ⏳ Pendiente — esperar test site |
| Tests en v16 | ⏳ Pendiente — esperar test site |

---

## PRs ya mergeados en main

| PR | Descripción |
|---|---|
| #29 | ADRs y documentos rescatados de branches históricas |
| #30 | Fixture de 22 roles custom |
| #31 | Filtros explícitos para evitar contaminación de fixture export |

---

## Cómo ponerte al tanto — leer en este orden

```
1. /home/erpnext/Developer/frappe-infrastructure/.claude/CLAUDE.md  ← reglas globales del ecosistema
2. /home/erpnext/frappe-bench-v16/.claude/CLAUDE.md                 ← contexto del bench v16
3. /home/erpnext/frappe-bench-v16/apps/condominium_management/CLAUDE.md  ← este app
```

Los 3 son obligatorios antes de tocar nada.

---

## Cómo abrir Claude Code correctamente para este app

**Este app vive en bench v16. Abrir VS Code desde el directorio correcto:**

```bash
cd /home/erpnext/frappe-bench-v16/apps/condominium_management
code .
```

Verificar entorno al inicio de sesión:

```bash
cd /home/erpnext/frappe-bench-v16
which bench        # debe ser /home/erpnext/frappe-bench-v16/env/bin/bench
node --version     # debe ser v24.x
echo $VIRTUAL_ENV  # debe ser /home/erpnext/frappe-bench-v16/env
```

**Si `which bench` apunta a `/home/erpnext/frappe-bench/env/bin/bench` — STOP.**
Estás en entorno v15 heredado. Cerrar la ventana y abrir desde bench v16.

---

## Qué NO tocar

| Qué | Por qué |
|---|---|
| `admin1.dev` y sites v15 | Entorno de producción en desarrollo — no modificar BD |
| ISSUE #7 — hooks universales | `hooks.py` líneas 190-198 comentados por razón documentada. Ver `docs/development/issue7-hooks-universales-contexto.md` |
| Registro `User` en Entity Type Configuration | Decisión pendiente — no eliminar sin autorización |
| 55 registros de test en BD v15 | Limpieza pendiente con backup previo |
| `master_template_registry.last_update` | Campo volátil — puede contaminar fixtures si no se filtra |
| BD de cualquier site | Ningún `UPDATE`/`INSERT`/`DELETE` sin autorización explícita |

---

## Contexto de branches históricas

Estas branches contienen trabajo previo sin mergear. No borrar sin análisis:

- `feature/financial-management` y variantes
- `feature/committee-management-clean`
- `feature/document-generation-framework`
- `feature/community-contributions-cross-site`
- `feature/physical-spaces`, `feature/companies-module`
- `release/v1.0.0`

El estado del código en `main` es el baseline válido post-auditoría.

---

## Próximo paso recomendado

**Crear `test-condominium.localhost`** — site aislado de tests en bench v16.

El patrón es idéntico a `facturacion_mexico`:
- Un site dev: `condo-v16.dev` (ya existe)
- Un site test: `test-condominium.localhost` (pendiente)

Secuencia para crear el test site (requiere autorización explícita):

```bash
cd /home/erpnext/frappe-bench-v16

# 1. Crear site (requiere MariaDB root password — el usuario lo corre)
bench new-site test-condominium.localhost --admin-password admin

# 2. Instalar ERPNext
bench --site test-condominium.localhost install-app erpnext

# 3. Instalar la app
bench --site test-condominium.localhost install-app condominium_management

# 4. Habilitar tests
bench --site test-condominium.localhost set-config allow_tests true

# 5. Verificar
bench --site test-condominium.localhost list-apps
```

Después del test site: setup mínimo en `condo-v16.dev` (Company base) y luego tests.

---

## Comandos de trabajo frecuentes

```bash
# Desarrollo
bench --site condo-v16.dev migrate
bench --site condo-v16.dev export-fixtures --app condominium_management
bench build --app condominium_management

# Tests (una vez creado test-condominium.localhost)
bench --site test-condominium.localhost run-tests --app condominium_management

# Diagnóstico (read-only)
bench --site condo-v16.dev list-apps
bench --site condo-v16.dev mariadb --execute "SELECT ..."
bench list-sites
```
