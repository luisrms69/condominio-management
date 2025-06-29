# 🏗️ ARQUITECTURA DEL MÓDULO 1: COMPANIES

## 📋 **Metadatos del Módulo**
- **Nombre:** Companies
- **Propósito:** Gestión de contratos de servicios entre empresas administradoras y condominios
- **Estado:** ✅ Implementado y Funcional
- **Versión:** 1.0
- **Fecha:** 28 de junio de 2025

---

## 🎯 **Objetivo del Módulo**

Gestionar las relaciones contractuales entre **empresas administradoras** y **condominios clientes**, incluyendo:

1. **Contratos de Servicios:** Acuerdos comerciales entre administradoras y condominios
2. **Información de Condominios:** Datos detallados de cada condominio (ubicación, accesos, contactos)
3. **Sincronización de Datos:** Configuración para compartir master data entre empresas

---

## 📊 **Estructura de DocTypes**

### **🏢 DocTypes Principales (3)**

#### **1. Service Management Contract**
- **Propósito:** Contrato principal entre administradora y condominio
- **Campos clave:** 
  - Empresas involucradas (administradora/cliente)
  - Términos financieros (tarifa, moneda, términos de pago)
  - Servicios proporcionados
  - Configuración de sincronización de datos
- **Validaciones:** Fechas, empresas diferentes, términos financieros

#### **2. Condominium Information** 
- **Propósito:** Información detallada del condominio cliente
- **Campos clave:**
  - Datos básicos (superficie, unidades, año construcción)
  - Información de acceso y transporte
  - Contactos y servicios disponibles
- **Validaciones:** Cálculo de áreas, contactos únicos

#### **3. Master Data Sync Configuration**
- **Propósito:** Configuración para sincronización automática de datos maestros
- **Campos clave:**
  - Empresa origen y empresas destino
  - Tipos de datos a sincronizar
  - Frecuencia y configuración de conflictos
- **Validaciones:** Empresas diferentes, tipos de datos válidos

### **📋 Child Tables (9)**

#### **Servicios y Configuración (3)**
1. **Contract Service Item** - Servicios incluidos en el contrato
2. **Sync Data Type** - Tipos de datos para sincronización
3. **Target Company Sync** - Empresas destino para sincronización

#### **Información de Condominio (6)**
4. **Access Point Detail** - Puntos de acceso al condominio
5. **Contact Information** - Contactos del condominio
6. **Operating Hours** - Horarios de operación
7. **Public Transport Option** - Opciones de transporte público
8. **Nearby Reference** - Referencias cercanas
9. **Service Information** - Servicios disponibles en el condominio

---

## 🔧 **Reglas de Negocio Implementadas**

### **Validaciones Críticas**

#### **Service Management Contract:**
```python
# Fechas del contrato
if contract_end < contract_start:
    frappe.throw(_("La fecha de fin del contrato no puede ser anterior a la fecha de inicio"))

# Empresas diferentes
if service_provider == client_condominium:
    frappe.throw(_("La empresa administradora no puede ser la misma que el condominio cliente"))

# Servicios únicos
if len(service_names) != len(set(service_names)):
    frappe.throw(_("No puede haber servicios duplicados"))
```

#### **Condominium Information:**
```python
# Validación de áreas
if abs((common_area + private_area) - total_area) > 1:
    frappe.msgprint(_("La suma de áreas no coincide con el área total"))

# Contactos primarios únicos
primary_contacts = [c for c in contacts if c.is_primary]
if len(primary_contacts) > 1:
    frappe.throw(_("Solo puede haber un contacto principal por tipo"))
```

#### **Master Data Sync Configuration:**
```python
# Empresa origen diferente a destinos
if target.target_company == source_company:
    frappe.throw(_("La empresa origen no puede ser también empresa destino"))
```

---

## 🇪🇸 **Estándares de Localización**

### **Regla Principal: Etiquetas en Español**
- ✅ **Variables/campos:** en inglés (`contract_name`, `service_provider`)
- ✅ **Labels/etiquetas:** en español ("Nombre del Contrato", "Empresa Administradora")
- ✅ **Opciones de Select:** en español ("Activo", "Suspendido", "Terminado")
- ✅ **Mensajes de error:** en español con función `_()`

### **Ejemplos de Traducciones Aplicadas:**
```json
// Correcto
{
  "fieldname": "contract_status",
  "label": "Estado del Contrato",
  "options": "Activo\nSuspendido\nTerminado"
}

// Corregido de inglés a español
{
  "fieldname": "data_type", 
  "label": "Tipo de Dato",
  "options": "Proveedor\nArtículo\nPlantilla de Email\nFormato de Impresión"
}
```

---

## 📁 **Estructura de Archivos**

### **Configuración del Módulo:**
```
condominium_management/
├── modules.txt                    # "Companies"
├── hooks.py                      # Configuración de módulos
└── companies/
    ├── __init__.py
    ├── modules.txt               # "Companies"
    └── doctype/
        ├── service_management_contract/
        │   ├── service_management_contract.json
        │   ├── service_management_contract.py
        │   ├── test_service_management_contract.py
        │   └── __init__.py
        ├── condominium_information/
        │   ├── condominium_information.json
        │   ├── condominium_information.py
        │   ├── test_condominium_information.py
        │   └── __init__.py
        └── [9 child tables con estructura similar]
```

