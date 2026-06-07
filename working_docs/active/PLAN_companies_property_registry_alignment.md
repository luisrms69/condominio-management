# Plan de Corrección — Companies / Property Registry
## Aislamiento multi-condominio · Unidad canónica · Physical Spaces

| Campo | Valor |
|---|---|
| **Estado** | Fase 1 + Fase 2A implementadas (2026-06-05) · Sin commit |
| **Fecha** | 2026-06-05 |
| **Contexto** | Resultado del reporte de auditoría (2026-06-05) |
| **Fuentes de verdad** | `frappe-infrastructure/projects/domika/arquitectura-producto-alcance.md v2.0` + `decisiones-tecnicas-frappe.md v1.0` |

> **Regla:** Este plan corrige desviaciones del código respecto a la arquitectura. No inventa entidades nuevas. No toca Financial Management. No implementa el vínculo Unidad↔Customer.

---

## Diagnóstico verificado

Antes de cada fase, los hechos comprobados en código y BD:

### Custom Fields de Company
- La BD tiene **27 Custom Fields sobre `Company`**.
- `hooks.py` ya los declara en `fixtures` con filtro explícito por fieldname (4 secciones: Condominio, Administración, Legal, Financiero).
- `fixtures/custom_field.json` contiene solo 56 registros de `Event`. **Cero de Company.**
- Causa probable: re-exportación parcial en algún punto sobreescribió el archivo con solo Event.
- El filtro en `hooks.py` es correcto. El archivo exportado está desincronizado.

**Los 27 campos verificados en BD:**

| Sección | Campos | Referencias en código |
|---|---|---|
| Condominio (10) | `condominium_section`, `company_type`, `property_usage_type`, `acquisition_type`, `property_status_type`, `cb_condominium_1`, `total_units`, `total_area_sqm`, `construction_year`, `floors_count` | Alta (company_type: 58, acquisition_type: 32, total_units: 21) |
| Administración (5) | `management_section`, `management_company`, `management_start_date`, `management_contract_end_date`, `managed_properties` | Alta (management_company: 14) |
| Legal (6) | `legal_section`, `legal_representative`, `legal_representative_id`, `cb_legal_1`, `registration_chamber_commerce`, `registration_date` | Media |
| Financiero (6) | `financial_section`, `monthly_admin_fee`, `reserve_fund`, `cb_financial_1`, `insurance_policy_number`, `insurance_expiry_date` | Alta (reserve_fund: 38, monthly_admin_fee: 4) |

**Nota sobre terminología:** `legal_representative_id` tiene label "Cédula Representante Legal" — terminología colombiana. No bloquea la corrección pero debe revisarse en un sprint posterior para usar "RFC / CURP" consistente con el resto del app.

**Todos los campos tienen al menos 1 referencia en código. Ninguno es candidato obvio a eliminación por esta sola auditoría.**

### Property Registry
- 2 registros en el site actual.
- **1 registro sin `physical_space`** (campo vacío).
- Aplicar `reqd: 1` sin migración previa bloquea el save de ese registro.

### Property Copropiedad
- DocType activo con `istable: 1`.
- **Cero referencias** fuera de sus propios archivos y el patch de migración.
- Patch `migrate_property_copropiedad_to_declared_owner.py` ya corrió.
- No hay riesgo de romper módulos al congelarlo.

### Permisos Physical Space
- Solo `System Manager`. Ningún rol administrativo puede gestionar espacios físicos.
- Roles existentes en fixtures relevantes: `Property Administrator`, `Property Manager`, `Condominium Manager`, `Administrator Condominio`.

---

## FASE 1 — Restaurar migrabilidad (fixtures de Company)

### Objetivo
Que `bench migrate` en cualquier instalación limpia produzca los mismos 27 campos sobre Company que tiene el site actual.

### Por qué es urgente
El app completo depende de `company_type`, `management_company`, `reserve_fund`, etc. Sin los campos en fixtures, toda instalación nueva (CI, staging, cliente) carece de ellos. Los errores son silenciosos porque `company_hooks.py` usa `hasattr(doc, "company_type")` como guard.

### Acciones

**A1 — Re-exportar fixtures incluyendo Company.**
El filtro ya está correcto en `hooks.py`. Solo hay que ejecutar la exportación:
```bash
bench --site condo-v16.dev export-fixtures --app condominium_management
```
Verificar que `custom_field.json` tenga registros con `"dt": "Company"` (deben ser 27) y con `"dt": "Event"` (deben ser 56).

