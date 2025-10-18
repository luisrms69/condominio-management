# Guía de Mantenimiento - Sistema de Documentación

**Propósito:** Instructivo completo para mantener, actualizar y expandir la documentación del proyecto Condominium Management.

**Audiencia:** Claude Code, desarrolladores, mantenedores del proyecto.

**Fecha creación:** 2025-10-17

---

## 📁 Estructura de Directorios

### getting-started/

**Propósito:** Guías de inicio rápido para nuevos usuarios.

**Contenido:**
- Instalación paso a paso
- Quick start guides
- Architecture overview de alto nivel (no técnico)

**Cuándo actualizar:**
- Cambios en proceso de instalación
- Nuevos requisitos del sistema
- Actualizaciones versiones Frappe/ERPNext

**Formato:**
- Lenguaje simple, no técnico
- Paso a paso con ejemplos
- Screenshots recomendados (opcional)

---

### user-guide/

**Propósito:** Guías prácticas para usuarios finales (administradores de condominios, personal operativo).

**Contenido actual:**
- physical-spaces.md (10.5 KB)
- companies.md (15.2 KB)

**Cuándo actualizar:**
- Nuevos módulos implementados
- Cambios en UI/workflows
- Nuevos casos de uso identificados
- Feedback de usuarios reales

**Formato obligatorio:**
```markdown
# [Nombre Módulo] - Guía de Usuario

Descripción breve de funcionalidad.

---

## ¿Qué es [Módulo]?

Explicación conceptual simple.

### Conceptos Clave

Lista de conceptos importantes.

---

## Configuración Inicial de [Módulo]

### Paso 1: [Acción]
### Paso 2: [Acción]
### Paso 3: [Acción]

---

## [Operación Común 1]
## [Operación Común 2]

---

## Casos de Uso Comunes

### Caso 1: [Escenario Real]
**Escenario:** Descripción situación
**Checklist:**
- ✅ Paso 1
- ✅ Paso 2

---

## Buenas Prácticas

### Naming Convention para [Entidad]
✅ **Bueno:** Ejemplos
❌ **Evitar:** Contraejemplos

---

## Preguntas Frecuentes (FAQ)

### ¿Pregunta común?
Respuesta clara y directa.

---

## Integración con Otros Módulos

### Con [Módulo X]
**Relación:** Descripción
**Uso:** Casos prácticos

---

## Recursos Adicionales

- **Arquitectura Técnica**: [Link a docs técnicos](../development/architecture/...)
- **Guía de Administración**: [Link a admin guide](../admin-guide/...)

---

**Actualizado:** YYYY-MM-DD
**Para usuarios:** [Audiencia específica]
```

**Elementos obligatorios:**
- H1 header con "- Guía de Usuario"
- Sección "¿Qué es...?"
- Al menos 1 caso de uso completo
- FAQ con mínimo 2 preguntas
- Recursos Adicionales con cross-references
- Footer con fecha y audiencia

---

### admin-guide/

**Propósito:** Guías para administradores de sistema, configuración técnica, mantenimiento.

**Contenido actual:**
- configuration.md (5.5 KB)
- maintenance.md (10.7 KB)
- security.md

**Cuándo actualizar:**
- Nuevas opciones de configuración
- Cambios en arquitectura multi-company
- Nuevos comandos bench específicos
- Actualizaciones de seguridad
- Cambios en fixtures

**Formato obligatorio:**
```markdown
# [Tema] del Sistema

Descripción breve orientada a sysadmins.

---

## Configuración Inicial

### 1. [Tarea Configuración]
**Ir a:** Ruta UI
**Verificar:**
- ✅ Item 1
- ✅ Item 2

---

## [Sección Operacional]

### [Subsección]

**Comando:**
```bash
bench --site admin1.dev [comando]
```

**Acciones:**
- Paso 1
- Paso 2

---

## Checklist de [Área]

- [ ] Tarea 1
- [ ] Tarea 2

---

## Troubleshooting Común

### [Problema X]
**Diagnóstico:**
```bash
[comando diagnóstico]
```

**Solución:**
[pasos resolución]

---

## Recursos Adicionales

- [Link relacionado 1](...)
- [Link relacionado 2](...)

---

**Actualizado:** YYYY-MM-DD
**Para:** System Administrators [y rol adicional si aplica]
```

