# ADR-0000: Estado Real de la App — Pre-migración v15→v16

**Fecha:** 2026-05-20
**Estado:** Informativo (snapshot)
**Autor:** Auditoría vía Claude Code — verificado contra filesystem y git history

---

## Contexto

Este documento registra el estado real observado de la app `condominium_management` antes de iniciar
la migración v15→v16. Establece la línea base objetiva: qué existe, qué funciona, qué está roto y
qué deuda técnica hay. Fue auditado directamente contra el código en `origin/main` commit `e0676aa`.

Ver ADR-0001 para la reconciliación de branches previa a la migración.

---

## 1. Versión y entorno

| Campo | Valor |
|-------|-------|
| Versión declarada | `0.0.1` (en `__init__.py` — no refleja el estado real) |
| Branch baseline | `origin/main` commit `e0676aa` |
| Frappe bench | v15 — `/home/erpnext/frappe-bench` |
| Frappe versión | 15.97.0 |
| ERPNext versión | 15.95.0 |
| Python | 3.12.3 |
| Sitio de desarrollo | `admin1.dev` (principal), `condo1.dev`, `condo2.dev`, `domika.dev` |

---

## 2. Módulos declarados

`modules.txt` declara 8 módulos:

| Módulo | Directorio | Estado |
|--------|-----------|--------|
| Companies | `companies/` | Funcional — hooks activos sobre `Company` de ERPNext |
| Committee Management | `committee_management/` | Funcional |
| Financial Management | `financial_management/` | Núcleo implementado |
| Document Generation | `document_generation/` | Hooks desactivados — ISSUE #7 |
| Physical Spaces | `physical_spaces/` | Funcional |
| Community Contributions | `community_contributions/` | Declarado, no verificado en entorno real |
| API Documentation System | `api_documentation_system/` | Meta-módulo funcional |
| Dashboard Consolidado | `dashboard_consolidado/` | Estado incierto |

---

## 3. DocTypes custom — inventario

**Total: 87 DocTypes** — todos con controller Python, ninguno con JS propio de DocType.

### Por módulo

| Módulo | Cantidad | DocTypes |
|--------|---------|---------|
| Companies | 23 | `access_point_detail`, `acquisition_type`, `company_type`, `compliance_requirement_type`, `condominium_information`, `contact_information`, `contract_service_item`, `document_template_type`, `enforcement_level`, `jurisdiction_level`, `master_data_sync_configuration`, `nearby_reference`, `operating_hours`, `policy_category`, `property_copropiedad`, `property_registry`, `property_status_type`, `property_usage_type`, `public_transport_option`, `service_information`, `service_management_contract`, `sync_data_type`, `target_company_sync` |
| Committee Management | 21 | `agreement_tracking`, `assembly_agenda`, `assembly_management`, `committee_kpi`, `committee_meeting`, `committee_member`, `committee_poll`, `community_event`, `event_activity`, `event_expense`, `event_organizer`, `event_registration`, `meeting_agenda_item`, `meeting_attendee`, `meeting_schedule`, `poll_option`, `progress_update`, `quorum_record`, `scheduled_meeting_item`, `vote_record`, `voting_system` |
| Financial Management | 13 | `billing_cycle`, `budget_planning`, `credit_balance_management`, `fee_component`, `fee_structure`, `financial_transparency_config`, `fine_management`, `payment_collection`, `premium_services_integration`, `property_account`, `property_type_filter`, `resident_account` |
| Document Generation | 8 | `configuration_field`, `conflict_detection_field`, `entity_configuration`, `entity_type_configuration`, `infrastructure_template_definition`, `master_template_registry`, `template_auto_assignment_rule`, `template_field_definition` |
| Dashboard Consolidado | 8 | `alert_channel`, `alert_configuration`, `dashboard_configuration`, `dashboard_snapshot`, `dashboard_widget_config`, `kpi_data_source`, `kpi_definition`, `module_monitor` |
| API Documentation System | 4 | `api_code_example`, `api_documentation`, `api_parameter`, `api_response_code` |
| Physical Spaces | 6 | `allowed_child_category`, `allowed_parent_category`, `component_type`, `physical_space`, `space_category`, `space_component` |
| Community Contributions | 3 | `contribution_category`, `contribution_request`, `registered_contributor_site` |

