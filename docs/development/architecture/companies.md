# Companies - Arquitectura Técnica

**Fecha implementación:** 2025-06-28
**Estado:** ✅ IMPLEMENTADO Y FUNCIONAL
**Versión:** 1.0

---

## Decisiones Clave

### Decisión 1: Modelo de Contratos de Servicios

**Contexto:** Necesitábamos gestionar relaciones contractuales entre empresas administradoras y condominios clientes.

**Decisión:** Crear **Service Management Contract** como DocType principal que vincula administradora con condominio cliente.

**Alternativas consideradas:**
- Usar solo Company de ERPNext (insuficiente para relaciones contractuales)
- Crear relación directa sin contrato (pérdida de información comercial)

**Consecuencias:**
- ✅ Información contractual completa (términos, servicios, fechas)
- ✅ Trazabilidad de relaciones comerciales
- ✅ Base para facturación y reporting
- ❌ DocType adicional que mantener

**Fecha:** 2025-06-28

---

### Decisión 2: Condominium Information Separado

**Contexto:** Condominios requieren información detallada (accesos, contactos, servicios) más allá de lo que Company standard provee.

**Decisión:** Crear **Condominium Information** como DocType independiente vinculado a Company.

**Alternativas consideradas:**
- Custom Fields en Company (demasiados campos, contamina Company)
- Child Table en Contract (información no contractual)

**Consecuencias:**
- ✅ Separación de concerns (Company = financiero, Condominium Info = operacional)
- ✅ Información detallada sin contaminar DocType core
- ✅ Reutilizable para múltiples contratos
- ❌ Link adicional que gestionar

**Fecha:** 2025-06-28

---

### Decisión 3: Master Data Sync Configuration

**Contexto:** Necesitábamos compartir master data (proveedores, artículos, templates) entre empresas del grupo.

**Decisión:** Sistema de **sincronización configurable** con empresa origen y múltiples destinos.

**Alternativas consideradas:**
- Sincronización automática total (riesgo de sobrescribir datos locales)
- Manual copy-paste (error-prone, no escalable)
- Database-level replication (complejidad innecesaria)

**Consecuencias:**
- ✅ Control granular de qué sincronizar
- ✅ Configuración de conflictos
- ✅ Escalable a N empresas
- ❌ Lógica de sincronización compleja
- ⚠️ Requiere validación de conflictos cuidadosa

**Fecha:** 2025-06-29

---

### Decisión 4: Validaciones Empresas Diferentes

**Contexto:** Prevenir configuraciones inválidas (empresa contratándose a sí misma, sincronizando consigo misma).

**Decisión:** **Validación estricta** que empresa origen ≠ empresa destino en todos los DocTypes.

**Consecuencias:**
- ✅ Previene errores de configuración
- ✅ Datos consistentes
- ✅ Tests más simples (casos inválidos rechazados temprano)
- ❌ Casos edge donde podría ser útil (rechazado intencionalmente)

**Fecha:** 2025-06-28

---

### Decisión 5: Child Tables para Información Detallada

**Contexto:** Condominios tienen múltiples contactos, accesos, servicios, referencias.

**Decisión:** **6 Child Tables** especializadas en Condominium Information.

**Alternativas consideradas:**
- JSON field (pérdida de tipado y validaciones)
- Tabla única genérica (complejidad queries)

**Consecuencias:**
- ✅ Tipado fuerte por tipo de información
- ✅ Validaciones específicas por child table
- ✅ Queries eficientes
- ❌ Más child tables que mantener
- ✅ Claridad en UI (sección por tipo)

**Fecha:** 2025-06-29

---

## Arquitectura Técnica

### Objetivo del Módulo

Gestionar relaciones contractuales entre **empresas administradoras** y **condominios clientes**:

1. **Contratos de Servicios** - Acuerdos comerciales
2. **Información de Condominios** - Datos operacionales detallados
3. **Sincronización de Datos** - Master data entre empresas

---

## DocTypes Principales

### 1. Service Management Contract

**Propósito:** Contrato principal entre administradora y condominio.

**Campos clave:**
- `service_provider` (Link: Company) - Empresa administradora
- `client_condominium` (Link: Company) - Condominio cliente
- `contract_start_date` / `contract_end_date` - Vigencia
- `monthly_fee` / `currency` - Términos financieros
- `contract_services` (Table) - Servicios incluidos
- `sync_configuration` (Link) - Configuración sincronización

**Validaciones implementadas:**
```python
# Fechas lógicas
if contract_end < contract_start:
    frappe.throw("Fecha fin no puede ser anterior a inicio")

# Empresas diferentes
if service_provider == client_condominium:
    frappe.throw("Administradora no puede ser cliente")

# Servicios únicos
if len(service_names) != len(set(service_names)):
    frappe.throw("No puede haber servicios duplicados")
```

---

### 2. Condominium Information

**Propósito:** Información detallada del condominio cliente.

