# CLAUDE.md — condominium_management

## Estado de migración
- **Migrada a v16:** Sí — `condo-v16.dev` instalado y migrate limpio (2026-05-22)
- **Versión origen:** v15 (Frappe 15.97, ERPNext 15.95)
- **En producción:** No — en desarrollo activo
- **Branch activo:** main
- **Versión:** 0.0.1

## Sites

### v16 (activos)

| Site | Propósito | Estado |
|---|---|---|
| `condo-v16.dev` | Desarrollo activo v16 | ✅ Instalado — frappe 16.18.2 + erpnext 16.18.3 + condominium_management 0.0.1 |
| `test-condominium.localhost` | Tests unitarios aislados | ⏳ Pendiente de crear |

### v15 (referencia histórica — no tocar sin autorización)

| Site | Rol original |
|---|---|
| `admin1.dev` | Matriz — site principal de desarrollo v15 |
| `condo1.dev`, `condo2.dev` | Sites contribuyentes multi-site |
| `domika.dev` | Matriz receptora multi-site |

**Estos sites están en bench v15 (`/home/erpnext/frappe-bench`). No ejecutar comandos v16 sobre ellos.**

## Entorno
Ver contexto global en `frappe-infrastructure/.claude/CLAUDE.md`.

**Bench:** /home/erpnext/frappe-bench-v16
**Comandos siempre con --site:**
```bash
bench --site condo-v16.dev migrate
bench --site condo-v16.dev export-fixtures --app condominium_management
bench --site test-condominium.localhost run-tests --app condominium_management
bench build --app condominium_management
```
**NUNCA:** `bench migrate` sin --site (afecta otros sitios del bench compartido)

## Regla de base de datos

**Ningún comando que modifique BD sin autorización explícita y backup previo.**

Esto incluye sin excepción:
- `frappe.db.set_value`, `frappe.db.sql`, `frappe.db.delete`
- `bench mariadb --execute` con `UPDATE`, `INSERT`, `DELETE`
- Ejecución manual de patches de datos

Aplica tanto en `condo-v16.dev` como en cualquier site v15.

---

## Qué hace esta app

Sistema de administración de condominios sobre ERPNext. Gestiona propiedades, finanzas (cuotas, facturación automática, multas), espacios físicos, comités, asambleas y contribuciones entre sitios (arquitectura multi-site).

---

## Módulos y DocTypes principales

**85 DocTypes** distribuidos en 8 módulos (conteo real post-instalación v16):

| Módulo | DocTypes | Estado |
|---|---|---|
| Companies | 23 | ✅ Funcional — extiende Company de ERPNext |
| Committee Management | 21 | ✅ Funcional — reuniones, asambleas, votaciones |
| Financial Management | 12 | ✅ Núcleo funcional implementado |
| Document Generation | 8 | ❌ Hooks desactivados — ISSUE #7 |
| Dashboard Consolidado | 8 | ⚠️ Estado incierto |
| Physical Spaces | 6 | ✅ Funcional |
| Community Contributions | 3 | ⚠️ No verificado en entorno real |
| API Documentation System | 4 | ✅ Meta-módulo funcional |

### DocTypes críticos de Financial Management

| DocType | Qué hace |
|---|---|
| `billing_cycle` | Ciclos de facturación con máquina de estados. Genera Sales Invoice automáticas por propiedad. Soporta 4 métodos: Monto Fijo, Por Indiviso (%), Por M2, Mixto. |
| `fee_structure` | Estructura de cuotas con validación de solapamiento, fondo de reserva, descuentos y recargos. |
| `property_account` | Vincula Property Registry con Customer de ERPNext. Calcula saldo pendiente y métricas YTD. |
| `fine_management` | Gestión de multas con escalamiento. |
| `payment_collection` | Registro de cobros con reconciliación. |

---

## Lógica crítica

### Hooks activos en Companies
`company_hooks.py` extiende el DocType `Company` de ERPNext con validaciones de condominio. Hooks: `after_insert`, `on_update`, `on_save`, `on_trash`.

### Custom Fields sobre ERPNext
27 custom fields en DocType `Company` (4 secciones). Ver `fixtures/custom_field.json`.