**Elementos obligatorios:**
- Comandos bash ejecutables (con --site admin1.dev)
- Checklists accionables
- Troubleshooting específico
- Footer con fecha y audiencia

---

### development/

**Propósito:** Documentación técnica completa para desarrolladores.

**Subdirectorios:**

#### development/architecture/

**Contenido:**
- overview.md (visión general módulos)
- domain-model.md (modelo dominio core)
- physical-spaces.md (114 KB - arquitectura completa)
- companies.md (arquitectura Companies module)
- committee-management.md (13.4 KB - arquitectura Committee)

**Cuándo actualizar:**
- Nuevos módulos implementados
- Decisiones arquitectónicas importantes (ADRs)
- Cambios en modelo de datos
- Refactorings mayores

**Formato obligatorio para arquitectura de módulo:**
```markdown
# [Nombre Módulo] - Arquitectura Técnica

Descripción técnica de alto nivel.

---

## Visión General

### Objetivo del Módulo
### Alcance
### Estado Actual

---

## DocTypes Principales

### 1. [DocType Name]

**Propósito:** Descripción técnica

**Campos principales:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| campo_1 | Data | Descripción |

**Validaciones:**
- Validación 1
- Validación 2

**Métodos principales:**
```python
def metodo_importante(self):
    """Descripción."""
    pass
```

---

## Decisiones Clave

### 1. [Nombre Decisión] (YYYY-MM-DD)

**Contexto:** ¿Por qué se necesitaba decisión?

**Decisión:** ¿Qué se decidió?

**Alternativas consideradas:**
1. Alternativa A - Razón rechazo
2. Alternativa B - Razón rechazo

**Consecuencias:**
- ✅ Positivas
- ⚠️ Trade-offs
- ❌ Limitaciones

**Fecha:** YYYY-MM-DD

---

## Flujos de Trabajo Principales

### Flujo 1: [Nombre]

**Trigger:** ¿Qué inicia el flujo?

**Pasos:**
1. Usuario hace X
2. Sistema valida Y
3. Se crea/actualiza Z

**Diagrama (opcional):**
```
[ASCII diagram o descripción]
```

---

## Testing

### Estrategia Testing

**Cobertura:**
- Layer 3: [Tests integración]
- Layer 4A: [Tests configuración]
- Layer 4B: [Tests performance]

**Archivos test:**
- tests/test_[module].py

---

## Integraciones

### Con [Módulo X]
**Tipo integración:** [API, Links, Hooks]
**Detalles:** Descripción técnica

---

## Roadmap

### Fase 1: [Nombre] ✅
- Feature 1
- Feature 2

### Fase 2: [Nombre] 🔄
- Feature pendiente 1

---

## Recursos Adicionales

- **User Guide**: [Link](../../user-guide/...)
- **Testing Guide**: [Link](../testing/...)

---

**Actualizado:** YYYY-MM-DD
**Estado módulo:** [Implementado/En desarrollo/Planificado]
```

**Elementos obligatorios:**
- Sección "DocTypes Principales" con tabla de campos
- Al menos 1 decisión arquitectónica embebida (formato ADR)
- Sección "Testing" con estrategia
- Roadmap con estado actual
- Cross-references a user guides y testing docs

#### development/testing/

**Contenido:**
- overview.md (estrategia testing general)
- layer3-guide.md (integration testing)
- layer4-guide.md (config/performance testing)
- best-practices.md (REGLAs consolidadas)

**Cuándo actualizar:**
- Nuevas metodologías de testing
- Cambios en framework de tests
- Nuevas REGLAs identificadas
- Issues framework Frappe que afecten testing

**Formato:**
- Ejemplos de código ejecutables
- Referencias a tests reales en condominium_management/tests/
- Comandos bench específicos

#### development/framework-knowledge/

**Contenido:**
- known-issues.md (limitaciones Frappe conocidas)
- workarounds.md (soluciones temporales)

**Cuándo actualizar:**
- Nuevo issue framework descubierto
- Workaround implementado
- Resolución upstream de issue conocido