**Campos clave:**
- `condominium_company` (Link: Company) - Vinculación a Company
- `total_surface_area` / `private_area` / `common_area` - Superficies
- `total_units` / `construction_year` - Datos básicos
- `access_points` (Table) - Puntos de acceso
- `contacts` (Table) - Contactos
- `operating_hours` (Table) - Horarios
- `public_transport` (Table) - Transporte público
- `nearby_references` (Table) - Referencias cercanas
- `services_available` (Table) - Servicios disponibles

**Validaciones implementadas:**
```python
# Validación de áreas (tolerancia 1m²)
if abs((common_area + private_area) - total_area) > 1:
    frappe.msgprint("Suma de áreas no coincide con total")

# Contacto primario único por tipo
primary_contacts = [c for c in contacts if c.is_primary]
contact_types = [c.contact_type for c in primary_contacts]
if len(contact_types) != len(set(contact_types)):
    frappe.throw("Solo un contacto principal por tipo")
```

---

### 3. Master Data Sync Configuration

**Propósito:** Configuración para sincronización automática de master data.

**Campos clave:**
- `source_company` (Link: Company) - Empresa origen
- `target_companies` (Table) - Empresas destino
- `data_types` (Table) - Tipos de datos a sincronizar
- `sync_frequency` (Select) - Frecuencia sincronización
- `conflict_resolution` (Select) - Estrategia conflictos

**Validaciones implementadas:**
```python
# Empresa origen ≠ destino
for target in target_companies:
    if target.target_company == source_company:
        frappe.throw("Empresa origen no puede ser destino")

# Tipos de datos únicos
if len(data_type_names) != len(set(data_type_names)):
    frappe.throw("No puede haber tipos de datos duplicados")
```

---

## Child Tables (9)

### Servicios y Configuración (3)

1. **Contract Service Item**
   - Servicios incluidos en contrato
   - Campos: `service_name`, `service_description`, `is_included`

2. **Sync Data Type**
   - Tipos de datos para sincronización
   - Opciones: Proveedor, Artículo, Plantilla Email, Formato Impresión

3. **Target Company Sync**
   - Empresas destino sincronización
   - Campos: `target_company`, `is_active`

### Información Condominio (6)

4. **Access Point Detail**
   - Puntos de acceso al condominio
   - Campos: `access_name`, `access_type`, `access_description`

5. **Contact Information**
   - Contactos del condominio
   - Campos: `contact_type`, `contact_name`, `phone`, `email`, `is_primary`

6. **Operating Hours**
   - Horarios de operación
   - Campos: `day_of_week`, `opening_time`, `closing_time`

7. **Public Transport Option**
   - Transporte público cercano
   - Campos: `transport_type`, `line_name`, `distance_meters`

8. **Nearby Reference**
   - Referencias cercanas para ubicación
   - Campos: `reference_type`, `reference_name`, `description`

9. **Service Information**
   - Servicios disponibles
   - Campos: `service_type`, `service_name`, `provider`

---

## Estándares de Localización

### Regla Principal: Español Obligatorio

**✅ Implementado correctamente:**
- Variables/campos: inglés (`contract_name`, `service_provider`)
- Labels/etiquetas: español ("Nombre del Contrato", "Empresa Administradora")
- Opciones Select: español ("Activo", "Suspendido", "Terminado")
- Mensajes error: español con función `_()`

**Ejemplo correcto:**
```json
{
  "fieldname": "contract_status",
  "label": "Estado del Contrato",
  "options": "Activo\nSuspendido\nTerminado"
}
```

---

## Estructura de Archivos

```
condominium_management/companies/
├── doctype/
│   ├── service_management_contract/
│   │   ├── service_management_contract.json
│   │   ├── service_management_contract.py
│   │   ├── test_service_management_contract.py
│   │   └── __init__.py
│   ├── condominium_information/
│   │   ├── condominium_information.json
│   │   ├── condominium_information.py
│   │   ├── test_condominium_information.py
│   │   └── __init__.py
│   ├── master_data_sync_configuration/
│   │   ├── master_data_sync_configuration.json
│   │   ├── master_data_sync_configuration.py
│   │   ├── test_master_data_sync_configuration.py
│   │   └── __init__.py
│   └── [9 child tables]/
└── __init__.py
```

---

## Testing Implementado

### Cobertura Tests

**Service Management Contract:**
- ✅ Creación básica
- ✅ Validación fechas
- ✅ Validación empresas diferentes
- ✅ Servicios únicos
- ✅ Labels en español

**Condominium Information:**
- ✅ Creación básica
- ✅ Validación áreas
- ✅ Contactos primarios únicos
- ✅ Child tables funcionando

**Master Data Sync Configuration:**
- ✅ Creación básica
- ✅ Validación empresa origen ≠ destino
- ✅ Tipos de datos únicos

---

## Recursos Adicionales

- [Physical Spaces Architecture](physical-spaces.md) - Arquitectura espacios físicos
- [Testing Best Practices](../testing/best-practices.md) - Metodología testing
- [Known Issues](../framework-knowledge/known-issues.md) - Issues framework

---

**Documentado:** 2025-10-17
**Fuente:** buzola-internal/ARCHITECTURE_MODULE_1_COMPANIES.md
**Mantenido por:** Dev Team
