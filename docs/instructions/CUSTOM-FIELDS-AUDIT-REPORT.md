# REPORTE AUDITORÍA CUSTOM FIELDS - VIOLACIÓN RG-009

**Fecha:** 2025-10-20
**Severidad:** 🔴 CRÍTICA
**Regla violada:** RG-009 (FIXTURES OBLIGATORIOS ZERO-CONFIG)
**Impacto:** Bloquea deployment en nuevos sitios

---

## RESUMEN EJECUTIVO

**PROBLEMA DETECTADO:**
32 custom fields del módulo Companies fueron implementados mediante código Python programático en lugar de fixtures JSON, violando la regla RG-009 de zero-config deployment.

**CONSECUENCIA:**
En una instalación fresh de condominium_management en un nuevo sitio, estos 32 custom fields NO se crearán automáticamente, causando:
- Campos faltantes en formulario Company
- Errores de validación
- Funcionalidad Companies v2.1 rota
- Deployment manual requerido (viola zero-config)

**ESTADO ACTUAL:**
- ✅ Funcionan en admin1.dev (instalados manualmente el 2025-07-09)
- ❌ NO funcionarán en instalaciones nuevas
- ❌ NO están en fixtures
- ❌ NO se auto-instalan con `bench install-app`

---

## ORIGEN DEL PROBLEMA

### Commit Original

**Commit:** 2172690024873d7a14342ddc7f352e0e1ceea35c
**Autor:** luisrms69
**Fecha:** 2025-07-09 23:09:11
**PR:** #16 - feat(companies): Companies v2.1 - DocTypes Master configurables completos

**Descripción del PR:**
```
### ✅ FASE 2: Company DocType Extensions
- 25+ custom fields organizados en secciones
- Validaciones específicas por tipo de empresa
- Hooks de validación para campos obligatorios
- Contadores automáticos para propiedades administradas
```

**Archivos creados en PR #16:**
```
condominium_management/companies/custom_fields/__init__.py
condominium_management/companies/custom_fields/company_custom_fields.py (246 líneas)
condominium_management/companies/install.py (33 líneas)
```

### Arquitectura Implementada (INCORRECTA)

**Archivo:** `condominium_management/companies/custom_fields/company_custom_fields.py`

**Propósito:** Crear 32 custom fields en Company DocType

**Método:**
```python
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_company_custom_fields():
	"""Crear campos personalizados para Company DocType"""
	custom_fields = {
		"Company": [
			{
				"fieldname": "condominium_section",
				"label": "Información de Condominio",
				"fieldtype": "Section Break",
				...
			},
			# ... 31 campos más
		]
	}
	create_custom_fields(custom_fields)
```

**¿Cómo se instalaron?**
- **NO automáticamente** (no está en hooks.py after_install)
- **Manualmente** ejecutando: `companies.install.install_company_customizations()`
- **Fecha instalación admin1.dev:** 2025-07-09 00:13:53 (según Custom Field creation timestamp)

---

## CUSTOM FIELDS AFECTADOS (32 totales)

### Sección 1: Información de Condominio (10 campos)

| Fieldname | Label | Fieldtype | Propósito |
|-----------|-------|-----------|-----------|
| condominium_section | Información de Condominio | Section Break | Header sección |
| company_type | Tipo de Empresa | Link (Company Type) | Clasificación |
| property_usage_type | Tipo de Uso de Propiedad | Link (Property Usage Type) | Uso propiedad |
| acquisition_type | Tipo de Adquisición | Link (Acquisition Type) | Cómo se adquirió |
| property_status_type | Estado de la Propiedad | Link (Property Status Type) | Estado actual |
| cb_condominium_1 | (Column Break) | Column Break | Layout |
| total_units | Total de Unidades | Int | Cantidad unidades |
| total_area_sqm | Área Total (m²) | Float | Superficie |
| construction_year | Año de Construcción | Int | Antigüedad |
| floors_count | Número de Pisos | Int | Niveles |

### Sección 2: Información de Administración (5 campos)

| Fieldname | Label | Fieldtype | Propósito |
|-----------|-------|-----------|-----------|
| management_section | Información de Administración | Section Break | Header sección |
| management_company | Empresa Administradora | Link (Company) | Quién administra |
| management_start_date | Fecha Inicio Administración | Date | Inicio contrato |
| management_contract_end_date | Fecha Fin Contrato | Date | Fin contrato |
| managed_properties | Propiedades Administradas | Int (read-only) | Contador automático |

### Sección 3: Información Legal (6 campos)