**A2 — Verificar integridad post-exportación.**
Confirmar que ningún campo de Company quedó fuera del filtro de hooks.py. El filtro actual es explícito por nombre de campo — si algún campo nuevo fue agregado a la BD pero no al filtro, no se exporta. Comparar:
```python
# Campos en BD: bench execute "frappe.get_all('Custom Field', {'dt': 'Company'}, ['fieldname'])"
# Campos en filtro hooks.py: los 27 listados explícitamente
# Delta: cualquier campo en BD que no esté en el filtro
```

**A3 — Revisar `master_template_registry.json` después de la exportación.**
El campo `last_update` de este DocType es volátil (cambia en cada operación). Si la exportación lo modifica, revertirlo al valor anterior antes de commitear.

### Archivos a tocar
- `condominium_management/fixtures/custom_field.json` — re-exportación (no edición manual)
- Posible: `condominium_management/fixtures/master_template_registry.json` — revertir si `last_update` cambió

### Riesgo
**Bajo.** La exportación no modifica BD. El único riesgo es sobreescribir accidentalmente `master_template_registry.json` con timestamp nuevo.

### Tests requeridos
- Test que verifique que los campos críticos existen en `tabCompany` post-migrate: `company_type`, `management_company`, `reserve_fund`, `monthly_admin_fee`.
- El test falla en CI si el fixture no tiene los campos. No es un "test que falla intencionalmente" — es una verificación de instalación limpia que debe pasar.

### Impacto en módulos dependientes
Sin esta fase, cualquier módulo que lea `doc.company_type`, `doc.reserve_fund`, etc. falla silenciosamente en instalación nueva. Bloquea CI confiable para todo el app.

### Decisión del dueño
Ninguna. Corrección técnica sin ambigüedad.

---

## FASE 2 — Sanear unidad canónica

### 2A — `physical_space` obligatorio en Property Registry

#### Objetivo
Que no pueda existir una unidad registral sin anclarla a su espacio físico.

#### Por qué
La arquitectura rectora define: *"Registro de unidades depende de: Espacios físicos"* y *"Todo se ancla a lugar / unidad / persona"*. Sin este campo obligatorio, los módulos de mantenimiento, control de acceso, reserva de amenidades y comunicación no pueden asumir que toda unidad tiene ubicación física.

#### Verificación previa obligatoria
En el site actual hay **1 registro sin `physical_space`**. Antes de activar `reqd: 1`, ese registro debe resolverse:
```sql
-- Identificar el registro:
SELECT name, property_name FROM `tabProperty Registry`
WHERE physical_space IS NULL OR physical_space = '';
```
Opciones: asignarle un Physical Space existente, o eliminarlo si es un registro de prueba.

#### Acciones

**B1 — Activar `reqd: 1` en `property_registry.json`** para el campo `physical_space`.

**B2 — Agregar validación en `property_registry.py`** que verifique que `physical_space.company == property_registry.company`. Una unidad no puede pertenecer a un espacio de otro condominio.

**B3 — Sobre `unique` en `physical_space`:** NO se aplica en esta fase. Casos como bodegas (B-01), cajones de estacionamiento (E-23) o unidades accesorias pueden requerir múltiples expedientes para un mismo espacio físico, o espacios físicos que no correspondan 1:1 con unidades registrales. La decisión de `unique` requiere análisis del modelo condominial completo antes de restringirlo.

#### Archivos a tocar
- `condominium_management/companies/doctype/property_registry/property_registry.json`
- `condominium_management/companies/doctype/property_registry/property_registry.py`

#### Riesgo
**Medio.** El único riesgo es el registro actual sin `physical_space`. Resolviendo ese registro previo a la implementación, el riesgo desaparece.

#### Tests requeridos
- Test que verifique que no se puede crear `Property Registry` sin `physical_space`.
- Test que verifique que `physical_space.company` debe coincidir con `property_registry.company`.

#### Impacto en módulos dependientes
Protege a todos los módulos que dependen de la ruta "lugar → unidad → persona". PUA (Personas), Financial Management, Mantenimiento, Accesos y Portal pueden asumir que toda unidad tiene espacio físico.

#### Decisión del dueño
¿El registro actual sin `physical_space` es un registro de prueba (eliminar) o un registro real que debe asignarse a un Physical Space?

---

### 2B — Congelar `Property Copropiedad`

#### Objetivo
Eliminar ambigüedad sobre qué child table representa titularidad. Que ningún módulo futuro use `Property Copropiedad` por error.