**Formato:**
```markdown
## [ISSUE-XXX] Descripción Issue

**Problema:**
Descripción detallada.

**Contexto:**
- Versión Frappe: vXX
- Archivo afectado: path/to/file.py:línea

**Reproducción:**
```python
# Código mínimo que reproduce issue
```

**Workaround actual:**
```python
# Solución temporal implementada
```

**Tracking:**
- GitHub Issue: [Link si existe]
- Estimado resolución: vXX / Desconocido
```

#### development/workflows/

**Contenido:**
- git-workflow.md (estrategia git, commits, branches)
- ci-cd.md (pipeline GitHub Actions)
- troubleshooting.md (problemas comunes desarrollo)

**Cuándo actualizar:**
- Cambios en política de branches
- Nuevos hooks pre-commit
- Actualizaciones CI/CD
- Nuevos problemas comunes identificados

---

### reference/

**Propósito:** Referencias API, schemas, especificaciones técnicas (futuro).

**Estado actual:** Preparado para expansión.

**Cuándo crear contenido:**
- Cuando se expongan APIs REST
- Documentación autogenerada con mkdocstrings
- Schemas JSON formales

---

### changelog/

**Propósito:** Historial de cambios del proyecto.

**Contenido:**
- CHANGELOG.md (include de ../../CHANGELOG.md)

**Cuándo actualizar:**
- Ver CLAUDE.md RG-011 para workflow versioning
- Actualizar con cada release/milestone
- Formato Keep a Changelog

**IMPORTANTE:**
- CHANGELOG.md real está en root del proyecto
- docs/changelog/CHANGELOG.md solo hace include
- NO editar docs/changelog/CHANGELOG.md directamente

---

### instructions/

**Propósito:** Instrucciones temporales para comunicación con Claude Code (NO se commitea).

**Contenido:**
- Archivos .md temporales para instrucciones específicas
- Borradores de documentación
- Notas de trabajo en progreso
- Comunicación directa con Claude Code

**IMPORTANTE:**
- ✅ Este directorio está en .gitignore
- ❌ NO commitear archivos de este directorio
- ✅ Usar para trabajo temporal y comunicación
- ✅ Borrar archivos una vez incorporados a documentación oficial

**Ubicación documentación de mantenimiento:**
- Ver: `docs/development/workflows/documentation-maintenance.md` (este archivo)

---

## 🎨 Estándares de Formato

### Headers

**H1 (único por archivo):**
```markdown
# Título Descriptivo - Tipo de Doc
```

Ejemplos:
- `# Physical Spaces - Guía de Usuario`
- `# Companies - Arquitectura Técnica`
- `# Mantenimiento del Sistema`

**H2-H6 (jerarquía lógica):**
- H2 para secciones principales
- H3 para subsecciones
- Evitar saltos de nivel (H2 → H4)

### Footers

**Footer obligatorio para todos los docs:**
```markdown
---

**Actualizado:** YYYY-MM-DD
**Para:** [Audiencia específica]
```

O con información adicional:
```markdown
---

**Actualizado:** YYYY-MM-DD
**Estado módulo:** [Estado si es arquitectura]
**Para:** [Audiencia]
```

### Cross-References

**Formato obligatorio:**
```markdown
[Texto descriptivo](../ruta/relativa/archivo.md)
```

**Ejemplos:**
```markdown
- **Arquitectura Técnica**: [Physical Spaces Architecture](../development/architecture/physical-spaces.md)
- **Guía de Usuario**: [Companies User Guide](../../user-guide/companies.md)
```

**Reglas:**
- Usar rutas relativas SIEMPRE
- Texto descriptivo claro
- Verificar que links funcionan en MkDocs

### Code Blocks

**Bash:**
```markdown
```bash
bench --site admin1.dev migrate
```
```

**Python:**
```markdown
```python
def ejemplo():
    """Docstring en español."""
    return True
```
```

**Importante:**
- Siempre especificar lenguaje
- Balancear backticks (3 apertura, 3 cierre)
- Para comandos bench, usar `admin1.dev` como site ejemplo

### Listas y Checklists

**Lista simple:**
```markdown
- Item 1
- Item 2
```