| Fieldname | Label | Fieldtype | Propósito |
|-----------|-------|-----------|-----------|
| legal_section | Información Legal | Section Break | Header sección |
| legal_representative | Representante Legal | Data | Nombre rep legal |
| legal_representative_id | Cédula Representante Legal | Data | ID rep legal |
| cb_legal_1 | (Column Break) | Column Break | Layout |
| registration_chamber_commerce | Registro Cámara de Comercio | Data | Registro legal |
| registration_date | Fecha de Registro | Date | Fecha registro |

### Sección 4: Información Financiera (6 campos)

| Fieldname | Label | Fieldtype | Propósito |
|-----------|-------|-----------|-----------|
| financial_section | Información Financiera | Section Break | Header sección |
| monthly_admin_fee | Cuota Administración Mensual | Currency | Cuota mensual |
| reserve_fund | Fondo de Reserva | Currency | Reservas |
| cb_financial_1 | (Column Break) | Column Break | Layout |
| insurance_policy_number | Póliza de Seguro | Data | Número póliza |
| insurance_expiry_date | Fecha Vencimiento Seguro | Date | Vencimiento |

### Lógica de Negocio

**Conditional Display (depends_on):**
- Campos condominio: `eval: doc.company_type == 'Condominio'`
- Campos administradora: `eval: doc.company_type == 'Administradora'`
- Contador managed_properties: Solo visible para Administradoras

**Validaciones:**
- `company_type` requerido para activar campos específicos
- Links a Master DocTypes configurables (Company Type, Property Usage Type, etc.)
- Fechas management_start_date < management_contract_end_date (no implementada)

---

## ESTADO ACTUAL EN ADMIN1.DEV

**Verificación ejecutada:**
```bash
bench --site admin1.dev execute "condominium_management.one_offs.check_custom_fields.run"
```

**Resultado:**
- ✅ 38 custom fields instalados en Company
- ✅ 32 son de condominium_management (resto HRMS ERPNext)
- ✅ Todos con labels en español (RG-001 compliance)
- ✅ Funcionando correctamente

**Metadata:**
- Owner: Administrator
- Modified By: Administrator
- Creation: 2025-07-09 00:13:53.475704
- Module: None ⚠️ (debería ser "Companies")

---

## PROBLEMA: ZERO-CONFIG DEPLOYMENT ROTO

### Escenario Fallido

**Setup:**
1. Nuevo sitio: `bench new-site nuevo.dev`
2. Instalar app: `bench --site nuevo.dev install-app condominium_management`
3. Migrar: `bench --site nuevo.dev migrate`

**Resultado esperado (RG-009):**
- ✅ Todos los DocTypes creados
- ✅ Todos los fixtures cargados
- ✅ Todos los custom fields instalados
- ✅ Sistema funcional sin configuración manual

**Resultado REAL:**
- ✅ DocTypes creados
- ✅ Fixtures cargados (12 masters)
- ❌ Custom fields NO instalados (falta fixture)
- ❌ Formulario Company incompleto
- ❌ Funcionalidad Companies v2.1 rota

### ¿Por qué NO se instalan?

**Archivo:** `condominium_management/companies/install.py`
```python
def install_company_customizations():
	"""Instalar personalizaciones de Company"""
	create_company_custom_fields()
	frappe.db.commit()
```

**Problema:** Esta función NO está registrada en `hooks.py`

**Verificación:**
```bash
$ grep "install_company_customizations" condominium_management/hooks.py
(sin resultados)
```

**Conclusión:** Los custom fields se instalaron MANUALMENTE en admin1.dev, no automáticamente.

---

## OTROS MÓDULOS AFECTADOS

### Verificación Exhaustiva

**Búsqueda ejecutada:**
```bash
find condominium_management -name "*custom_field*" -o -name "install.py"
```

**Resultado:**
- ❌ physical_spaces: NO tiene custom fields Python
- ❌ financial_management: NO tiene custom fields Python
- ❌ committee_management: NO tiene custom fields Python
- ❌ dashboard_consolidado: NO tiene custom fields Python

**Conclusión:** El problema está AISLADO al módulo Companies.

### Auditoría Custom Fields Sistema Completo

**Total custom fields en sistema:** 118
- Company: 38 (32 condominium + 6 HRMS)
- Otros DocTypes ERPNext: 77 (instalados por ERPNext/HRMS)
- DocTypes propios app: 0

**Conclusión:** Solo los 32 custom fields de Companies están afectados.

---

## ANÁLISIS DEL CÓDIGO

### ¿El archivo .py tiene lógica útil?

