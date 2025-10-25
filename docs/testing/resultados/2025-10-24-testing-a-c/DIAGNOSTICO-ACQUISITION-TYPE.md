# DIAGNÓSTICO: acquisition_type.json FIXTURE

**Fecha:** 2025-10-24
**Contexto:** Preparación para reparación acquisition_type.json (P0 - bloquea Committee Management)
**Autor:** Análisis comparativo pre-reparación

---

## 📊 RESUMEN EJECUTIVO

| Aspecto | Estado |
|---------|--------|
| **Prioridad** | 🔴 P0 - CRÍTICA |
| **Impacto** | Bloquea testing completo Committee Management (3 DocTypes) |
| **Estado fixture** | ❌ DISABLED (acquisition_type.json.DISABLED) |
| **Estado hooks.py** | ❌ COMENTADO (línea 326) |
| **Causa raíz** | INCOMPATIBILIDAD fixture original vs DocType JSON |
| **Tests bloqueados** | 2 suites (test_committee_member.py, test_agreement_tracking.py) |

---

## 🔍 COMPARACIÓN: DIAGNÓSTICO ANTERIOR VS ACTUAL

### Diagnóstico PR #24 (2025-10-22)

**Documento:** `docs/development/pr-24-fixtures-investigation.md` (líneas 40-105)

**Conclusión PR #24:**
- ❌ **INCORRECTA:** "Export-fixtures introdujo cambios destructivos (document_checklist → required_documents)"
- ❌ **INCORRECTA:** "Datos de negocio perdidos por export-fixtures"
- ⚠️ **ACCIÓN SUGERIDA:** "REVERTIR fixture a estado anterior"

**Datos pérdida reportados:**
```
| Compra     | "Escritura pública\nCertificado..." | → null |
| Herencia   | "Registro civil\nTestamento..."     | → null |
| Donación   | "Escritura pública de donación..."  | → null |
| Adjudicación | "Sentencia judicial..."           | → null |
```

---

### Diagnóstico ACTUAL (2025-10-24)

**Investigación completada:** Análisis git history + DocType JSON + BD actual

**Conclusión ACTUAL:**
- ✅ **CORRECTA:** DocType SIEMPRE tuvo `required_documents` (desde commit inicial 14fbbfa)
- ✅ **CORRECTA:** Fixture original usaba campo INCORRECTO (`document_checklist`)
- ✅ **CORRECTA:** Export-fixtures reflejó CORRECTAMENTE el estado BD actual (required_documents=null)

**Evidencia git:**
```bash
# Commit original DocType (PR #16 - 2025-07-09)
git show 14fbbfa:condominium_management/companies/doctype/acquisition_type/acquisition_type.json

# Campos desde SIEMPRE:
- acquisition_name
- requires_notary
- required_documents  ← ESTE es el campo correcto
- is_active

# NUNCA existió campo: document_checklist
```

---

## 🧩 CAUSA RAÍZ IDENTIFICADA

### Problema: Fixture Creado Manualmente con Campo Incorrecto

