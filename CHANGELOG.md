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
- Plan testing sistema completo: Sección J (Manuales usuario/administrador post-testing)
- Plan testing: Checkpoint técnico integridad fixtures post A-C
- Plan testing: Item A7 con tabla fixtures críticos P0-P2
- Reporte testing Secciones A+I+B1: REPORTE-TESTING-A-C.md (85% completitud, 13/24 items)
- Diagnóstico completo acquisition_type.json: DIAGNOSTICO-ACQUISITION-TYPE.md (causa raíz, comparación diagnósticos, 3 opciones solución)
- Campo description en Policy Category DocType (Small Text)
- Fixture policy_category.json: 19 categorías profesionales completas con chapter_mapping y descriptions
- Diagnóstico policy_category.json: DIAGNOSTICO-POLICY-CATEGORY.md (análisis fixture P1, 15 categorías profesionales)
- Reporte Dashboard Consolidado: REPORTE-DASHBOARD-CONSOLIDADO.md (falso positivo script testing corregido)

### Changed
- Fixtures Companies: 9 habilitados (64%), 5 deshabilitados (36%) - acquisition_type + company_type + policy_category reparados
- Scripts obsoletos marcados con headers OBSOLETO (install.py, company_custom_fields.py)

### Fixed
- Violación RG-009: Custom fields Company ahora migran automáticamente vía fixtures
- Contaminación export-fixtures: 7 fixtures problemáticos protegidos con extensión .DISABLED
- Zero-config deployment: Nuevos sitios instalarán custom fields automáticamente
- **company_type.json: Reparado con códigos cortos (ADMIN, CONDO, PROV, CONTR) para compatibilidad test suite**
- **acquisition_type.json (P0): Reparado con required_documents poblados** - Script one-off idempotente, fixture habilitado, Committee Management desbloqueado
- **policy_category.json (P1): Habilitado con 19 categorías profesionales** - Campo description añadido, 15 categorías nuevas con chapter_mapping completo, 4 originales actualizadas
- **Script verificar_b2_b4_anticipado.py**: Corregido check B4 Dashboard Consolidado (buscaba DocType inexistente, ahora verifica 3 DocTypes módulo)

### Testing
- Ejecución testing Sección A (Preparación entorno): 8/8 items completados
- Ejecución testing Sección I (Roles migrables): 3/4 checks (75%), fixture roles faltante identificado
- Ejecución testing Sección B1 (Company test): 100% éxito, company_type.json reparación verificada
- Scripts automatización testing: verificar_roles_i1_i4.py, crear_company_test_b1.py, verificar_b2_b4_anticipado.py
- Script testing B2-B4 corregido: Dashboard Consolidado check ahora verifica DocTypes correctos del módulo

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