**NO.** El archivo `company_custom_fields.py` SOLO define custom fields.

**Contenido:**
1. `create_company_custom_fields()` - Crea los 32 custom fields
2. `remove_company_custom_fields()` - Los elimina (uninstall)

**NO contiene:**
- ❌ Validaciones de negocio
- ❌ Hooks
- ❌ Lógica compleja
- ❌ Cálculos
- ❌ Transformaciones

**Es 100% definición de campos** (debería ser JSON fixture).

### Archivo install.py

**Propósito:** Wrapper para instalar/desinstalar custom fields

**Contenido:**
```python
def install_company_customizations():
	create_company_custom_fields()
	frappe.db.commit()

def uninstall_company_customizations():
	remove_company_custom_fields()
	frappe.db.commit()
```

**Uso actual:** Ninguno (no llamado desde hooks.py)

**Debería eliminarse** si migramos a fixtures.

---

## OPCIONES DE SOLUCIÓN

### Opción A: Fixtures JSON (RECOMENDADA)

**Descripción:**
Exportar los 32 custom fields actuales a fixture JSON usando `export-fixtures`.

**Ventajas:**
- ✅ Cumple RG-009 (zero-config)
- ✅ Patrón estándar Frappe
- ✅ Auto-instalación en nuevos sitios
- ✅ Control de versiones (JSON en git)
- ✅ Frappe maneja actualizaciones
- ✅ Sin código Python extra

**Desventajas:**
- ⚠️ Archivo JSON grande (~500-800 líneas estimadas)
- ⚠️ Menos legible que Python

**Implementación:**
```bash
# 1. Exportar custom fields actuales
bench --site admin1.dev export-fixtures --app condominium_management

# 2. Agregar Custom Field a hooks.py fixtures
fixtures = [
	# ... existentes
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "=", "Company"],
			["fieldname", "in", [
				"condominium_section", "company_type", ..., "insurance_expiry_date"
			]]
		]
	}
]

# 3. Eliminar archivos Python
rm condominium_management/companies/custom_fields/company_custom_fields.py
rm condominium_management/companies/install.py
```

**Esfuerzo:** 1-2 horas (exportar, validar, tests)

---

### Opción B: After Install Hook

**Descripción:**
Registrar `install_company_customizations()` en hooks.py `after_install`.

**Ventajas:**
- ✅ Código Python existente sigue funcionando
- ✅ Instalación automática nuevos sitios
- ✅ Lógica centralizada en .py

**Desventajas:**
- ❌ NO cumple RG-009 (fixtures obligatorios)
- ❌ Ejecuta cada vez (no idempotente clean)
- ❌ Hook after_install corre UNA VEZ (updates manuales)
- ❌ Más complejo que fixtures
- ❌ Frappe recomienda fixtures para custom fields

**Implementación:**
```python
# hooks.py
after_install = "condominium_management.companies.install.install_company_customizations"
```

**Esfuerzo:** 15 minutos (agregar hook, tests)

---

### Opción C: Patch (NO RECOMENDADA para Custom Fields)

**Descripción:**
Crear patch en `patches.txt` para instalar custom fields.

**Ventajas:**
- ✅ Idempotente (ejecuta una vez)
- ✅ Versionado (trackeado en patches)

**Desventajas:**
- ❌ Patches son para migraciones de datos, NO custom fields
- ❌ NO cumple RG-009
- ❌ Frappe recomienda fixtures para DocType-level changes
- ❌ Complejidad innecesaria

**NO RECOMENDADO** según best practices Frappe.

---

## RECOMENDACIÓN FINAL

**OPCIÓN A: Fixtures JSON**

**Razones:**
1. **Cumple RG-009** (zero-config deployment obligatorio)
2. **Best practice Frappe** (fixtures para custom fields)
3. **Auto-instalación** en nuevos sitios
4. **Mantenibilidad** superior
5. **Control versiones** (JSON en git)

**Plan de Implementación:**

### Fase 1: Exportar y Validar (30 min)

```bash
# 1. Exportar custom fields actuales de admin1.dev
bench --site admin1.dev export-fixtures --app condominium_management

# 2. Verificar archivo generado
cat condominium_management/fixtures/custom_field.json

# 3. Validar JSON syntax
python -m json.tool condominium_management/fixtures/custom_field.json > /dev/null
```

### Fase 2: Configurar hooks.py (15 min)