**Lista numerada:**
```markdown
1. Primer paso
2. Segundo paso
```

**Checklist:**
```markdown
- [ ] Tarea pendiente
- [x] Tarea completada
- ✅ Tarea verificada
```

### Tablas

**Formato estándar:**
```markdown
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Valor 1   | Valor 2   | Valor 3   |
```

**Importante:**
- Headers en negrita automático
- Alineación consistente

### Emojis

**Uso permitido:**
- ✅ Para indicar "correcto"
- ❌ Para indicar "incorrecto/prohibido"
- ⚠️ Para advertencias
- 🔄 Para "en progreso"
- 📋 Para "pendiente"

**NO usar:**
- Emojis decorativos excesivos
- Emojis en títulos H1-H3 (salvo excepciones)

---

## 🔄 Procedimientos de Actualización

### Agregar Nueva Guía de Usuario

**Escenario:** Nuevo módulo implementado que necesita user guide.

**Pasos:**

1. **Crear archivo markdown:**
   ```bash
   touch docs/user-guide/[nombre-modulo].md
   ```

2. **Usar template user guide** (ver sección Formato Obligatorio arriba)

3. **Escribir contenido mínimo:**
   - ¿Qué es el módulo?
   - Configuración inicial (3-5 pasos)
   - Al menos 1 caso de uso completo
   - FAQ con 2-4 preguntas
   - Buenas prácticas
   - Cross-references

4. **Agregar a mkdocs.yml:**
   ```yaml
   nav:
     - User Guide:
       - Physical Spaces: user-guide/physical-spaces.md
       - Companies: user-guide/companies.md
       - [Nombre Módulo]: user-guide/[nombre-modulo].md  # ← AGREGAR AQUÍ
   ```

5. **Verificar build:**
   ```bash
   mkdocs build --strict
   ```

6. **Commit en feature branch:**
   ```bash
   git checkout -b feature/docs-user-guide-[modulo]
   git add docs/user-guide/[nombre-modulo].md mkdocs.yml
   git commit -m "docs(user-guide): agregar guía de usuario para [Módulo]"
   ```

---

### Agregar Nueva Arquitectura Técnica

**Escenario:** Nuevo módulo implementado que necesita documentación técnica.

**Pasos:**

1. **Crear archivo en architecture/:**
   ```bash
   touch docs/development/architecture/[nombre-modulo].md
   ```

2. **Usar template arquitectura** (ver sección development/architecture/ arriba)

3. **Contenido mínimo obligatorio:**
   - Visión general del módulo
   - Al menos 3 DocTypes documentados con tabla de campos
   - Al menos 1 decisión arquitectónica embebida (formato ADR)
   - Sección Testing con estrategia
   - Roadmap con estado actual

4. **Actualizar overview.md:**
   ```bash
   # Editar docs/development/architecture/overview.md
   # Agregar sección para nuevo módulo con estado y descripción
   ```

5. **Agregar a mkdocs.yml:**
   ```yaml
   nav:
     - Development:
       - Architecture:
         - Overview: development/architecture/overview.md
         - Physical Spaces: development/architecture/physical-spaces.md
         - Companies: development/architecture/companies.md
         - Committee Management: development/architecture/committee-management.md
         - [Nombre Módulo]: development/architecture/[nombre-modulo].md  # ← AQUÍ
   ```

6. **Verificar y commit:**
   ```bash
   mkdocs build --strict
   git checkout -b feature/docs-architecture-[modulo]
   git add docs/development/architecture/
   git add mkdocs.yml
   git commit -m "docs(architecture): agregar arquitectura técnica para [Módulo]"
   ```

---

### Actualizar Documentación Existente

**Escenario:** Cambio en funcionalidad, nueva feature, bug fix que afecta docs.

**Identificar qué actualizar:**

| Cambio | Documentos a actualizar |
|--------|------------------------|
| Nuevo campo en DocType | Architecture doc del módulo (tabla campos) + User guide (si visible al usuario) |
| Cambio workflow | User guide (sección casos de uso) + Architecture (flujos de trabajo) |
| Nueva validación | Architecture (sección validaciones) |
| Cambio UI | User guide (screenshots, pasos) |
| Nueva configuración | Admin guide (configuration.md o maintenance.md) |
| Nuevo comando bench | Admin guide + development/workflows/ |
| Issue framework nuevo | development/framework-knowledge/known-issues.md |
| Workaround implementado | development/framework-knowledge/workarounds.md |

