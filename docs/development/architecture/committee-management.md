# Committee Management - Arquitectura Técnica

Sistema completo de gestión democrática digital para comités de administración de condominios.

---

## Decisiones Clave

### 1. Testing Granular Methodology (2025-07-12)

**Contexto:**
El módulo Committee Management enfrentó crisis de testing con 82 métodos fallando en 8 de 9 DocTypes, 3,538 líneas de código con errores fundamentales.

**Decisión:**
Implementar REGLA #32 - Testing Granular Methodology con 4 capas (Unit → Mocked → Integration → Configuration) y base class compartida `CommitteeTestBaseGranular`.

**Alternativas consideradas:**
- Reparar tests existentes (estimado 12-16 horas)
- Reescritura desde cero con framework (estimado 8-12 horas) ← Seleccionada

**Consecuencias:**
- ✅ Reducción 200+ líneas duplicadas
- ✅ 1 base class reutilizable para 9 DocTypes
- ✅ Setup compartido (Company, User, Roles, Master data)
- ✅ Cleanup automático con error handling
- ✅ Validación JSON universal detecta inconsistencias

**Fecha:** 2025-07-12

---

### 2. Voting System con Digital Signatures (2025-07-10)

**Contexto:**
Necesidad de sistema de votación electrónica con trazabilidad legal y soporte para votación anónima.

**Decisión:**
Implementar Voting System DocType con digital signatures obligatorias, IP tracking para auditoría, y opción de votación anónima configurable.

**Alternativas consideradas:**
- Votación solo presencial registrada manualmente
- Sistema de votación sin trazabilidad digital ← Rechazada
- Votación electrónica con firma digital ← Seleccionada

**Consecuencias:**
- ✅ Trazabilidad completa de votos
- ✅ Cumplimiento legal con firma digital
- ✅ Flexibilidad votación anónima/pública
- ⚠️ Dependencias en cadena: Voting → Assembly → Physical Space → Space Category

**Fecha:** 2025-07-10

---

### 3. Assembly Management con Quorum Legal (2025-07-10)

**Contexto:**
Asambleas de condominios requieren cumplimiento legal estricto de quorum y convocatorias formales.

**Decisión:**
Implementar Assembly Management como DocType submittable con validación automática de quorum legal, proceso formal de convocatoria (primera y segunda llamada), y verificación de cumplimiento legal.

**Alternativas consideradas:**
- Sistema manual sin validación automática
- Validación de quorum simplificada
- Workflow submittable con validaciones estrictas ← Seleccionada

**Consecuencias:**
- ✅ Cumplimiento legal garantizado
- ✅ Workflow formal con estados
- ✅ Trazabilidad completa de convocatorias
- ⚠️ Complejidad en validaciones de fechas y horarios

**Fecha:** 2025-07-10

---

### 4. Agreement Tracking con ToDo Integration (2025-07-09)

**Contexto:**
Acuerdos tomados en reuniones y asambleas requieren seguimiento automático del progreso y responsables.

**Decisión:**
Implementar Agreement Tracking DocType con auto-generación de número de acuerdo, progress tracking mediante child table, status automático por fechas vencidas, y creación automática de ToDo para responsables.

**Alternativas consideradas:**
- Seguimiento manual en documentos
- Sistema de tareas simple sin integración
- Agreement Tracking integrado con ToDo ← Seleccionada

**Consecuencias:**
- ✅ Seguimiento automático de acuerdos
- ✅ Integración nativa con sistema ToDo de Frappe
- ✅ Visibilidad en tiempo real del progreso
- ✅ Template validado para otros DocTypes del módulo

**Fecha:** 2025-07-09

---

### 5. Committee Member con Roles Únicos (2025-07-09)

**Contexto:**
Comités de administración tienen roles específicos (Presidente, Secretario, Tesorero, Vocales) que deben ser únicos por comité y tener permisos diferenciados.

**Decisión:**
Implementar Committee Member DocType con constraint de roles únicos por comité, integración con Property Registry para vincular a residentes, expense approval limits por rol, y capacidad de firma digital.

**Alternativas consideradas:**
- Roles flexibles sin restricción de unicidad
- Permisos homogéneos para todos los miembros
- Roles únicos con permisos granulares ← Seleccionada

**Consecuencias:**
- ✅ Prevención de duplicación de roles críticos (ej: dos Presidentes)
- ✅ Auto-assignment de committee_position_weight para ordenamiento
- ✅ Permission flags diferenciados por rol
- ✅ Business logic validation en tests