**Fixture original (PR #16):**
```json
{
  "doctype": "Acquisition Type",
  "name": "Compra",
  "acquisition_name": "Compra",
  "requires_notary": 1,
  "document_checklist": "Escritura pública\n...",  ← CAMPO NO EXISTE EN DOCTYPE
  "is_active": 1
}
```

**DocType JSON (DESDE SIEMPRE):**
```json
{
  "fieldname": "required_documents",  ← CAMPO CORRECTO
  "fieldtype": "Text",
  "label": "Documentos Requeridos"
}
```

### ¿Cómo ocurrió?

**Hipótesis más probable:**
1. Developer creó fixture MANUALMENTE (no con export-fixtures)
2. Developer usó nombre de campo INCORRECTO (`document_checklist` en lugar de `required_documents`)
3. Fixture nunca fue probado en instalación limpia
4. BD desarrollo sí tiene los datos (insertados manualmente o por UI)
5. Export-fixtures (PR #24) exportó CORRECTAMENTE el estado BD → `required_documents: null`

**¿Por qué BD tiene NULL?**
- Fixture original con `document_checklist` fue ignorado por Frappe (campo no existe)
- Los 4 registros se crearon con `required_documents = NULL`
- Datos "perdidos" NUNCA existieron en BD, solo en fixture incorrecto

---

## 📋 ESTADO ACTUAL COMPLETO

### 1. Fixture File

**Ubicación:** `condominium_management/fixtures/acquisition_type.json.DISABLED`

**Contenido (4 registros):**
```json
[
  {
    "acquisition_name": "Compra",
    "docstatus": 0,
    "doctype": "Acquisition Type",
    "is_active": 1,
    "modified": "2025-10-07 14:02:36.061800",
    "name": "Compra",
    "required_documents": null,  ← CORRECTO (campo existe en DocType)
    "requires_notary": 1
  },
  // ... 3 registros más (Herencia, Donación, Adjudicación)
]
```

**Estado:** ❌ DISABLED (extensión .DISABLED)

---

### 2. Hooks Configuration

**Archivo:** `condominium_management/hooks.py`

**Estado:** ❌ COMENTADO (línea 326)
```python
# "Acquisition Type",  # ⚠️ DISABLED - Requiere script restauración document_checklist
```

---

### 3. Base de Datos Actual

**Tabla:** `tabAcquisition Type`

**Estructura:**
```
Field                Type          Null   Default
----                 ----          ----   -------
name                 varchar(140)  NO     (PK)
acquisition_name     varchar(140)  YES    (UNI)
requires_notary      int(1)        NO     0
required_documents   text          YES    NULL    ← Todos NULL
is_active            int(1)        NO     1
```

**Registros (4):**
```
name          acquisition_name  required_documents  requires_notary
Adjudicación  Adjudicación     NULL                0
Compra        Compra           NULL                1
Donación      Donación         NULL                1
Herencia      Herencia         NULL                1
```

---

### 4. Impacto en Committee Management

**Tests bloqueados:** 2 suites completas

1. `test_committee_member.py` - @unittest.skip
   ```python
   @unittest.skip("Committee Management test disabled - Acquisition Type fixture issue (PR #24)")
   ```

2. `test_agreement_tracking.py` - @unittest.skip
   ```python
   @unittest.skip("Committee Management test disabled - Acquisition Type fixture issue (PR #24)")
   ```

**Dependencia:**
- Property Registry requiere Acquisition Type
- Committee Member depende de Property Registry
- Agreement Tracking depende de Property Registry

**Flujo bloqueado:**
```
Acquisition Type (fixtures)
  → Property Registry (DocType)
    → Committee Member (tests)
    → Agreement Tracking (tests)
```

---

## 💡 PROPUESTA DE SOLUCIÓN

### Opción 1: POBLAR DATOS + HABILITAR FIXTURE (Recomendada)

**Pasos:**

1. **Poblar BD con datos de negocio**
   ```sql
   UPDATE `tabAcquisition Type`
   SET required_documents = 'Escritura pública\nCertificado de libertad y tradición\nPaz y salvo predial\nCertificado de valorización'
   WHERE name = 'Compra';

   UPDATE `tabAcquisition Type`
   SET required_documents = 'Registro civil de defunción\nTestamento\nSentencia de sucesión\nCertificado de libertad y tradición'
   WHERE name = 'Herencia';

   UPDATE `tabAcquisition Type`
   SET required_documents = 'Escritura pública de donación\nCertificado de libertad y tradición\nCertificado de no estar en proceso de divorcio'
   WHERE name = 'Donación';

   UPDATE `tabAcquisition Type`
   SET required_documents = 'Sentencia judicial\nCertificado de libertad y tradición\nActa de remate'
   WHERE name = 'Adjudicación';
   ```

2. **Export-fixtures actualizado**
   ```bash
   bench --site admin1.dev export-fixtures --app condominium_management
   ```

3. **Verificar fixture generado**
   - Confirmar que `required_documents` ahora tiene datos
   - Remover `modified` y `docstatus` si es necesario

4. **Habilitar fixture**
   ```bash
   mv condominium_management/fixtures/acquisition_type.json.DISABLED \
      condominium_management/fixtures/acquisition_type.json
   ```

5. **Descomentar hooks.py**
   ```python
   "Acquisition Type",  # ✅ ENABLED - Datos required_documents poblados
   ```

6. **Commit changes**
   ```bash
   git add condominium_management/fixtures/acquisition_type.json
   git add condominium_management/hooks.py
   git commit -m "fix(companies): reparar acquisition_type.json con datos required_documents"
   ```

**Ventajas:**
- ✅ Datos de negocio preservados
- ✅ Fixture correcto desde inicio
- ✅ Instalaciones limpias funcionarán
- ✅ Committee Management desbloqueado

**Desventajas:**
- ⚠️ Requiere poblado manual BD (via SQL o script)

---

### Opción 2: HABILITAR FIXTURE CON NULL (Rápida pero incompleta)

**Pasos:**

1. **Habilitar fixture sin modificar**
   ```bash
   mv condominium_management/fixtures/acquisition_type.json.DISABLED \
      condominium_management/fixtures/acquisition_type.json
   ```

2. **Descomentar hooks.py**
   ```python
   "Acquisition Type",  # ⚠️ ENABLED - required_documents vacíos (pendiente poblar)
   ```

3. **Documentar pendiente**
   - Agregar TODO en PLAN-TESTING-SISTEMA.md
   - Crear issue "Poblar required_documents en Acquisition Type"

**Ventajas:**
- ✅ Rápido (5 min)
- ✅ Desbloquea Committee Management testing

**Desventajas:**
- ❌ Datos de negocio faltantes
- ❌ Instalaciones limpias tendrán Acquisition Types sin documentos requeridos
- ❌ No aprovecha datos originales del fixture PR #16

---

### Opción 3: CREAR SCRIPT ONE-OFF IDEMPOTENTE (Profesional)

**Script:** `condominium_management/one_offs/poblar_acquisition_type_documents.py`

```python
#!/usr/bin/env python3
"""
Script one-off: Poblar required_documents en Acquisition Type

Ejecutar: bench --site admin1.dev execute "condominium_management.one_offs.poblar_acquisition_type_documents.run"
"""
import frappe

ACQUISITION_DOCUMENTS = {
    "Compra": """Escritura pública
Certificado de libertad y tradición
Paz y salvo predial
Certificado de valorización""",

    "Herencia": """Registro civil de defunción
Testamento
Sentencia de sucesión
Certificado de libertad y tradición""",

    "Donación": """Escritura pública de donación
Certificado de libertad y tradición
Certificado de no estar en proceso de divorcio""",

    "Adjudicación": """Sentencia judicial
Certificado de libertad y tradición
Acta de remate"""
}

def run():
    """Poblar required_documents si están vacíos (idempotente)."""
    print("=" * 70)
    print("POBLAR REQUIRED_DOCUMENTS - ACQUISITION TYPE")
    print("=" * 70)

    for name, documents in ACQUISITION_DOCUMENTS.items():
        if frappe.db.exists("Acquisition Type", name):
            doc = frappe.get_doc("Acquisition Type", name)

            if not doc.required_documents:
                doc.required_documents = documents
                doc.save(ignore_permissions=True)
                print(f"✅ {name}: Documentos poblados")
            else:
                print(f"⏭️ {name}: Ya tiene documentos (skip)")
        else:
            print(f"⚠️ {name}: NO existe en BD")

    frappe.db.commit()
    print("\n✅ Script completado")
```

**Workflow:**
```bash
# 1. Ejecutar script
bench --site admin1.dev execute "condominium_management.one_offs.poblar_acquisition_type_documents.run"

# 2. Export-fixtures
bench --site admin1.dev export-fixtures --app condominium_management

# 3. Habilitar fixture
mv condominium_management/fixtures/acquisition_type.json.DISABLED \
   condominium_management/fixtures/acquisition_type.json

# 4. Descomentar hooks.py
# 5. Commit
```

**Ventajas:**
- ✅ Idempotente (safe re-run)
- ✅ Documentado en código
- ✅ Reproducible
- ✅ Facilita testing

**Desventajas:**
- ⚠️ Requiere crear script (15 min)

---

## 🎯 RECOMENDACIÓN FINAL

### **Opción 3: Script One-Off + Export + Habilitar**

**Justificación:**
1. **Profesional:** Script documented, reproducible, idempotent
2. **Seguro:** No manual SQL, easily testable
3. **Completo:** Datos de negocio preservados desde fixture original
4. **Traceable:** Script queda en one_offs/ para referencia futura

**Tiempo estimado:** 30 minutos
- Script creación: 10 min
- Ejecución + export: 5 min
- Habilitar + commit: 5 min
- Testing verification: 10 min

**Próximo paso:** Crear script one-off y ejecutar workflow completo

---

## 📝 LECCIONES APRENDIDAS

### Para Futuros Fixtures

1. **NUNCA crear fixtures manualmente** - Siempre usar `bench export-fixtures`
2. **VERIFICAR campos** contra DocType JSON antes de poblar fixture
3. **TESTING instalación limpia** obligatorio antes de merge
4. **DOCUMÉNTAR origen datos** si fixtures tienen datos de negocio

### Sobre Export-Fixtures

- ✅ Export-fixtures es **confiable** y **correcto**
- ✅ NO introduce bugs, solo refleja estado BD
- ⚠️ Timestamps/ordering changes son **cosméticos** (OK)
- ❌ NO asumir "export-fixtures rompió algo" sin investigar

---

**Última actualización:** 2025-10-24 23:45
**Estado:** DIAGNÓSTICO COMPLETO - Listo para implementación Opción 3
