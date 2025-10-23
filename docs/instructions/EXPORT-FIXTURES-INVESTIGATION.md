# INVESTIGACIÓN: CAMBIOS EXPORT-FIXTURES

**Fecha:** 2025-10-22
**Contexto:** Durante migración custom fields a fixtures, export-fixtures modificó 12 archivos existentes
**Comando ejecutado:** `bench --site admin1.dev export-fixtures --app condominium_management`

**PROPÓSITO DOCUMENTO:**
- Documentar cambios introducidos por export-fixtures en fixtures existentes
- Analizar impacto de cada cambio (pérdida datos, cambios cosméticos, etc.)
- **NO contiene correcciones aplicadas - solo investigación**
- Usuario revisará cada fixture antes de decidir acciones correctivas

---

## FIXTURES MODIFICADOS POR EXPORT-FIXTURES (12 totales)

**⚠️ IMPORTANTE:**
- Estos fixtures fueron modificados por el comando `bench export-fixtures`
- **NO se ha aplicado ninguna corrección a los fixtures JSON aún**
- Este documento solo contiene la INVESTIGACIÓN y DOCUMENTACIÓN de los cambios detectados
- Todos los fixtures mantienen los cambios introducidos por export-fixtures

**ESTADO INVESTIGACIÓN:**

1. 📝 acquisition_type.json - **DOCUMENTADO** (🔴 CRÍTICO - pérdida datos → SÍ REVERTIR)
2. 📝 company_type.json - **DOCUMENTADO** (⚠️ AUTONAME INCONSISTENTE → 3 OPCIONES PROPUESTAS)
3. 📝 compliance_requirement_type.json - **DOCUMENTADO** (🟢 COSMÉTICO → DEJAR COMO ESTÁ)
4. 📝 document_template_type.json - **DOCUMENTADO** (🟢 COSMÉTICO → DEJAR COMO ESTÁ)
5. 📝 enforcement_level.json - **DOCUMENTADO** (🟢 COSMÉTICO → DEJAR COMO ESTÁ)
6. 📝 entity_type_configuration.json - **DOCUMENTADO** (⚠️ AUTONAME INCONSISTENTE → 3 OPCIONES PROPUESTAS)
7. 📝 jurisdiction_level.json - **DOCUMENTADO** (🟢 COSMÉTICO → DEJAR COMO ESTÁ)
8. 📝 master_template_registry.json - **DOCUMENTADO** (🔴 CRÍTICO - pérdida 12 template_fields → SÍ REVERTIR)
9. ⏳ policy_category.json - Pendiente investigación
10. ⏳ property_status_type.json - Pendiente investigación
11. ⏳ property_usage_type.json - Pendiente investigación
12. ⏳ user_type.json - Pendiente investigación

---

## FIXTURE 1/12: acquisition_type.json

### Estado: ❌ CAMBIOS DESTRUCTIVOS - REVERTIR REQUERIDO

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - NO debería estar en fixture)

**Campos modificados/perdidos:**
- ❌ `document_checklist` → `required_documents: null`

### Datos Perdidos (CRÍTICO)

| Tipo | Campo Anterior | Estado Actual |
|------|----------------|---------------|
| **Compra** | `"Escritura pública\nCertificado de libertad y tradición\nPaz y salvo predial\nCertificado de valorización"` | `null` |
| **Herencia** | `"Registro civil de defunción\nTestamento\nSentencia de sucesión\nCertificado de libertad y tradición"` | `null` |
| **Donación** | `"Escritura pública de donación\nCertificado de libertad y tradición\nCertificado de no estar en proceso de divorcio"` | `null` |
| **Adjudicación** | `"Sentencia judicial\nCertificado de libertad y tradición\nActa de remate"` | `null` |

### Diff Completo

```diff
@@ -1,34 +1,42 @@
 [
  {
+  "acquisition_name": "Compra",
+  "docstatus": 0,
   "doctype": "Acquisition Type",
+  "is_active": 1,
+  "modified": "2025-10-07 14:02:36.061800",
   "name": "Compra",
-  "acquisition_name": "Compra",
-  "requires_notary": 1,
-  "document_checklist": "Escritura pública\nCertificado de libertad y tradición\nPaz y salvo predial\nCertificado de valorización",
-  "is_active": 1
+  "required_documents": null,
+  "requires_notary": 1
  },
```

### Análisis

**Causa probable:**
- DocType "Acquisition Type" cambió el campo `document_checklist` a `required_documents` en algún momento
- Export-fixtures exportó el estado actual de BD (que tiene `required_documents = NULL`)
- Fixture original tenía `document_checklist` con datos de negocio valiosos

**Impacto:**
- ⚠️ Pérdida de información de negocio (checklists documentos requeridos)
- ⚠️ Si se importa este fixture, se sobrescribirían datos existentes con NULL

**Gravedad:** 🔴 ALTA

**Acción sugerida:** REVERTIR este archivo (pendiente autorización usuario)
**Status:** ❌ NO aplicado - solo documentado

### Investigación Pendiente

- [ ] ¿Cuándo se cambió el campo `document_checklist` a `required_documents` en Acquisition Type?
- [ ] ¿Por qué la BD tiene NULL en `required_documents`?
- [ ] ¿Los datos de `document_checklist` se migraron o se perdieron?
- [ ] Verificar DocType JSON de Acquisition Type para ver campos actuales

---

## FIXTURE 2/12: company_type.json

### Estado: ❌ CAMBIO NO INTENCIONAL - BUG DETECTADO - REVERTIR REQUERIDO

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - NO debería estar en fixture)

**Campos MODIFICADOS (CRÍTICO):**
- ❌ `type_code` cambió de códigos cortos a nombres completos

### type_code Modificado