```python
# hooks.py - Agregar a fixtures list
fixtures = [
	# ... fixtures existentes (12) ...
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "=", "Company"],
			["fieldname", "in", [
				"condominium_section", "company_type", "property_usage_type",
				"acquisition_type", "property_status_type", "cb_condominium_1",
				"total_units", "total_area_sqm", "construction_year", "floors_count",
				"management_section", "management_company", "management_start_date",
				"management_contract_end_date", "managed_properties",
				"legal_section", "legal_representative", "legal_representative_id",
				"cb_legal_1", "registration_chamber_commerce", "registration_date",
				"financial_section", "monthly_admin_fee", "reserve_fund",
				"cb_financial_1", "insurance_policy_number", "insurance_expiry_date"
			]]
		]
	}
]
```

### Fase 3: Testing Instalación Fresh (30 min)

```bash
# 1. Crear sitio test
bench new-site test-zero-config.dev --admin-password admin

# 2. Instalar app
bench --site test-zero-config.dev install-app condominium_management

# 3. Verificar custom fields instalados
bench --site test-zero-config.dev execute \
  "condominium_management.one_offs.check_custom_fields.run"

# Debe mostrar: ✅ Custom Fields en Company DocType: 32+
```

### Fase 4: Cleanup (15 min)

```bash
# Eliminar archivos Python obsoletos
git rm condominium_management/companies/custom_fields/company_custom_fields.py
git rm condominium_management/companies/install.py
git rm -r condominium_management/companies/custom_fields/

# Commit
git commit -m "fix(companies): migrar custom fields de Python a fixtures JSON

Corrige violación RG-009 (zero-config deployment):
- Exportar 32 custom fields Company a fixtures/custom_field.json
- Registrar en hooks.py fixtures
- Eliminar código Python programático obsoleto

Validado con instalación fresh en test-zero-config.dev

BREAKING: Requiere bench migrate en sitios existentes"
```

### Fase 5: Documentación (15 min)

**Actualizar docs/development/workflows/troubleshooting.md:**

```markdown
## Custom Fields faltantes después de install

**Síntoma:** Formulario Company no muestra campos de condominio

**Solución:**
1. Verificar fixtures cargados:
   bash
   bench --site [sitio] import-fixtures --app condominium_management


2. Si persiste, reinstalar app:
   bash
   bench --site [sitio] reinstall --app condominium_management

```

---

## IMPACTO Y RIESGOS

### Impacto Positivo

- ✅ Zero-config deployment funcional
- ✅ Cumplimiento RG-009
- ✅ Instalaciones futuras sin manual setup
- ✅ Código más limpio (menos Python)
- ✅ Control versiones custom fields

### Riesgos

⚠️ **RIESGO MEDIO:** Sitios existentes (admin1.dev)
- **Problema:** Ya tienen custom fields instalados
- **Solución:** `import-fixtures` es idempotente, no duplica
- **Validación:** Probar en admin1.dev antes de commit

⚠️ **RIESGO BAJO:** Orden de campos
- **Problema:** Fixture puede cambiar idx
- **Solución:** Exportar con orden actual preservado

### Plan de Rollback

**Si algo falla:**
```bash
# 1. Restaurar archivos Python
git checkout HEAD~1 -- condominium_management/companies/custom_fields/
git checkout HEAD~1 -- condominium_management/companies/install.py

# 2. Reinstalar custom fields manualmente
bench --site [sitio] execute \
  "condominium_management.companies.install.install_company_customizations"
```

---

## CRONOGRAMA PROPUESTO

| Fase | Actividad | Tiempo | Ejecutor |
|------|-----------|--------|----------|
| 1 | Exportar custom fields a JSON | 30 min | Claude Code |
| 2 | Actualizar hooks.py | 15 min | Claude Code |
| 3 | Test instalación fresh | 30 min | Claude Code |
| 4 | Validar admin1.dev | 15 min | Usuario |
| 5 | Cleanup código Python | 15 min | Claude Code |
| 6 | Documentación | 15 min | Claude Code |
| 7 | Commit y PR | 10 min | Claude Code |
| **TOTAL** | | **2 horas** | |

---

## CONCLUSIÓN

**Hallazgo:** Violación crítica RG-009 en módulo Companies
**Afecta:** 32 custom fields en Company DocType
**Origen:** PR #16 (2025-07-09)
**Solución recomendada:** Opción A (Fixtures JSON)
**Esfuerzo:** 2 horas
**Prioridad:** Alta (bloquea deployment)

**Próximo paso:** Autorización para implementar Opción A

---

**Preparado:** 2025-10-20
**Ejecutor:** Claude Code
**Estado:** ⏳ Esperando autorización implementación
