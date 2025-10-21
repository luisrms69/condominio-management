# Arquitectura - Overview

Visión general de la arquitectura del sistema de gestión de condominios.

---

## Módulos Core Implementados

### 1. Companies
**Estado:** ✅ Implementado
**Propósito:** Gestión de contratos entre administradoras y condominios

**DocTypes principales:**
- Service Management Contract
- Condominium Information
- Master Data Sync Configuration

**[Ver documentación completa →](companies.md)**

---

### 2. Physical Spaces
**Estado:** ✅ Implementado
**Propósito:** Framework geoespacial con jerarquía ilimitada

**DocTypes principales:**
- Physical Space
- Space Category
- Space Component
- Component Type

**[Ver documentación completa →](physical-spaces.md)**

---

### 3. Residents (Planificado)
**Estado:** 🔄 En desarrollo
**Propósito:** Gestión de residentes y perfiles de usuarios

---

### 4. Access Control (Planificado)
**Estado:** 📋 Planificado
**Propósito:** Control de accesos con QR dinámicos

---

### 5. Maintenance Professional (Planificado)
**Estado:** 📋 Planificado
**Propósito:** Programación multi-nivel de mantenimiento

---

### 6. Committee Management
**Estado:** ✅ Implementado
**Propósito:** Gestión democrática digital completa con asambleas y votaciones

**DocTypes principales:**
- Committee Member
- Agreement Tracking
- Committee Meeting
- Assembly Management
- Voting System
- Committee Poll
- Community Event
- Committee KPI
- Meeting Schedule

**[Ver documentación completa →](committee-management.md)**

---

## Patrones Arquitectónicos Globales

### Override Class > Hooks
Preferencia por override de clases sobre hooks para lógica compleja.

**Razón:** Mayor control, mejor testing, menos efectos colaterales.

---

### Fixtures First
Toda configuración debe ser fixture para zero-config deployment.

**Razón:** Instalaciones nuevas funcionan sin configuración manual.

---

### Multi-Company Separation
Separación financiera completa usando sistema multi-company de ERPNext.

**Razón:** Contabilidad independiente por condominio.

---

### Nested Set para Jerarquías
Modelo nested set para estructuras jerárquicas ilimitadas.

**Razón:** Queries eficientes, soporte framework completo.

---

## Decisiones Transversales

### Idioma: Español Obligatorio
- Variables/código: inglés
- Labels/UI: español
- Mensajes: español

**Ver:** [CLAUDE.md RG-001](../../CLAUDE.md)

---

### Testing: Granular Híbrido
- Layer 3: Integración DocTypes
- Layer 4A: Configuration validation
- Layer 4B: Performance benchmarks

**Ver:** [Testing Best Practices](../testing/best-practices.md)

---

### Zero-Config Deployment
Todo debe funcionar después de `bench install-app` sin configuración manual.

**Implementación:** Fixtures para roles, permisos, configuraciones.

---

## Estructura de Módulos

```
condominium_management/
├── companies/           # Contratos y sincronización
├── physical_spaces/     # Framework geoespacial
├── residents/          # (Futuro) Gestión residentes
├── access_control/     # (Futuro) QR y accesos
├── maintenance_professional/  # (Futuro) Mantenimiento
└── committee_management/      # (Futuro) Asambleas
```

---

## Integración ERPNext

### DocTypes Heredados
- Company (core ERPNext)
- Contact (core Frappe)
- Address (core Frappe)

### DocTypes Nuevos
- Service Management Contract
- Condominium Information
- Physical Space
- [Más módulos...]

### Custom Fields
**Convención:** Prefijo `cm_*` para evitar conflictos

---

## Recursos Adicionales

### Arquitectura por Módulo
- [Physical Spaces](physical-spaces.md) - Espacios físicos jerárquicos
- [Companies](companies.md) - Contratos y sincronización
- [Domain Model](domain-model.md) - Modelo de dominio

### Otros Recursos
- [Testing](../testing/overview.md) - Estrategia testing
- [Framework Knowledge](../framework-knowledge/known-issues.md) - Known issues
- [Workflows](../workflows/git-workflow.md) - Procesos desarrollo

---

**Actualizado:** 2025-10-17
**Mantenido por:** Dev Team