**Pasos:**

1. **Feature branch:**
   ```bash
   git checkout -b feature/docs-update-[descripcion]
   ```

2. **Editar archivo(s) relevante(s)**

3. **Actualizar footer:**
   ```markdown
   **Actualizado:** 2025-10-17  # ← Fecha actual
   ```

4. **Verificar cross-references** siguen funcionando

5. **Build y commit:**
   ```bash
   mkdocs build --strict
   git add docs/
   git commit -m "docs([área]): actualizar [archivo] por [razón cambio]"
   ```

---

### Documentar Decisión Arquitectónica (ADR)

**Escenario:** Se toma decisión técnica importante que debe quedar registrada.

**Pasos:**

1. **Identificar archivo arquitectura relevante:**
   - Si afecta módulo específico → docs/development/architecture/[modulo].md
   - Si es decisión transversal → docs/development/architecture/overview.md

2. **Agregar en sección "Decisiones Clave":**
   ```markdown
   ## Decisiones Clave

   ### 1. [Decisión Existente] (YYYY-MM-DD)
   [...]

   ### X. [Nombre Nueva Decisión] (YYYY-MM-DD)

   **Contexto:**
   Describir situación que requería decisión. ¿Qué problema resolvemos?

   **Decisión:**
   ¿Qué decidimos hacer? Ser específico y técnico.

   **Alternativas consideradas:**
   1. **Alternativa A**: Descripción - Razón rechazo
   2. **Alternativa B**: Descripción - Razón rechazo
   3. **Alternativa C**: Descripción - Razón rechazo

   **Consecuencias:**
   - ✅ **Positivas**: Beneficios de la decisión
   - ⚠️ **Trade-offs**: Compromisos aceptados
   - ❌ **Limitaciones**: Qué NO resuelve

   **Fecha:** YYYY-MM-DD
   ```

3. **Actualizar footer del documento**

4. **Commit:**
   ```bash
   git add docs/development/architecture/[modulo].md
   git commit -m "docs(architecture): documentar decisión [nombre] en [módulo]"
   ```

---

## 🔧 Integración MkDocs

### Estructura mkdocs.yml

**Ubicación:** `/mkdocs.yml` (root del proyecto)

**Secciones principales:**
```yaml
site_name: Condominium Management
site_description: Sistema de Gestión de Condominios
theme:
  name: material
  # ...

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quick-start.md
  - User Guide:
    - Physical Spaces: user-guide/physical-spaces.md
    - Companies: user-guide/companies.md
  - Admin Guide:
    - Configuration: admin-guide/configuration.md
    - Maintenance: admin-guide/maintenance.md
    - Security: admin-guide/security.md
  - Development:
    - Setup: development/setup.md
    - Architecture:
      - Overview: development/architecture/overview.md
      # ...
    - Testing:
      - Overview: development/testing/overview.md
      # ...
  - Reference:
    - API Reference: reference/README.md
  - Changelog: changelog/CHANGELOG.md

plugins:
  - search
  - include-markdown
  - redirects:
      redirect_maps:
        'physical_spaces_architecture.md': 'development/architecture/physical-spaces.md'
        # ...

markdown_extensions:
  - toc:
      permalink: true
  - admonition
  - codehilite
  - tables
```

### Agregar Página a Navegación

**Regla:** TODA página markdown en docs/ DEBE estar en nav de mkdocs.yml

**Formato:**
```yaml
- [Título Mostrado]: ruta/relativa/archivo.md
```

**Jerarquía:**
```yaml
- Sección Nivel 1:
  - Subsección Nivel 2:
    - Página: archivo.md
  - Otra Subsección:
    - Página: archivo.md
```

**Importante:**
- Usar 2 espacios para indentación
- Título puede diferir del H1 del archivo
- Ruta relativa desde docs/

### Configurar Redirects

**Escenario:** Archivo movido de ubicación, evitar 404s.

