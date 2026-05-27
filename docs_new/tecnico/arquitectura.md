# Arquitectura multi-company — condominium_management

**Validado:** 2026-05-27
**Fuente:** Diagnóstico de código ejecutado sobre la rama `feature/docs-new-workflow` + revisión de todos los DocTypes del app.

---

## Modelo operativo

| Concepto | Definición |
|---|---|
| Site | Representa una administradora |
| Company | Representa un condominio administrado |
| Relación | Una administradora gestiona múltiples condominios dentro del mismo site |

Un site ERPNext/Frappe contiene:
- Una Company con `company_type = ADMIN` (la administradora propietaria del site)
- Una o más Companies con `company_type = CONDO` (los condominios que gestiona)
- Catálogos compartidos disponibles para todas las Companies del site

La información financiera, operativa y transaccional de cada condominio se mantiene separada por Company. ERPNext garantiza separación de Plan de Cuentas y documentos contables por Company nativa.

---

## Regla principal

> Todo DocType operativo o transaccional específico de un condominio debe estar ligado a Company directa o indirectamente.

Si un DocType no tiene campo `company`, debe justificarse como:
- **Catálogo compartido** — no representa información específica de un condominio
- **Configuración global** — aplica al site completo
- **Relación indirecta segura** — el DocType padres tiene `company` y la relación es unívoca (no puede haber ambigüedad)
- **Deuda técnica** — identificado como gap, pendiente de corrección

Un DocType sin justificación explícita es un riesgo de mezcla de datos entre condominios.

---

## Clasificación de DocTypes

### DocTypes con `company` directo requerido ✅

Son el núcleo de la separación por condominio. Ningún registro puede existir sin company.

| DocType | Módulo |
|---|---|
| Property Registry | Companies |
| Condominium Information | Companies |
| Physical Space | Physical Spaces |
| Contribution Request | Community Contributions |
| Billing Cycle | Financial Management |
| Fee Structure | Financial Management |
| Property Account | Financial Management |
| Resident Account | Financial Management |
| Budget Planning | Financial Management |
| Financial Transparency Config | Financial Management |
| Premium Services Integration | Financial Management |
| KPI Definition | Dashboard Consolidado |
| Dashboard Snapshot | Dashboard Consolidado |

`Dashboard Configuration` usa `company_filter` (nombre distinto pero mismo propósito).

### DocTypes con relación indirecta a Company ⚠️

No tienen `company` directo. La separación depende de que el DocType padre esté correctamente asignado.

| DocType | Ruta indirecta | Módulo |
|---|---|---|
| Fine Management | → Property Account → company | Financial Management |
| Payment Collection | → Property Account / Billing Cycle → company | Financial Management |
| Credit Balance Management | → Property Account → company | Financial Management |
| Committee Meeting | → Physical Space → company | Committee Management |
| Assembly Management | → Physical Space → company | Committee Management |
| Committee Member | → Property Registry → company | Committee Management |
| Meeting Schedule | `committee_company` (campo no estándar) | Committee Management |

**Riesgo:** Queries y listas en la UI de ERPNext filtran por `company` directo. Los DocTypes indirectos requieren código custom para filtrar correctamente. Cualquier reporte o lista sobre estos DocTypes debe hacer el JOIN explícitamente.

**Meeting Schedule** usa `committee_company` en lugar de `company` — inconsistente con el resto del app. Debe evaluarse en tarea específica.

### DocTypes pendientes de verificación ❓

No fueron verificados completamente durante el diagnóstico. Pueden tener company directa, indirecta, o ninguna.

| DocType | Módulo | Riesgo si no tiene company |
|---|---|---|
| Committee Poll | Committee Management | Mezcla de condominios |
| Agreement Tracking | Committee Management | Mezcla de condominios |
| Community Event | Committee Management | Mezcla de condominios |
| Voting System | Committee Management | Mezcla de condominios |

### Catálogos compartidos ✅

No representan información específica de un condominio. Su uso es correcto sin campo `company`.