**Fecha:** 2025-07-09

---

## Visión General

El módulo Committee Management implementa gestión democrática digital completa para comités de administración de condominios, cubriendo desde reuniones ordinarias hasta asambleas formales con votación electrónica.

### Módulos Principales

**Gestión de Comité:**
- Committee Member - Miembros con roles y permisos
- Committee KPI - Métricas de performance

**Reuniones y Asambleas:**
- Committee Meeting - Reuniones ordinarias con agenda
- Meeting Schedule - Programación anual de reuniones
- Assembly Management - Asambleas formales con quorum legal

**Votación y Consenso:**
- Voting System - Votación electrónica con trazabilidad
- Committee Poll - Encuestas rápidas para consensus

**Seguimiento y Eventos:**
- Agreement Tracking - Seguimiento automático de acuerdos
- Community Event - Organización de eventos comunitarios

---

## DocTypes Principales

### 1. Committee Member

Gestión de miembros del comité con roles específicos y permisos diferenciados.

**Campos principales:**
- `member_name` (Link a Resident) - Residente que es miembro
- `committee_role` (Select) - Presidente, Secretario, Tesorero, Vocal
- `start_date`, `end_date` (Date) - Período de servicio
- `expense_approval_limit` (Currency) - Límite de aprobación de gastos
- `can_approve_expenses`, `can_sign_documents` (Check) - Permisos

**Validaciones:**
- Role único por comité (solo un Presidente, un Secretario, etc.)
- Integration con Property Registry para verificar residencia
- Auto-assignment de `committee_position_weight` para ordenamiento

**Testing:**
12/12 tests OK (~1.7s) - Unique constraints y auto-assignment validados

---

### 2. Agreement Tracking

Seguimiento automático de acuerdos con integración ToDo.

**Campos principales:**
- `agreement_number` (Data) - Auto-generado
- `agreement_title` (Data) - Título del acuerdo
- `description` (Text Editor) - Descripción detallada
- `responsible_person` (Link a User) - Responsable
- `due_date` (Date) - Fecha límite
- `status` (Select) - Pending, In Progress, Completed, Overdue
- `progress_tracking` (Table) - Child table con milestones

**Funcionalidades:**
- Auto-generación de número de acuerdo secuencial
- Status automático basado en fechas vencidas
- Creación automática de ToDo para responsable
- Progress tracking con child table

**Testing:**
12/12 tests OK (~1.8s) - Template base validado para framework testing

---

### 3. Committee Meeting

Gestión de reuniones con agenda y asistencia.

**Campos principales:**
- `meeting_title` (Data) - Título de la reunión
- `meeting_date` (Date) - Fecha de la reunión
- `meeting_type` (Select) - Ordinaria, Extraordinaria
- `meeting_format` (Select) - Presencial, Virtual, Híbrida
- `agenda_items` (Table) - Child table con items de agenda
- `attendance` (Table) - Child table con asistencia

**Funcionalidades:**
- Agenda management con voting tracking
- Virtual/Hybrid meeting support (integración futura con videoconferencia)
- Attendance automation
- Minutes generation ready (integración futura con templates)

**Validaciones:**
- Required fields: meeting_title, meeting_date, meeting_type, meeting_format
- Validación de fechas pasadas
- Hooks con campo `meeting_time` (por implementar)

---

### 4. Assembly Management

Gestión formal de asambleas con cumplimiento legal de quorum.

**Campos principales:**
- `assembly_type` (Select) - Ordinaria, Extraordinaria
- `convocation_date` (Date) - Fecha de convocatoria
- `assembly_date` (Date) - Fecha de asamblea
- `first_call_time`, `second_call_time` (Time) - Horarios llamadas
- `physical_space` (Link) - Ubicación de la asamblea
- `quorum_percentage` (Percent) - Porcentaje de quorum requerido
- `attendees` (Table) - Child table con asistentes

**Workflow:**
1. Convocatoria formal (emails automáticos)
2. Primera llamada con quorum completo
3. Segunda llamada con quorum reducido
4. Validación automática de quorum legal
5. Submit para formalizar

**Validaciones:**
- Quorum validation automática
- Legal compliance verification
- Required fields: assembly_type, convocation_date, assembly_date, first_call_time, second_call_time, physical_space
- Hooks con campo `extraordinary_reason` (por implementar para asambleas extraordinarias)

