# ADR-0000: Estado Real de la App — Pre-migración

**Fecha:** 2026-04-26  
**Estado:** Informativo (snapshot)  
**Autor:** Auditoría automatizada vía Claude Code

---

## Contexto

Este documento registra el estado real observado de la app `condominium_management` antes de cualquier refactorización mayor. Su propósito es establecer una línea base objetiva: qué existe, qué funciona, qué está roto y qué no debería estar.

---

## 1. Módulos declarados

`modules.txt` declara 8 módulos:

| Módulo | Directorio |
|--------|-----------|
| Companies | `companies/` |
| Document Generation | `document_generation/` |
| Community Contributions | `community_contributions/` |
| Physical Spaces | `physical_spaces/` |
| Committee Management | `committee_management/` |
| Financial Management | `financial_management/` |
| API Documentation System | `api_documentation_system/` |
| Dashboard Consolidado | `dashboard_consolidado/` |

---

## 2. DocTypes custom — inventario completo

**Total: 87 DocTypes** (todos con controller Python, ninguno con JS propio).

### Companies (23 DocTypes)
`access_point_detail`, `acquisition_type`, `company_type`, `compliance_requirement_type`, `condominium_information`, `contact_information`, `contract_service_item`, `document_template_type`, `enforcement_level`, `jurisdiction_level`, `master_data_sync_configuration`, `nearby_reference`, `operating_hours`, `policy_category`, `property_copropiedad`, `property_registry`, `property_status_type`, `property_usage_type`, `public_transport_option`, `service_information`, `service_management_contract`, `sync_data_type`, `target_company_sync`

### Committee Management (21 DocTypes)
`agreement_tracking`, `assembly_agenda`, `assembly_management`, `committee_kpi`, `committee_meeting`, `committee_member`, `committee_poll`, `community_event`, `event_activity`, `event_expense`, `event_organizer`, `event_registration`, `meeting_agenda_item`, `meeting_attendee`, `meeting_schedule`, `poll_option`, `progress_update`, `quorum_record`, `scheduled_meeting_item`, `vote_record`, `voting_system`

### Financial Management (13 DocTypes)
`billing_cycle`, `budget_planning`, `credit_balance_management`, `fee_component`, `fee_structure`, `financial_transparency_config`, `fine_management`, `payment_collection`, `premium_services_integration`, `property_account`, `property_type_filter`, `resident_account`

### Document Generation (8 DocTypes)
`configuration_field`, `conflict_detection_field`, `entity_configuration`, `entity_type_configuration`, `infrastructure_template_definition`, `master_template_registry`, `template_auto_assignment_rule`, `template_field_definition`

### Dashboard Consolidado (8 DocTypes)
`alert_channel`, `alert_configuration`, `dashboard_configuration`, `dashboard_snapshot`, `dashboard_widget_config`, `kpi_data_source`, `kpi_definition`, `module_monitor`

### API Documentation System (4 DocTypes)
`api_code_example`, `api_documentation`, `api_parameter`, `api_response_code`

### Physical Spaces (6 DocTypes)
`allowed_child_category`, `allowed_parent_category`, `component_type`, `physical_space`, `space_category`, `space_component`

### Community Contributions (3 DocTypes)
`contribution_category`, `contribution_request`, `registered_contributor_site`

---

## 3. Fixtures exportados

**Ubicación:** `condominium_management/fixtures/`  
**Total:** 13 archivos JSON — todos activos en `hooks.py`

| Archivo | Contenido |
|---------|-----------|
| `custom_field.json` | 32 custom fields en DocType `Company` (4 secciones) |
| `master_template_registry.json` | Plantillas de infraestructura |
| `policy_category.json` | 15+ categorías de políticas |
| `contribution_category.json` | 6 categorías de contribuciones |
| `compliance_requirement_type.json` | Tipos de requerimientos de cumplimiento |
| `document_template_type.json` | Tipos de plantillas de documentos |
| `jurisdiction_level.json` | 4 niveles (Municipal, Estatal, Federal, Internacional) |
| `property_status_type.json` | 6 estados de propiedad |
| `property_usage_type.json` | 5 tipos de uso |
| `acquisition_type.json` | Tipos de adquisición |
| `company_type.json` | Tipos de empresa |
| `enforcement_level.json` | 4 niveles de enforcement |
| `entity_type_configuration.json` | Configuración de tipo de entidad |

**Brecha crítica de fixtures:** 87 DocTypes existen en código, pero solo 13 fixtures cubren datos de catálogo. Los 74 DocTypes restantes no tienen fixtures. Cualquier instalación nueva queda sin datos de referencia para la mayoría de los módulos.

---

## 4. Lógica de negocio implementada

### Financial Management — núcleo funcional real

**`billing_cycle`**: Ciclos de facturación con máquina de estados (Borrador → Programado → Activo → Facturado → Completado). Genera `Sales Invoice` automáticas por propiedad. Soporta 4 métodos de cálculo: Monto Fijo, Por Indiviso (%), Por M2, Mixto.