---

## 4. Fixtures exportados

**Total: 13 archivos JSON** — todos activos en `hooks.py`.

| Fixture | Contenido |
|---------|-----------|
| `custom_field.json` | 32 custom fields sobre DocType `Company` de ERPNext |
| `master_template_registry.json` | Plantillas de infraestructura |
| `policy_category.json` | 15+ categorías |
| `contribution_category.json` | 6 categorías |
| `compliance_requirement_type.json` | Tipos de requerimientos |
| `document_template_type.json` | Tipos de plantillas |
| `jurisdiction_level.json` | 4 niveles |
| `property_status_type.json` | 6 estados |
| `property_usage_type.json` | 5 tipos |
| `acquisition_type.json` | Tipos de adquisición |
| `company_type.json` | Tipos de empresa |
| `enforcement_level.json` | 4 niveles |
| `entity_type_configuration.json` | Configuración de entidad |

**Brecha:** 74 de 87 DocTypes no tienen fixture. Instalación nueva queda sin datos de referencia
para la mayoría de módulos.

---

## 5. Dependencias

- **Frappe apps requeridas:** `erpnext` (declarado en `hooks.py`)
- **Dependencias Python externas:** Ninguna — código puro Frappe
- **Import directo de erpnext detectado:** `from erpnext.setup.utils import enable_all_roles_and_domains` en `utils.py:45` — potencial bloqueante en v16

---

## 6. Lógica de negocio implementada

### Financial Management — núcleo funcional real

- **`billing_cycle`:** Máquina de estados, generación de `Sales Invoice` automática por propiedad. 4 métodos: Monto Fijo, Por Indiviso (%), Por M2, Mixto.
- **`fee_structure`:** Estructura de cuotas con validación de solapamiento, fondo de reserva (0-50%), descuentos y recargos.
- **`property_account`:** Vincula `Property Registry` con `Customer` de ERPNext. Calcula saldo pendiente desde facturas activas.
- **`fine_management`:** Multas con escalamiento.
- **`payment_collection`:** Registro de cobros.

### Committee Management — funcional

Gestión completa de reuniones, asambleas, votaciones, KPIs y eventos comunitarios.

### Companies — funcional con hooks activos

`company_hooks.py` extiende `Company` de ERPNext con validaciones de condominio.
32 custom fields distribuidos en 4 secciones.

### Document Generation — hooks desactivados (ISSUE #7)

Framework implementado pero auto-detección de entidades no operativa. Ver sección de problemas.

### Physical Spaces — funcional

Jerarquía de espacios con categorías, componentes y tipos.

### Community Contributions — no verificado en entorno real

API cross-site definida pero arquitectura multi-site no validada operativamente.

---

## 7. Problemas críticos conocidos

### ISSUE #7 — Hooks universales de Document Generation desactivados (CRÍTICO)

**Archivo:** `hooks.py` líneas ~190-198

```python
# TEMPORALMENTE DESACTIVADOS: Interfieren con setup wizard de ERPNext
# ISSUE #7: Reactivar con verificaciones de contexto
# PRIORIDAD: CRÍTICA
# "*": {
#     "after_insert": "...auto_detection.on_document_insert",
#     "on_update": "...auto_detection.on_document_update",
# },
```

El módulo Document Generation no puede detectar automáticamente nuevas entidades.
Contexto técnico completo: `docs/development/issue7-hooks-universales-contexto.md`

### 22 roles custom sin fixture (BLOQUEANTE para v16)

Los DocTypes referencian 22 roles custom en sus permisos, pero **no existe fixture de Roles**.
Existen en `admin1.dev` pero no en código. Instalación limpia (incluyendo v16) queda con permisos rotos.