---

### 5. Voting System

Sistema de votación electrónica con trazabilidad legal.

**Campos principales:**
- `voting_topic` (Data) - Tema a votación
- `voting_method` (Select) - Abierta, Secreta
- `eligible_voters` (Table) - Child table con votantes elegibles
- `votes_cast` (Table) - Child table con votos emitidos
- `digital_signature` (Data) - Firma digital del votante
- `ip_address` (Data) - IP tracking para auditoría
- `anonymous` (Check) - Votación anónima

**Funcionalidades:**
- Electronic voting con digital signatures
- Anonymous voting opcional
- Real-time results calculation
- IP tracking para auditoría y seguridad

**Dependencias:**
- Committee Member (para elegibles)
- Assembly Management (contexto de votación)
- Physical Space → Space Category (dependencias en cadena)

---

### 6. Committee Poll

Polling rápido para consensus building.

**Campos principales:**
- `poll_title` (Data) - Título de la encuesta
- `poll_description` (Text) - Descripción
- `poll_options` (Table) - Child table con opciones
- `responses` (Table) - Child table con respuestas
- `anonymous` (Check) - Respuestas anónimas
- `deadline` (Date) - Fecha límite

**Funcionalidades:**
- Quick consensus polls con child table poll_options
- Real-time response tracking
- Anonymous support
- Integration con Committee Meeting

**Testing:**
Framework granular aplicado - Layer 1 tests 100% exitosos, child table requirement documentado

---

### 7. Community Event

Organización de eventos comunitarios.

**Campos principales:**
- `event_name` (Data) - Nombre del evento
- `event_date` (Date) - Fecha del evento
- `physical_space` (Link) - Ubicación
- `budget` (Currency) - Presupuesto asignado
- `registrations` (Table) - Child table con registros
- `evaluation` (Table) - Child table con evaluación post-evento

**Funcionalidades:**
- Event planning con budget tracking
- Registration management
- Resource allocation
- Post-event evaluation

**Testing:**
Framework granular aplicado - Complex dependencies manejadas con mocking efectivo

---

### 8. Committee KPI

Métricas de performance del comité.

**Campos principales:**
- `kpi_period` (Select) - Mensual, Trimestral, Anual
- `meetings_held` (Int) - Reuniones realizadas
- `agreements_completed` (Int) - Acuerdos completados
- `completion_rate` (Percent) - Tasa de cumplimiento
- `trend_analysis` (Table) - Child table con análisis de tendencia

**Funcionalidades:**
- Performance metrics automáticos
- Trend analysis
- Dashboard data provision
- Comparative reporting

**Testing:**
Framework granular aplicado - Diagnostic tests identifican field mismatch en hooks

---

### 9. Meeting Schedule

Programación anual de reuniones.

**Campos principales:**
- `schedule_year` (Int) - Año de programación
- `scheduled_meetings` (Table) - Child table con reuniones programadas
- `template_agenda` (Text) - Agenda template base
- `auto_create_meetings` (Check) - Creación automática

**Workflow:**
1. Crear programación anual (submittable)
2. Submit para formalizar
3. Auto-creación de Committee Meeting según schedule
4. Sync con Committee Meeting

**Testing:**
Framework granular aplicado - Submittable workflow + child table manejado exitosamente

---

## Flujos de Trabajo Principales

### Flujo 1: Reunión Ordinaria del Comité

```
1. Meeting Schedule → auto-create → Committee Meeting
2. Committee Meeting → agenda_items definidos
3. Durante reunión → votes en agenda items
4. Acuerdos tomados → Agreement Tracking created
5. Agreement Tracking → ToDo created para responsables
6. Progress tracking → actualización de milestones
7. Completion → status "Completed"
```

### Flujo 2: Asamblea Formal con Votación

```
1. Assembly Management created → convocation_date set
2. Email automático → convocation a todos los residentes
3. assembly_date llega → first_call_time
4. Quorum validation → si cumple, procede
5. Si no cumple → second_call_time con quorum reducido
6. Voting System activated → digital signatures
7. Real-time vote counting
8. Assembly submit → formalización
9. Minutes generation (futuro)
```

### Flujo 3: Seguimiento de Acuerdos

```
1. Agreement Tracking created (manual o desde Meeting)
2. responsible_person assigned → ToDo auto-created
3. progress_tracking child table → milestones
4. due_date approaching → notifications
5. Status auto-update basado en fechas
6. Completion → Agreement closed
7. KPI metrics updated
```