**`fee_structure`**: Estructura de cuotas con validación de solapamiento, fondo de reserva (0-50%), descuentos pronto pago (0-20%), recargos mora (0-10%), componentes por porcentaje o monto fijo. Previene estructuras activas superpuestas.

**`property_account`**: Vincula `Property Registry` con `Customer` de ERPNext. Calcula saldo pendiente desde `Sales Invoice`, métricas YTD, retraso promedio de pagos. Crea Customer automáticamente si no existe.

**`fine_management`**: Gestión de multas con escalamiento y seguimiento de cumplimiento.

**`payment_collection`**: Registro de cobros con reconciliación.

**`credit_balance_management`**: Gestión de saldos a favor.

**`budget_planning`**: Planificación presupuestal (lógica básica, sin integración financiera ERPNext verificada).

**`resident_account`**: Cuenta de residente (relación con property_account no completamente clara en código).

**`premium_services_integration`**: Integración servicios premium (estado de implementación real desconocido sin revisar el controller).

**`financial_transparency_config`**: Configuración de transparencia (parece ser configuración, no lógica operativa).

### Committee Management — funcional

Gestión completa de reuniones, asambleas, votaciones, acuerdos y KPIs de comité. Incluye programación de reuniones y seguimiento de asistencia/quórum.

### Companies — funcional con hooks activos

`company_hooks.py` extiende el DocType `Company` de ERPNext con validaciones específicas de condominio. Tiene hooks para `after_insert`, `on_update`, `on_save`, `on_trash`.

### Physical Spaces — funcional

Jerarquía de espacios físicos con categorías, componentes y tipos. Hooks activos para validación y detección.

### Community Contributions — parcialmente implementado

API para contribuciones cross-site (`cross_site_api.py`, `contribution_manager.py`). La arquitectura multi-site (contribuyentes → domika.dev) está definida pero no verificada como funcional.

### Document Generation — hooks desactivados (ROTO)

Sistema de plantillas de documentos con auto-detección de entidades. **Los hooks universales están comentados** (ver sección 5). El sistema no detecta nuevas entidades automáticamente.

### Dashboard Consolidado — estado incierto

`api.py`, `kpi_engine.py`, `data_aggregators.py` existen. Sin revisión de si las queries funcionan con los datos reales del sistema.

### API Documentation System — meta-módulo

Sistema que auto-documenta los endpoints de la app. Incluye scanner, parser, generador de esquemas y decorador. Parece funcional como herramienta de desarrollo.

---

## 5. Dependencias

### Apps Frappe requeridas
- `erpnext` — declarado en `hooks.py` como `required_apps = ["erpnext"]`
- `frappe` — implícito (framework base)

### Dependencias Python externas
**Ninguna.** `pyproject.toml` no declara dependencias propias. El código usa exclusivamente la API de Frappe.

### Dependencias implícitas detectadas en código
- `frappe.utils` (datetime, hashing, etc.)
- `erpnext.accounts` (balance de cuentas, Sales Invoice)
- `erpnext.setup.doctype.company` (extensión vía custom fields)

---

## 6. Problemas conocidos y cosas rotas

### CRÍTICO: ISSUE #7 — Hooks universales desactivados

**Archivo:** `hooks.py` líneas 190-198  
**Estado:** Comentado intencionalmente, marcado como CRÍTICA

```python
# TEMPORALMENTE DESACTIVADOS: Los hooks universales ("*") interfieren con el setup wizard de ERPNext
# causando errores de validación de enlaces durante CI.
# ISSUE #7: Reactivar hooks universales con verificaciones de contexto
# PRIORIDAD: CRÍTICA - Debe resolverse inmediatamente después del merge
# "*": {
#     "after_insert": "...auto_detection.on_document_insert",
#     "on_update": "...auto_detection.on_document_update",
# },
```

El módulo Document Generation no puede detectar automáticamente nuevas entidades. La funcionalidad de auto-asignación de plantillas no está operativa.

### ADVERTENCIA: Versión no actualizada

`__init__.py` reporta `__version__ = "0.0.1"` a pesar de que el sistema es sustancialmente más avanzado. El CHANGELOG no está sincronizado con el estado real del código.

### ADVERTENCIA: Fixtures insuficientes

Solo 13 de los 87 DocTypes tienen cobertura de fixtures. Una instalación nueva no tendrá datos de catálogo para: todos los DocTypes de Committee Management, Financial Management, Physical Spaces, Dashboard, Community Contributions, y la mayoría de Companies.

### ADVERTENCIA: `property_type_filter` sin uso claro

DocType en Financial Management cuyo propósito en el flujo operativo no está documentado.

### ADVERTENCIA: `premium_services_integration` — implementación incierta

El nombre sugiere integración con servicios externos, pero no hay dependencias externas en el código. Podría ser un DocType de configuración con funcionalidad futura.

---

## 7. Archivos sueltos que no deberían estar

### En la raíz del repositorio (fuera del paquete Python)

**`layer4_complex_tests_backup/`** — Directorio con 14 archivos de test en la raíz del repo (`/apps/condominium_management/layer4_complex_tests_backup/`). No está dentro del paquete Python, no tiene `__init__.py`, no puede ejecutarse con `bench run-tests`. Es un directorio huérfano de backup.

