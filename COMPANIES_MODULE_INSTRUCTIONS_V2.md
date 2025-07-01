# 📋 Módulo Companies - Instrucciones Corregidas y Actualizadas

## 📝 **Metadatos de la Configuración**
- **Versión:** 2.0 (Actualizada con reglas de español)
- **Basado en:** Implementación exitosa y correcciones aplicadas
- **Estado:** ✅ Validado en entorno real 
- **Framework:** Frappe v15 / ERPNext
- **Módulo:** Companies
- **DocTypes:** 12 (3 principales + 9 child tables)

---

## 🇪🇸 **REGLA CRÍTICA: ETIQUETAS EN ESPAÑOL**

### **⚠️ IMPORTANTE: APLICAR SIEMPRE**
**TODAS las etiquetas (labels) y opciones DEBEN estar en español, incluso si las instrucciones originales vienen en inglés.**

#### **✅ Ejemplos Correctos:**
```json
{
  "fieldname": "contract_name",        // ✅ Variable en inglés
  "fieldtype": "Data",
  "label": "Nombre del Contrato",      // ✅ Label en español
  "reqd": 1
}

{
  "fieldname": "contract_status",
  "fieldtype": "Select", 
  "label": "Estado del Contrato",      // ✅ Label en español
  "options": "Activo\nSuspendido\nTerminado"  // ✅ Opciones en español
}
```

#### **❌ Ejemplos Incorrectos:**
```json
{
  "fieldname": "contract_name",
  "label": "Contract Name",           // ❌ Label en inglés
}

{
  "fieldname": "data_type",
  "label": "Tipo de Dato",            // ✅ Label correcto
  "options": "Supplier\nItem"         // ❌ Opciones en inglés
}
```

---

## 🎯 **PASO 1: Configuración Base Crítica**

### **1.1 Verificar/Corregir modules.txt**
```bash
# CRÍTICO: Verificar contenido actual
cat ~/frappe-bench/apps/condominium_management/condominium_management/modules.txt

# DEBE CONTENER EXACTAMENTE:
# Companies
# (Sin espacios, sin caracteres extra)

# Si está incorrecto, corregir:
echo "Companies" > ~/frappe-bench/apps/condominium_management/condominium_management/modules.txt
```

### **1.2 Actualizar hooks.py Completo**
```python
# ~/frappe-bench/apps/condominium_management/condominium_management/hooks.py

from . import __version__ as app_version

app_name = "condominium_management"
app_title = "Condominium Management"
app_publisher = "Buzola"
app_description = "Sistema integral de gestión de condominios"
app_email = "it@buzola.mx"
app_license = "gpl-3.0"

# CRÍTICO: No debe estar comentado
required_apps = ["frappe", "erpnext"]

# CRÍTICO: Configuración de módulos
modules = {
    "companies": {
        "color": "blue",
        "icon": "octicon octicon-organization",
        "type": "module",
        "label": "Companies"
    }
}
```

### **1.3 Verificar Estructura de Carpetas**
```bash
# Verificar que existe y tiene estructura correcta
ls -la ~/frappe-bench/apps/condominium_management/condominium_management/companies/

# Debe mostrar:
# companies/
# ├── __init__.py
# ├── modules.txt (contiene "Companies")
# ├── doctype/
# │   ├── __init__.py
# │   └── [carpetas de doctypes]
```

---

## 🏗️ **PASO 2: Crear DocTypes con Comandos Correctos**

### **2.1 DocTypes Principales**
```bash
cd ~/frappe-bench

# Service Management Contract
bench make-doctype "Service Management Contract" --app condominium_management --module companies

# Master Data Sync Configuration  
bench make-doctype "Master Data Sync Configuration" --app condominium_management --module companies

# Condominium Information
bench make-doctype "Condominium Information" --app condominium_management --module companies
```

### **2.2 Child Tables**
```bash
# Contract Service Item
bench make-doctype "Contract Service Item" --app condominium_management --module companies --is-child-table

# Target Company Sync
bench make-doctype "Target Company Sync" --app condominium_management --module companies --is-child-table

# Sync Data Type
bench make-doctype "Sync Data Type" --app condominium_management --module companies --is-child-table

# Access Point Detail
bench make-doctype "Access Point Detail" --app condominium_management --module companies --is-child-table

# Contact Information
bench make-doctype "Contact Information" --app condominium_management --module companies --is-child-table

# Nearby Reference
bench make-doctype "Nearby Reference" --app condominium_management --module companies --is-child-table

# Operating Hours
bench make-doctype "Operating Hours" --app condominium_management --module companies --is-child-table

# Public Transport Option
bench make-doctype "Public Transport Option" --app condominium_management --module companies --is-child-table

# Service Information
bench make-doctype "Service Information" --app condominium_management --module companies --is-child-table
```

