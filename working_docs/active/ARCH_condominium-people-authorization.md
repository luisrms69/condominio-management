# Arquitectura — Condominium People
## Fase 1: Property User Authorization
### Autorización Operativa User ↔ Property Registry

| Campo | Valor |
|---|---|
| **Estado** | v4 — Revisión independiente completada. Pendiente cierre interno D2/D5/D7 |
| **Fecha** | 2026-06-05 |
| **Autores** | Luis Montanaro / Claude Code |
| **Revisión independiente** | Validada — ver Sección 14 para condiciones de autorización |

> **AVISO:** Arquitectura en discusión. No implementado. Las decisiones definitivas migrarán a
> `docs_new/tecnico/arquitectura.md` y/o `docs/adr/` cuando se implemente.

---

## Índice

1. [Condominium People como dominio funcional](#1-condominium-people-como-dominio-funcional)
2. [Roadmap conceptual por fases](#2-roadmap-conceptual-por-fases)
3. [Fase 1: Property User Authorization — qué resuelve](#3-fase-1-property-user-authorization)
4. [Mapa de responsabilidades — separación de conceptos](#4-mapa-de-responsabilidades)
5. [Los dos planos: operativo-login vs stakeholder-sin-login](#5-los-dos-planos)
6. [Integración con Frappe/ERPNext — diagnóstico real](#6-integración-con-frappeerpnext)
7. [DocTypes propuestos para Fase 1](#7-doctypes-propuestos-para-fase-1)
8. [Helpers / API mínima](#8-helpers--api-mínima)
9. [Integración con módulos del app](#9-integración-con-módulos-del-app)
10. [Alcance de Fase 1](#10-alcance-de-fase-1)
11. [Decisiones arquitectónicas abiertas](#11-decisiones-arquitectónicas-abiertas)
12. [Riesgos](#12-riesgos)
13. [Preguntas para revisión independiente](#13-preguntas-para-revisión-independiente)
14. [Recomendación antes de implementar](#14-recomendación-antes-de-implementar)

---

## 1. Condominium People como dominio funcional

**Condominium People** es el dominio funcional completo que resuelve **quién es quién en el condominio** y qué puede hacer cada uno en el sistema.

Cubre personas con login, personas sin login, titulares, residentes, representantes, contactos administrativos, visitantes y cualquier entidad humana relevante para la operación del condominio.

**Este documento NO abandona ese dominio.** Lo implementa de forma incremental.

### 1.1 Por qué no se implementa de una vez

El error clásico en sistemas condominiales es construir un módulo gigante tipo "Person Profile" desde el inicio. Ese camino:
- Duplica lo que Frappe ya tiene (`User`, `Contact`, `Address`)
- Crea una identidad paralela que diverge del sistema de permisos de Frappe
- Añade complejidad antes de validar qué casos de negocio realmente necesitan una entidad propia

La estrategia correcta es **native-first, incremental**:
1. Usar al máximo lo que Frappe/ERPNext ya resuelve
2. Crear solo la capa que Frappe genuinamente no provee
3. Añadir entidades propias cuando haya un caso de negocio real que justifique lo que ninguna entidad nativa resuelve

### 1.2 Primera pieza: autorización operativa

La necesidad más urgente y concreta es: **¿qué User puede hacer qué sobre qué propiedad?**

Eso no lo resuelve ninguna entidad nativa de Frappe. Ahí empieza Condominium People.

---

## 2. Roadmap conceptual por fases

Las siguientes fases son conceptuales. **Solo Fase 1 es el objeto de este documento.** Las fases siguientes se describen para mostrar hacia dónde crece el dominio, no como compromisos de implementación.

### Fase 1 — Autorización operativa (este documento)

**¿Qué User puede hacer qué sobre qué Property Registry?**

- `Property Relationship Type` — catálogo de tipos de relación condominial
- `Property User Authorization` — vínculo User ↔ Property Registry con permisos
- Helpers: `can_user_vote_for_property`, `get_authorized_properties`, etc.
- Sin portal completo
- Sin entidad de persona propia
- Sin sincronización de Contact

### Fase 2 — Stakeholders y contactos por propiedad

**¿Quiénes son los stakeholders de una propiedad, con o sin login?**

- Integración explícita con `Contact` / `Address` nativos de Frappe
- Destinatarios de comunicaciones formales
- Propietarios sin login
- Representantes legales
- Contactos administrativos y de emergencia
- Herramientas opcionales para sugerir creación de Contact desde `Property Declared Owner`

### Fase 3 — Portal/App de condóminos

**¿Cómo accede el condómino al sistema desde su dispositivo?**

- Experiencia de usuario condominial (portal web o app)
- Selección de propiedad representada
- Consulta de estado de cuenta
- Consulta de documentos
- RSVP, encuestas, reservas, tickets
- User Permissions sync activado en este punto (diferido de Fase 1)

### Fase 4 — Integraciones operativas completas

**¿Cómo se conecta People con el resto del app?**

- Committee Poll con respuesta por propiedad
- Voting System con unicidad por propiedad
- Community Event RSVP completo
- Tickets vinculados a propiedad
- Reservas de amenidades
- Comunicación formal y operativa integrada
- Committee workflows con validación PUA

### Fase 5 — Extensiones futuras

**¿Qué casos especiales pueden requerir entidades nuevas?**

- Visitantes y acceso temporal
- Proveedores y personal de mantenimiento
- Staff del condominio
- Access control físico
- Vehículos
- Documentos personales de propietarios
- Familiares como entidades (solo si Contact no es suficiente)

> **Principio:** Ninguna entidad nueva en Fase 5 debe crearse sin un caso de negocio real que Contact/Address/User no resuelva. Siempre justificar contra capacidades nativas de Frappe.

---

## 3. Fase 1: Property User Authorization

### 3.1 Qué resuelve

El módulo **Property User Authorization (PUA)** es la primera pieza fundacional de Condominium People. Responde:

> **¿Qué User puede actuar sobre qué Property Registry, bajo qué relación condominial, con qué permisos específicos?**

### 3.2 Por qué no se implementa `Condominium Person Profile` en Fase 1

`Contact`, `Address` y `User` de Frappe cubren la gestión de personas sin necesidad de una entidad propia. Crear un `Condominium Person Profile` en Fase 1 implicaría:
- Duplicar campos de `User` (nombre, email) o de `Contact`
- Crear una entidad de identidad paralela al sistema de permisos de Frappe
- Añadir complejidad antes de validar si el dominio necesita algo que Contact/User no resuelven

Si en fases futuras aparece una necesidad concreta que Contact/Address/User genuinamente no cubren, se evaluará una entidad adicional. Mientras tanto, no se crea.

### 3.3 Qué NO sustituye PUA

| PUA no reemplaza | Porque |
|---|---|
| `User` | PUA no gestiona identidad ni login |
| `Contact` / `Address` | PUA no gestiona stakeholders sin login |
| `Property Declared Owner` | PUA no gestiona titularidad declarada |
| `Customer` | PUA no define la entidad cobrable |
| `Property Registry` | PUA no es la unidad física/registral |

---

## 4. Mapa de responsabilidades

### 4.1 Tabla de entidades

| Entidad | Qué representa | Qué NO es |
|---|---|---|
| `User` | **Solo identidad de login y autenticación** | No es propietario, residente ni persona completa |
| `Contact` / `Address` | Personas/entidades relevantes sin login (stakeholders) | No tienen acceso al sistema |
| `Customer` | Entidad cobrable (si Financial Management lo confirma) | No es un producto. Ver nota 4.2 |
| `Item` | Concepto cobrado: cuota, recargo, reserva, penalización | No es la unidad |
| `Property Registry` | Unidad física/registral del condominio | No es el propietario. No es la entidad cobrable directa |
| `Property Declared Owner` | Titularidad declarada ante la administración (historial) | No es identidad de acceso. No es cobranza |
| `Property User Authorization` | Autorización operativa de un User sobre una Property Registry | No es identidad. No es titularidad. No es cobranza |

### 4.2 Advertencia: `User` no es una persona condominial

> **`User` es solo cuenta de acceso al sistema.**
>
> No debe cargarse con semántica condominial: no es propietario, no es residente, no es condómino, no es stakeholder ni persona completa.
>
> La semántica condominial vive fuera del User, en:
> - `Property User Authorization` — para acceso operativo
> - `Contact / Address` — para stakeholders sin login
> - `Property Declared Owner` — para titularidad declarada/histórica

Si se empieza a tratar al User como "el propietario", se duplican responsabilidades que deben vivir en otras entidades y se contaminan los mecanismos de permisos de Frappe.

### 4.3 Property Registry es el spine del dominio

> **`Property Registry` es el eje estable de relación entre autorización, titularidad, contacto y cobranza.**

El modelo correcto:
```
PUA               → Property Registry
Contact           → Property Registry
Property Declared Owner → Property Registry
Customer (futuro) → Property Registry
```

El modelo prohibido en Fase 1:
```
PUA → Customer   ← NO
```

**Por qué es importante esta regla:** Si Financial Management cambia su modelo de cobranza (Customer = Unit, Customer = Persona, o cualquier otro), PUA debe permanecer estable. Al vincular PUA solo con Property Registry y nunca con Customer, la autorización operativa queda desacoplada de las decisiones de cobranza.

### 4.5 Advertencia: `Customer = Unit` es una hipótesis diferida

> **PUA no depende de `Customer`.** PUA solo depende de `Property Registry`.
>
> `Customer = Unit` es una hipótesis de cobranza, todavía no confirmada, que pertenece a Financial Management (actualmente congelado).
>
> PUA debe permanecer estable aunque Financial Management decida un modelo de cobranza diferente a Customer=Unit.

Nota: `Item` representa conceptos cobrados (cuota de mantenimiento, recargo, penalización), no la unidad. La unidad puede modelarse como `Customer` para efectos de cobranza, pero eso es una decisión de Financial Management que PUA no anticipa ni requiere.

### 4.6 Casos concretos

| Caso | Cómo se modela |
|---|---|
| Propietario ausente, sin login | `Property Declared Owner` + `Contact` — sin User ni PUA |
| Residente con login, sin derecho a estado de cuenta | `User` + PUA (`can_view_statement=0`) |
| Arrendatario con login y permisos limitados | `User` + PUA (relationship: Arrendatario, `can_vote=0`) |
| Administrador con acceso a muchas unidades | `User` con roles administrativos — PUA no aplica para gestión |
| Usuario con varias propiedades | Un PUA por propiedad autorizada |
| Propiedad con varios usuarios autorizados | Varios PUAs sobre la misma `Property Registry` |
| Copropietario sin login | `Property Declared Owner` + `Contact` |

---

## 5. Los dos planos

### 5.1 Plano operativo con login

Para personas con acceso al sistema. Acciones que requieren `User`:
- Votar en asamblea
- Responder encuestas del comité
- Hacer RSVP a eventos comunitarios
- Levantar tickets
- Reservar amenidades
- Consultar estado de cuenta por portal/app
- Acceder a portal/app condominial

**Vínculo:**
```
User → Property User Authorization → Property Registry
```

### 5.2 Plano stakeholder sin login

Para personas relevantes que no necesitan acceso al sistema:
- Propietario ausente o no tecnológico
- Copropietario sin cuenta
- Representante legal sin login
- Destinatario de comunicaciones formales
- Contacto de emergencia

**Vínculo:**
```
Contact / Address → Property Registry
Property Declared Owner → Property Registry
```

**Regla:** No debe forzarse que toda persona tenga `User`. El sistema debe operar para propiedades cuyos titulares no tienen cuenta.

### 5.3 Límite de comunicaciones

- **Comunicación operativa por portal/app** → `can_receive_portal_communications` en PUA → Fase 3
- **Comunicación formal y pasiva** (convocatorias, estados de cuenta, documentos legales) → `Customer → Contact` — independiente de PUA

Esta separación es intencional y debe preservarse. La comunicación formal no depende de que exista un User autorizado.

---

## 6. Integración con Frappe/ERPNext — diagnóstico real

### 6.1 Principio rector: native-first

> No crear lo que Frappe ya provee. Crear solo la capa mínima que Frappe genuinamente no provee.

### 6.2 Estado real de User Permissions en Frappe v16 (verificado en código)

**Hallazgo crítico confirmado:** En Frappe v16, el campo `apply_user_permissions` fue eliminado de `tabDocPerm`. La columna no existe. El mecanismo cambió.

**Cómo funciona User Permissions en Frappe v16:**
- Se crean registros `User Permission`: `{user, allow: "Property Registry", for_value: "PR-001"}`
- Frappe evalúa estas permisiones automáticamente — sin configuración per-rol
- El setting `apply_strict_user_permissions` en Site Config controla el nivel de restricción

**Estado actual del codebase (verificado):**

| Item | Estado |
|---|---|
| `apply_user_permissions` en DocPerm | ❌ Eliminado en Frappe v16 — columna inexistente |
| `Condómino` rol con permiso en Property Registry | ❌ No existe — solo acceden: System Manager, Property Administrator, Property Manager |
| User Permissions de tipo `Property Registry` en el site | ❌ Ninguna registrada |
| `apply_strict_user_permissions` en site config | ⚠️ No verificado — pendiente de diagnóstico |

**Implicación:** Para que User Permissions funcionen para condóminos, se necesita:
1. Agregar permiso de lectura al rol `Condómino` en `property_registry.json`
2. Verificar el valor de `apply_strict_user_permissions` antes de ese cambio
3. Crear User Permission records al activar un PUA

**Esta configuración está diferida a Fase 3 (portal).** Ver Decisión D1 y Sección 14.

### 6.3 Diferir User Permissions no reduce el valor de Fase 1

> El primer PR entrega la **fuente funcional de autorización**: los helpers ya desbloquean módulos consumidores sin necesidad de User Permissions.
>
> User Permissions es una **optimización de visibilidad** para el portal. Su ausencia no impide que Poll, Voting o RSVP funcionen si consultan los helpers.
>
> Diferir User Permissions a Fase 3 ≠ diferir Condominium People.

### 6.4 Roles relacionados existentes (verificado)

- `Condómino` — rol de condómino, `desk_access: 1`, sin permiso en Property Registry
- `Residente Propietario` — existe, sin permiso en Property Registry
- `Property Administrator`, `Property Manager` — gestión administrativa
- `Condominium Manager`, `Administrator Condominio` — administración general
- `Committee Member`, `Committee President`, `Committee Secretary` — roles de comité

---

## 7. DocTypes propuestos para Fase 1

### 7.1 `Property Relationship Type` (catálogo maestro)

**Justificación de DocType vs Select hardcodeado:**

Un Select hardcodeado no es configurable por instalación. Los tipos de relación condominial varían según legislación estatal y reglamento interno. Un DocType permite:
- Agregar tipos locales sin modificar código
- Deshabilitar tipos no aplicables
- Configurar permisos por defecto diferenciados por instalación

**Patrón de carga inicial:** `after_migrate` idempotente — mismo patrón que `Committee Position` y `Event Checklist Item` en este repo. Crea solo si no existe, nunca sobreescribe.

> **Por qué no fixtures:** Los fixtures en Frappe sobreescriben registros existentes en cada `bench migrate`. Si una instalación ajustó defaults de un tipo de relación, el migrate los revertiría. El patrón idempotente preserva customizaciones locales.

**Campos:**

| Fieldname | Fieldtype | Reqd | Descripción |
|---|---|---|---|
| `relationship_name` | Data | Sí | Nombre único del tipo |
| `is_active` | Check | — | default 1 |
| `default_can_vote` | Check | — | default para can_vote al crear PUA |
| `default_can_respond_polls` | Check | — | |
| `default_can_rsvp_events` | Check | — | |
| `default_can_create_tickets` | Check | — | |
| `default_can_reserve_amenities` | Check | — | |
| `default_can_view_statement` | Check | — | |
| `default_can_receive_portal_communications` | Check | — | |
| `notes` | Small Text | — | |

**Ejemplos de defaults:**

| Tipo | vote | polls | rsvp | tickets | amenities | statement | comms |
|---|---|---|---|---|---|---|---|
| Propietario | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Copropietario | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Residente | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Arrendatario | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Familiar | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Apoderado | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Staff / Proveedor | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |

Los defaults se aplican al crear una autorización vía JS onchange. Son editables individualmente en cada PUA.

---

### 7.2 `Property User Authorization`

**Propiedades:**
```
track_changes: 1
autoname: PUA-.YYYY.-
```

**Campos:**

| Fieldname | Fieldtype | Reqd | Descripción |
|---|---|---|---|
| `company` | Link → Company | Sí | Derivado de property_registry. Read-only. Debe coincidir con property_registry.company |
| `user` | Link → User | Sí | Usuario autorizado |
| `property_registry` | Link → Property Registry | Sí | Propiedad sobre la que se autoriza |
| `relationship_type` | Link → Property Relationship Type | Sí | Tipo de relación condominial |
| `is_active` | Check | — | default 1 |
| `valid_from` | Date | — | Inicio de vigencia. Opcional — si vacío, válido desde creación |
| `valid_until` | Date | — | Fin de vigencia. Opcional — si vacío, sin expiración |
| `source_reference` | Data | — | Referencia del acto que origina: "Contrato 2024-001", "Acuerdo asamblea ordinaria" |
| `authorized_by` | Link → User | — | Read-only. Auto-filled en before_save |
| `authorized_on` | Datetime | — | Read-only. Auto-filled en before_save |
| **Permisos condominiales** | | | |
| `can_vote` | Check | — | Puede votar en asamblea |
| `can_respond_polls` | Check | — | Puede responder encuestas |
| `can_rsvp_events` | Check | — | Puede hacer RSVP a eventos |
| `can_create_tickets` | Check | — | Puede crear tickets |
| `can_reserve_amenities` | Check | — | Puede reservar amenidades |
| `can_view_statement` | Check | — | Puede ver estado de cuenta por portal |
| `can_receive_portal_communications` | Check | — | Recibe notificaciones por portal/app |
| **User Permissions (Fase 3)** | | | |
| `user_permission_property_registry` | Link → User Permission | — | Read-only. Referencia al UP creado para Property Registry (Fase 3) |
| `user_permission_company` | Link → User Permission | — | Read-only. Referencia al UP creado para Company (Fase 3) |
| `notes` | Small Text | — | |

**Reglas de negocio:**

1. `company` se deriva de `property_registry.company` automáticamente — read-only, no editable
2. `company` debe coincidir con `property_registry.company` — validado en `validate()`
3. `valid_until` > `valid_from` si ambos existen — validado en `validate()`
4. Al seleccionar `relationship_type`, los permisos por defecto se precargan vía JS — editables después
5. `authorized_by` = `frappe.session.user` en `before_save`
6. Los campos de User Permissions son Read-only — se gestionan via hooks en Fase 3

**Sobre la regla de unicidad:** Ver Decisión D2 en Sección 11.

---

## 8. Helpers / API mínima

Ubicación: `condominium_management/condominium_people/utils.py`

```python
def get_authorized_properties(user, permission=None, company=None):
    """
    Lista de property_registry donde user tiene autorización activa y vigente.
    permission: campo can_* — si None, retorna todas.
    company: filtra por condominio.
    Considera is_active, valid_from <= today, valid_until >= today (o vacío).
    """

def can_user_act_for_property(user, property_registry, action):
    """
    Punto de entrada único para permisos condominiales.
    action: uno de can_vote, can_respond_polls, can_rsvp_events,
            can_create_tickets, can_reserve_amenities,
            can_view_statement, can_receive_portal_communications
    Retorna True para System Manager (bypass de negocio).
    """

# Aliases por legibilidad:
def can_user_vote_for_property(user, property_registry): ...
def can_user_respond_poll_for_property(user, property_registry): ...
def can_user_rsvp_for_property(user, property_registry): ...
def can_user_create_ticket_for_property(user, property_registry): ...
def can_user_reserve_amenity_for_property(user, property_registry): ...
def can_user_view_statement(user, property_registry): ...

def get_active_authorization(user, property_registry):
    """
    Retorna el PUA activo y vigente para user+property, o None.
    Útil para obtener relación, fechas y todos los permisos en un query.
    """

def get_effective_permissions(user, property_registry):
    """
    Retorna dict con todos los permisos efectivos, o None si no hay autorización.
    """

def get_authorized_users_for_property(property_registry, permission=None):
    """
    Lista de users con autorización activa sobre una propiedad.
    Útil para Voting/Poll cuando se necesita saber quiénes pueden actuar.
    """
```

**Reglas de consumo:**
1. Los módulos importan estos helpers — no reimplementan autorización
2. System Manager siempre devuelve True — bypass para operaciones administrativas
3. Los helpers calculan vigencia en tiempo real — sin necesidad de cron

---

## 9. Integración con módulos del app

### 9.1 Committee Poll

El voto/respuesta cuenta por propiedad. Índice único: `(poll, property_registry)`.

PUA valida quién puede actuar (`can_respond_polls`). Poll impone unicidad de respuesta. La regla de desempate entre dos usuarios autorizados para la misma propiedad pertenece al módulo Poll, no a PUA.

### 9.2 Voting System

Igual que Poll. PUA valida quién puede votar; Voting impone `(voting, property_registry)` único.

**Decisión de Voting pendiente (no de PUA):** Si dos usuarios con `can_vote=1` en la misma propiedad intentan votar, Voting decide la regla. Opciones: primero gana, último actualizable, solo principal designado.

### 9.3 Community Event RSVP

PUA valida `can_rsvp_events`. El RSVP se registra con `(event, property_registry, user)`.

### 9.4 Committee Member (coexistencia temporal)

`Committee Member` ya tiene `user → property_registry` como solución temporal. Coexisten en Fase 1. La migración hacia PUA es deuda técnica a documentar, no a resolver en este PR.

### 9.5 Estados de cuenta

| Flujo | Fuente |
|---|---|
| Consulta por portal (Fase 3) | PUA: `can_view_statement = 1` |
| Emisión y envío formal | Customer → Contact — independiente de PUA |

La separación es intencional. La emisión formal no requiere que el condómino tenga User ni PUA.

### 9.6 Comunicaciones

| Tipo | Fuente |
|---|---|
| Notificaciones por portal/app (Fase 3) | PUA: `can_receive_portal_communications` |
| Comunicaciones formales | Contact / Address |

### 9.7 Property Declared Owner

Se mantiene separado como titularidad declarada/histórica. En fases futuras puede servir como fuente de sugerencia para crear Contact, User o PUA — pero no de forma automática. La creación de PUA siempre requiere acción administrativa explícita.

---

## 10. Alcance de Fase 1

### Dentro del MVP de implementación (Fase 1)

- `Property Relationship Type` DocType + defaults vía `after_migrate`
- `Property User Authorization` DocType con validaciones
- Permisos por defecto precargados desde `relationship_type` vía JS
- Helpers Python en `utils.py`
- Tests: validación de autorizaciones, helpers, vigencia, unicidad
- Sin User Permissions sync (diferido a Fase 3)

### Diferido a fases posteriores

| Capacidad | Fase |
|---|---|
| User Permissions sync | Fase 3 |
| Portal condominial | Fase 3 |
| Stakeholders/Contactos por propiedad | Fase 2 |
| Committee Poll completo | Fase 4 |
| Voting completo | Fase 4 |
| RSVP completo | Fase 4 |
| Tickets, Amenidades, Estado de cuenta | Fase 4 |
| Visitantes, proveedores, access control | Fase 5 |
| Financial Management, Property Account | Deferred sin fase asignada |

---

## 11. Decisiones arquitectónicas abiertas

### D1 — User Permissions: ¿automático, configurable o diferido a Fase 3?

**Diagnóstico actual (verificado):**
- `apply_user_permissions` eliminado de Frappe v16
- `Condómino` sin permiso en Property Registry
- `apply_strict_user_permissions` no verificado en el site

**Pendiente antes de decidir:**
1. Verificar valor de `apply_strict_user_permissions` en site config
2. Verificar qué ocurre al agregar lectura al rol `Condómino` en Property Registry sin User Permissions creadas
3. Verificar que roles administrativos no quedan afectados

**Recomendación actual:** Diferir a Fase 3. Los helpers funcionan sin User Permissions. El sync agrega UX de visibilidad nativa, no funcionalidad de negocio.

### D2 — Unicidad: ¿user + property o user + property + relationship?

**Opción A:** Una sola PUA activa por `user + property_registry` — simple, potencialmente restrictivo

**Opción B:** Una sola activa por `user + property_registry + relationship_type` — permite múltiples relaciones sobre la misma propiedad

**Consideración:** Si un usuario puede ser Propietario y también Apoderado de un tercero sobre la misma unidad, opción B es más correcta. Pero los helpers tomarían la unión de permisos, que en la práctica es más permisiva.

**Decisión sugerida:** Opción A para Fase 1 con documentación explícita de la limitación. Migrar a B si un caso real lo requiere.

### D3 — Vigencia y expiración automática

**Recomendación:** Los helpers calculan vigencia en tiempo real (`valid_until >= today`). Sin cron. Cron puede agregarse en Fase 3 si hay degradación de performance.

### D4 — `is_primary_voter` / `is_primary_authorized_user`

Esta decisión pertenece al módulo Voting, no a PUA. PUA define quién puede actuar; Voting define la regla de desempate. No agregar este campo en Fase 1.

### D5 — Módulo propio `condominium_people`

**Recomendación:** Módulo propio desde Fase 1, dado que PUA es transversal al app y el dominio crecerá con portal, stakeholders, tickets y amenidades.

### D6 — Permiso de lectura `Condómino` en Property Registry

Requiere diagnóstico previo (D1). No activar sin verificar efectos de `apply_strict_user_permissions`.

### D7 — Identidad de persona fragmentada vs entidad unificada ✅ CERRADO

**Decisión:** En Fase 1 se acepta explícitamente que no existe una entidad única que represente a la persona humana completa.

Las entidades se mantienen separadas:
- `User` — cuenta de login/autenticación
- `Contact / Address` — stakeholder sin login
- `Property Declared Owner` — titularidad declarada/histórica
- `Property User Authorization` — autorización operativa sobre una propiedad

Esta separación es intencional y native-first. **No se crea `Condominium Person Profile` en Fase 1.**

**Costo aceptado:** El sistema no puede responder "muéstrame todo sobre esta persona humana" sin una reconciliación adicional entre User, Contact y Property Declared Owner.

**Riesgo de reconciliación futura:** Si se intenta cruzar entidades por nombre o email, pueden generarse errores por homónimos, capturas inconsistentes, apellidos compuestos o cambios de correo.

**Mitigación:** Cualquier reconciliación futura debe usar una llave estable **opcional** cuando exista — RFC, CURP u otro identificador confiable — no matching difuso por nombre. Este identificador ya existe como campo `owner_id` en `Property Declared Owner`.

**Nota en el roadmap:** Reconciliación de persona/identidad es una posible fase futura — solo si Contact/User/Property Declared Owner demuestran ser insuficientes para un caso de negocio concreto. No crear `Person Profile` sin ese caso probado.

---

## 12. Riesgos

| ID | Riesgo | Sev | Descripción | Mitigación |
|---|---|---|---|---|
| R1 | Sobrecargar `User` con semántica condominial | Alta | Si se trata al User como propietario/residente/persona, se duplican responsabilidades y se contamina el sistema de permisos de Frappe. | User solo para login/autenticación. Toda semántica condominial vive en PUA, Contact, Property Declared Owner. |
| R2 | Acoplar PUA a Customer=Unit antes de resolver Financial | Media | Si PUA depende de Customer, queda atada a una decisión de cobranza no cerrada. | PUA solo depende de Property Registry. Sin Link a Customer en Fase 1. |
| R3 | `Condómino` sin permiso base en Property Registry | Alta | Verificado: el rol `Condómino` no tiene permiso de lectura en Property Registry. Sin ese permiso, User Permissions no tendrían efecto. | Diferir User Permissions sync a Fase 3. Diagnosticar `apply_strict_user_permissions` antes de agregar permiso. |
| R4 | `apply_strict_user_permissions` desconocido | Alta | Sin verificar ese setting, agregar permiso al rol Condómino puede exponer TODAS las propiedades si no hay User Permissions creadas. | Verificar el setting antes de Fase 3. No agregar permiso al rol en Fase 1. |
| R5 | Desincronización PUA ↔ User Permission | Alta | Si se borra un User Permission manualmente en Frappe, el campo de referencia en PUA queda huérfano. | Los campos `user_permission_*` en PUA son referencias explícitas. Validar en `validate()` antes de operar. (Aplica a Fase 3.) |
| R6 | Roles mixtos — administrador y condómino | Media | Un usuario puede tener `Condominium Manager` y ser condómino. User Permissions de Property Registry pueden restringir su vista administrativa. | Verificar que roles administrativos tienen acceso completo y no aplican User Permissions en Frappe v16. (Fase 3.) |
| R7 | Ambigüedad de voto con múltiples autorizados | Media | Dos usuarios con `can_vote=1` sobre la misma propiedad pueden generar conflicto legal en asamblea. | Resolver regla de desempate en Voting antes de implementarlo. PUA no toma esta decisión. |
| R8 | Exposición de datos financieros via `can_view_statement` | Media | Si el portal no está implementado, el riesgo es bajo. Cuando se implemente, el endpoint debe ser seguro. | Habilitar `can_view_statement` solo cuando el portal tenga el endpoint correspondiente. (Fase 3.) |
| R9 | Committee Member y PUA en conflicto | Baja | Committee Member ya tiene `user → property_registry`. Coexistencia puede generar consultas ambiguas. | No modificar Committee Member en Fase 1. Documentar como deuda técnica. |
| R10 | Proliferación de User Permissions | Baja | En condominios con 200+ unidades, `tabUser Permission` puede crecer. Frappe evalúa todas en cada query. | Monitorear en Fase 3. Caching si hay degradación. (No aplica a Fase 1.) |
| R11 | Reconciliación futura de persona por matching frágil | Media | Si User, Contact y Property Declared Owner quedan fragmentados sin llave estable, futuras consultas centradas en persona pueden requerir matching por nombre/email — propenso a errores por homónimos o capturas inconsistentes. | Aceptar fragmentación en Fase 1 (D7 cerrado). Cualquier reconciliación futura debe usar `owner_id` (RFC/CURP) cuando exista, no matching difuso. |
| R12 | Customer como hub equivocado en joins futuros | Media | Cuando Financial Management se reactive, puede surgir la tentación de usar `Customer` como eje de joins entre PUA, Contact y Property Declared Owner. Esto acoplaría la autorización a la cobranza. | Mantener `Property Registry` como spine del dominio. Customer es entidad cobrable, no eje del dominio People. La regla `PUA → Property Registry` nunca `PUA → Customer` debe respetarse. |

---

## 13. Preguntas para revisión independiente

**Sobre el dominio Condominium People:**
1. ¿La división entre Condominium People como dominio completo y PUA como Fase 1 es correcta? ¿Falta algo en la visión del dominio antes de implementar la primera pieza?
2. ¿PUA es una primera pieza suficientemente sólida, o falta alguna capa mínima de stakeholders desde Fase 1?
3. ¿Es correcto evitar `Condominium Person Profile` en Fase 1? ¿Qué señales justificarían crear una entidad propia de persona en fases futuras?
4. ¿Hay riesgo de sobreusar `User` como si fuera una persona completa en el diseño actual?

**Sobre el alcance del MVP:**
5. ¿La separación conceptual `User` (login), `Contact` (stakeholder sin login), `Property Declared Owner` (titularidad), `Customer` (cobrable) y `PUA` (autorización operativa) es correcta y suficiente para un sistema condominial en México?
6. ¿PUA debe mantenerse totalmente independiente de `Customer` hasta que Financial Management se reactive? ¿Hay casos de negocio que requieran vincular PUA con Customer desde Fase 1?

**Sobre User Permissions:**
7. Dado que `apply_user_permissions` fue eliminado en Frappe v16 y el rol `Condómino` no tiene permiso en Property Registry, ¿es correcto diferir el sync de User Permissions a Fase 3 (portal)?
8. ¿El patrón de referencias explícitas (`user_permission_property_registry`) para evitar desincronización es suficiente, o hay un riesgo estructural mayor?

**Sobre conflictos de autorización:**
9. Si dos usuarios tienen `can_vote=1` sobre la misma propiedad y ambos votan en la misma asamblea, ¿la regla de desempate ("primero gana" o similar) en el módulo Voting es aceptable legalmente para asambleas condominiales en México?
10. ¿Debe PUA tener `is_primary_voter` para desempatar, o esa responsabilidad pertenece completamente al módulo Voting?

**Sobre la comunicación:**
11. ¿La separación `comunicación formal → Contact/Customer` vs `comunicación operativa por portal → PUA` es operativamente viable? ¿Cómo se gestiona la transición cuando un condómino sin User recibe un estado de cuenta formal?

**Sobre identidad fragmentada:**
12. ¿Se acepta explícitamente la identidad fragmentada en Fase 1 (User ≠ Contact ≠ Property Declared Owner)? ¿Es suficiente para los casos de negocio de Fase 1?
13. ¿Conviene reservar desde ahora el campo `owner_id` (RFC/CURP) en `Property Declared Owner` como llave futura de reconciliación, o se difiere totalmente?

**Sobre el spine del dominio:**
14. ¿Property Registry queda confirmado como spine del dominio frente a Customer? ¿Hay algún caso donde PUA debería linkear a Customer en lugar de solo a Property Registry?

**Sobre el diseño general:**
15. ¿Hay alguna entidad o relación en el dominio condominial mexicano que este diseño no contemple y que pueda requerir cambios arquitectónicos significativos?

---

## 14. Recomendación antes de implementar

### Estado post revisión independiente

La revisión independiente **valida la arquitectura general de Fase 1**:
- ✅ PUA sí basta como primera pieza de Condominium People
- ✅ No es necesario implementar stakeholders/Contact en Fase 1
- ✅ PUA debe mantenerse independiente de Customer/Financial Management
- ✅ Property Registry como spine del dominio

### Decisiones que deben cerrarse internamente antes del primer PR

| Decisión | Estado | Acción |
|---|---|---|
| D2 — Unicidad user + property | 🟡 Sugerida Opción A | Confirmar: un PUA activo por user + property_registry |
| D5 — Módulo propio condominium_people | 🟡 Recomendado | Confirmar módulo propio desde Fase 1 |
| D7 — Identidad fragmentada aceptada | ✅ Cerrado en v4 | Documentado y aceptado |
| Regla Property Registry como spine | ✅ Cerrado en v4 | Documentado: PUA → Property Registry, nunca PUA → Customer |
| D1/D6 — User Permissions | ⚠️ Diferido a Fase 3 | Verificar `apply_strict_user_permissions` antes de Fase 3, no antes de Fase 1 |

### Primer PR — lo que entra

- `Property Relationship Type` DocType + defaults vía `after_migrate`
- `Property User Authorization` DocType con validaciones
- Helpers en `utils.py`: `can_user_act_for_property`, `get_authorized_properties` y aliases
- Tests: autorizaciones, helpers, vigencia, unicidad
- **Sin User Permissions sync** — diferido a Fase 3
- **Sin dependencia de Customer**
- **Sin Person Profile**
- **Sin stakeholders/Contact**

### Lo que NO entra en el primer PR

- User Permissions sync (Fase 3)
- Permiso `Condómino` en Property Registry (Fase 3)
- Portal condominial (Fase 3)
- Módulos consumidores: Poll, Voting, RSVP, Tickets, Amenidades (Fase 4)
- Migración desde Committee Member o Property Declared Owner
- Cualquier dependencia de Customer o Financial Management

### Condición para autorizar implementación

El primer PR puede autorizarse cuando se confirme internamente:
1. **D2:** Unicidad `user + property_registry` como regla del MVP
2. **D5:** Módulo propio `condominium_people` desde Fase 1

D7 y la regla de spine ya están cerrados en este documento.

---

*Fin del documento — v4.*
*Revisión independiente completada. Pendiente: confirmar D2 y D5 internamente → autorizar Fase 1.*
