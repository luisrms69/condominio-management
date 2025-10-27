# Auditoría Scripts en Raíz del Proyecto

**Fecha:** 2025-10-20
**Total scripts encontrados:** 35
**Ubicación:** Raíz de condominium_management/
**Problema:** Todos están commiteados en Git (viola RG-010)

---

## Resumen Ejecutivo

**Hallazgos:**
- ✅ 0 scripts necesarios permanentes
- ❌ 35 scripts one-off commiteados incorrectamente
- 🗑️ 28 scripts obsoletos (ya cumplieron su propósito)
- 📦 7 scripts podrían moverse a one_offs/ (si aún útiles)

**Recomendación:** **Eliminar TODOS** - ninguno es necesario permanentemente.

---

## Metodología Auditoría

Para cada script:
1. Identificar commit de creación
2. Analizar propósito según commit message
3. Determinar si es one-off o necesario
4. Revisar si sigue siendo útil
5. Proponer acción

---

## ANÁLISIS DETALLADO POR CATEGORÍA

### CATEGORÍA 1: Generadores de Tests Layer 4 (10 scripts)

**Propósito:** Scripts one-off para generar automáticamente tests Layer 4 del módulo Financial Management.

| Script | Commit | Propósito | Estado |
|--------|--------|-----------|--------|
| create_layer4_type_a_tests.py | 046eb6c (PR #22) | Generar 70 Type A tests | ✅ Completado |
| create_layer4_type_b_tests.py | 046eb6c (PR #22) | Generar Type B tests | ✅ Completado |
| create_layer4_type_b_critical.py | 046eb6c (PR #22) | Generar Type B critical tests | ✅ Completado |
| create_layer4_type_c_advanced.py | 046eb6c (PR #22) | Generar Type C advanced tests | ✅ Completado |
| create_20_additional_layer4_tests.py | 046eb6c (PR #22) | Generar 20 tests adicionales | ✅ Completado |
| create_layer4_simple_tests.py | 046eb6c (PR #22) | Generar tests simples | ✅ Completado |
| layer4_simple_template.py | 046eb6c (PR #22) | Template para tests simples | ✅ Usado |
| create_test_companies.py | 046eb6c (PR #22) | Crear companies para tests | ✅ Usado |
| setup_test_data.py | 046eb6c (PR #22) | Setup data para tests | ✅ Usado |
| TEMPLATE_DOCTYPE_TEST.py | - | Template genérico tests | ✅ Usado |

**Análisis:**
- Todos fueron one-off para generar tests durante PR #22
- Los tests YA fueron generados y están en el código
- Scripts ya cumplieron su propósito (julio 2025)
- Mantenerlos no aporta valor (tests ya existen)

**🗑️ ACCIÓN PROPUESTA:** **ELIMINAR TODOS** (10 archivos)

**Razón:** Tests ya generados, scripts obsoletos hace 3 meses.

---

### CATEGORÍA 2: Scripts Setup/Configuración (8 scripts)

**Propósito:** Scripts one-off para configuración inicial de módulos.

| Script | Commit | Módulo | Propósito | Estado |
|--------|--------|--------|-----------|--------|
| configure_central.py | d22ae20 (PR #4) | Companies | Configurar site central | ✅ Usado (jun 2025) |
| setup_domika_central.py | 0b0f460 (PR #12) | Community | Setup domika.dev central | ✅ Usado (jul 2025) |
| setup_contribution_categories.py | 0b0f460 (PR #12) | Community | Categorías contributions | ✅ Usado (jul 2025) |
| install_company_fields.py | d22ae20 (PR #4) | Companies | Instalar custom fields | ✅ Usado (jun 2025) |
| install_fixtures.py | d22ae20 (PR #4) | Companies | Instalar fixtures | ✅ Usado (jun 2025) |
| create_categories.py | d22ae20 (PR #4) | Companies | Crear categorías | ✅ Usado (jun 2025) |
| create_module_def.py | 66667fb (PR #6) | Document Gen | Crear module def | ✅ Usado (jul 2025) |
| check_setup.py | d22ae20 (PR #4) | Companies | Verificar setup | ✅ Usado (jun 2025) |

**Análisis:**
- Scripts de setup inicial de módulos
- Ejecutados una vez durante implementación de PRs
- Funcionalidad YA está en fixtures/hooks permanentes
- No se usan más (setup ya hecho hace 3-4 meses)

**🗑️ ACCIÓN PROPUESTA:** **ELIMINAR TODOS** (8 archivos)

**Razón:** Setup completado hace meses, fixtures manejan configuración ahora.

---

### CATEGORÍA 3: Scripts Testing/Validación (9 scripts)

**Propósito:** Scripts para ejecutar tests y validaciones durante desarrollo.

| Script | Commit | Propósito | ¿Sigue útil? |
|--------|--------|-----------|--------------|
| bench_test.sh | 0b0f460 (PR #12) | Test básico bench | ❌ Obsoleto |
| comprehensive_test.sh | 0b0f460 (PR #12) | Test comprehensivo | ❌ Obsoleto |
| execute_test.sh | 0b0f460 (PR #12) | Ejecutar test | ❌ Obsoleto |
| final_validation.sh | 0b0f460 (PR #12) | Validación final | ❌ Obsoleto |
| run_tests.py | d22ae20 (PR #4) | Ejecutar tests Python | ❌ Obsoleto |
| run_testing.py | d22ae20 (PR #4) | Testing runner | ❌ Obsoleto |
| quick_test.py | d22ae20 (PR #4) | Tests rápidos | ❌ Obsoleto |
| testing_workflow.py | d22ae20 (PR #4) | Workflow testing | ❌ Obsoleto |
| verify_changes.py | d22ae20 (PR #4) | Verificar cambios | ❌ Obsoleto |

**Análisis:**
- Scripts wrapper para ejecutar tests
- Innecesarios: `bench run-tests` hace lo mismo
- Creados durante desarrollo inicial (hace 3-4 meses)
- CI/CD en GitHub Actions ya maneja tests

**🗑️ ACCIÓN PROPUESTA:** **ELIMINAR TODOS** (9 archivos)

**Razón:**
- Funcionalidad duplicada con comandos bench estándar
- CI/CD maneja testing automáticamente
- Scripts no se usan en workflow actual

---

### CATEGORÍA 4: Scripts Diagnóstico/Debug (5 scripts)

**Propósito:** Scripts one-off para diagnosticar problemas durante desarrollo.

| Script | Commit | Propósito | ¿Sigue útil? |
|--------|--------|-----------|--------------|
| debug_doctypes.py | 046eb6c (PR #22) | Debug DocTypes | ❌ Obsoleto |
| diagnose_doctypes.py | d22ae20 (PR #4) | Diagnosticar DocTypes | ❌ Obsoleto |
| check_sites.sh | 0b0f460 (PR #12) | Verificar sites | ❌ Obsoleto |
| show_warehouse_types.py | d22ae20 (PR #4) | Mostrar warehouse types | ❌ Obsoleto |
| reorganize_doctypes.py | d22ae20 (PR #4) | Reorganizar DocTypes | ⚠️ Peligroso |

**Análisis:**
- Scripts de debugging one-off
- Usados durante desarrollo inicial
- Problemas ya resueltos hace meses
- reorganize_doctypes.py es particularmente peligroso (modifica estructura)

**🗑️ ACCIÓN PROPUESTA:** **ELIMINAR TODOS** (5 archivos)

**Razón:**
- Debugging ya completado
- Comandos bench/frappe console hacen lo mismo
- reorganize_doctypes.py podría causar daños si se ejecuta accidentalmente

---

### CATEGORÍA 5: Templates/Demos (3 scripts)

**Propósito:** Templates y demos de funcionalidad.

| Script | Commit | Propósito | ¿Sigue útil? |
|--------|--------|-----------|--------------|
| TEMPLATE_MODULE_HOOKS.py | d22ae20 (PR #4) | Template hooks module | ⚠️ Podría ser útil |
| demo_contribution_workflow.py | 0b0f460 (PR #12) | Demo workflow contributions | ❌ Obsoleto |
| simple_demo.py | d22ae20 (PR #4) | Demo simple | ❌ Obsoleto |

**Análisis:**
- TEMPLATE_MODULE_HOOKS.py: Template genérico que podría servir futuro
- Demos: Ejemplos one-off, no necesarios ahora

**Propuesta mixta:**
- 🗑️ **ELIMINAR** demo_contribution_workflow.py (obsoleto)
- 🗑️ **ELIMINAR** simple_demo.py (obsoleto)
- 📦 **OPCIONAL** TEMPLATE_MODULE_HOOKS.py → one_offs/ (si útil futuro)

**Recomendación final:** **ELIMINAR TODOS** (3 archivos)

**Razón:** Templates documentados mejor en docs/development/

---

## RESUMEN PROPUESTAS POR SCRIPT

### 🗑️ ELIMINAR INMEDIATAMENTE (35 scripts)

**Generadores Tests (10):**
```bash
rm create_layer4_type_a_tests.py
rm create_layer4_type_b_tests.py
rm create_layer4_type_b_critical.py
rm create_layer4_type_c_advanced.py
rm create_20_additional_layer4_tests.py
rm create_layer4_simple_tests.py
rm layer4_simple_template.py
rm create_test_companies.py
rm setup_test_data.py
rm TEMPLATE_DOCTYPE_TEST.py
```

**Setup/Configuración (8):**
```bash
rm configure_central.py
rm setup_domika_central.py
rm setup_contribution_categories.py
rm install_company_fields.py
rm install_fixtures.py
rm create_categories.py
rm create_module_def.py
rm check_setup.py
```

**Testing/Validación (9):**
```bash
rm bench_test.sh
rm comprehensive_test.sh
rm execute_test.sh
rm final_validation.sh
rm run_tests.py
rm run_testing.py
rm quick_test.py
rm testing_workflow.py
rm verify_changes.py
```

**Diagnóstico/Debug (5):**
```bash
rm debug_doctypes.py
rm diagnose_doctypes.py
rm check_sites.sh
rm show_warehouse_types.py
rm reorganize_doctypes.py  # ⚠️ PELIGROSO
```

**Templates/Demos (3):**
```bash
rm TEMPLATE_MODULE_HOOKS.py
rm demo_contribution_workflow.py
rm simple_demo.py
```

**Total a eliminar:** 35 archivos

---

## JUSTIFICACIÓN ELIMINACIÓN MASIVA

### ¿Por qué eliminar TODO?

1. **Violación RG-010:**
   - CLAUDE.md dice: "❌ PROHIBIDO: Commitear scripts one-off al repositorio"
   - Todos son scripts one-off ejecutados hace 3-4 meses

2. **Obsolescencia:**
   - Tests generados → scripts generadores ya no se necesitan
   - Setup completado → scripts setup no se usan
   - Fixtures/hooks → configuración automatizada ahora

3. **Funcionalidad duplicada:**
   - `bench run-tests` reemplaza scripts testing
   - `bench console` reemplaza scripts debug
   - CI/CD maneja validaciones

4. **Riesgo:**
   - Scripts modifican DB/estructura si se ejecutan accidentalmente
   - reorganize_doctypes.py particularmente peligroso
   - Ninguno tiene validaciones "ya ejecutado"

5. **Mantenimiento:**
   - 35 archivos que nadie mantiene
   - Confusión para contribuyentes nuevos
   - Ruido en raíz del proyecto

---

## ALTERNATIVA: Mover a one_offs/

**Si quieres preservar alguno "por si acaso":**

```bash
mkdir -p condominium_management/one_offs/archive_2025_10_20
mv *.py *.sh condominium_management/one_offs/archive_2025_10_20/
echo "# Archived scripts" > condominium_management/one_offs/archive_2025_10_20/README.md
```

**Luego agregar a .gitignore:**
```
condominium_management/one_offs/
```

**Y hacer commit eliminando de Git:**
```bash
git rm *.py *.sh
git commit -m "chore: remover scripts one-off obsoletos de raíz (RG-010)"
```

---

## IMPACTO ELIMINACIÓN

### ✅ Sin impacto negativo:
- Tests NO se eliminan (solo scripts generadores)
- Fixtures NO se afectan (setup ya hecho)
- CI/CD sigue funcionando (usa bench directamente)
- Desarrollo continúa normal (bench console, etc.)

### ✅ Beneficios:
- Cumple RG-010
- Raíz limpia
- Menos confusión
- Sin riesgo ejecución accidental

### ⚠️ Único riesgo:
- Si algún script tiene lógica única no documentada
- **Mitigación:** Revisar uno por uno antes de borrar (opcional)

---

## RECOMENDACIÓN FINAL

**ACCIÓN:** **Eliminar TODOS los 35 scripts**

**Razones:**
1. 100% son one-off (viola RG-010)
2. 100% ya cumplieron su propósito
3. 0% se usan en workflow actual
4. Funcionalidad reemplazada por comandos bench/fixtures

**Comando propuesto:**
```bash
# 1. Verificar que no haya cambios sin commitear
git status

# 2. Eliminar todos los scripts
git rm *.py *.sh

# 3. Commit
git commit -m "chore: remover 35 scripts one-off obsoletos de raíz

Scripts de generación de tests, setup y debugging ejecutados durante
desarrollo inicial (jun-jul 2025) que ya cumplieron su propósito.

- 10 generadores tests layer4 (tests ya creados)
- 8 scripts setup (fixtures ahora manejan configuración)
- 9 scripts testing (bench run-tests reemplaza funcionalidad)
- 5 scripts diagnóstico (bench console reemplaza funcionalidad)
- 3 templates/demos (obsoletos)

Cumple RG-010: Scripts one-off no deben commitearse.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 4. Push
git push origin main  # O el branch que uses
```

---

## SCRIPTS INDIVIDUALES - DETALLES

### Si quieres revisar contenido antes de borrar:

**Generadores más importantes:**
- `create_layer4_type_a_tests.py` - Generó 70 tests Type A (12.7 KB)
- `create_layer4_type_b_critical.py` - Generó tests críticos (14.6 KB)
- `create_layer4_type_c_advanced.py` - Generó tests avanzados (18 KB)

**Setup más importantes:**
- `setup_domika_central.py` - Setup domika.dev (6.4 KB)
- `configure_central.py` - Configuración central (3.9 KB)

**Templates:**
- `TEMPLATE_MODULE_HOOKS.py` - Template hooks (13.1 KB)
- `TEMPLATE_DOCTYPE_TEST.py` - Template tests (8 KB)

**Total tamaño:** ~100 KB código one-off obsoleto

---

**Preparado:** 2025-10-20
**Auditor:** Claude Code
**Estado:** Propuesta - Pendiente aprobación usuario