#### Estado confirmado
- `Property Copropiedad` no tiene referencias fuera de sus propios archivos y el patch de migración.
- El patch ya corrió. Los datos migrados viven en `Property Declared Owner`.
- `Property Registry` usa `declared_owners → Property Declared Owner`. `Property Copropiedad` es un DocType huérfano activo.

#### Acciones

**C1 — Agregar campo `description` en `property_copropiedad.json`** con texto explícito:
```
DEPRECATED — usar Property Declared Owner. Este DocType se mantiene solo para 
compatibilidad con el patch de migración. No usar en nuevos módulos o referencias.
```

**C2 — No eliminar el DocType en esta fase.** La tabla puede tener datos en instalaciones v15 que no han corrido el patch. Eliminar el DocType y la tabla borraría esos datos. El congelamiento documental es suficiente para esta fase.

**C3 — Mantener `test_property_copropiedad.py`** como evidencia del estado migrado. No eliminarlo — sirve para verificar que la migración funcionó.

#### Archivos a tocar
- `condominium_management/companies/doctype/property_copropiedad/property_copropiedad.json` — campo `description`

#### Riesgo
**Bajo.** Solo cambio documental en el JSON.

#### Tests requeridos
Ninguno adicional. Los tests existentes documentan el estado correcto.

#### Decisión del dueño
Ninguna — congelamiento documental sin riesgo.

---

## FASE 3 — Permisos de Physical Space y Condominium Information

### Objetivo
Que los roles administrativos puedan gestionar los DocTypes base del condominio sin acceso de System Manager.

### 3A — Physical Space

**Estado:** Solo `System Manager`. Un administrador del condominio no puede modelar su espacio físico.

**Permisos propuestos** (solo roles existentes en fixtures):

| Rol | Read | Write | Create | Delete |
|---|---|---|---|---|
| System Manager | ✓ | ✓ | ✓ | ✓ |
| Property Administrator | ✓ | ✓ | ✓ | — |
| Property Manager | ✓ | — | — | — |
| Condominium Manager | ✓ | ✓ | ✓ | — |

**Justificación:** `Property Administrator` gestiona el inventario de unidades y espacios. `Property Manager` solo consulta. `Condominium Manager` administra el condominio en general. `Administrator Condominio` no se agrega aquí — tiene rol más amplio que puede cubrirse a través de `Condominium Manager`.

### 3B — Condominium Information

**Estado:** Solo `System Manager` y `Company Administrator`. Falta `Property Administrator`.

**Permisos a agregar:**

| Rol | Read | Write | Create | Delete |
|---|---|---|---|---|
| Property Administrator | ✓ | ✓ | ✓ | — |

### 3C — User Permissions (diferido)

User Permissions por Company es la barrera de aislamiento real. En Frappe v16, se implementan como registros en `tabUser Permission` (el campo `apply_user_permissions` por rol fue eliminado). Su implementación está diferida al PR del portal (Fase 3 de PUA), que es cuando los condóminos necesitan visibilidad restringida a sus propiedades.

**Lo que este plan NO hace:** crear ni activar User Permissions automáticas.

**Lo que sí hace:** documentar en `CLAUDE.md` del módulo que el aislamiento real por Company requiere User Permissions y que esto se activa junto con el portal.

### 3D — Service Management Contract (decisión separada)

**No bloquea esta fase.** La pregunta "¿es Nivel 1/2 o DocType operativo?" es una decisión arquitectónica independiente que no afecta Fase 1 ni Fase 2.

Si es Nivel 1/2 (relación Domika↔Condominio): `client_condominium` es correcto y no debe cambiarse.
Si es operativo del condominio: debe seguir la convención `company`.

Esta decisión queda como pregunta abierta al dueño, sin bloquear las demás fases.

### Archivos a tocar
- `condominium_management/physical_spaces/doctype/physical_space/physical_space.json`
- `condominium_management/companies/doctype/condominium_information/condominium_information.json`
- `CLAUDE.md` del módulo — nota sobre User Permissions diferidas

### Riesgo
**Bajo.** Agregar permisos amplía visibilidad. No rompe datos. Verificar que los roles agregados no tengan otras restricciones que invaliden el acceso esperado.

### Decisión del dueño
¿`Service Management Contract` es DocType de Nivel 1/2 (Domika↔Condominio) o DocType operativo del condominio?

---

## FASE 4 — Clasificar catálogos (sin cambio de modelo)

### Objetivo
Documentar la política de catálogos para que futuras decisiones sean consistentes. No modificar ningún catálogo ahora.

### Propuesta de clasificación