**Agregar en redirect_maps:**
```yaml
plugins:
  - redirects:
      redirect_maps:
        'ruta/vieja/archivo.md': 'ruta/nueva/archivo.md'
```

**Ejemplo real:**
```yaml
redirect_maps:
  'physical_spaces_architecture.md': 'development/architecture/physical-spaces.md'
  'LAYER3_TESTING_GUIDE.md': 'development/testing/layer3-guide.md'
```

### Include-Markdown (CHANGELOG)

**Propósito:** CHANGELOG.md debe estar en root (convención) pero accesible en docs/

**Setup actual:**
```yaml
plugins:
  - include-markdown
```

**En docs/changelog/CHANGELOG.md:**
```markdown
{!../../CHANGELOG.md!}
```

**IMPORTANTE:**
- NO editar docs/changelog/CHANGELOG.md directamente
- Editar ../../CHANGELOG.md (root del proyecto)
- Include se procesa en build time

### Verificar Build

**Comando obligatorio antes de commit:**
```bash
mkdocs build --strict
```

**Flags:**
- `--strict`: Falla si hay warnings (links rotos, etc.)

**Errores comunes:**
- Links rotos (path incorrecto)
- Páginas en docs/ no incluidas en nav
- Headers duplicados
- Code fences desbalanceados

**Fix típico:**
```bash
# Si hay error "Page not found: xyz.md"
# Agregar xyz.md a nav en mkdocs.yml

# Si hay error "Link broken: [text](path)"
# Verificar path relativo correcto
```

### Servir Localmente (Desarrollo)

**Comando:**
```bash
mkdocs serve
```

**Acceso:**
http://127.0.0.1:8000

**Útil para:**
- Previsualizar cambios
- Verificar navegación
- Verificar cross-references
- Probar búsqueda

---

## 📋 Checklists

### Checklist: Agregar Nueva Documentación

- [ ] Crear archivo .md en directorio apropiado
- [ ] Usar template correcto según tipo de doc
- [ ] Incluir H1 header único
- [ ] Escribir contenido mínimo según template
- [ ] Agregar footer con fecha y audiencia
- [ ] Incluir cross-references relevantes
- [ ] Agregar página a mkdocs.yml nav
- [ ] Ejecutar `mkdocs build --strict` sin errores
- [ ] Crear feature branch apropiado
- [ ] Commit con mensaje convencional
- [ ] Actualizar fecha en docs relacionados si aplica

### Checklist: Actualizar Documentación Existente

- [ ] Identificar todos los docs que requieren actualización
- [ ] Crear feature branch `feature/docs-update-[descripcion]`
- [ ] Editar contenido afectado
- [ ] Actualizar footer con fecha actual
- [ ] Verificar cross-references siguen funcionando
- [ ] Ejecutar `mkdocs build --strict` sin errores
- [ ] Commit con mensaje descriptivo
- [ ] Si es cambio mayor, actualizar CHANGELOG.md

### Checklist: Documentar Decisión Arquitectónica

- [ ] Identificar archivo arquitectura relevante
- [ ] Agregar en sección "Decisiones Clave" con formato ADR
- [ ] Incluir: Contexto, Decisión, Alternativas, Consecuencias, Fecha
- [ ] Actualizar footer del documento
- [ ] Ejecutar `mkdocs build --strict`
- [ ] Commit: `docs(architecture): documentar decisión [nombre]`

---

## 🚨 Errores Comunes y Soluciones

### Error: "Page not found" en mkdocs build

**Causa:** Archivo .md existe en docs/ pero no está en mkdocs.yml nav

**Solución:**
```bash
# Agregar archivo a mkdocs.yml en sección apropiada
nano mkdocs.yml
# Añadir línea en nav
mkdocs build --strict  # Verificar
```

---

### Error: "Link broken" en mkdocs build

**Causa:** Cross-reference con path incorrecto

**Solución:**
```bash
# Verificar path relativo
# Desde docs/user-guide/companies.md → docs/development/architecture/companies.md
# Path correcto: ../development/architecture/companies.md

# NO: /development/architecture/companies.md (absoluto)
# NO: development/architecture/companies.md (sin ../)
```