Roles afectados:
```
Administrador Financiero, Administrator Condominio, API Manager, API User,
Assembly Participant, Comité Administración, Committee Member, Committee President,
Committee Secretary, Company Administrator, Condominium Manager, Condómino,
Configuration Approver, Configuration Manager, Contador Condominio, Event Organizer,
Gestor de Dashboards, Master Template Manager, Property Administrator,
Property Manager, Residente Propietario, Usuario de Dashboards
```

Documentación del hallazgo: `docs/audit/hallazgo-roles-sin-fixture.md`

### CI desactivado

`ci.yml` renombrado a `ci.yml.disabled` en commit `3a9f2cc`. No hay gate de validación automática.
Se reactivará con configuración v16 como parte de la migración.

### Import de módulo interno de ERPNext

`utils.py:45`: `from erpnext.setup.utils import enable_all_roles_and_domains`
Debe verificarse que esta función existe en ERPNext v16 antes de instalar.

### Brecha de fixtures (74 DocTypes sin cobertura)

Una instalación nueva no tendrá datos de catálogo para la mayoría de módulos.
Solo 13 de 87 DocTypes tienen fixture.

---

## 8. Deuda técnica de tests

- **~224 archivos de test estimados** distribuidos en los módulos.
- Tests **L4 Type B con nombres ficticios** que no prueban funcionalidad real:
  `test_fee_structure_l4_type_b_quantum_computing.py`,
  `test_billing_cycle_l4_type_b_metaverse_integration.py`,
  `test_financial_transparency_config_l4_type_b_blockchain_integration.py`, etc.
- **`layer4_complex_tests_backup/`** en raíz del repo — directorio huérfano no ejecutable con bench.
- Tests L1–L3 y L4 básicos sí prueban funcionalidad real.

---

## 9. Archivos y directorios anómalos

| Elemento | Ubicación | Problema |
|----------|-----------|---------|
| `layer4_complex_tests_backup/` | Raíz del repo | Directorio huérfano, no ejecutable |
| `companies/custom_fields/` | Módulo companies | Solo `__init__.py`, sin contenido |
| `config/` | Módulo raíz | Solo `__init__.py`, vestigial |
| `committee_management/report/` | Módulo committee | Solo `__init__.py`, sin reports |
| `templates/pages/` | Módulo raíz | Solo `__init__.py`, sin páginas |
| `test_factories.py` | Raíz del módulo Python | Debería estar en `tests/` |

---

## 10. Arquitectura multi-site (estado declarado vs verificado)

- `admin1.dev` — site principal de desarrollo
- `condo1.dev`, `condo2.dev` — sites contribuyentes
- `domika.dev` — matriz receptora

La API cross-site existe en código (`community_contributions/api/cross_site_api.py`) pero
**no está verificada como funcional en entorno real**. Validación operativa de oct-2025 confirmó
sistema operacional con 9 hallazgos; ver `docs/audit/reporte-ux-testing-2025-10-27.md`.

---

## 11. Branches — estado post-reconciliación

Ver ADR-0001 para el análisis completo. Resumen:

- **Baseline:** `origin/main` commit `e0676aa` — código consolidado completo
- **Historia reescrita:** commit `3d2c046` es grafted (filter-branch rewrite)
- **Conservadas con historia:** `feature/financial-management` (73 commits), `feature/committee-management-clean` (48 commits)
- **Autorizadas para eliminar:** 8 branches — ver ADR-0001

---

## 12. Resumen ejecutivo

| Dimensión | Estado |
|-----------|--------|
| DocTypes | 87 — todos con controller Python |
| Fixtures | 13/87 — brecha importante |
| Lógica financiera core | Implementada (BillingCycle, FeeStructure, PropertyAccount) |
| Document Generation | Roto — hooks ISSUE #7 |
| CI | Desactivado — se reescribe para v16 |
| Tests | ~224 archivos — muchos ficticios, deuda técnica alta |
| Roles | 22 roles sin fixture — BLOQUEANTE para v16 |
| Dependencias externas | Ninguna — solo Frappe + ERPNext |
| Import erpnext directo | 1 — `enable_all_roles_and_domains` en `utils.py` |
| Versión declarada | 0.0.1 — no refleja estado real |