| DocType | Módulo |
|---|---|
| Company Type | Companies |
| Property Status Type | Companies |
| Property Usage Type | Companies |
| Acquisition Type | Companies |
| Jurisdiction Level | Companies |
| Enforcement Level | Companies |
| Compliance Requirement Type | Companies |
| Space Category | Physical Spaces |
| Component Type | Physical Spaces |
| Contribution Category | Community Contributions |
| Document Template Type | Document Generation |
| Policy Category | Document Generation |
| Entity Type Configuration | Document Generation |

### DocType cross-company por diseño ⚠️

| DocType | Detalle |
|---|---|
| Service Management Contract | Tiene `service_provider` (Company ADMIN) y `client_condominium` (Company CONDO). Representa el contrato entre administradora y condominio — cruzar companies es intencional. |

---

## Reportes y dashboards

**Operación normal:** todos los reportes financieros son por Company/condominio.
No se requieren reportes cross-company para la operación financiera diaria.

**Dashboards consolidados:** solo para monitoreo de la administradora. Muestran conteos, estados y métricas agregadas. **No mezclan saldos ni transacciones financieras como si fueran una sola entidad.**

La separación contable que garantiza ERPNext por Company no debe violarse en ningún reporte o proceso del app.

---

## Condominium Information — estado y decisión pendiente

`Condominium Information` es un DocType normal (no Single) en el módulo Companies.

**Lo que debería ser:** información operacional extendida del condominio — datos descriptivos, infraestructura, referencias geográficas — que no cabe en los custom fields de Company.

**Estado actual (2026-05-27):**

| Aspecto | Estado |
|---|---|
| `company` | Campo requerido — correcto |
| Consumido por código | Solo `module_monitor.py` (conteo de registros) |
| autoname | `None` → nombres hash (`bj34hq8a92`) — no garantiza 1 registro por Company |
| Duplicidad por Company | Sin autoname único, puede haber múltiples CI para la misma Company |
| Campos duplicados | `total_units`, `total_area`, `construction_year` existen también en Company (custom fields) |
| Navegación | Sin workspace — no aparece en menú lateral |

**Decisión pendiente:** Reparar el diseño (autoname `field:company`, eliminar duplicados, crear workspace, wiring a código) o redefinir la fuente de verdad para esos campos cuando exista un caso de uso funcional real que lo justifique.

No tomar esta decisión sin un caso de uso concreto. Hoy CI no bloquea ningún flujo operativo.

---

## Gaps conocidos

1. **Committee Management — relaciones indirectas no verificadas completamente.** Los 21 DocTypes del módulo no tienen `company` directo. Queries de lista y reportes requieren JOINs custom. Pendiente: verificar Committee Poll, Agreement Tracking, Community Event, Voting System.

2. **Meeting Schedule — `committee_company` en lugar de `company`.** Inconsistente. Evaluar si es intencional o bug de naming.

3. **Condominium Information — diseño incompleto.** Detalle en sección anterior.

4. **Document Generation — hooks universales desactivados (ISSUE #7).** Los hooks `"*"` están comentados en `hooks.py` líneas ~190-198. El módulo no detecta entidades automáticamente. Ver `docs_new/tecnico/hooks.md`.

---

## Principio de seguridad

> Ningún flujo del app debe mezclar información de condominios distintos salvo que sea un dashboard consolidado explícito y controlado.

Este principio aplica a:
- Queries de base de datos
- Reportes
- Listas en UI
- Procesos automáticos (billing, fines, collections)
- APIs

Si un proceso cruza Companies sin justificación explícita, es un bug de arquitectura.

---

## Referencias

- Diagnóstico ejecutado en sesión 2026-05-27: revisión de todos los DocTypes del app contra esta arquitectura.
- `docs_new/tecnico/fixtures.md` — Company Type IDs y custom fields sobre Company.
- `docs_new/tecnico/hooks.md` — hooks de Company y Document Generation.
- `docs_new/usuario/instalacion-y-configuracion.md` — configuración de Company como condominio.
- `docs/` — documentación previa. Revisar vigencia antes de usar; puede contener información obsoleta sobre Company Type IDs o comparaciones con `type_name` en lugar de `name`.