### **hooks.py - Configuración Crítica:**
```python
required_apps = ["frappe", "erpnext"]

modules = {
    "companies": {
        "color": "blue",
        "icon": "octicon octicon-organization",
        "type": "module",
        "label": "Companies"
    }
}
```

---

## ⚙️ **Funcionalidades Técnicas**

### **Naming Series Implementados:**
- **SMC-.YYYY.-** para Service Management Contract
- **MDSC-.YYYY.-** para Master Data Sync Configuration
- **CI-.####** para Condominium Information

### **Links y Relaciones:**
- **Company** → Service Provider / Client Condominium
- **Currency** → Moneda del contrato (default: MXN)
- **Payment Terms** → Términos de pago estándar de ERPNext

### **Permisos por Rol:**
```json
{
  "role": "System Manager",     // Control total
  "role": "Accounts Manager",   // Lectura/escritura de contratos
  "role": "Company Administrator"  // Gestión de información de condominio
}
```

---

## 🔄 **Flujos de Trabajo**

### **1. Creación de Contrato de Servicios:**
```
1. Crear Service Management Contract
   ├── Definir empresas (administradora/cliente)
   ├── Establecer términos financieros
   ├── Agregar servicios proporcionados
   └── Configurar sincronización de datos

2. Validaciones automáticas
   ├── Fechas del contrato coherentes
   ├── Empresas diferentes
   ├── Servicios únicos
   └── Términos financieros válidos

3. Al confirmar (Submit)
   ├── Crear configuración de sincronización automática
   ├── Generar eventos de calendario para renovación
   └── Activar flujos de datos entre empresas
```

### **2. Configuración de Información de Condominio:**
```
1. Crear Condominium Information
   ├── Vincular a Company existente
   ├── Agregar información básica (áreas, unidades)
   ├── Definir puntos de acceso
   ├── Configurar contactos
   └── Establecer servicios disponibles

2. Validaciones automáticas
   ├── Coherencia en cálculo de áreas
   ├── Contacto principal único por tipo
   └── Información de acceso completa
```

### **3. Sincronización de Master Data:**
```
1. Configurar Master Data Sync Configuration
   ├── Definir empresa origen
   ├── Seleccionar empresas destino
   ├── Especificar tipos de datos
   └── Establecer frecuencia

2. Ejecución automática
   ├── Scheduler diario para sync automático
   ├── Resolución de conflictos según configuración
   └── Log de errores y seguimiento
```

---

## 📈 **Métricas y Monitoreo**

### **KPIs del Módulo:**
- **Contratos Activos:** Número de contratos vigentes
- **Condominios Gestionados:** Total de condominios bajo administración
- **Configuraciones de Sync:** Sincronizaciones activas
- **Tasa de Éxito de Sync:** % de sincronizaciones exitosas

### **Reportes Sugeridos:**
1. **Contratos por Vencer** - Dashboard de renovaciones próximas
2. **Ingresos por Administradora** - Análisis financiero por empresa
3. **Estado de Sincronizaciones** - Monitoreo técnico de datos
4. **Condominios por Región** - Análisis geográfico

---

## 🔮 **Expansiones Futuras**

### **Funcionalidades Planeadas:**
1. **Automatización de Facturación** - Generación automática basada en contratos
2. **Portal de Cliente** - Acceso web para condominios
3. **Integración con Contabilidad** - Links directos con módulos financieros
4. **Geolocalización** - Mapas y ubicación GPS de condominios
5. **Análisis Predictivo** - ML para optimización de servicios

### **Integraciones Técnicas:**
- **API REST** para sincronización externa
- **Webhooks** para notificaciones en tiempo real
- **Mobile App** para gestión en campo
- **Business Intelligence** para analytics avanzados

---

## 🎯 **Lecciones Aprendidas**

### **Factores Críticos de Éxito:**
1. **modules.txt correcto** - Debe coincidir exactamente con carpetas
2. **hooks.py completo** - Configuración de módulos es esencial
3. **Etiquetas en español** - Consistencia en localización
4. **Validaciones robustas** - Prevenir errores de datos desde el diseño

### **Mejores Prácticas Identificadas:**
- **Diagnóstico antes de acción** - Entender el problema antes de solucionarlo
- **Iteración sobre perfección** - MVP funcional antes que solución completa
- **Documentación contemporánea** - Documentar mientras se desarrolla
- **Estándares consistentes** - Aplicar reglas uniformemente

---

## 📋 **Checklist de Implementación**

### **Pre-requisitos:**
- [ ] Frappe v15 / ERPNext instalado
- [ ] App condominium_management creada
- [ ] Developer mode habilitado

### **Configuración Base:**
- [ ] modules.txt correcto ("Companies")
- [ ] hooks.py con configuración de módulos
- [ ] Estructura de carpetas companies/

### **DocTypes:**
- [ ] 3 DocTypes principales creados
- [ ] 9 Child tables implementadas
- [ ] Archivos Python completos (.py, test_.py, __init__.py)
- [ ] Todas las etiquetas en español

### **Validación:**
- [ ] bench migrate exitoso
- [ ] DocTypes visibles en interfaz
- [ ] Documentos se pueden crear y guardar
- [ ] Validaciones de negocio funcionando

---

**📝 Arquitectura validada en entorno real**
**🎯 Base sólida para expansión del sistema**
**✅ Listo para desarrollo de módulos siguientes**

---

**Elaborado por:** Equipo de Desarrollo Condominium Management  
**Validado por:** Claude 4 Sonnet  
**Fecha:** 28 de junio de 2025