| Catálogo | Tipo propuesto | Justificación |
|---|---|---|
| `Company Type` | **HQ** | Tipos de empresa son universales |
| `Property Status Type` | **HQ** | Estados de propiedad son universales |
| `Property Usage Type` | **HQ** | Tipos de uso son universales |
| `Acquisition Type` | **HQ** | Tipos de adquisición son universales |
| `Enforcement Level` | **HQ** | Niveles de enforcement son universales |
| `Jurisdiction Level` | **HQ** | Niveles jurisdiccionales son universales |
| `Compliance Requirement Type` | **HQ** | Tipos de requisito legal son universales |
| `Document Template Type` | **HQ** | Tipos de documento son universales |
| `Policy Category` | **HQ con extensión local posible** | 19 categorías estándar; un condominio puede necesitar categorías propias en el futuro |
| `Space Category` | **HQ con extensión local posible** | 51 categorías; escala grande sugiere posible personalización |

**Regla propuesta (para aprobación del dueño):**
> Los catálogos sin campo `company` son maestros HQ. Se instalan via fixtures. La instalación puede agregar registros locales pero no elimina los de HQ. Si un condominio necesita variantes propias en el futuro, el catálogo migra a un modelo con campo `company` opcional (global = sin company, local = con company).

### Acción
Agregar comentario en `hooks.py` junto a cada fixture declarando su tipo. No modificar ningún doctype ni fixture.

### Decisión del dueño
¿Se aprueba la regla "HQ vs extensión local posible" como política del app para catálogos?

---

## FASE 5 — Protección de módulos dependientes

### Qué protege este plan (sin implementar nada extra)

| Módulo | Lo que protege | Fase que lo entrega |
|---|---|---|
| Personas del condominio (PUA) | `property_registry` con `company` y `physical_space` | Fase 2A |
| Gestión financiera | Unidad canónica con `indiviso_percentage` anclada a espacio físico | Fase 2A |
| Votación | `indiviso_percentage` confiable en unidad registral | Ya existe |
| Mantenimiento | `physical_space` referenciable desde la unidad | Fase 2A |
| Control de acceso | Cadena `physical_space → property_registry → persona` | Fase 2A + PUA |
| Comunicación | Ruta personas → unidad verificable | Fase 2A + PUA |
| Portal | User Permissions por Company | Diferido (Fase 3 de PUA) |

### Lo que NO se implementa aquí

**Vínculo Unidad↔Customer:** La arquitectura rectora define "unidad propia canónica + Customer auxiliar". `Property Account` en Financial Management ya tiene ese vínculo. `Property Registry` NO debe agregar un campo `customer` directo. El vínculo pertenece al módulo de cobranza. Financial Management está congelado. No tocar.

---

## Decisiones del dueño

| # | Decisión | Estado | Bloquea |
|---|---|---|---|
| D1 | ¿El registro sin `physical_space` es dato de prueba? | ⚠️ Pendiente confirmación — identificado como `PROP-2026-00004` "Demo Apt 202", creado por Administrator el 2026-05-28, `physical_space: null`. Apariencia de demo. | Fase 2A |
| D2 | `Service Management Contract` es Nivel 1/2 Domika↔Condominio | ✅ Aprobado | — |
| D3 | Regla "HQ vs extensión local posible" para catálogos | ✅ Aprobado | — |

---

## Qué queda bloqueado hasta cerrar este plan

1. **CI confiable** — hasta Fase 1, cualquier instalación limpia no tiene los campos de Company. Los tests pasan parcialmente.
2. **Onboarding operativo** — no puede diseñarse el flujo "espacios → unidades → personas" si `physical_space` no es obligatorio (Fase 2A).
3. **Módulo Personas (PUA)** — la columna vertebral queda incompleta sin la corrección de Fase 2A.
4. **Cualquier informe que filtre por espacio físico** — si hay unidades sin `physical_space`, los informes tienen huecos.

---

## Fase 1 — Completada (2026-06-05)

**Causa raíz confirmada:** Frappe v16 sobreescribe el archivo de fixture cuando hay múltiples entradas para el mismo DocType. La segunda entrada (Event) sobreescribía la primera (Company). Solución: agregar `"prefix": "companies"` a la entrada de Company.

**Lo que se hizo:**
1. Identificado el bug de sobreescritura en `export-fixtures` de Frappe.
2. Agregado `"prefix": "companies"` en `hooks.py` para la entrada de Company.
3. Re-exportado fixtures: ahora hay dos archivos separados:
   - `companies_custom_field.json` — 27 Custom Fields sobre Company
   - `custom_field.json` — 74 Custom Fields sobre Event