---

## Integración con Otros Módulos

### Con Physical Spaces

**Uso:**
- Assembly Management vincula con Physical Space para ubicación
- Community Event usa Physical Space para venue
- Committee Meeting puede vincular a espacio específico

**Dependencias:**
- Space Category (dependencia en cadena para Voting System)
- Physical Space validation para capacidad de eventos

### Con Companies

**Uso:**
- Committee Member vinculado a Company (condominio)
- Multi-company support para múltiples condominios
- Financial separation de budgets por Company

**Validaciones:**
- Committee roles únicos por Company
- KPI metrics por Company

### Con Residents (Futuro)

**Integración planificada:**
- Committee Member links a Resident Profile
- Voting System eligible voters desde Residents
- Assembly attendees desde Residents
- Property Registry validation

---

## Framework de Testing

### REGLA #32 - Testing Granular Methodology

El módulo Committee Management implementa framework de testing granular de 4 capas:

**Layer 1: Unit Tests**
- Validación de campos individuales
- Required fields configuration
- JSON vs Meta consistency

**Layer 2: Mocked Tests**
- Business logic con dependencies mockeadas
- Validation hooks
- Auto-assignments y cálculos

**Layer 3: Integration Tests**
- Flujos completos multi-DocType
- Validación con base de datos real
- Dependency chains

**Layer 4: Configuration Tests**
- Metadata integrity
- Permission configuration
- Hooks & events validation

### CommitteeTestBaseGranular

Base class compartida para todos los DocTypes del módulo:

**Características:**
- Shared infrastructure setup (Company, User, Roles, Master data)
- Enhanced REGLA #29 cleanup con error handling
- Universal validation tests parametrizados
- Configuración declarativa por DocType

**Beneficios:**
- 1 base class → 9 DocTypes reutilizan
- Eliminación 200+ líneas duplicadas
- Setup compartido creado una vez
- Cleanup automático en reverse dependency order

**Ver:** [Testing Best Practices](../testing/best-practices.md) para detalles completos de REGLA #32

---

## Roadmap de Implementación

### Fase 1: Framework Development ✅ COMPLETADO (2025-07-12)
- ✅ Agreement Tracking validation exhaustiva
- ✅ CommitteeTestBase framework creation
- ✅ Expert validation y mejoras implementadas

### Fase 2: Core DocTypes ✅ COMPLETADO (2025-07-12)
- ✅ Agreement Tracking (12/12 tests OK)
- ✅ Committee Member (12/12 tests OK)
- ✅ Testing framework validation exitosa

### Fase 3: Framework Escalabilidad ✅ COMPLETADO (9/9 DocTypes)
- ✅ Assembly Management - Framework granular aplicado
- ✅ Committee Meeting - Validation hooks identificadas
- ✅ Voting System - Dependencias en cadena documentadas
- ✅ Committee Poll - Child table requirements
- ✅ Committee KPI - Field mismatch diagnosticado
- ✅ Community Event - Complex dependencies manejadas
- ✅ Meeting Schedule - Submittable workflow validado

### Fase 4: Testing Granular ✅ COMPLETADO
- ✅ REGLA #32 implementada completamente
- ✅ Layer 1-4 tests: success rate 100%
- ✅ CommitteeTestBaseGranular framework escalable

### Fase 5: Deployment Preparation ✅ COMPLETADO
- ✅ Documentation architecture completa
- ✅ Framework documentado y reutilizable
- ✅ Testing templates para futuros módulos
- ✅ PR #18 actualizado y listo para review

### Fase 6: Production Ready (Planificado)
- 🔄 Integration con Residents module
- 🔄 Email automation para convocatorias
- 🔄 Minutes generation templates
- 🔄 Dashboard visualization de KPIs
- 🔄 Mobile app integration para votación

---

## Recursos Adicionales

- [Overview Arquitectura](overview.md) - Visión general sistema
- [Physical Spaces](physical-spaces.md) - Arquitectura espacios físicos
- [Companies](companies.md) - Arquitectura gestión condominios
- [Testing Best Practices](../testing/best-practices.md) - REGLA #32 detallada
- [Known Issues](../framework-knowledge/known-issues.md) - Framework limitations

---

**Actualizado:** 2025-10-17
**Basado en:** Implementación Committee Management module + REGLA #32 Testing Framework