---

## 📝 **PASO 3: Configuración JSON con Etiquetas en Español**

### **3.1 Service Management Contract (Ejemplo Completo)**
```json
{
 "doctype": "DocType",
 "name": "Service Management Contract",
 "module": "Companies",
 "app": "condominium_management",
 "istable": 0,
 "naming_rule": "By \"Naming Series\" field",
 "title_field": "contract_name",
 "fields": [
  {
   "fieldname": "naming_series",
   "fieldtype": "Select",
   "label": "Serie",                    // ✅ Español
   "options": "SMC-.YYYY.-",
   "reqd": 1,
   "default": "SMC-.YYYY.-"
  },
  {
   "fieldname": "contract_name",
   "fieldtype": "Data",
   "label": "Nombre del Contrato",      // ✅ Español
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "section_break_companies",
   "fieldtype": "Section Break",
   "label": "Información de las Empresas"  // ✅ Español
  },
  {
   "fieldname": "service_provider",
   "fieldtype": "Link",
   "label": "Empresa Administradora",   // ✅ Español
   "options": "Company",
   "reqd": 1
  },
  {
   "fieldname": "client_condominium",
   "fieldtype": "Link",
   "label": "Condominio Cliente",       // ✅ Español
   "options": "Company",
   "reqd": 1
  },
  {
   "fieldname": "contract_status",
   "fieldtype": "Select",
   "label": "Estado del Contrato",      // ✅ Español
   "options": "Activo\nSuspendido\nTerminado",  // ✅ Opciones en español
   "default": "Activo"
  }
  // ... más campos con etiquetas en español
 ],
 "permissions": [
  {
   "role": "System Manager",
   "read": 1,
   "write": 1,
   "create": 1,
   "delete": 1
  }
 ]
}
```

### **3.2 Child Tables - Ejemplos con Etiquetas Corregidas**

#### **Sync Data Type (Corregido)**
```json
{
 "doctype": "DocType",
 "name": "Sync Data Type",
 "module": "Companies",
 "app": "condominium_management",
 "istable": 1,
 "fields": [
  {
   "fieldname": "data_type",
   "fieldtype": "Select",
   "label": "Tipo de Dato",             // ✅ Español
   "options": "Proveedor\nArtículo\nPlantilla de Email\nFormato de Impresión\nFlujo de Trabajo\nRol de Usuario\nCampo Personalizado",  // ✅ Opciones en español
   "reqd": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "sync_enabled",
   "fieldtype": "Check",
   "label": "Habilitado",               // ✅ Español
   "default": 1,
   "in_list_view": 1
  }
 ]
}
```

#### **Contact Information**
```json
{
 "fields": [
  {
   "fieldname": "contact_type",
   "fieldtype": "Select",
   "label": "Tipo de Contacto",         // ✅ Español
   "options": "Administración\nSeguridad\nMantenimiento\nEmergencias\nOtro",  // ✅ Opciones en español
   "reqd": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "contact_name",
   "fieldtype": "Data",
   "label": "Nombre de Contacto",       // ✅ Español
   "in_list_view": 1
  }
 ]
}
```

---

## 🇪🇸 **PASO 4: Verificación de Etiquetas en Español**

### **4.1 Checklist de Verificación**
```bash
# Script para verificar etiquetas en español
#!/bin/bash
echo "🇪🇸 Verificando etiquetas en español..."

for json_file in ~/frappe-bench/apps/condominium_management/condominium_management/companies/doctype/*/*.json; do
    echo "Verificando: $json_file"
    
    # Buscar labels que podrían estar en inglés (patrones comunes)
    grep -n '"label":.*"[A-Z].*"' "$json_file" | grep -v "Serie\|Nombre\|Tipo\|Estado\|Fecha\|Email\|Empresa"
    
    # Buscar options que podrían estar en inglés
    grep -n '"options":.*"[A-Z]' "$json_file" | grep -v "MXN\|USD"
done
```

### **4.2 Patrones de Etiquetas Comunes en Español**
```
Contract → Contrato
Name → Nombre  
Type → Tipo
Status → Estado
Date → Fecha
Company → Empresa
Service → Servicio
Configuration → Configuración
Information → Información
Details → Detalles
Options → Opciones
Settings → Configuraciones
Management → Gestión
Administration → Administración
```

---