4. `master_template_registry.json` revertido (solo cambió `last_update`, campo volátil).
5. Agregado `test_install.py` en `companies/` — verifica 6 campos críticos post-migrate.

**Archivos modificados (sin commit):**
- `hooks.py` — prefix "companies" en fixture de Company
- `fixtures/companies_custom_field.json` — nuevo archivo (27 Company custom fields)
- `fixtures/custom_field.json` — actualizado (74 Event custom fields, event fields nuevos incluidos)
- `companies/test_install.py` — nuevo test de instalación

**Pendiente para el PR:**
- Confirmar D1 sobre `PROP-2026-00004`
- Si se aprueba Fase 2A: hacer `physical_space` reqd y resolver el registro demo

---

## Fase 2A — Completada (2026-06-05)

**D1 resuelta:** `PROP-2026-00004 "Demo Apt 202"` confirmado como demo. Verificación:
- Property Account: vacío
- Property User Authorization: vacío
- Linked docs: vacío
- Eliminado correctamente con cascade en Property Declared Owner

**Lo que se hizo:**
1. Eliminado registro demo `PROP-2026-00004` de la BD.
2. `property_registry.json` — `physical_space: reqd: 1`
3. `property_registry.py` — `validate_physical_space_company()` agregado en `before_save`
4. `test_property_registry.py`:
   - `create_test_data` — crea Space Category "Test Unit" para tests
   - `_get_or_create_test_space()` — helper que crea Physical Space de test
   - `_base_doc` — incluye `physical_space` en todos los campos obligatorios
   - `test_physical_space_required` — verifica que sin physical_space falla
   - `test_physical_space_company_must_match` — verifica que el space debe ser del mismo company
   - `tearDown` — limpia Physical Space de test
5. `bench migrate` limpio post-cambios.

**`unique` sobre `physical_space`:** NO aplicado — diferido. Casos de bodegas, cajones y unidades accesorias requieren análisis antes de restringirlo.

**Archivos modificados (sin commit):**
- `companies/doctype/property_registry/property_registry.json` — reqd en physical_space
- `companies/doctype/property_registry/property_registry.py` — validación company consistency
- `companies/doctype/property_registry/test_property_registry.py` — tests actualizados + 2 nuevos

---

## Resumen de cambios pendientes de commit

| Archivo | Cambio |
|---|---|
| `hooks.py` | prefix "companies" para fixture de Company custom fields |
| `fixtures/companies_custom_field.json` | nuevo (27 Company custom fields) |
| `fixtures/custom_field.json` | actualizado (74 Event custom fields) |
| `companies/test_install.py` | nuevo test de instalación |
| `property_registry.json` | physical_space: reqd |
| `property_registry.py` | validate_physical_space_company() |
| `test_property_registry.py` | tests actualizados + 2 nuevos |

---

## Fase 3 — Completada (2026-06-06)

**Physical Space** — permisos agregados en `physical_space.json`:
- `Property Administrator`: R/W/C, sin delete
- `Condominium Manager`: R/W/C, sin delete
- `Property Manager`: R solamente

**Condominium Information** — permisos agregados en `condominium_information.json`:
- `Property Administrator`: R/W/C, sin delete

**User Permissions automáticas:** DIFERIDAS al PR del portal condominial. Documentado en `CLAUDE.md` + `docs/adr/0003-*`.

**Service Management Contract:** sin cambios de código. Decisión D2 documentada en `docs/adr/0003-service-management-contract-level.md`.

---

## Fase 4 — Completada (2026-06-06)

**Catálogos HQ (Regla D3):**
- `docs/adr/0002-catalog-hq-policy.md` — decisión permanente documentada
- `hooks.py` § POLÍTICA DE CATÁLOGOS — comentarios inline
- `mkdocs.yml` — sección ADR agregada al nav (ADR-0000 a ADR-0003)
- `CLAUDE.md` — referencia breve, sin duplicar análisis

---

## Pendientes explícitos (fuera de este PR)

| Pendiente | Bloqueante | PR esperado |
|---|---|---|
| User Permissions automáticas por Company | No (solo portal) | PR portal condominial (Fase 3 PUA) |
| `unique` sobre `physical_space` | No | Requiere análisis bodegas/cajones primero |
| Vínculo Unidad↔Customer (Property Account) | No | PR Financial Management (congelado) |
| Committee Poll con validación PUA | No | Próximo PR |
| Eliminar `Property Copropiedad` DocType | No | PR limpieza técnica |

---

*Fin del plan.*
*Estado: Fases 1, 2A, 3 y 4 completadas · bench migrate pendiente · commit pendiente autorización.*