---

### Error: Code fence desbalanceado

**Causa:** Apertura con 3 backticks pero cierre incorrecto

**Detección:**
```bash
# Contar backticks en archivo
grep -c '^```' docs/path/file.md
# Debe ser número par
```

**Solución:**
```markdown
# ✅ CORRECTO
```bash
comando
```

# ❌ INCORRECTO
```bash
comando
``  # ← Solo 2 backticks
```

---

### Error: H1 header duplicado

**Causa:** Más de un # header en archivo

**Detección:**
```bash
grep -n '^# ' docs/path/file.md
# Debe retornar solo 1 línea
```

**Solución:**
- Dejar solo 1 H1 al inicio del archivo
- Otros headers deben ser H2 (##) o inferiores

---

### Footer inconsistente

**Problema:** Footer no sigue formato estándar

**Formato correcto:**
```markdown
---

**Actualizado:** 2025-10-17
**Para:** [Audiencia]
```

**NO usar:**
```markdown
Updated: 2025-10-17  # ← Inglés
Last modified: ...    # ← Formato diferente
---
Actualizado: ...      # ← Sin **
```

---

## 🎯 Mejores Prácticas

### 1. Documentación como Código

- ✅ Docs versionados en git junto con código
- ✅ Feature branches para cambios docs
- ✅ Pull requests para review
- ✅ CI/CD verifica `mkdocs build --strict`

### 2. Single Source of Truth

- ✅ CHANGELOG.md en root (no duplicar)
- ✅ Include-markdown para referenciar
- ✅ Cross-references en lugar de duplicar contenido

### 3. Actualización Proactiva

**Cuándo actualizar docs:**
- ✅ DURANTE desarrollo de feature (no después)
- ✅ Antes de merge de PR
- ✅ Al documentar decisión arquitectónica
- ✅ Al descubrir issue framework

**NO hacer:**
- ❌ "Actualizaré docs después"
- ❌ Merge sin actualizar docs
- ❌ Docs desactualizados vs código

### 4. Audiencia Específica

**Separar claramente:**
- User guides → Usuarios finales (no técnico)
- Admin guides → Sysadmins (comandos, config)
- Development → Desarrolladores (técnico completo)

**NO mezclar:**
- Contenido técnico en user guides
- Tutoriales paso a paso en architecture docs

### 5. Ejemplos Reales

**Preferir:**
- ✅ Ejemplos ejecutables y testeables
- ✅ Comandos bash que funcionan
- ✅ Código Python sintácticamente correcto
- ✅ Screenshots de UI real (opcional)

**Evitar:**
- ❌ Pseudo-código genérico
- ❌ Ejemplos "TODO: agregar ejemplo"
- ❌ Placeholders sin contenido

### 6. Navegación Intuitiva

**Estructura lógica:**
- Getting Started → User Guide → Admin Guide → Development
- General → Específico
- Básico → Avanzado

**Cross-references abundantes:**
- Desde user guide → architecture (para profundizar)
- Desde architecture → user guide (para contexto)
- Desde troubleshooting → related guides

---

## 🔗 Referencias

### Documentación Externa

- **MkDocs**: https://www.mkdocs.org/
- **Material for MkDocs**: https://squidfunk.github.io/mkdocs-material/
- **Keep a Changelog**: https://keepachangelog.com/es/
- **Conventional Commits**: https://www.conventionalcommits.org/

### Documentación Interna

- **CLAUDE.md**: Reglas de desarrollo y comandos (root proyecto)
- **CHANGELOG.md**: Historial de cambios (root proyecto)
- **mkdocs.yml**: Configuración MkDocs (root proyecto)
- **docs/development/architecture/overview.md**: Visión general módulos

---

## 📞 Contacto y Soporte

**Para dudas sobre documentación:**
1. Consultar este archivo (MAINTENANCE.md)
2. Revisar CLAUDE.md (reglas generales)
3. Buscar ejemplos en docs/ existentes
4. GitHub Issues para problemas MkDocs

---

**Preparado por:** Claude Code
**Fecha:** 2025-10-17
**Versión:** 1.0
**Próxima revisión:** Al completar nuevos módulos mayores
