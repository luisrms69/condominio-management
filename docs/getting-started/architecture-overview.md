# Visión General de Arquitectura

## Módulos Core

### 1. Companies (Multi-Company)
Gestión de condominios independientes con separación financiera completa.

**DocTypes:**
- Company (heredado ERPNext)
- Condominium-specific settings

### 2. Physical Spaces
Sistema de espacios físicos jerárquicos con anidamiento ilimitado.

**DocTypes:**
- Physical Space
- Space Category
- Space Component
- Component Type

### 3. Residents
Gestión de residentes y usuarios del sistema.

**DocTypes:**
- Resident Profile
- Contact (heredado Frappe)

## Patrones Arquitectónicos

### Jerarquía Nested Set
Los espacios físicos utilizan el modelo **Nested Set** de Frappe para soportar jerarquías ilimitadas de manera eficiente.

### Multi-Company Separation
Separación financiera completa a nivel de base de datos usando el sistema multi-company de ERPNext.

### Override Class Pattern
Prioridad a override class sobre hooks para enlaces bidireccionales y lógica compleja.

## Más Información Técnica

Para documentación técnica detallada, ver:

- **[Arquitectura Desarrollo](../development/architecture/overview.md)**
- **[Physical Spaces Técnico](../development/architecture/physical-spaces.md)**
- **[Companies Técnico](../development/architecture/companies.md)**

---

**Última actualización:** 2025-10-17