### En la raíz del módulo Python (`condominium_management/`)

Los siguientes archivos son legítimos y esperados en Frappe:
- `__init__.py` ✅
- `hooks.py` ✅
- `install.py` ✅
- `modules.txt` ✅
- `patches.txt` ✅

Los siguientes son cuestionables:
- **`test_factories.py`** — Factory de datos para tests ubicada en la raíz del módulo en lugar de un directorio `tests/` o `utils/`. No es un problema funcional pero es inconsistente con la estructura de los otros módulos.
- **`utils.py`** — Contiene `before_tests()` y helpers. Mezcla setup de tests con utilities de producción.

### Directorio vacío/vestigial
- `companies/custom_fields/` — Solo tiene `__init__.py`. El contenido real (custom fields) está en `fixtures/custom_field.json`. Este directorio no tiene propósito activo.
- `config/` — Solo tiene `__init__.py`. En Frappe v15 la configuración de módulos se maneja diferente. Directorio posiblemente heredado de una versión anterior.
- `committee_management/report/` — Solo tiene `__init__.py`. No hay reports implementados.
- `templates/pages/` — Solo tiene `__init__.py`. No hay páginas web implementadas.

---

## 8. Estado de los tests

### Volumen total

El número de archivos de test es desproporcionadamente alto. Conteo aproximado por módulo:

| Módulo | Archivos test |
|--------|--------------|
| financial_management (12 doctypes × ~15 tests) | ~180 |
| committee_management | ~20 |
| community_contributions | ~5 |
| dashboard_consolidado | ~3 |
| api_documentation_system | ~2 |
| layer4_complex_tests_backup (raíz repo) | 14 |
| **Total estimado** | **~224** |

### Capas de tests (nomenclatura L1-L4)

Los tests siguen una estratificación:
- **L1**: Validación de campos
- **L2**: Lógica de negocio
- **L3**: Integración
- **L4**: Tests avanzados (database schema, field config, hooks, meta consistency, permissions, simple)

### Tests L4 Type B y C — señal de alerta

Los archivos L4 Type B incluyen nombres como:
- `test_fee_structure_l4_type_b_quantum_computing.py`
- `test_billing_cycle_l4_type_b_metaverse_integration.py`
- `test_financial_transparency_config_l4_type_b_blockchain_integration.py`
- `test_credit_balance_management_l4_type_b_ai_optimization.py`

Estos nombres no corresponden a funcionalidades reales de la app. Son archivos generados automáticamente que probablemente no prueban comportamiento real del sistema. **Representan deuda técnica de testing que infla el conteo sin agregar valor.**

### Infraestructura de tests

- `test_factories.py` en raíz del módulo: `TestDataFactory` class para crear datos de prueba
- `companies/test_utils.py`: helpers adicionales
- `hooks.py` registra `before_tests` que configura Company, roles y registros básicos
- `frappe.flags.skip_test_records = True` en `tests/__init__.py` (según audit)

---

## 9. Arquitectura multi-site (estado declarado vs verificado)

El sistema declara una arquitectura donde:
- `admin1.dev` es el site principal de desarrollo
- `condo1.dev`, `condo2.dev` son sites contribuyentes independientes
- `domika.dev` es la matriz receptora de contribuciones

La lógica de `community_contributions/api/cross_site_api.py` implementa la API para esto. **No hay evidencia en este audit de que los sites contribuyentes existan o que la sincronización esté probada.**

---

## 10. Resumen ejecutivo

| Dimensión | Estado | Notas |
|-----------|--------|-------|
| DocTypes | 87 creados | Todos con controller Python |
| Fixtures | 13/87 con cobertura | Brecha importante |
| Lógica financiera core | Implementada | BillingCycle, FeeStructure, PropertyAccount |
| Document Generation | Roto (hooks off) | ISSUE #7 pendiente |
| Tests unitarios | Exceso patológico | ~224 archivos, muchos sin valor real |
| Dependencias externas | Ninguna | Solo Frappe + ERPNext |
| Versión declarada | 0.0.1 | No refleja estado real |
| Archivos huérfanos | layer4_complex_tests_backup/ | En raíz del repo, no ejecutable |
| Directorios vestigiales | 4 directorios vacíos | custom_fields/, config/, report/, templates/pages/ |

---

## Decisiones pendientes que este audit sugiere

1. **Eliminar `layer4_complex_tests_backup/`** de la raíz del repo.
2. **Purgar tests L4 Type B con nombres ficticios** (quantum, blockchain, metaverse, AI optimization).
3. **Resolver ISSUE #7** o documentar formalmente que Document Generation no es funcional.
4. **Completar fixtures** para los módulos sin cobertura si se necesita zero-config deployment.
5. **Actualizar `__version__`** a algo que refleje el estado real.
6. **Limpiar directorios vacíos** vestigiales.
7. **Verificar `community_contributions` cross-site** en un entorno real antes de considerar esa funcionalidad como operativa.
