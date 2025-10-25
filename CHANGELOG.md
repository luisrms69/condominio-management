# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Added
- Sistema de documentación con MkDocs
- Estructura base de carpetas docs/
- Configuración inicial del proyecto
- Fixture custom_field.json con 27 custom fields Company (migración de código programático)
- Documentación auditoría: CUSTOM-FIELDS-AUDIT-REPORT.md
- Documentación investigación: EXPORT-FIXTURES-INVESTIGATION.md

### Changed
- Fixtures Companies: 8 habilitados (7 válidos + 1 reparado), 6 deshabilitados (contaminados/errores)
- Scripts obsoletos marcados con headers OBSOLETO (install.py, company_custom_fields.py)

### Fixed
- Violación RG-009: Custom fields Company ahora migran automáticamente vía fixtures
- Contaminación export-fixtures: 7 fixtures problemáticos protegidos con extensión .DISABLED
- Zero-config deployment: Nuevos sitios instalarán custom fields automáticamente
- **company_type.json: Reparado con códigos cortos (ADMIN, CONDO, PROV, CONTR) para compatibilidad test suite**

## [0.1.0] - 2025-10-17

### Added
- Módulo Physical Spaces con jerarquía nested set
- Sistema de categorías de espacios (Space Category)
- Componentes recursivos (Space Component)
- Tipos de componentes (Component Type)
- Módulo Companies con extensiones para condominios

### Testing
- Tests Layer 3 para Physical Spaces
- Tests Layer 4 para validaciones complejas
- Framework de testing granular (REGLAs 42-59)

---

**Formato:** [Keep a Changelog](https://keepachangelog.com/es/)
**Versionado:** [Semántico 0.x.x](https://semver.org/lang/es/) (Alpha)