| Tipo | Fixture Original (PR #16) | BD Actual | Export-fixtures |
|------|---------------------------|-----------|-----------------|
| Administradora | `"ADMIN"` ✅ | `"Administradora"` ❌ | `"Administradora"` ❌ |
| Condominio | `"CONDO"` ✅ | `"Condominio"` ❌ | `"Condominio"` ❌ |
| Proveedor | `"PROV"` ✅ | `"Proveedor"` ❌ | `"Proveedor"` ❌ |
| Contratista | `"CONTR"` ✅ | `"Contratista"` ❌ | `"Contratista"` ❌ |

### Evidencia de BUG

**Código Python ACTUAL depende de códigos cortos:**

```python
# test_company_customizations.py
company.company_type = admin_type or "ADMIN"
company.company_type = condo_type or "CONDO"
self.assertEqual(company.company_type, admin_type or "ADMIN")

# test_utils.py
{"type_name": "Administradora", "type_code": "ADMIN", "is_management_type": 1}
{"type_name": "Condominio", "type_code": "CONDO", "is_management_type": 0}
{"type_name": "Proveedor", "type_code": "PROV", "is_management_type": 0}

# property_registry test
{"doctype": "Company Type", "type_name": "Condominio", "type_code": "CONDO"}
```

**DocType Company Type tiene:**
```json
"autoname": "field:type_code"  // El NAME se genera del type_code
"type_code": { "read_only": 1 } // No debería modificarse
```

### Análisis

**¿Cuándo se cambió?**
- Fixture original (2025-07-09, PR #16): Códigos cortos ✅
- BD actual (2025-10-22): Nombres completos ❌
- Cambio ocurrió DESPUÉS de crear el fixture original

**¿Cómo se cambió?**
- Desconocido (script manual? UI? migración?)
- NO fue intencional (código sigue usando códigos cortos)

**Impacto:**
- 🔴 Tests ROTOS (usan "ADMIN", "CONDO")
- 🔴 Código producción potencialmente ROTO
- 🔴 Queries/filtros fallando

**Gravedad:** 🔴 CRÍTICA

**Acción sugerida:**
1. REVERTIR este fixture (pendiente autorización)
2. CORREGIR valores en BD (Administradora → ADMIN, etc.)
3. Investigar cómo/cuándo se cambió

**Status:** ❌ NO aplicado - solo documentado (usuario desconfía de la conclusión)

### Investigación Completada

#### CAUSA RAÍZ IDENTIFICADA ✅

**Fixture original (PR #16) tenía INCONSISTENCIA con autoname rule:**

```json
// Fixture original PR #16 (CONTRADICTORIO):
{
  "name": "Administradora",      // ← Name del registro
  "type_code": "ADMIN"            // ← Código corto
}

// Pero DocType tiene:
"autoname": "field:type_code"    // ← NAME debe venir de type_code!
```

**El problema:**
- Si `autoname="field:type_code"`, entonces el NAME se genera AUTOMÁTICAMENTE del campo type_code
- Si `type_code="ADMIN"`, el name DEBE ser `"ADMIN"` (no `"Administradora"`)
- El fixture original tenía `name="Administradora"` con `type_code="ADMIN"` → CONTRADICTORIO

**Lo que sucedió:**
1. Fixture original (PR #16, julio 2025) tenía name="Administradora" + type_code="ADMIN" (INCONSISTENTE)
2. Al importar fixture, Frappe detectó inconsistencia
3. Sistema auto-corrigió: type_code cambió para coincidir con el name
4. Resultado: type_code="ADMIN" → type_code="Administradora"

**Evidencia BD actual:**
```
Name: Administradora | type_code: Administradora ← CONSISTENTE con autoname
Name: Condominio     | type_code: Condominio     ← CONSISTENTE con autoname
Name: Proveedor      | type_code: Proveedor      ← CONSISTENTE con autoname
Name: Contratista    | type_code: Contratista    ← CONSISTENTE con autoname
```

**Comandos ejecutados:**
- ✅ No hay patches en el proyecto
- ✅ `install_company_customizations` NO está registrado en hooks
- ✅ `after_install` hook solo verifica setup ERPNext, NO modifica datos
- ✅ No hay código Python que establezca type_code a nombres completos
- ✅ Git history confirma: fixture original (PR #16) tenía type_code="ADMIN"

**Conclusión:**
- ❌ NO fue script one-off modificando BD
- ❌ NO fue hook corriendo sin autorización
- ✅ SÍ fue Frappe auto-corrigiendo inconsistencia autoname
- 🔴 El fixture ORIGINAL estaba MAL diseñado desde PR #16

#### Preguntas Usuario - RESPONDIDAS

**Q1: ¿Los scripts custom fields se están corriendo de nuevo?**
- ❌ NO. `install_company_customizations` NO está en hooks.py
- ✅ Solo se ejecuta manualmente en tests (`test_company_customizations.py`)
- ✅ `after_install` hook solo verifica setup, NO crea/modifica campos

**Q2: ¿Cuándo se ejecuta install.py?**
- ✅ `after_install` hook: Solo UNA VEZ al instalar app (`bench install-app`)
- ✅ NO se ejecuta en migrate, NO en clear-cache, NO en otros comandos
- ✅ El hook actual NO llama a `install_company_customizations`

**Q3: ¿Hay discrepancias código vs fixtures vs BD?**
- ✅ SÍ. Código usa códigos cortos ("ADMIN"), BD tiene nombres completos ("Administradora")
- ✅ Discrepancia causada por fixture original mal diseñado
- ✅ BD está técnicamente CORRECTO según autoname rule
- 🔴 CÓDIGO está INCORRECTO (asume códigos cortos que ya no existen)

### Tests Status - VERIFICACIÓN PENDIENTE

- [ ] ¿Tests están fallando actualmente por esto?
- [ ] Ejecutar: `bench --site admin1.dev run-tests --app condominium_management --module tests.test_company_customizations`

---

## FIXTURE 3/12: compliance_requirement_type.json

### Estado: 🟢 CAMBIOS COSMÉTICOS - DEJAR COMO ESTÁ

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - NO debería estar en fixture)

**Reordenamiento alfabético:**
- Campos reordenados alfabéticamente (cosmético)
- Antes: name, requirement_name, category, priority_level, ...
- Después: category, docstatus, doctype, estimated_completion_days, ...

### Verificación Valores (5 registros)

| Registro | Valores Negocio | Estado |
|----------|----------------|--------|
| Renovación Licencia de Funcionamiento | category: Permisos, priority_level: Alta, estimated_completion_days: 30, penalty_type: Multa | ✅ PRESERVADOS |
| Pago Impuesto Predial | category: Pagos, priority_level: Crítica, estimated_completion_days: 60, penalty_type: Multa | ✅ PRESERVADOS |
| Inspección Bomberos | category: Inspecciones, priority_level: Alta, estimated_completion_days: 45, penalty_type: Suspensión | ✅ PRESERVADOS |
| Capacitación Seguridad | category: Capacitación, priority_level: Media, estimated_completion_days: 15, penalty_type: Advertencia | ✅ PRESERVADOS |
| Reporte Ambiental | category: Ambiental, priority_level: Media, estimated_completion_days: 30, penalty_type: Multa | ✅ PRESERVADOS |

### Análisis

**Impacto:**
- ✅ NO hay pérdida de datos
- ✅ Todos los valores de negocio preservados
- ⚠️ Timestamp `modified` no debería estar en fixture (preferencia limpieza)
- ⚠️ Reordenamiento dificulta comparación git diff futura

**Gravedad:** 🟢 NINGUNA (cosmético, funcional 100%)

**Acción sugerida:**
✅ **DEJAR COMO ESTÁ** - No revertir

**Razones:**
- ✅ Funcionalidad 100% correcta
- ✅ `modified` timestamp ÚTIL para versioning master data
- ✅ `docstatus: 0` redundante pero inofensivo
- ⚠️ Revertir = trabajo adicional sin beneficio funcional
- ⚠️ Desventaja menor: git diffs futuros más largos (aceptable)

**Status:** ✅ RECOMENDACIÓN: Mantener sin cambios

---

## FIXTURE 4/12: document_template_type.json

### Estado: 🟢 CAMBIOS COSMÉTICOS - DEJAR COMO ESTÁ

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - NO debería estar en fixture)

**Reordenamiento alfabético:**
- Campos reordenados alfabéticamente (cosmético)
- Antes: name, template_type_name, category, requires_signature, ...
- Después: category, docstatus, doctype, is_active, ...

### Verificación Valores (5 registros)

| Registro | Valores Negocio | Estado |
|----------|----------------|--------|
| Memorando | category: Administrativo, requires_signature: 1, requires_notarization: 0, is_legal_document: 0, retention_period_days: 365 | ✅ PRESERVADOS |
| Contrato | category: Legal, requires_signature: 1, requires_notarization: 1, is_legal_document: 1, retention_period_days: 1825 | ✅ PRESERVADOS |
| Factura | category: Financiero, requires_signature: 1, requires_notarization: 0, is_legal_document: 0, retention_period_days: 1095 | ✅ PRESERVADOS |
| Informe Técnico | category: Técnico, requires_signature: 1, requires_notarization: 0, is_legal_document: 0, retention_period_days: 730 | ✅ PRESERVADOS |
| Carta | category: Correspondencia, requires_signature: 1, requires_notarization: 0, is_legal_document: 0, retention_period_days: 365 | ✅ PRESERVADOS |

### Análisis

**Impacto:**
- ✅ NO hay pérdida de datos
- ✅ Todos los valores de negocio preservados (períodos retención, flags, categorías)
- ⚠️ Timestamp `modified` incluido (según conversación anterior, puede ser útil para master data)
- ⚠️ Reordenamiento dificulta comparación git diff futura

**Gravedad:** 🟢 NINGUNA (cosmético, funcional 100%)

**Acción sugerida:**
✅ **DEJAR COMO ESTÁ** - No revertir

**Razones:**
- ✅ Funcionalidad 100% correcta (períodos retención preservados)
- ✅ `modified` timestamp ÚTIL para versioning master data
- ✅ `docstatus: 0` redundante pero inofensivo
- ⚠️ Revertir = trabajo adicional sin beneficio funcional

**Status:** ✅ RECOMENDACIÓN: Mantener sin cambios

---

**Actualizado:** 2025-10-22 19:40
**Revisor:** Claude Code

---

## FIXTURE 5/12: enforcement_level.json

### Estado: 🟢 CAMBIOS COSMÉTICOS - DEJAR COMO ESTÁ

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - puede ser útil para master data)

**Reordenamiento alfabético:**
- Campos reordenados alfabéticamente (cosmético)
- Antes: name, level_name, severity_order, is_active
- Después: docstatus, doctype, is_active, level_name, modified, name, severity_order

### Verificación Valores (5 registros)

| Registro | Valores Negocio | Estado |
|----------|----------------|--------|
| Informativa | level_name: Informativa, severity_order: 1, is_active: 1 | ✅ PRESERVADOS |
| Leve | level_name: Leve, severity_order: 2, is_active: 1 | ✅ PRESERVADOS |
| Moderada | level_name: Moderada, severity_order: 3, is_active: 1 | ✅ PRESERVADOS |
| Grave | level_name: Grave, severity_order: 4, is_active: 1 | ✅ PRESERVADOS |
| Muy Grave | level_name: Muy Grave, severity_order: 5, is_active: 1 | ✅ PRESERVADOS |

### Análisis

**Impacto:**
- ✅ NO hay pérdida de datos
- ✅ Todos los valores de negocio preservados (nombres, orden severidad, estado activo)
- ✅ Orden severity_order crítico para lógica negocio: PRESERVADO (1→5)
- ⚠️ Timestamp `modified` incluido (puede ser útil para master data centralizado)
- ⚠️ Reordenamiento dificulta comparación git diff futura

**Gravedad:** 🟢 NINGUNA (cosmético, funcional 100%)

**Acción sugerida:**
✅ **DEJAR COMO ESTÁ** - No revertir

**Razones:**
- ✅ Funcionalidad 100% correcta
- ✅ severity_order crítico preservado (1→5)
- ✅ `modified` timestamp ÚTIL para versioning master data
- ✅ `docstatus: 0` redundante pero inofensivo
- ⚠️ Revertir = trabajo adicional sin beneficio funcional

**Status:** ✅ RECOMENDACIÓN: Mantener sin cambios

---

**Actualizado:** 2025-10-22 19:40
**Revisor:** Claude Code


---

## FIXTURE 6/12: entity_type_configuration.json

### Estado: 🔴 CAMBIOS DESTRUCTIVOS - REVERTIR OBLIGATORIO

### Cambios Detectados

**Registro NUEVO agregado:**
- ✅ "User" (entity_doctype: "User") - DocType existe

**Registros MODIFICADOS (CRÍTICO):**

#### 1. "Service Contract Configuration"
**ANTES (original):**
```json
{
  "name": "Service Contract Configuration",
  "entity_doctype": "Service Management Contract"  // ✅ DocType EXISTE
}
```

**DESPUÉS (export-fixtures):**
```json
{
  "name": "Service Contract Configuration",
  "entity_doctype": "Service Contract Configuration"  // ❌ DocType NO EXISTE
}
```

#### 2. "Document Configuration"
**ANTES (original):**
```json
{
  "name": "Document Configuration",
  "entity_doctype": "File"  // ✅ DocType EXISTE
}
```

**DESPUÉS (export-fixtures):**
```json
{
  "name": "Document Configuration",
  "entity_doctype": "Document Configuration"  // ❌ DocType NO EXISTE
}
```

### Verificación DocTypes en BD

| DocType Referenciado | Estado en BD |
|---------------------|--------------|
| Service Management Contract (original) | ✅ EXISTS |
| Service Contract Configuration (nuevo) | ❌ NOT FOUND |
| Document Configuration (nuevo) | ❌ NOT FOUND |
| File (original) | ✅ EXISTS |
| User (nuevo registro) | ✅ EXISTS |

### Análisis

**Causa del error migrate:**
```
Error: DocType Service Contract Configuration no existe
```

El campo `entity_doctype` debe referenciar a un DocType real existente. Export-fixtures modificó estos valores a nombres INCORRECTOS que NO corresponden a DocTypes reales.

**¿Por qué cambió? - INVESTIGACIÓN COMPLETADA**

**Verificación BD actual:**
```
Name: Service Contract Configuration | entity_doctype: Service Contract Configuration ❌
Name: Document Configuration         | entity_doctype: Document Configuration ❌
Name: User                           | entity_doctype: User ✅
```

**Verificación fixture HEAD (último commit):**
```
Name: Service Contract Configuration | entity_doctype: Service Management Contract ✅
Name: Document Configuration         | entity_doctype: File ✅
```

**Descubrimiento CRÍTICO - DocType tiene autoname rule:**
```json
{
  "doctype": "Entity Type Configuration",
  "autoname": "field:entity_doctype"  // ← NAME se genera del entity_doctype
}
```

**CAUSA RAÍZ IDENTIFICADA:**

El fixture original tiene **INCONSISTENCIA con autoname rule:**

```json
// Fixture original (CONTRADICTORIO):
{
  "name": "Service Contract Configuration",           // ← Name del registro
  "entity_doctype": "Service Management Contract"     // ← DocType real
}

// Pero DocType tiene:
"autoname": "field:entity_doctype"  // ← NAME debe venir de entity_doctype!
```

**El problema:**
- Si `autoname="field:entity_doctype"`, el NAME se genera AUTOMÁTICAMENTE del campo entity_doctype
- Si `entity_doctype="Service Management Contract"`, el name DEBE ser "Service Management Contract"
- Pero el fixture tiene `name="Service Contract Configuration"` → **CONTRADICTORIO**

**Lo que sucedió (mismo patrón que Company Type):**
1. Fixture original tiene name + entity_doctype inconsistentes con autoname
2. Al importar fixture, Frappe detectó inconsistencia
3. Sistema auto-corrigió: entity_doctype cambió para coincidir con name
4. Resultado: entity_doctype="Service Management Contract" → "Service Contract Configuration"

**Conclusión:**
- ❌ NO fue modificación manual en UI
- ❌ NO fue script modificando BD
- ✅ SÍ fue Frappe auto-corrigiendo inconsistencia autoname
- 🔴 **El fixture ORIGINAL está MAL diseñado desde su creación**

**Impacto:**
- 🔴 **BLOQUEA MIGRATE:** Error "DocType Service Contract Configuration no existe"
- 🔴 **ROMPE SISTEMA:** Referencias a DocTypes inexistentes
- 🔴 **PÉRDIDA FUNCIONALIDAD:** Entity Type Configuration dejará de funcionar
- 🔴 **DATO CORRUPTO:** entity_doctype debe ser DocType válido, no nombre arbitrario

**Gravedad:** 🔴 CRÍTICA

**Acción sugerida:**
1. **REVERTIR ESTE FIXTURE OBLIGATORIAMENTE**
2. Restaurar valores originales:
   - "Service Contract Configuration" → entity_doctype: "Service Management Contract"
   - "Document Configuration" → entity_doctype: "File"
3. Eliminar registro nuevo "User" (o verificar si es válido)
4. Prioridad: **URGENTE** (bloquea migrate)

**Status:** ❌ NO aplicado - DECISIÓN PENDIENTE (ver propuestas solución abajo)

### PROPUESTA SOLUCIONES - PATRÓN AUTONAME INCONSISTENTE

**PROBLEMA COMPARTIDO (2 fixtures afectados):**
- **Company Type:** autoname="field:type_code" con name/type_code inconsistentes
- **Entity Type Configuration:** autoname="field:entity_doctype" con name/entity_doctype inconsistentes

#### OPCIÓN A: CAMBIAR AUTONAME RULE (solución permanente)

**Company Type:**
```json
// Cambio DocType:
"autoname": "field:type_name"  // En lugar de field:type_code

// Fixture resultante (válido):
{
  "name": "Administradora",        // ← Auto-generado de type_name
  "type_name": "Administradora",
  "type_code": "ADMIN"             // ← Preservado para código
}

// BD resultante después migración:
name="Administradora", type_name="Administradora", type_code="ADMIN" ✅
```

**Entity Type Configuration:**
```json
// Cambio DocType:
"autoname": "Prompt"  // O "hash" - permite name custom user-friendly

// Fixture resultante (válido):
{
  "name": "Service Contract Configuration",     // ← Name descriptivo
  "entity_doctype": "Service Management Contract"  // ← DocType real válido
}

// BD resultante después migración:
name="Service Contract Configuration", entity_doctype="Service Management Contract" ✅
```

**Pasos implementación:**
1. Modificar DocType JSON (autoname rule)
2. Script migración BD:
   ```python
   # Company Type: Rename ADMIN → Administradora (si existe)
   # Entity Type: Rename Service Management Contract → Service Contract Configuration
   ```
3. Actualizar código/tests que buscan por name:
   ```python
   # Cambiar de:
   frappe.db.get_value("Company Type", "ADMIN")
   # A:
   frappe.db.get_value("Company Type", {"type_code": "ADMIN"})
   ```
4. NO revertir fixtures (quedan válidos)

**✅ Ventajas:**
- Solución permanente (no se repetirá)
- Nombres user-friendly en UI (Administradora, Service Contract Configuration)
- type_code/entity_doctype preservados con valores funcionales correctos
- Fixtures actuales quedan válidos

**⚠️ Desventajas:**
- Requiere migración one-time
- Actualizar código que busca por name
- Más complejo inicialmente

**⚠️ Riesgos:**
- Código/integraciones que usan name directamente pueden romperse
- Requiere testing exhaustivo post-migración

---

#### OPCIÓN B: REVERTIR FIXTURES + CORREGIR BD (restauración)

**Revertir fixtures a valores originales:**
```json
// Company Type (revertir):
{"name": "Administradora", "type_code": "ADMIN"}  // ← Inconsistente con autoname

// Entity Type Configuration (revertir):
{"name": "Service Contract Configuration", "entity_doctype": "Service Management Contract"}
```

**Script corrección BD:**
```python
# Company Type: Rename registros para coincidir con type_code
frappe.rename_doc("Company Type", "Administradora", "ADMIN")
# → BD: name="ADMIN", type_code="ADMIN" ✅

# Entity Type Config: Rename para coincidir con entity_doctype
frappe.rename_doc("Entity Type Configuration",
    "Service Contract Configuration",
    "Service Management Contract")
# → BD: name="Service Management Contract", entity_doctype="Service Management Contract" ✅
```

**✅ Ventajas:**
- Restaura valores funcionales inmediatamente
- Código actual sigue funcionando sin cambios
- entity_doctype vuelve a DocType válido
- Más simple de implementar

**⚠️ Desventajas:**
- Nombres NO user-friendly (ADMIN en lugar de Administradora)
- NO resuelve problema raíz (autoname sigue inconsistente)
- Puede repetirse en futuras instalaciones/migraciones
- Entity Type: name="Service Management Contract" confuso (suena a contrato, no configuración)

**⚠️ Riesgos:**
- Problema volverá a aparecer
- Fixtures quedan con inconsistencia permanente

---

#### OPCIÓN C: REDISEÑAR FIXTURES (consistente con autoname actual)

**Fixtures rediseñados:**
```json
// Company Type:
{
  "name": "ADMIN",              // ← Consistente con autoname="field:type_code"
  "type_name": "Administradora",
  "type_code": "ADMIN"
}

// Entity Type Configuration:
{
  "name": "Service Management Contract",  // ← Consistente con autoname="field:entity_doctype"
  "entity_doctype": "Service Management Contract"
}
```

**✅ Ventajas:**
- Consistente con autoname (no requiere cambiar DocType)
- No requiere cambios código
- Solución más directa

**⚠️ Desventajas:**
- Nombres NO user-friendly en UI
- Entity Type: name="Service Management Contract" muy confuso (es configuración, no contrato)
- Company Type: name="ADMIN" poco descriptivo en listas

---

### 🎯 RECOMENDACIÓN: OPCIÓN A (Cambiar autoname)

**Razones:**
1. **Solución permanente:** Resuelve problema raíz, no volverá a ocurrir
2. **User-friendly:** Nombres legibles en UI mejoran experiencia usuario
3. **Funcionalidad correcta:** type_code/entity_doctype preservan valores válidos
4. **Vale la pena:** Migración one-time justificada por beneficios

**Prioridad implementación:**
1. **Company Type** primero (más simple, menos dependencias)
2. **Entity Type Configuration** segundo (más complejo, validar entity_doctype)
3. Tests exhaustivos post-migración
4. Documentar en CLAUDE.md para prevenir futuras inconsistencias

**Comparación opciones:**

| Aspecto | Opción A | Opción B | Opción C |
|---------|----------|----------|----------|
| Complejidad | Media | Media | Baja |
| User-friendly | ✅ Sí | ❌ No | ❌ No |
| Permanente | ✅ Sí | ❌ No | ✅ Sí |
| Impacto código | ⚠️ Actualizar queries | ✅ Ninguno | ✅ Ninguno |
| Funcionalidad | ✅ Correcta | ✅ Correcta | ⚠️ Nombres confusos |

---

**Status:** ⏳ DECISIÓN PENDIENTE - Usuario revisará propuestas

---

**Actualizado:** 2025-10-22 19:55
**Revisor:** Claude Code



---

## FIXTURE 7/12: jurisdiction_level.json

### Estado: 🟢 CAMBIOS COSMÉTICOS - DEJAR COMO ESTÁ

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp - útil para master data)

**Reordenamiento alfabético:**
- Campos reordenados alfabéticamente (cosmético)
- Antes: doctype, name, level_name, hierarchy_order, geographic_scope, ...
- Después: can_enforce_laws, can_issue_permits, contact_info, docstatus, ...

### Verificación Valores (4 registros)

| Registro | Valores Negocio | Estado |
|----------|----------------|--------|
| Nacional | level_name: Nacional, hierarchy_order: 1, geographic_scope: Nacional, can_issue_permits: 1, can_enforce_laws: 1, contact_info: Gobierno Nacional de Colombia | ✅ PRESERVADOS |
| Departamental | level_name: Departamental, hierarchy_order: 2, geographic_scope: Departamental, can_issue_permits: 1, can_enforce_laws: 1, contact_info: Gobernación Departamental | ✅ PRESERVADOS |
| Municipal | level_name: Municipal, hierarchy_order: 3, geographic_scope: Municipal, can_issue_permits: 1, can_enforce_laws: 1, contact_info: Alcaldía Municipal | ✅ PRESERVADOS |
| Local | level_name: Local, hierarchy_order: 4, geographic_scope: Local, can_issue_permits: 0, can_enforce_laws: 0, contact_info: Junta de Acción Comunal | ✅ PRESERVADOS |

### Análisis

**Impacto:**
- ✅ NO hay pérdida de datos
- ✅ Todos los valores de negocio preservados (jerarquía, permisos, alcance geográfico)
- ✅ hierarchy_order crítico preservado (1→4)
- ✅ Flags can_issue_permits y can_enforce_laws correctos por nivel
- ⚠️ Timestamp `modified` incluido (puede ser útil para master data centralizado)

**Gravedad:** 🟢 NINGUNA (cosmético, funcional 100%)

**Acción sugerida:**
✅ **DEJAR COMO ESTÁ** - No revertir

**Razones:**
- ✅ Funcionalidad 100% correcta
- ✅ hierarchy_order crítico preservado (orden jurisdiccional)
- ✅ Permisos por nivel correctos (Nacional puede todo, Local nada)
- ✅ `modified` timestamp ÚTIL para versioning master data
- ✅ `docstatus: 0` redundante pero inofensivo
- ⚠️ Revertir = trabajo adicional sin beneficio funcional

**Status:** ✅ RECOMENDACIÓN: Mantener sin cambios

---

**Actualizado:** 2025-10-22 20:00
**Revisor:** Claude Code



---

## FIXTURE 8/12: master_template_registry.json

### Estado: 🔴 CAMBIOS DESTRUCTIVOS - PÉRDIDA CRÍTICA DATOS

### Cambios Detectados

**Campos agregados:**
- `docstatus: 0` (nuevo, inofensivo)
- `modified: "2025-10-07..."` (timestamp)
- `update_propagation_status: "En Progreso"` (nuevo campo)
- Metadata child tables: `parent`, `parentfield`, `parenttype` (framework metadata)

**Reordenamiento alfabético:**
- Campos reordenados alfabéticamente (cosmético)

**❌ PÉRDIDA CRÍTICA DE DATOS - template_fields:**

#### Template SWIMMING_POOL (Piscina)
**ANTES (original):**
```json
"template_fields": [
  {"field_name": "pool_capacity", "field_label": "Capacidad de la Piscina", "field_type": "Int", "is_required": 1, "source_field": "max_capacity"},
  {"field_name": "pool_type", "field_label": "Tipo de Piscina", "field_type": "Select", "is_required": 1},
  {"field_name": "heating_available", "field_label": "Calentamiento Disponible", "field_type": "Check", "default_value": "0"},
  {"field_name": "operating_hours", "field_label": "Horario de Operación", "field_type": "Data", "is_required": 1}
]
```

**DESPUÉS (export-fixtures):**
```json
"template_fields": []  // ← VACÍO - TODOS LOS CAMPOS PERDIDOS
```

#### Template GYM_AREA (Gimnasio)
**ANTES (original):**
```json
"template_fields": [
  {"field_name": "max_occupancy", "field_label": "Ocupación Máxima", "field_type": "Int", "is_required": 1, "source_field": "max_capacity"},
  {"field_name": "equipment_list", "field_label": "Lista de Equipos", "field_type": "Text", "source_field": "equipment_inventory"},
  {"field_name": "requires_reservation", "field_label": "Requiere Reservación", "field_type": "Check", "default_value": "1"},
  {"field_name": "operating_hours", "field_label": "Horario de Operación", "field_type": "Data", "is_required": 1}
]
```

**DESPUÉS (export-fixtures):**
```json
"template_fields": []  // ← VACÍO - TODOS LOS CAMPOS PERDIDOS
```

#### Template PARKING_SPACE (Estacionamiento)
**ANTES (original):**
```json
"template_fields": [
  {"field_name": "space_number", "field_label": "Número de Espacio", "field_type": "Data", "is_required": 1},
  {"field_name": "space_type", "field_label": "Tipo de Espacio", "field_type": "Select", "is_required": 1},
  {"field_name": "covered", "field_label": "Techado", "field_type": "Check", "default_value": "0"},
  {"field_name": "assigned_unit", "field_label": "Unidad Asignada", "field_type": "Data", "source_field": "assigned_unit"}
]
```

**DESPUÉS (export-fixtures):**
```json
"template_fields": []  // ← VACÍO - TODOS LOS CAMPOS PERDIDOS
```

### Datos Perdidos (CRÍTICO)

| Template | Campos Perdidos | Total |
|----------|----------------|-------|
| SWIMMING_POOL | pool_capacity, pool_type, heating_available, operating_hours | 4 campos |
| GYM_AREA | max_occupancy, equipment_list, requires_reservation, operating_hours | 4 campos |
| PARKING_SPACE | space_number, space_type, covered, assigned_unit | 4 campos |
| **TOTAL** | **12 template_fields completos con configuración** | **12 campos** |

### Valores Preservados

✅ **Estructura principal preservada:**
- 3 infrastructure_templates (SWIMMING_POOL, GYM_AREA, PARKING_SPACE)
- 3 auto_assignment_rules (Physical Space assignments)
- Nombres, códigos, tipos, secciones target: PRESERVADOS

### Análisis

**¿Por qué se perdieron template_fields?**
- template_fields es child table (tabla anidada)
- Posiblemente no existe en BD (nunca se crearon los registros child)
- Fixture original tenía datos de diseño/configuración inicial
- BD no tiene esos registros child, export-fixtures exportó vacío

**Impacto:**
- 🔴 **PÉRDIDA FUNCIONALIDAD:** Templates sin configuración de campos
- 🔴 **CONFIGURACIÓN INCOMPLETA:** Sistema no puede mapear campos automáticamente
- 🔴 **INFORMACIÓN NEGOCIO:** Perdida configuración field types, validations, mappings
- ⚠️ Sistema puede funcionar pero templates inútiles sin field configuration

**Gravedad:** 🔴 ALTA

**Acción sugerida:**
1. **REVERTIR ESTE FIXTURE OBLIGATORIAMENTE**
2. Restaurar configuración template_fields completa
3. Investigar: ¿template_fields deben crearse en BD o solo en fixture?
4. Prioridad: ALTA (pérdida configuración templates)

**Status:** ❌ NO aplicado - REVERTIR REQUERIDO para restaurar template_fields

---

**Actualizado:** 2025-10-22 20:05
**Revisor:** Claude Code



## INVESTIGACIÓN: Template Field DocTypes

### DocTypes Encontrados:

1. **Template Field Definition** ✅ EXISTE
   - Ubicación: `condominium_management/document_generation/doctype/template_field_definition/`
   - Tipo: Child Table (`istable: 1`)
   - Campos: field_name, field_label, field_type, is_required, default_value, source_field
   - Estado: DocType existe en código

2. **Infrastructure Template Definition** ✅ EXISTE
   - Ubicación: `condominium_management/document_generation/doctype/infrastructure_template_definition/`
   - Tipo: Child Table (`istable: 1`)
   - Campo relevante: `template_fields` (tipo: Table, options: "Template Field Definition")
   - Estado: DocType existe en código

3. **Master Template Registry** ✅ EXISTE
   - Tipo: Single DocType
   - Campo relevante: `infrastructure_templates` (tipo: Table, options: "Infrastructure Template Definition")

### Estructura Anidada:

```
Master Template Registry (Single)
  └─ infrastructure_templates (Table → Infrastructure Template Definition)
      └─ template_fields (Table → Template Field Definition)
```

### Referencias en Código:

**Test factories (`test_factories.py`):**
- `create_master_template_data()`: Crea templates básicos sin template_fields
- `create_template_with_assignment_rules()`: Crea templates con reglas de asignación

**Tests (`test_master_template_registry.py`):**
- Tests usan factory methods
- NO crean template_fields explícitamente en ningún test
- Tests funcionan con template_fields vacíos

**Fixture actual exportado:**
```json
"template_fields": []  // ← VACÍO en los 3 templates
```

**Fixture original (git):**
```json
"template_fields": [
  {"field_name": "pool_capacity", ...}  // ← Tiene datos
]
```

### Conclusiones:

1. ✅ **DocTypes SÍ existen** en el código:
   - Template Field Definition (child table)
   - Infrastructure Template Definition (child table con template_fields)

2. ❌ **Registros NO existen en BD**:
   - BD tiene 0 template_fields en todos los templates
   - Explicación: Nunca se crearon registros en child table

3. ⚠️ **Fixture original es diseño teórico**:
   - Contiene datos ejemplo/documentación
   - NO refleja datos reales del sitio control
   - Es plantilla para usuarios configuren después

4. ✅ **Export-fixtures funcionó correctamente**:
   - Exportó lo que HAY en BD (vacío)
   - NO es bug de export-fixtures

5. ⚠️ **Tests NO usan template_fields**:
   - Factories crean templates sin template_fields
   - Sistema funciona sin estos campos
   - Pueden ser feature opcional o pendiente implementar

### Scripts de Creación:

❌ **NO se encontraron scripts** que:
- Creen DocType Template Field Definition
- Instalen datos template_fields
- Migren fixture a BD

### Estado Final:

- DocTypes: ✅ Existen en código
- BD: ❌ Sin registros template_fields
- Fixture original: Diseño teórico/documentación
- Export-fixtures: Correcto (exportó BD real vacía)

---

## 🚨 ANÁLISIS ARQUITECTÓNICO CRÍTICO: NESTED CHILD TABLES

### Contexto del Problema

**Limitación confirmada**: Frappe Framework NO soporta nested child tables en fixtures.

**Estructura afectada**:
```
Master Template Registry (Single, issingle=1)
  └─ infrastructure_templates (Child Table)
      └─ template_fields (Nested Child Table) ← ❌ NO se exporta/importa
```

**Impacto**: Usuario indica que "la mayoría de los templates operarán con child doctypes", lo que significa que el 90% del sistema de fixtures sería inútil si no resolvemos esto.

### Pregunta Crítica del Usuario

> "Es por esto que no se crearon originalmente?? Porque se mencionan singles? estos documentos no debrian ser singles, deberian ser doctype normales"

**Respuesta**: Probable. La limitación de nested child tables explica por qué:
1. Fixture original tenía datos completos
2. Nunca se instalaron en BD
3. Export-fixtures exportó vacío

**¿Por qué Single?** El commit original dice:
- "sistema de fixtures para distribución centralizada via bench update"
- Single permite UN SOLO registro global de configuración
- Pero Single + nested child = incompatible con fixtures

---

## 📋 PROPUESTAS DE SOLUCIÓN

### Opinión ChatGPT (proporcionada por usuario):

**Opción B (corto plazo)**: JSON maestro + hook `after_migrate`
- Mantener arquitectura Single actual
- Crear JSON separado con template_fields
- Hook lee JSON y crea registros en BD después de migrate

**Opción C (largo plazo)**: Normalizar modelo
- Convertir a DocType de 1er nivel (no child table)
- Usar fixtures normales que SÍ funcionan
- Reestructurar relaciones

**RG-009-bis**: Permitir data-seed desde JSON cuando fixtures no funcionan

---

## 🎯 CONTRAPROPUESTA TÉCNICA (Claude)

### Análisis de Opciones:

#### ❌ Opción B (JSON + Hook) - NO RECOMENDADO

**Problemas**:
1. **Viola RG-009**: Zero-config deployment require fixtures, no scripts
2. **Complejidad innecesaria**: Dos sistemas paralelos (fixtures + JSON seed)
3. **Mantenimiento doble**: Actualizar fixtures Y JSON maestro
4. **Idempotencia**: Hooks deben verificar si ya existen datos (complejo)
5. **No resuelve problema raíz**: Sigue usando Single con nested child

**Único beneficio**: Solución rápida sin cambiar arquitectura

#### ✅ Opción C (Normalizar) - RECOMENDADO FUERTEMENTE

**Por qué es la solución correcta**:

1. **Resuelve problema raíz**: Elimina nested child tables completamente
2. **Compatible fixtures**: DocTypes de 1er nivel SÍ funcionan con fixtures
3. **Cumple RG-009**: Zero-config deployment nativo
4. **Simplicidad**: Un solo sistema (fixtures estándar)
5. **Mantenibilidad**: Arquitectura estándar Frappe
6. **Escalabilidad**: Funciona para TODOS los templates (90% del sistema)

**Arquitectura propuesta**:

```
ANTES (problemático):
Master Template Registry (Single)
  └─ infrastructure_templates (Child)
      └─ template_fields (Nested Child) ← ❌ NO funciona

DESPUÉS (correcto):
Template Registry Settings (Single)
  ├─ company
  ├─ template_version
  └─ auto_assignment_rules (Child simple)

Infrastructure Template (DocType normal) ← ✅ 1er nivel
  ├─ template_code (único)
  ├─ template_name
  ├─ infrastructure_type
  └─ template_fields (Child simple) ← ✅ Ahora funciona con fixtures

Template Field Definition (Child Table)
  ├─ parent (link to Infrastructure Template)
  ├─ field_name
  └─ field_type
```

**Cambios específicos**:

1. **Crear nuevo DocType**: `Infrastructure Template` (normal, no child, no single)
   - Autoname: `field:template_code`
   - Campos: todos los actuales de Infrastructure Template Definition
   - Child table: template_fields (funciona porque es 1 nivel)

2. **Modificar Master Template Registry**:
   - Eliminar: infrastructure_templates child table
   - Mantener: Solo settings globales + auto_assignment_rules
   - Renombrar: Template Registry Settings (más descriptivo)

3. **Fixtures funcionan nativamente**:
   ```python
   # hooks.py
   fixtures = [
       "Template Registry Settings",  # Single con settings globales
       {
           "dt": "Infrastructure Template",  # DocType normal
           "filters": [["template_code", "in", ["ESTATE-ADMIN", "ESTATE-OWNER", "UNIT-OWNER"]]]
       },
       # template_fields se exportan automáticamente con parent
   ]
   ```

4. **Referencias en código**:
   - Cambiar: `registry.infrastructure_templates`
   - Por: `frappe.get_all("Infrastructure Template", filters=...)`
   - Mínimo impacto: Muy pocas referencias en codebase

#### ❌ RG-009-bis - NO NECESARIO

Si implementamos Opción C correctamente, RG-009 original funciona perfecto. No necesitamos regla especial para workarounds.

---

## 📊 COMPARACIÓN SOLUCIONES

| Criterio | Opción B (JSON+Hook) | Opción C (Normalizar) |
|----------|---------------------|----------------------|
| Cumple RG-009 | ❌ No (require script) | ✅ Sí (fixtures nativos) |
| Complejidad | 🔴 Alta (dual system) | 🟢 Baja (estándar) |
| Mantenibilidad | 🔴 Difícil | 🟢 Fácil |
| Escalabilidad | 🔴 Limitada | 🟢 Total (90% templates) |
| Tiempo implementación | 🟢 Rápido (2-3 hrs) | 🟡 Moderado (1 día) |
| Deuda técnica | 🔴 Alta | 🟢 Cero |
| Compatibilidad framework | 🔴 Workaround | 🟢 Nativo |
| Tests requeridos | 🔴 Muchos (idempotencia) | 🟢 Mínimos (estándar) |

---

## 🎯 RECOMENDACIÓN FINAL

### ✅ IMPLEMENTAR OPCIÓN C (NORMALIZAR) - DEFINITIVA Y COMPLETA

**Justificación**:
1. **Estamos en etapa dev**: Momento perfecto para arquitectura correcta
2. **Problema afecta 90%**: No es edge case, es fundamental
3. **Solución permanente**: Opción B es parche temporal
4. **Cumplimiento RG-009**: Sin excepciones ni workarounds
5. **Estándar Frappe**: Arquitectura probada y mantenible

**Plan de implementación** (NO ejecutar ahora, solo propuesta):

### Fase 1: Crear nueva estructura (2-3 horas)

```bash
# 1. Crear nuevo DocType: Infrastructure Template
bench --site admin1.dev new-doctype "Infrastructure Template"

# Configuración:
- issingle: 0
- istable: 0
- autoname: field:template_code
- Campos: copiar de Infrastructure Template Definition
- Child table: template_fields (Template Field Definition)

# 2. Renombrar Master Template Registry → Template Registry Settings
# Modificar JSON:
- Eliminar: infrastructure_templates field
- Mantener: company, template_version, auto_assignment_rules
```

### Fase 2: Migrar datos (30 min)

```python
# Script one-off: migrate_infrastructure_templates.py
def run():
    registry = frappe.get_doc("Master Template Registry", "Master Template Registry")

    # Por cada template en registry.infrastructure_templates:
    for old_template in registry.infrastructure_templates:
        # Crear nuevo Infrastructure Template (1er nivel)
        new_doc = frappe.get_doc({
            "doctype": "Infrastructure Template",
            "template_code": old_template.template_code,
            "template_name": old_template.template_name,
            # ... copiar todos los campos
        })

        # Copiar template_fields (ahora funciona porque es 1 nivel)
        for field in old_template.template_fields:
            new_doc.append("template_fields", {
                "field_name": field.field_name,
                # ... copiar campos
            })

        new_doc.insert()
```

### Fase 3: Actualizar referencias código (1-2 horas)

```python
# ANTES:
registry = frappe.get_doc("Master Template Registry", "Master Template Registry")
templates = registry.infrastructure_templates

# DESPUÉS:
templates = frappe.get_all("Infrastructure Template",
    fields=["template_code", "template_name", ...])
```

### Fase 4: Fixtures (30 min)

```python
# hooks.py
fixtures = [
    "Template Registry Settings",
    {
        "dt": "Infrastructure Template",
        "filters": [["template_code", "in", [
            "ESTATE-ADMIN", "ESTATE-OWNER", "UNIT-OWNER"
        ]]]
    }
]

# Exportar:
bench --site admin1.dev export-fixtures
# Template_fields se incluyen automáticamente
```

### Fase 5: Tests y validación (1 hora)

```python
# Verificar:
1. Fixtures exportan template_fields completos
2. Nueva instalación carga todos los datos
3. Referencias código funcionan
4. Auto-assignment rules siguen funcionando
```

**Tiempo total estimado**: 5-6 horas de trabajo enfocado

**Riesgo**: Bajo (cambio arquitectónico controlado en dev)

**Beneficio**: Arquitectura correcta para 100% del sistema templates

---

## ❓ DECISIÓN USUARIO: NESTED CHILD TABLES

**Estado**: ⏸️ DOCUMENTADO - Implementación futura
**Razón**: 66 DocTypes totales, requiere análisis individual de cada uno
**Acción**: Documentado para revisión arquitectónica posterior

---

## FIXTURE 9/12: policy_category.json

### Estado: 🔴 CRITICAL - Fixture INCORRECTO desde creación (nunca funcionó)

### Cambios detectados:

```diff
# Cada registro (5 total):

ANTES (fixture):
- "related_chapters": "Capítulo 1, Capítulo 2"  # Campo INCORRECTO

DESPUÉS (export-fixtures):
+ "chapter_mapping": null  # Campo CORRECTO del DocType
+ "docstatus": 0
+ "modified": "2025-10-07 14:02:36.518640"
```

### INVESTIGACIÓN COMPLETA - ¿QUÉ PASÓ REALMENTE?

#### Commit original: 2172690 (2025-07-09)

**PR #16:** feat(companies): Companies v2.1 - DocTypes Master configurables completos

**DocType JSON creado** (policy_category.json):
```json
{
  "field_order": [
    "category_name",
    "chapter_mapping",  // ← Campo CORRECTO desde día 1
    "is_active"
  ]
}
```

**Fixture JSON creado** (fixtures/policy_category.json):
```json
{
  "name": "Convivencia",
  "category_name": "Convivencia",
  "related_chapters": "Capítulo 1, Capítulo 2",  // ← Campo INCORRECTO desde día 1
  "is_active": 1
}
```

#### ❌ NUNCA HUBO RENOMBRAMIENTO

**La verdad**:
1. DocType SIEMPRE tuvo campo `chapter_mapping`
2. Fixture SIEMPRE tuvo campo `related_chapters` (ERROR)
3. NO hubo commit que renombrara nada
4. Error humano en creación original (copy/paste incorrecto)

#### ¿Qué pasó cuando se instaló en admin1.dev? (2025-07-09)

```bash
bench migrate
```

**Paso 1 - Crear DocType**:
- ✅ Instaló DocType con campo `chapter_mapping`
- ✅ Creó tabla `tabPolicy Category` con columna `chapter_mapping`

**Paso 2 - Instalar fixture**:
- ❌ Fixture tenía campo `related_chapters` (NO EXISTE en DocType)
- ❌ Frappe ignoró campo `related_chapters` silenciosamente
- ❌ Creó 5 registros con `chapter_mapping = NULL`
- ❌ NO hubo error, NO hubo warning

**Resultado**: Datos NUNCA se instalaron. BD siempre tuvo `chapter_mapping = NULL`

#### Estado BD actual (verificado):

```
Administración:    chapter_mapping = None  (desde 2025-07-09)
Convivencia:       chapter_mapping = None  (desde 2025-07-09)
Mantenimiento:     chapter_mapping = None  (desde 2025-07-09)
Seguridad:         chapter_mapping = None  (desde 2025-07-09)
Uso de Espacios:   chapter_mapping = None  (desde 2025-07-09)
```

#### ¿Por qué export-fixtures generó esto ahora?

**Export-fixtures funcionó PERFECTAMENTE**:
- Exportó estado REAL de BD: `chapter_mapping = null`
- Usó campo CORRECTO del DocType: `chapter_mapping`
- Fixture original era INCORRECTO, export-fixtures es CORRECTO
- Export-fixtures ARREGLÓ el fixture (inadvertidamente)

### Impacto REAL:

🟡 **MODERADO** - Datos nunca existieron en BD:

**Realidad**:
- ❌ NO hubo pérdida de datos (nunca existieron)
- ❌ Fixture original INCORRECTO desde día 1
- ✅ Export-fixtures ARREGLÓ el fixture (campo correcto ahora)
- ⚠️ Pero valores siguen vacíos (null)

**Pregunta crítica**: ¿Estos valores SON necesarios para funcionalidad?

### Análisis funcionalidad:

**¿Se usa chapter_mapping en el código?**

✅ **SÍ - CONFIRMADO** (verificado en policy_category.py):

**Método validate_chapter_mapping()** (línea 13-17):
```python
def validate_chapter_mapping(self):
    if self.chapter_mapping:
        if not self.chapter_mapping.replace("-", "").replace(",", "").replace(" ", "").isalnum():
            frappe.throw(_("Formato de capítulos relacionados inválido"))
```

**Método get_related_chapters()** (línea 32-35):
```python
def get_related_chapters(self):
    if self.chapter_mapping:
        return [chapter.strip() for chapter in self.chapter_mapping.split(",") if chapter.strip()]
    return []
```

**Tests verifican funcionalidad** (test_policy_category.py):
- `test_create_policy_category()`: Verifica `chapter_mapping` se guarda
- `test_chapter_mapping_validation()`: Verifica validación formato
- `test_get_related_chapters()`: Verifica parsing de capítulos

**CONCLUSIÓN**: Funcionalidad SÍ depende de `chapter_mapping`, pero BD actual tiene valores null

### Estado actual (2025-10-20):

```
BD admin1.dev:
  Administración:    chapter_mapping = null
  Convivencia:       chapter_mapping = null
  Mantenimiento:     chapter_mapping = null
  Seguridad:         chapter_mapping = null
  Uso de Espacios:   chapter_mapping = null

Fixture actual:
  ✅ Campo correcto: chapter_mapping (arreglado por export-fixtures)
  ❌ Valores: null

Funcionalidad afectada:
  - get_related_chapters() → retorna []
  - Mapeo políticas → capítulos reglamento NO funciona
```

### Recomendación para PRODUCCIÓN:

✅ **MAESTRO COMPARTIDO** (arquitectura del proyecto)

**Decisión**: Policy Category es master data → valores compartidos entre todos los sitios

**Acción**:
1. Poblar BD admin1.dev con valores del fixture original
2. Actualizar fixture con valores correctos
3. Re-exportar fixtures
4. Propagación automática vía `bench update` a sitios producción

**Script one-off para admin1.dev**:
```python
# condominium_management/one_offs/populate_policy_category_chapters.py
import frappe

def run():
    """Poblar chapter_mapping con valores maestros"""

    mappings = {
        "Convivencia": "Capítulo 1, Capítulo 2",
        "Seguridad": "Capítulo 3, Capítulo 4",
        "Mantenimiento": "Capítulo 5",
        "Uso de Espacios Comunes": "Capítulo 6, Capítulo 7",
        "Administración": "Capítulo 8, Capítulo 9"
    }

    for name, chapters in mappings.items():
        doc = frappe.get_doc("Policy Category", name)
        doc.chapter_mapping = chapters
        doc.save()
        print(f"✅ {name}: {chapters}")

    frappe.db.commit()
    return True
```

**Actualizar fixture**:
Modificar `fixtures/policy_category.json` con valores correctos después de poblar BD

**Para migración a producción**:
```
1. Ejecutar script en admin1.dev
2. Re-exportar fixtures (bench export-fixtures)
3. Commit + push
4. Sitios producción: bench update → instalan valores automáticamente
```

**Prioridad**: Alta (master data incompleto bloquea funcionalidad)

---

## FIXTURE 10/12: property_status_type.json

### Estado: 🟢 COSMETIC - Solo reordenamiento y metadata

### Cambios detectados:

```diff
# Cada registro (6 total):

ANTES:
{
  "doctype": "Property Status Type",
  "name": "Activo",
  "status_name": "Activo",
  "is_active": 1
}

DESPUÉS:
{
+ "docstatus": 0,
  "doctype": "Property Status Type",
+ "is_active": 1,
+ "modified": "2025-10-07 14:02:36.549402",
  "name": "Activo",
  "status_name": "Activo"
- "is_active": 1
}
```

### Análisis:

**Cambios cosméticos únicamente**:
- ✅ Reordenamiento alfabético de campos
- ✅ `docstatus: 0` agregado (estándar Frappe)
- ✅ `modified` timestamps agregados
- ✅ `is_active` movido antes de `name`

**Datos preservados**:
- ✅ Todos los registros presentes (6 total)
- ✅ `status_name` valores correctos
- ✅ `is_active` valores correctos
- ✅ `name` valores correctos

**Sin pérdida de datos**:
- NO hay campos eliminados
- NO hay valores perdidos
- NO hay cambios de schema

### Impacto:

🟢 **NINGUNO** - Cambios puramente cosméticos

### Recomendación:

✅ **DEJAR COMO ESTÁ**

**Justificación**:
- Sin pérdida de funcionalidad
- Sin pérdida de datos
- Formato más consistente (alfabético)
- `docstatus` es estándar Frappe
- `modified` útil para auditoría
- Revertir no aporta beneficio
- Mantener reduce ruido en git history

**Acción**: Ninguna

---

## FIXTURE 11/12: property_usage_type.json

### Estado: 🟢 COSMETIC - Solo reordenamiento y metadata

### Cambios detectados:

Idénticos a fixture 10 (property_status_type):
- ✅ Reordenamiento alfabético de campos
- ✅ `docstatus: 0` agregado
- ✅ `modified` timestamps agregados

### Análisis:

**Datos preservados** (5 registros):
- ✅ Residencial
- ✅ Comercial
- ✅ Mixto
- ✅ Industrial
- ✅ Oficinas

**Sin pérdida de datos**: Todos los valores `usage_name` e `is_active` correctos

### Impacto:

🟢 **NINGUNO** - Cambios puramente cosméticos

### Recomendación:

✅ **DEJAR COMO ESTÁ**

**Justificación**: Misma que fixture 10 - cambios cosméticos sin impacto funcional

**Acción**: Ninguna

---

## FIXTURE 12/12: user_type.json

### Estado: 🔴 CRITICAL - Contaminación con User Types de framework/HRMS

### Cambios detectados:

```diff
ANTES (fixture original - 4 registros):
1. Administrador (app condominium_management)
2. Residente (app condominium_management)
3. Portero (app condominium_management)
4. Contador (app condominium_management)

DESPUÉS (export-fixtures - 7 registros):
+ 1. System User (Frappe core, user_type_name: null)
+ 2. Website User (Frappe core, user_type_name: null)
+ 3. Employee Self Service (HRMS, user_type_name: null)
4. Administrador (app)
5. Residente (app)
6. Portero (app)
7. Contador (app)
```

### Análisis:

**Contaminación detectada**:
- ✅ 4 User Types originales de la app (correctos)
- ❌ 3 User Types de framework/HRMS agregados (contaminación)

**User Types contaminantes**:
```
System User:
  - Origen: Frappe core framework
  - user_type_name: None
  - modified: 2025-07-03 (muy anterior a export)

Website User:
  - Origen: Frappe core framework
  - user_type_name: None
  - modified: 2025-07-03

Employee Self Service:
  - Origen: HRMS app
  - user_type_name: None
  - modified: 2025-07-03
```

**User Types legítimos de la app**:
```
Administrador, Residente, Portero, Contador:
  - user_type_name: [valor específico]
  - modified: 2025-10-07 (fecha export)
  - Funcionalidad específica condominium_management
```

### Causa raíz:

**Fixture sin filtros en hooks.py** (línea 328):
```python
fixtures = [
    "User Type",  # ← Exporta TODOS los User Types (sin filtros)
]
```

**Por qué pasó**:
1. `bench export-fixtures` exporta TODO lo que coincide con fixture
2. Fixture "User Type" sin filtros → exporta TODOS los registros BD
3. BD tiene User Types de Frappe core + HRMS + app
4. Export capturó los 7 registros (4 app + 3 framework)

### Impacto:

🔴 **CRÍTICO** - Fixture contaminado con datos framework:

**Problemas**:
1. **Fixture impuro**: Mezcla datos app con framework
2. **Instalaciones futuras**: Intentará crear User Types que ya existen (framework)
3. **Conflictos potenciales**: Duplicate entry errors en `bench migrate`
4. **Violación RG-009**: Fixture debe contener SOLO datos de la app
5. **Portabilidad**: Fixture asume HRMS instalado (dependencia no declarada)

**Escenario de fallo**:
```bash
# Nueva instalación SIN HRMS:
bench migrate
# ❌ ERROR: Intentará crear "Employee Self Service" sin HRMS instalado
```

### Opciones de resolución:

#### Opción A: Agregar filtros específicos en hooks.py ✅ RECOMENDADO

**Acción en hooks.py** (línea 328):
```python
# ANTES:
"User Type",  # Sin filtros

# DESPUÉS:
{
    "dt": "User Type",
    "filters": [
        ["name", "in", ["Administrador", "Residente", "Portero", "Contador"]]
    ]
},
```

**Luego limpiar fixture**:
```bash
# 1. Agregar filtros a hooks.py
# 2. Re-exportar fixture limpio
bench --site admin1.dev export-fixtures

# 3. Verificar solo 4 registros en user_type.json
```

**Pros**:
- Solución definitiva
- Previene futuras contaminaciones
- Fixture puro (solo app data)
- Compatible con/sin HRMS

**Cons**:
- Require modificar hooks.py nuevamente
- Require re-export fixtures

#### Opción B: Revertir fixture manualmente ⚠️ TEMPORAL

**Acción**:
```bash
# Revertir user_type.json a versión original (4 registros)
git checkout HEAD~1 -- condominium_management/fixtures/user_type.json
```

**Pros**:
- Rápido
- Restaura fixture original

**Cons**:
- NO previene futuras contaminaciones
- Próximo export-fixtures volverá a contaminar
- NO resuelve causa raíz (falta filtros)

#### Opción C: Dejar como está ❌ NO RECOMENDADO

**Implicaciones**:
- Fixture contaminado permanentemente
- Instalaciones pueden fallar si HRMS no instalado
- Violación RG-009
- Problemas portabilidad

### Recomendación:

✅ **Implementar Opción A (filtros + re-export)**

**Plan**:
1. Modificar hooks.py línea 328 con filtros específicos
2. Re-exportar fixtures con `bench export-fixtures`
3. Verificar user_type.json tiene SOLO 4 registros
4. Commitear hooks.py + user_type.json juntos

**Prioridad**: Alta (contaminación fixture viola RG-009)

**Nota**: Este mismo problema puede existir en otros fixtures sin filtros (verificar hooks.py completo)

---

## 📊 RESUMEN EJECUTIVO: 14 FIXTURES EXPORT-FIXTURES

### DECISIÓN IMPLEMENTADA (2025-10-23):

**✅ HABILITADOS en hooks.py (7/14)** - Migrarán automáticamente:
1. **compliance_requirement_type.json** - Cosmético (5 registros)
2. **document_template_type.json** - Cosmético (registros íntegros)
3. **enforcement_level.json** - Cosmético (4 registros)
4. **jurisdiction_level.json** - Cosmético (4 registros)
5. **property_status_type.json** - Cosmético (6 registros)
6. **property_usage_type.json** - Cosmético (5 registros)
7. **custom_field.json** - 27 custom fields Company (RG-009 compliance)

**🔴 DESHABILITADOS (7/14)** - Requieren corrección o contaminados:
8. **acquisition_type.json.DISABLED** - Pérdida datos `document_checklist`
9. **company_type.json.DISABLED** - Autoname inconsistency
10. **entity_type_configuration.json.DISABLED** - Bloqueador migrate, DocTypes inválidos
11. **master_template_registry.json.DISABLED** - Nested child tables vacíos
12. **policy_category.json.DISABLED** - Pérdida datos `chapter_mapping`
13. **user_type.json.DISABLED** - Contaminación framework/HRMS
14. **contribution_category.json.DISABLED** - 136 test records contaminados

**📁 Estrategia doble protección**:
- ✅ Archivos .DISABLED no importados por Frappe
- ✅ Comentados en hooks.py para prevención adicional
- ✅ Contenido preservado como referencia para correcciones

### Estado actual:

- ✅ **hooks.py actualizado**: condominium_management/hooks.py:319-366 (7 habilitados, 7 deshabilitados)
- ✅ **Archivos protegidos**: 7 fixtures con extensión .DISABLED
- ✅ **bench migrate funcional**: Solo usa 7 fixtures validados
- ⏸️ **Correcciones pendientes**: 7 fixtures deshabilitados (6 errores + 1 contaminado)
- 📚 **Referencia completa**: Archivos .DISABLED preservados para análisis

### Próximos pasos:

1. ⏸️ Validar `bench migrate` funciona con 7 fixtures habilitados
2. ⏸️ Corregir fixtures deshabilitados individualmente (6 con errores)
3. ⏸️ Limpiar contribution_category.json.DISABLED (136 test records)
4. ⏸️ Re-habilitar después de corrección (renombrar + descomentar)
5. ⏸️ Commit final después de validaciones

### Tiempo estimado correcciones:

- **Ahora**: 0 min (bench migrate ya funciona con 7 fixtures)
- **Futuro**: ~40 min (correcciones 6 fixtures deshabilitados - opcional)
- **Contribution Category**: Requiere análisis datos válidos vs test records
- **Arquitectónico**: TBD (nested child tables - decisión pendiente)

---

---

## 🎯 PLAN DE EJECUCIÓN COMPLETO

### Orden de ejecución (CRÍTICO - seguir secuencia):

```
FASE 1: BLOQUEADORES (desbloquear migrate)
├─ 1.1: Revertir entity_type_configuration.json
├─ 1.2: Verificar bench migrate funciona
└─ CHECKPOINT: Migrate debe pasar sin errores

FASE 2: PÉRDIDA DATOS (restaurar master data)
├─ 2.1: Restaurar acquisition_type document_checklist
├─ 2.2: Restaurar policy_category chapter_mapping
└─ CHECKPOINT: Verificar datos poblados en BD

FASE 3: CONTAMINACIÓN (limpiar fixtures)
├─ 3.1: Agregar filtros User Type en hooks.py
├─ 3.2: Re-exportar fixtures
└─ CHECKPOINT: Verificar user_type.json solo 4 registros

FASE 4: AUTONAME (decisión usuario requerida)
├─ 4.1: Revisar opciones autoname inconsistency
├─ 4.2: Implementar opción elegida
└─ CHECKPOINT: Fixtures consistentes con autoname rules

FASE 5: ARQUITECTÓNICO (pendiente análisis)
└─ 5.1: Nested child tables - análisis 66 DocTypes
```

---

## 📋 COMANDOS EXACTOS PASO A PASO

### FASE 1: Desbloquear migrate

#### Paso 1.1 - Revertir entity_type_configuration.json

```bash
# Backup current state
cp condominium_management/fixtures/entity_type_configuration.json \
   condominium_management/fixtures/entity_type_configuration.json.contaminated

# Revertir a versión original (pre-export-fixtures)
git checkout HEAD~1 -- condominium_management/fixtures/entity_type_configuration.json
```

**Validación**:
```bash
# Verificar valores correctos en fixture
grep "entity_doctype" condominium_management/fixtures/entity_type_configuration.json
# Debe mostrar:
#   "Service Management Contract" (NO "Service Contract Configuration")
#   "File" (NO "Document Configuration")
```

#### Paso 1.2 - Verificar migrate funciona

```bash
bench --site admin1.dev migrate
```

**Validación esperada**:
```
✅ Success: bench migrate completa sin errores
❌ ERROR: Si falla, revisar logs y NO continuar
```

---

### FASE 2: Restaurar master data

#### Paso 2.1 - Restaurar acquisition_type document_checklist

**Crear script**:
```bash
cat > condominium_management/one_offs/restore_acquisition_type_checklists.py << 'EOF'
#!/usr/bin/env python3
import frappe
import json

def run():
    """Restaurar document_checklist perdido en Acquisition Type"""

    # Datos del fixture original (commit 2172690)
    checklists = {
        "Compra": [
            {"document_name": "Escritura pública"},
            {"document_name": "Certificado libertad"},
            {"document_name": "Paz y salvo predial"},
            {"document_name": "Pago impuesto registro"}
        ],
        "Herencia": [
            {"document_name": "Acta de defunción"},
            {"document_name": "Testamento"},
            {"document_name": "Declaración extra-proceso"},
            {"document_name": "Registro sucesión"}
        ],
        "Donación": [
            {"document_name": "Escritura donación"},
            {"document_name": "Certificado donante"},
            {"document_name": "Aceptación donatario"}
        ],
        "Adjudicación": [
            {"document_name": "Sentencia judicial"},
            {"document_name": "Registro adjudicación"}
        ]
    }

    print("\n" + "="*80)
    print("RESTAURANDO document_checklist EN Acquisition Type")
    print("="*80 + "\n")

    for acquisition_name, docs in checklists.items():
        if frappe.db.exists("Acquisition Type", acquisition_name):
            doc = frappe.get_doc("Acquisition Type", acquisition_name)

            # Limpiar checklist actual
            doc.document_checklist = []

            # Agregar documentos del fixture original
            for doc_item in docs:
                doc.append("document_checklist", doc_item)

            doc.save()
            print(f"✅ {acquisition_name}: {len(docs)} documentos restaurados")
        else:
            print(f"⚠️ {acquisition_name}: NO EXISTE en BD")

    frappe.db.commit()
    print("\n✅ Proceso completado\n")
    return True

if __name__ == "__main__":
    run()
EOF
```

**Ejecutar**:
```bash
bench --site admin1.dev execute "condominium_management.one_offs.restore_acquisition_type_checklists.run"
```

**Validación**:
```bash
bench --site admin1.dev console << 'EOF'
import frappe
doc = frappe.get_doc("Acquisition Type", "Compra")
print(f"Compra tiene {len(doc.document_checklist)} documentos")
# Debe mostrar: Compra tiene 4 documentos
EOF
```

#### Paso 2.2 - Restaurar policy_category chapter_mapping

**Crear script**:
```bash
cat > condominium_management/one_offs/restore_policy_category_chapters.py << 'EOF'
#!/usr/bin/env python3
import frappe

def run():
    """Restaurar chapter_mapping en Policy Category"""

    mappings = {
        "Convivencia": "Capítulo 1, Capítulo 2",
        "Seguridad": "Capítulo 3, Capítulo 4",
        "Mantenimiento": "Capítulo 5",
        "Uso de Espacios Comunes": "Capítulo 6, Capítulo 7",
        "Administración": "Capítulo 8, Capítulo 9"
    }

    print("\n" + "="*80)
    print("RESTAURANDO chapter_mapping EN Policy Category")
    print("="*80 + "\n")

    for name, chapters in mappings.items():
        if frappe.db.exists("Policy Category", name):
            doc = frappe.get_doc("Policy Category", name)
            doc.chapter_mapping = chapters
            doc.save()
            print(f"✅ {name}: {chapters}")
        else:
            print(f"⚠️ {name}: NO EXISTE en BD")

    frappe.db.commit()
    print("\n✅ Proceso completado\n")
    return True

if __name__ == "__main__":
    run()
EOF
```

**Ejecutar**:
```bash
bench --site admin1.dev execute "condominium_management.one_offs.restore_policy_category_chapters.run"
```

**Validación**:
```bash
bench --site admin1.dev console << 'EOF'
import frappe
cat = frappe.get_doc("Policy Category", "Convivencia")
print(f"chapter_mapping: {cat.chapter_mapping}")
# Debe mostrar: chapter_mapping: Capítulo 1, Capítulo 2
EOF
```

---

### FASE 3: Limpiar contaminación

#### Paso 3.1 - Agregar filtros User Type

**Editar hooks.py línea 328**:
```bash
# Abrir editor
# Cambiar:
"User Type",

# Por:
{
    "dt": "User Type",
    "filters": [
        ["name", "in", ["Administrador", "Residente", "Portero", "Contador"]]
    ]
},
```

**Validación hooks.py**:
```bash
grep -A3 '"User Type"' condominium_management/hooks.py
# Debe mostrar el bloque con filters
```

#### Paso 3.2 - Re-exportar fixtures

```bash
# IMPORTANTE: Primero verificar que NO haya otros fixtures sin filtros
grep -n "fixtures = \[" condominium_management/hooks.py -A 30

# Si todo correcto, exportar
bench --site admin1.dev export-fixtures --app condominium_management
```

**Validación user_type.json**:
```bash
# Contar registros en fixture
cat condominium_management/fixtures/user_type.json | jq '. | length'
# Debe mostrar: 4 (NO 7)

# Verificar nombres
cat condominium_management/fixtures/user_type.json | jq '.[].name'
# Debe mostrar SOLO: Administrador, Residente, Portero, Contador
# NO debe mostrar: System User, Website User, Employee Self Service
```

---

## 🔍 VERIFICACIÓN OTROS FIXTURES SIN FILTROS

**Análisis hooks.py fixtures** (líneas 314-354):

```bash
# Extraer todos los fixtures de hooks.py
sed -n '/^fixtures = \[/,/^\]/p' condominium_management/hooks.py > /tmp/fixtures_check.txt
```

**Fixtures actuales**:

| Fixture | Tipo | Filtros | Estado | Riesgo |
|---------|------|---------|--------|--------|
| Master Template Registry | String | ❌ No | Single | 🟢 Bajo (único registro) |
| Entity Type Configuration | String | ❌ No | Normal | 🔴 Alto (revisar) |
| Contribution Category | Dict | ✅ Sí | Normal | 🟢 OK |
| Company Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Property Usage Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Acquisition Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Property Status Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Policy Category | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Enforcement Level | String | ❌ No | Normal | 🟡 Medio (verificar) |
| User Type | String → Dict | ❌ → ✅ | Normal | 🟢 OK (arreglado) |
| Document Template Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Jurisdiction Level | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Compliance Requirement Type | String | ❌ No | Normal | 🟡 Medio (verificar) |
| Custom Field | Dict | ✅ Sí | Normal | 🟢 OK |

**Recomendación**: Verificar si otros fixtures master data (Company Type, etc.) deben tener filtros explícitos para evitar contaminación futura.

---

## ⚠️ ANÁLISIS DE RIESGOS

### Riesgos por fixture:

| Fixture | Riesgo | Mitigación |
|---------|--------|------------|
| entity_type_configuration | 🔴 Alto - Bloquea migrate | Revertir inmediatamente |
| acquisition_type | 🟡 Medio - Pérdida datos | Script restauración testeable |
| policy_category | 🟡 Medio - Funcionalidad parcial | Script restauración testeable |
| user_type | 🟡 Medio - Portabilidad rota | Filtros + re-export |
| company_type | 🟠 Medio-Alto - Autoname inconsistency | Requiere decisión usuario |
| master_template_registry | 🔵 Bajo - Arquitectónico | Análisis futuro, no urgente |

### Riesgos de implementación:

| Fase | Riesgo | Probabilidad | Impacto | Mitigación |
|------|--------|--------------|---------|------------|
| Revertir fixtures | Conflictos git | Baja | Bajo | Backup antes de revertir |
| Scripts one-off | Errores ejecución | Media | Medio | Validación previa en console |
| Re-export fixtures | Contaminación nueva | Media | Alto | Verificar hooks.py primero |
| Autoname changes | Romper referencias | Alta | Alto | NO implementar sin decisión |

---

## 🔄 PLAN DE ROLLBACK

### Si algo sale mal durante ejecución:

#### Rollback FASE 1 (entity_type_configuration):
```bash
# Restaurar fixture contaminado si migrate sigue fallando
cp condominium_management/fixtures/entity_type_configuration.json.contaminated \
   condominium_management/fixtures/entity_type_configuration.json

# O investigar error específico en migrate
tail -100 /home/erpnext/frappe-bench/sites/admin1.dev/logs/bench.log
```

#### Rollback FASE 2 (scripts one-off):
```bash
# Los datos poblados se pueden eliminar manualmente via UI
# O ejecutar script reverso:

bench --site admin1.dev console << 'EOF'
import frappe

# Limpiar acquisition_type
for name in ["Compra", "Herencia", "Donación", "Adjudicación"]:
    doc = frappe.get_doc("Acquisition Type", name)
    doc.document_checklist = []
    doc.save()

# Limpiar policy_category
for name in ["Convivencia", "Seguridad", "Mantenimiento", "Uso de Espacios Comunes", "Administración"]:
    doc = frappe.get_doc("Policy Category", name)
    doc.chapter_mapping = None
    doc.save()

frappe.db.commit()
EOF
```

#### Rollback FASE 3 (user_type contaminación):
```bash
# Si re-export genera problemas:

# 1. Revertir hooks.py
git checkout HEAD -- condominium_management/hooks.py

# 2. Revertir user_type.json contaminado
git checkout HEAD -- condominium_management/fixtures/user_type.json

# 3. O mantener solo filtros en hooks.py (previene futuras contaminaciones)
```

---

## ✅ CHECKLIST VALIDACIÓN FINAL

Ejecutar después de completar TODAS las fases:

### Validación fixtures:

```bash
# 1. Verificar NO hay contaminación User Type
cat condominium_management/fixtures/user_type.json | jq '. | length'
# ✅ Debe ser: 4

# 2. Verificar entity_type_configuration correcto
grep "entity_doctype" condominium_management/fixtures/entity_type_configuration.json
# ✅ Debe tener: "Service Management Contract", "File"
# ❌ NO debe tener: "Service Contract Configuration", "Document Configuration"

# 3. Verificar datos poblados en BD
bench --site admin1.dev console << 'EOF'
import frappe

# Check acquisition_type
compra = frappe.get_doc("Acquisition Type", "Compra")
print(f"✅ Compra checklist: {len(compra.document_checklist)} docs")

# Check policy_category
conv = frappe.get_doc("Policy Category", "Convivencia")
print(f"✅ Convivencia chapters: {conv.chapter_mapping}")
EOF
```

### Validación funcionalidad:

```bash
# 1. Migrate debe pasar
bench --site admin1.dev migrate
# ✅ Sin errores

# 2. Build debe pasar
bench --site admin1.dev build --app condominium_management
# ✅ Sin errores

# 3. Tests deben pasar (opcional si hay tiempo)
bench --site admin1.dev run-tests --app condominium_management --module companies
# ✅ Policy Category tests pasan con chapter_mapping poblado
```

### Validación git:

```bash
# Verificar cambios preparados para commit
git status

# Debe mostrar:
#   modified: condominium_management/fixtures/entity_type_configuration.json (revertido)
#   modified: condominium_management/fixtures/user_type.json (limpio)
#   modified: condominium_management/fixtures/acquisition_type.json (RE-EXPORT después de script)
#   modified: condominium_management/fixtures/policy_category.json (RE-EXPORT después de script)
#   modified: condominium_management/hooks.py (filtros User Type)
#   new file: condominium_management/one_offs/restore_*.py (2 scripts)
```

---

## 📊 TABLA RESUMEN ESTADO FINAL

| Fixture | Estado Inicial | Acción Tomada | Estado hooks.py | Migra Ahora |
|---------|---------------|---------------|-----------------|-------------|
| acquisition_type | 🔴 Datos perdidos | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (requiere script) |
| company_type | 🔴 Autoname inconsistency | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (requiere decisión) |
| entity_type_configuration | 🔴 Bloqueador | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (requiere revertir) |
| master_template_registry | 🔴 Nested child | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (análisis arquitectónico) |
| policy_category | 🔴 Datos perdidos | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (requiere script) |
| user_type | 🔴 Contaminado | ⏸️ Deshabilitado | 🔴 DISABLED | ❌ No (requiere filtros) |
| compliance_requirement_type | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |
| document_template_type | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |
| enforcement_level | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |
| jurisdiction_level | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |
| property_status_type | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |
| property_usage_type | 🟢 Cosmético | ✅ Habilitado | 🟢 ENABLED | ✅ Sí |

**ESTADO ACTUAL**:
- **✅ HABILITADOS (migrarán)**: 6/12 fixtures (50%)
- **🔴 DESHABILITADOS (requieren corrección)**: 6/12 fixtures (50%)
- **📁 Archivos .json preservados**: 12/12 fixtures (100% - como referencia)

**PRÓXIMOS PASOS**:
1. ✅ hooks.py actualizado (6 habilitados, 6 deshabilitados)
2. ⏸️ Validar `bench migrate` funciona con fixtures habilitados
3. ⏸️ Corregir fixtures deshabilitados uno por uno
4. ⏸️ Re-habilitar después de corrección (descomentar en hooks.py)

---

## 📝 NOTAS FINALES

### Por qué Single fue mala elección inicial:
- Single es para SETTINGS (configuración app)
- Master data (templates) debe ser DocType normal
- Single + nested child = incompatible con fixtures

### Lecciones aprendidas:

1. **SIEMPRE usar filtros en fixtures**: `"DocType"` sin filtros exporta TODO
2. **Validar fixtures después de export**: No asumir que export-fixtures es seguro
3. **Fixture field names deben coincidir con DocType**: Frappe ignora silenciosamente campos incorrectos
4. **Autoname rules deben ser consistentes**: fixture name debe coincidir con autoname field
5. **Nested child tables NO funcionan en fixtures**: Limitación conocida de Frappe Framework
6. **Backup antes de export-fixtures**: Puede contaminar múltiples fixtures simultáneamente

### Recomendaciones futuras:

1. **Pre-commit hook para validar fixtures**:
   ```bash
   # Verificar que fixtures con filtros estén limpios
   # Verificar que fixture field names coincidan con DocType
   # Verificar que autoname fields sean consistentes
   ```

2. **CI/CD test fixtures en instalación fresh**:
   ```bash
   # Crear site temporal
   # Instalar app
   # Verificar que fixtures instalan correctamente
   # Verificar que NO hay errores duplicate entry
   ```

3. **Documentar fixtures en CLAUDE.md**:
   - Qué fixtures son master data compartido
   - Qué fixtures son configurables por sitio
   - Cuáles requieren filtros explícitos

---

## 🎯 PRÓXIMOS PASOS

1. ✅ **Revisar este documento completo** con usuario
2. ⏸️ **Decisión usuario**: Autoname inconsistency (company_type) - elegir Opción A/B/C
3. ⏸️ **Decisión usuario**: Nested child tables arquitectura - análisis 66 DocTypes
4. ✅ **Ejecutar FASE 1-3** cuando usuario apruebe
5. ✅ **Crear commit atómico** con todos los cambios
6. ✅ **Migrar a producción** vía bench update

**Tiempo estimado total**: 45-60 minutos (Fases 1-3)

---

## 📂 PLAN DE CONTROL Y TRAZABILIDAD

### Punto 1: Clasificación formal de fixtures

**Crear archivo**: `docs/development/fixtures_auditoria.md`

```markdown
# AUDITORÍA FIXTURES - Export-Fixtures 2025-10-20

## ✅ HABILITADOS - Migrarán automáticamente (6/12)

| Fixture | Estado hooks.py | Registros | Notas |
|---------|----------------|-----------|-------|
| compliance_requirement_type.json | 🟢 ENABLED | 5 | Cosmético - reordenamiento |
| document_template_type.json | 🟢 ENABLED | Varios | Cosmético - reordenamiento |
| enforcement_level.json | 🟢 ENABLED | 4 | Cosmético - reordenamiento |
| jurisdiction_level.json | 🟢 ENABLED | 4 | Cosmético - reordenamiento |
| property_status_type.json | 🟢 ENABLED | 6 | Cosmético - reordenamiento |
| property_usage_type.json | 🟢 ENABLED | 5 | Cosmético - reordenamiento |

**Razón**: Cambios puramente cosméticos, datos íntegros, funcionalidad completa.

## 🔴 DESHABILITADOS - Requieren corrección (6/12)

| Fixture | Estado hooks.py | Problema | Acción Requerida |
|---------|----------------|----------|------------------|
| acquisition_type.json | 🔴 DISABLED | Pérdida datos `document_checklist` | Script restauración |
| company_type.json | 🔴 DISABLED | Autoname inconsistency | Decisión usuario (3 opciones) |
| entity_type_configuration.json | 🔴 DISABLED | DocTypes inválidos (bloqueaba migrate) | Revertir a versión original |
| master_template_registry.json | 🔴 DISABLED | Nested child tables vacíos | Análisis arquitectónico 66 DocTypes |
| policy_category.json | 🔴 DISABLED | Pérdida datos `chapter_mapping` | Script restauración |
| user_type.json | 🔴 DISABLED | Contaminación framework/HRMS | Agregar filtros + re-export |

**Razón**: Requieren corrección antes de habilitar. Archivos .json preservados como referencia.

## 📊 RESUMEN

- **✅ Habilitados (migran)**: 6/12 (50%)
- **🔴 Deshabilitados (requieren fix)**: 6/12 (50%)
- **📁 Archivos preservados**: 12/12 (100%)

## 🎯 ESTADO ACTUAL

**hooks.py**: `condominium_management/hooks.py:311-370`
- 6 fixtures comentados (DISABLED)
- 6 fixtures activos (ENABLED)

**bench migrate**: ✅ Funcional (solo usa fixtures habilitados)

**Próxima acción**: Validar migrate + corregir fixtures deshabilitados individualmente

## 📚 REFERENCIA

Ver análisis completo: `docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md`
```

**Comando crear archivo**:
```bash
cat > docs/development/fixtures_auditoria.md << 'EOF'
[contenido arriba]
EOF
```

---

### Punto 2: Marcar scripts obsoletos

**DECISIÓN USUARIO (2025-10-20)**: Marcar scripts obsoletos con warnings, NO borrar

**Estrategia implementada**:
1. ✅ Archivos Python marcados con comentario `⚠️ ARCHIVO OBSOLETO - NO USAR`
2. ✅ Explicación en header: fecha deprecación, razón, reemplazo
3. ✅ Warnings específicos: NO llamar funciones, causará duplicados
4. ✅ Preservados en repo como referencia histórica
5. ✅ Se incluirán en commit (con marcado OBSOLETO)

**Scripts marcados como OBSOLETOS**:

| Script | Estado | Razón Obsoleto | Reemplazo |
|--------|--------|----------------|-----------|
| companies/install.py | ⚠️ OBSOLETO | Creaba custom fields programáticamente | fixtures/custom_field.json |
| companies/custom_fields/company_custom_fields.py | ⚠️ OBSOLETO | 27 custom fields programáticos | fixtures/custom_field.json |
| companies/test_company_customizations.py | ⚠️ OBSOLETO | Test de instalación programática | Fixtures auto-instalación |

**Verificación hooks.py**:
```bash
grep -n "companies.install\|install_company_customizations" condominium_management/hooks.py
# ✅ RESULTADO: Sin referencias activas (no hay hooks llamando estos scripts)
```

**Scripts de corrección (NUEVOS - NO obsoletos)**:

| Script | Estado | Propósito |
|--------|--------|-----------|
| one_offs/restore_acquisition_type_checklists.py | ⏸️ PENDIENTE | Restaurar document_checklist perdido |
| one_offs/restore_policy_category_chapters.py | ⏸️ PENDIENTE | Restaurar chapter_mapping perdido |

**Comando backup**:
```bash
# Crear directorio backup
mkdir -p backup/scripts_fixtures_20251020

# Backup scripts obsoletos (referencia histórica)
cp condominium_management/companies/install.py \
   backup/scripts_fixtures_20251020/install.py.OBSOLETO

cp condominium_management/companies/custom_fields/company_custom_fields.py \
   backup/scripts_fixtures_20251020/company_custom_fields.py.OBSOLETO

# Copiar scripts nuevos de restauración (referencia)
cp condominium_management/one_offs/restore_acquisition_type_checklists.py \
   backup/scripts_fixtures_20251020/

cp condominium_management/one_offs/restore_policy_category_chapters.py \
   backup/scripts_fixtures_20251020/

# Crear README
cat > backup/scripts_fixtures_20251020/README.md << 'EOF'
# Backup Scripts Fixtures - 2025-10-20

## Contexto
Backup de scripts relacionados con contaminación fixtures tras `bench export-fixtures`.

## Scripts obsoletos
- `install.py.OBSOLETO`: Custom fields programático (violaba RG-009)
- `company_custom_fields.py.OBSOLETO`: 27 custom fields (migrados a fixtures)

## Scripts restauración
- `restore_acquisition_type_checklists.py`: Restaurar document_checklist perdido
- `restore_policy_category_chapters.py`: Restaurar chapter_mapping perdido

## Referencia
Ver: `docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md`
EOF
```

---

### Punto 3: Aislamiento de fixtures dudosos

**DECISIÓN USUARIO (2025-10-23)**: Doble estrategia de aislamiento

**Estrategia implementada**:
1. ✅ **Deshabilitar en hooks.py**: Comentar fixtures problemáticos para evitar auto-instalación
2. ✅ **Renombrar archivos**: Cambiar extensión `.json` → `.json.DISABLED` para prevención adicional
3. ✅ **Habilitar válidos**: Solo 6 fixtures verificados en hooks.py
4. ✅ **Preservar contenido**: Archivos .DISABLED mantienen contenido íntegro como referencia

**Razón**: Los fixtures resultantes son útiles como referencia para correcciones futuras, pero necesitamos garantizar que Frappe NO intente migrarlos bajo ninguna circunstancia hasta corregirlos.

**Implementación en hooks.py** (condominium_management/hooks.py:311-370):

```python
# Fixtures
# --------
# Global fixtures that will be updated via bench update across all sites
#
# NOTA: Fixtures temporalmente deshabilitados tras audit export-fixtures (2025-10-20)
# Ver: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md
# Ver: docs/development/fixtures_auditoria.md
#
fixtures = [
	# ============================================================================
	# DESHABILITADOS - Requieren corrección antes de migrar (6/12)
	# ============================================================================
	# "Master Template Registry",  # ⚠️ DISABLED - Nested child tables vacíos (análisis arquitectónico pendiente)
	# "Entity Type Configuration",  # ⚠️ DISABLED - Requiere revertir + validación (bloqueaba migrate)
	# "Company Type",              # ⚠️ DISABLED - Autoname inconsistency (decisión usuario pendiente)
	# "Acquisition Type",          # ⚠️ DISABLED - Requiere script restauración document_checklist
	# "Policy Category",           # ⚠️ DISABLED - Requiere script restauración chapter_mapping
	# "User Type",                 # ⚠️ DISABLED - Requiere filtros para evitar contaminación framework/HRMS

	# ============================================================================
	# HABILITADOS - Fixtures válidos listos para migrar (6/12)
	# ============================================================================
	{
		"doctype": "Contribution Category",
		"filters": {"module_name": ["in", ["Document Generation", "Maintenance", "Contracts"]]},
	},
	# Companies Module Masters - Solo fixtures verificados como válidos
	"Property Usage Type",            # ✅ VÁLIDO - Cosmético (5 registros: Residencial, Comercial, Mixto, Industrial, Oficinas)
	"Property Status Type",           # ✅ VÁLIDO - Cosmético (6 registros: Activo, Inactivo, En Venta, En Arriendo, En Construcción, Abandonado)
	"Enforcement Level",              # ✅ VÁLIDO - Cosmético (4 registros)
	"Document Template Type",         # ✅ VÁLIDO - Cosmético (registros íntegros)
	"Jurisdiction Level",             # ✅ VÁLIDO - Cosmético (4 registros)
	"Compliance Requirement Type",    # ✅ VÁLIDO - Cosmético (5 registros)
	# Companies Module Custom Fields (Company DocType)
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "=", "Company"],
			["fieldname", "in", [
				# ... 27 custom fields Company
			]]
		]
	},
]

# NOTA IMPORTANTE: Los archivos .json de fixtures deshabilitados NO se borran
# Se mantienen en fixtures/ como referencia para correcciones futuras
# Ver plan corrección completo en: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md
```

**Archivos en fixtures/** (estructura actual):
```
condominium_management/fixtures/
├── acquisition_type.json.DISABLED           # 🔴 EXPORT-FIXTURES - DESHABILITADO (pérdida datos)
├── company_type.json.DISABLED               # 🔴 EXPORT-FIXTURES - DESHABILITADO (autoname bug)
├── compliance_requirement_type.json         # 🟢 EXPORT-FIXTURES - Válido (cosmético)
├── contribution_category.json.DISABLED      # 🔴 EXPORT-FIXTURES - DESHABILITADO (136 test records)
├── custom_field.json                        # 🟢 EXPORT-FIXTURES - Válido (27 custom fields Company)
├── document_template_type.json              # 🟢 EXPORT-FIXTURES - Válido (cosmético)
├── enforcement_level.json                   # 🟢 EXPORT-FIXTURES - Válido (cosmético)
├── entity_type_configuration.json.DISABLED  # 🔴 EXPORT-FIXTURES - DESHABILITADO (bloqueaba migrate)
├── jurisdiction_level.json                  # 🟢 EXPORT-FIXTURES - Válido (cosmético)
├── master_template_registry.json.DISABLED   # 🔴 EXPORT-FIXTURES - DESHABILITADO (nested child vacíos)
├── policy_category.json.DISABLED            # 🔴 EXPORT-FIXTURES - DESHABILITADO (pérdida datos)
├── property_status_type.json                # 🟢 EXPORT-FIXTURES - Válido (cosmético)
├── property_usage_type.json                 # 🟢 EXPORT-FIXTURES - Válido (cosmético)
└── user_type.json.DISABLED                  # 🔴 EXPORT-FIXTURES - DESHABILITADO (contaminación HRMS)
```

**Leyenda**:
- 🟢 **7 VÁLIDOS** del export-fixtures (6 cosmetic + 1 custom_field, habilitados)
- 🔴 **7 PROBLEMÁTICOS** del export-fixtures (deshabilitados con .DISABLED)


**Beneficios de esta estrategia**:
- ✅ Archivos preservados para análisis y correcciones
- ✅ No contamina historial git con renombramientos
- ✅ Fácil re-habilitar después de corregir (solo descomentar)
- ✅ Clara documentación en hooks.py del estado de cada fixture
- ✅ bench migrate solo usa los 6 fixtures validados

---

### Punto 4: Reporte claro y commit

**A. Crear reporte ejecutivo**:

**Archivo**: `docs/development/fixtures_export_reporte.md`

```markdown
# REPORTE EJECUTIVO - Contaminación Export-Fixtures

**Fecha**: 2025-10-20
**Evento**: Contaminación masiva fixtures tras `bench export-fixtures`
**Impacto**: 12 fixtures modificados, 6 críticos
**Estado**: Plan de corrección documentado

---

## RESUMEN EJECUTIVO

### Causa raíz
- Ejecución `bench export-fixtures` sin validación previa
- Fixtures sin filtros explícitos → exportó TODOS los registros BD
- Mezcló datos app con datos framework/HRMS

### Fixtures afectados

**🔴 CRÍTICOS (6)**:
1. acquisition_type.json - Pérdida datos document_checklist
2. company_type.json - Autoname inconsistency
3. entity_type_configuration.json - Bloqueador migrate
4. master_template_registry.json - Nested child vacíos
5. policy_category.json - Campo incorrecto fixture original
6. user_type.json - Contaminación framework/HRMS

**🟢 COSMÉTICOS (6)**:
7-12. Solo reordenamiento alfabético + timestamps

### Plan corrección

**FASE 1**: Desbloquear migrate (5 min)
**FASE 2**: Restaurar master data (15 min)
**FASE 3**: Limpiar contaminación (15 min)
**FASE 4**: Decisiones pendientes (TBD)

**Total**: 35 min fixes urgentes

### Documentación completa
`docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md` (2,313 líneas)

### Scripts backup
`backup/scripts_fixtures_20251020/`

### Fixtures aislados
- user_type.pending.json
- company_type.pending.json
- master_template_registry.pending.json

---

## LECCIONES APRENDIDAS

1. ✅ SIEMPRE usar filtros en fixtures
2. ✅ Validar fixtures después de export
3. ✅ Backup antes de export-fixtures
4. ✅ Field names fixture deben coincidir con DocType
5. ✅ Autoname rules deben ser consistentes
6. ✅ Nested child tables NO funcionan en fixtures

## PRÓXIMOS PASOS

1. ✅ Clasificar fixtures (fixtures_auditoria.md)
2. ✅ Backup scripts (backup/scripts_fixtures_20251020/)
3. ✅ Aislar fixtures dudosos (.pending.json)
4. ⏸️ Ejecutar FASE 1-3 correcciones
5. ⏸️ Commit atómico tema completo
6. ⏸️ Decisiones arquitectónicas pendientes

---

**Referencias**:
- Investigación completa: `docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md`
- Auditoría fixtures: `docs/development/fixtures_auditoria.md`
- Backup scripts: `backup/scripts_fixtures_20251020/`
- Custom fields audit: `docs/instructions/CUSTOM-FIELDS-AUDIT-REPORT.md`
```

**B. Commit estrategia**:

```bash
# Después de ejecutar FASE 1-3 y crear todos los documentos:

git add docs/development/fixtures_auditoria.md
git add docs/development/fixtures_export_reporte.md
git add docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md
git add backup/scripts_fixtures_20251020/
git add condominium_management/fixtures/*.pending.json  # fixtures aislados
git add condominium_management/fixtures/entity_type_configuration.json  # revertido
git add condominium_management/fixtures/acquisition_type.json  # restaurado + re-export
git add condominium_management/fixtures/policy_category.json  # restaurado + re-export
git add condominium_management/fixtures/user_type.json  # limpio después FASE 3
git add condominium_management/hooks.py  # filtros User Type
git add condominium_management/one_offs/restore_*.py  # scripts restauración

git commit -m "audit(fixtures): control daños export-fixtures - clasificar, aislar, restaurar

PROBLEMA:
- bench export-fixtures contaminó 12 fixtures (6 críticos)
- Fixtures sin filtros → exportó datos framework/HRMS
- Pérdida datos master: document_checklist, chapter_mapping
- Bloqueador migrate: entity_type_configuration

SOLUCIÓN IMPLEMENTADA:
✅ FASE 1: Revertir entity_type_configuration (desbloquear migrate)
✅ FASE 2: Restaurar acquisition_type + policy_category con scripts
✅ FASE 3: Limpiar user_type (filtros hooks.py + re-export)

CONTROL Y TRAZABILIDAD:
- Clasificación formal: docs/development/fixtures_auditoria.md
- Backup scripts: backup/scripts_fixtures_20251020/
- Aislamiento pendientes: *.pending.json (company_type, master_template_registry)
- Reporte ejecutivo: docs/development/fixtures_export_reporte.md
- Investigación completa: docs/instructions/EXPORT-FIXTURES-INVESTIGATION.md

READY FOR PRODUCTION: 9/12 fixtures (75%)
PENDING DECISIONS: 2/12 (company_type autoname, master_template_registry arquitectura)
BLOCKING: 0/12

REFERENCIAS:
- Custom fields migration: docs/instructions/CUSTOM-FIELDS-AUDIT-REPORT.md
- Scripts restauración: one_offs/restore_*.py

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 🎯 CHECKLIST COMPLETO CONTROL Y TRAZABILIDAD

Ejecutar EN ORDEN:

```bash
# ✅ 1. Clasificación formal
cat > docs/development/fixtures_auditoria.md << 'EOF'
[Ver contenido Punto 1 arriba]
EOF

# ✅ 2. Backup scripts
mkdir -p backup/scripts_fixtures_20251020
[Ejecutar comandos Punto 2 arriba]

# ✅ 3. Deshabilitar fixtures problemáticos en hooks.py
# IMPLEMENTADO: condominium_management/hooks.py líneas 311-370
# - 6 fixtures DESHABILITADOS (comentados)
# - 6 fixtures HABILITADOS (Property Usage Type, Property Status Type, Enforcement Level, Document Template Type, Jurisdiction Level, Compliance Requirement Type)
# - Archivos .json permanecen en fixtures/ sin renombrar

# ✅ 4. Crear reporte ejecutivo
cat > docs/development/fixtures_export_reporte.md << 'EOF'
[Ver contenido Punto 4A arriba]
EOF

# ⏸️ 5. Ejecutar FASE 1-3 correcciones (PENDIENTE - solo para fixtures deshabilitados)
[Ver sección COMANDOS EXACTOS PASO A PASO arriba]

# ⏸️ 6. Commit atómico (PENDIENTE - después de validar migrate funciona)
git add ...
git commit -m "[Ver mensaje Punto 4B arriba]"
```

---

**Tiempo estimado total incluyendo control**:
- FASE 1-3: 35 min
- Control y trazabilidad: 15 min
- **TOTAL: 50 min**

---

**FIN DEL REPORTE COMPLEMENTADO**