### Arquitectura multi-site (Community Contributions)
- `admin1.dev` — site principal de desarrollo v15
- `condo1.dev`, `condo2.dev` — sites contribuyentes
- `domika.dev` — matriz receptora
- API en `community_contributions/api/cross_site_api.py`
- **Estado:** declarado en código pero NO verificado como funcional en entorno real

---

## Problemas críticos conocidos

1. **ISSUE #7 — Hooks universales desactivados** en `hooks.py` líneas 190-198. Los hooks `"*"` de Document Generation están comentados porque interferían con el setup wizard de ERPNext en CI. El módulo Document Generation no detecta entidades automáticamente. **Pendiente de resolución. No reactivar sin análisis.**

2. **Brecha de fixtures:** Solo 13 de 85 DocTypes tienen fixtures. Una instalación nueva no tendrá datos de referencia para la mayoría de los módulos.

3. **Tests L4 Type B con nombres ficticios:** Archivos como `test_fee_structure_l4_type_b_quantum_computing.py`, `test_billing_cycle_l4_type_b_metaverse_integration.py`. No prueban funcionalidad real — deuda técnica de testing.

4. **`layer4_complex_tests_backup/`** en raíz del repo — directorio huérfano, no ejecutable con bench.

5. **Directorios vestigiales vacíos:** `companies/custom_fields/`, `config/`, `committee_management/report/`, `templates/pages/`.

6. **User en Entity Type Configuration** — registro `User` presente en fixture de entidades. Pendiente decisión: conservar o eliminar. No tocar sin autorización.

7. **55 registros de test en BD v15** — en `admin1.dev`, pendientes de limpieza. No limpiar sin autorización explícita y backup previo.

8. **`master_template_registry.last_update` volátil** — campo que cambia con cada operación, puede contaminar fixture export si no se filtra.

---

## Dependencias

**Apps de Frappe requeridas:** erpnext (declarado en `required_apps`)
**Dependencias externas:** Ninguna — solo Frappe + ERPNext API
**Apps en el mismo bench v16:** facturacion_mexico, llantascs_customs, facturacion_mx, dfp_external_storage, hrms, payments, wiki, erpnext_proposals

---

## Fixtures

13 archivos en `condominium_management/fixtures/`, todos activos en `hooks.py`:
- `custom_field.json` — 27 custom fields en Company
- `role.json` — 22 roles custom
- Catálogos: policy_category, contribution_category, compliance_requirement_type, document_template_type, jurisdiction_level, property_status_type, property_usage_type, acquisition_type, company_type, enforcement_level, entity_type_configuration, master_template_registry

**72 DocTypes sin fixtures** — instalación nueva queda sin datos de referencia para la mayoría de módulos.

---

## Tests

```bash
bench --site test-condominium.localhost run-tests --app condominium_management
pytest apps/condominium_management/ -v --tb=short
```

**Site de tests:** `test-condominium.localhost` (pendiente de crear — ver CONTINUITY.md)

~224 archivos de test estimados. Muchos L4 Type B son ficticios y no prueban funcionalidad real. Tests reales en módulos individuales bajo `[modulo]/tests/`.

---

## Branches abiertas (trabajo previo sin mergear)

| Branch | Estado |
|---|---|
| feature/financial-management | Sin mergear |
| feature/financial-management-clean | Sin mergear |
| feature/financial-management-reconstruction | Sin mergear |
| feature/committee-management-clean | Sin mergear |
| feature/document-generation-framework | Sin mergear |
| feature/community-contributions-cross-site | Sin mergear |
| feature/physical-spaces | Sin mergear |
| feature/companies-module | Sin mergear |
| emergency/reset-to-48ea382 | Branch de emergencia |
| release/v1.0.0 | Sin mergear |

---

## Antes de cada PR

- [ ] Tests pasan en test-condominium.localhost
- [ ] Fixtures exportados si hubo cambios de Custom Fields, Roles, DocPerms
- [ ] Patch creado si hay cambios de esquema con datos
- [ ] `bench --site condo-v16.dev migrate` limpio
- [ ] Ver checklist global en `frappe-infrastructure/CONTRIBUTING.md`

---

## Auditoría pre-migración

Ver `docs/adr/0000-estado-real-pre-migracion.md` para el estado completo documentado el 2026-04-26.