## 🐍 **PASO 5: Archivos Python con Validaciones en Español**

### **5.1 Mensajes de Error en Español**
```python
# service_management_contract.py (Ejemplo)
import frappe
from frappe.model.document import Document
from frappe import _

class ServiceManagementContract(Document):
    def validate(self):
        self.validate_contract_dates()
        self.validate_companies()
    
    def validate_contract_dates(self):
        """Validar fechas del contrato"""
        if self.contract_end and self.contract_start:
            if self.contract_end < self.contract_start:
                frappe.throw(_("La fecha de fin del contrato no puede ser anterior a la fecha de inicio"))
    
    def validate_companies(self):
        """Validar que las empresas son diferentes"""
        if self.service_provider == self.client_condominium:
            frappe.throw(_("La empresa administradora no puede ser la misma que el condominio cliente"))
```

### **5.2 Mensajes Comunes en Español**
```python
# Errores críticos
frappe.throw(_("Campo requerido: {0}").format(field_label))
frappe.throw(_("La fecha de inicio no puede ser mayor que la fecha de fin"))
frappe.throw(_("El valor debe ser mayor que cero"))

# Advertencias
frappe.msgprint(_("Se recomienda completar este campo"), alert=True)
frappe.msgprint(_("Información guardada exitosamente"))

# Validaciones
if not self.contract_name:
    frappe.throw(_("El nombre del contrato es obligatorio"))
```

---

## 🚀 **PASO 6: Ejecutar Configuración**

### **6.1 Secuencia de Comandos Final**
```bash
# 1. Ir al directorio correcto
cd ~/frappe-bench

# 2. Verificar que modules.txt es correcto
cat apps/condominium_management/condominium_management/modules.txt
# Debe mostrar: Companies

# 3. Verificar hooks.py tiene configuración de módulos
grep -A 5 "modules = {" apps/condominium_management/condominium_management/hooks.py

# 4. Verificar etiquetas en español (opcional)
# Ejecutar script de verificación del PASO 4.1

# 5. Migrar
bench migrate

# 6. Construir assets
bench build

# 7. Reiniciar
bench restart
```

### **6.2 Verificación Final**
```bash
# Verificar que DocTypes aparecen con etiquetas en español
bench --site [sitio] console

# En console:
>>> import frappe
>>> frappe.get_meta("Service Management Contract").get_field("contract_name").label
# Debe retornar: "Nombre del Contrato"

>>> frappe.get_meta("Sync Data Type").get_field("data_type").options
# Debe retornar: "Proveedor\nArtículo\n..."
```

---

## 🎯 **Checklist de Validación Final con Español**

### **✅ Configuración Base:**
- [ ] modules.txt contiene exactamente "Companies"
- [ ] hooks.py tiene required_apps = ["frappe", "erpnext"]
- [ ] hooks.py tiene configuración modules = {...}
- [ ] Carpeta companies/ existe con __init__.py

### **✅ DocTypes:**
- [ ] 3 DocTypes principales creados
- [ ] 9 Child tables creadas
- [ ] Todos tienen archivos .py, .json, test_.py
- [ ] **JSON válido con TODAS las etiquetas en español**

### **✅ Etiquetas en Español:**
- [ ] **Todos los "label" en español**
- [ ] **Todas las "options" de Select en español**
- [ ] **Mensajes de error en español en archivos .py**
- [ ] **Descripciones y help text en español**

### **✅ Funcionalidad:**
- [ ] bench migrate sin errores
- [ ] Module Def creado automáticamente
- [ ] DocTypes visibles en interfaz web con etiquetas en español
- [ ] Documentos se pueden crear y guardar

---

## 📋 **Traducciones de Referencia**

### **Campos Comunes:**
```
name → Nombre
type → Tipo
status → Estado
date → Fecha
start_date → Fecha de Inicio
end_date → Fecha de Fin
company → Empresa
description → Descripción
enabled → Habilitado
active → Activo
configuration → Configuración
information → Información
details → Detalles
contact → Contacto
address → Dirección
phone → Teléfono
email → Email
```

### **Opciones de Select Comunes:**
```
Active → Activo
Inactive → Inactivo
Enabled → Habilitado
Disabled → Deshabilitado
Pending → Pendiente
Completed → Completado
In Progress → En Progreso
Cancelled → Cancelado
Draft → Borrador
Submitted → Enviado
```

---

**📝 Esta configuración está validada con la regla de etiquetas en español**
**🇪🇸 SIEMPRE verificar que labels y options estén en español**
**✅ Lista para proceder con módulos siguientes aplicando estas reglas**