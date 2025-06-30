# 📋 DOCUMENTACIÓN COMPLETA DE CAMPOS EN DOCTYPES

**Proyecto:** Condominium Management - Sistema de Gestión de Condominios  
**Módulo:** Companies  
**Fecha:** 28 de junio de 2025  

---

## 🎯 **PROPÓSITO**

Este documento documenta todos los campos específicos modificados en los DocTypes del módulo Companies, incluyendo cambios de tipo, nuevos campos agregados, traducciones de opciones y modificaciones estructurales. Es una referencia técnica para futuros desarrollos y mantenimiento del sistema.

---

## 📊 **DOCTYPES MODIFICADOS**

### **1. NEARBY REFERENCE (Referencia Cercana)**

**Archivo:** `/companies/doctype/nearby_reference/nearby_reference.json`

#### **Campo Modificado: distance**
| Propiedad | Valor Original | Valor Actual |
|-----------|----------------|--------------|
| **fieldname** | `distance` | `distance` |
| **fieldtype** | `Float` | `Select` ✅ |
| **label** | `Distance` | `Distancia` ✅ |
| **options** | N/A | `Menos de 50 metros\nEntre 50 y 150 metros\nEntre 150 y 500 metros\nMás de 500 metros` ✅ |
| **in_list_view** | 0 | 1 |

#### **Campos Existentes (sin cambios):**

| Fieldname | Fieldtype | Label | Options | Configuración |
|-----------|-----------|-------|---------|---------------|
| `reference_type` | Select | Tipo de Referencia | Centro Comercial, Parque, Hospital, Escuela, Universidad, Centro Deportivo, Supermercado, Restaurante, Otro | reqd: 1, in_list_view: 1 |
| `reference_name` | Data | Nombre de Referencia | - | reqd: 1 |
| `directions` | Small Text | Indicaciones | - | - |

---

### **2. ACCESS POINT DETAIL (Detalle de Punto de Acceso)**

**Archivo:** `/companies/doctype/access_point_detail/access_point_detail.json`

#### **Nuevos Campos para Control de Acceso:**

| Fieldname | Fieldtype | Label | Options | Configuración |
|-----------|-----------|-------|---------|---------------|
| `access_control_method` | Select | Método de Control de Acceso | Tarjeta, Código, Huella, Reconocimiento Facial, QR, Otro | - |
| `who_can_access` | MultiSelectPills | Quiénes Pueden Acceder | Residentes y Condóminos, Visitas, Proveedores, Personal de Servicio | - |

#### **Nuevos Campos para Tipos de Vehículos:**

| Fieldname | Fieldtype | Label | Options | Configuración |
|-----------|-----------|-------|---------|---------------|
| `access_vehicle_type` | Select | Tipo de Acceso | Solo Peatonal, Solo Vehículos, Vehículos y Peatones | in_list_view: 1 |

#### **Nuevos Campos para Horarios de Operación:**

| Fieldname | Fieldtype | Label | Options | Configuración |
|-----------|-----------|-------|---------|---------------|
| `opening_time` | Time | Hora de Apertura | - | - |
| `closing_time` | Time | Hora de Cierre | - | - |
| `operating_days` | MultiSelectPills | Días de Operación | Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo | - |

#### **Campos Existentes (sin cambios):**

| Fieldname | Fieldtype | Label | Options | Configuración |
|-----------|-----------|-------|---------|---------------|
| `access_point_type` | Select | Tipo de Punto de Acceso | Peatonal, Vehicular, Mixto, Emergencia | reqd: 1, in_list_view: 1 |
| `access_point_name` | Data | Nombre del Punto de Acceso | - | reqd: 1 |
| `security_level` | Select | Nivel de Seguridad | Bajo, Medio, Alto, Restringido | - |

---

### **3. CONDOMINIUM INFORMATION (Información del Condominio)**

**Archivo:** `/companies/doctype/condominium_information/condominium_information.json`

#### **Campo Agregado: gps_coordinates**

| Fieldname | Fieldtype | Label | Description | Configuración |
|-----------|-----------|-------|-------------|---------------|
| `gps_coordinates` | Data | Coordenadas GPS | Coordenadas GPS del condominio para navegación (formato: latitud, longitud). Ejemplo: 19.432608, -99.133209 | - |

#### **Campo Modificado: how_to_arrive**

| Fieldname | Fieldtype | Label | Description | Configuración |
|-----------|-----------|-------|-------------|---------------|
| `how_to_arrive` | Text | Instrucciones Generales de Cómo Llegar | Coloca direcciones generales de como llegar al sitio, particularmente si se tienen que tomar caminos no claramente definidos, puedes además indicar las principales vías de acceso y demás información que consideres ayude a alguien sin conocimiento del área a llegar | - |

#### **Modificación Estructural: Eliminación de Pestaña**

**Pestaña eliminada:** "Contacto y Servicios"

**Nueva estructura de pestañas:**

1. **Tab Break 1:** "Información General"
   - **Section:** "Información Básica"
   - **Campos:** company, company_name, commercial_name, construction_year, total_units, total_area, common_area, private_area

2. **Tab Break 2:** "Cómo Llegar"
   - **Section:** "Instrucciones de Llegada"
   - **Campos:** how_to_arrive, gps_coordinates, parking_information
   - **Section:** "Transporte Público"
   - **Campos:** public_transport (tabla)
   - **Section:** "Referencias Cercanas"
   - **Campos:** nearby_references (tabla)

3. **Tab Break 3:** "Accesos"
   - **Section:** "Puntos de Acceso"
   - **Campos:** access_points (tabla)

#### **Campos Existentes (sin cambios):**

| Fieldname | Fieldtype | Label | Configuración |
|-----------|-----------|-------|---------------|
| `company` | Link | Condominio | options: Company, reqd: 1 |
| `company_name` | Data | Nombre | fetch_from: company.company_name, read_only: 1 |
| `commercial_name` | Data | Nombre Comercial | - |
| `construction_year` | Int | Año de Construcción | - |
| `total_units` | Int | Total de Unidades | - |
| `total_area` | Float | Superficie Total (m²) | precision: 2 |
| `common_area` | Float | Área Común (m²) | precision: 2 |
| `private_area` | Float | Área Privada (m²) | precision: 2 |
| `parking_information` | Text | Información de Estacionamiento | - |
| `public_transport` | Table | Opciones de Transporte Público | options: Public Transport Option |
| `nearby_references` | Table | Referencias Cercanas | options: Nearby Reference |
| `access_points` | Table | Puntos de Acceso | options: Access Point Detail |

---

### **4. SYNC DATA TYPE (Tipo de Dato de Sincronización)**

**Archivo:** `/companies/doctype/sync_data_type/sync_data_type.json`

#### **Campo con Opciones Traducidas: data_type**

| Propiedad | Valor Original | Valor Actual |
|-----------|----------------|--------------|
| **fieldname** | `data_type` | `data_type` |
| **fieldtype** | `Select` | `Select` |
| **label** | `Data Type` | `Tipo de Dato` ✅ |
| **options** | `Supplier\nItem\nEmail Template\nPrint Format\nWorkflow\nUser Role\nCustom Field` | `Proveedor\nArtículo\nPlantilla de Email\nFormato de Impresión\nFlujo de Trabajo\nRol de Usuario\nCampo Personalizado` ✅ |
| **reqd** | 1 | 1 |
| **in_list_view** | 1 | 1 |

#### **Campos Existentes (sin cambios):**

| Fieldname | Fieldtype | Label | Configuración |
|-----------|-----------|-------|---------------|
| `sync_enabled` | Check | Habilitado | default: 1 |
| `filter_conditions` | Small Text | Condiciones de Filtro | - |
| `last_sync_count` | Int | Registros Última Sync | read_only: 1 |

---

### **5. SERVICE MANAGEMENT CONTRACT (Contrato de Gestión de Servicios)**

**Archivo:** `/companies/doctype/service_management_contract/service_management_contract.json`

#### **Campo Corregido: payment_terms**

| Propiedad | Valor Original | Valor Actual |
|-----------|----------------|--------------|
| **fieldname** | `payment_terms` | `payment_terms` |
| **fieldtype** | `Link` | `Link` |
| **label** | `Payment Terms` | `Términos de Pago` ✅ |
| **options** | `Payment Terms` | `Payment Term` ✅ |

---

## 📊 **RESUMEN DE MODIFICACIONES POR TIPO**

### **Cambios de Tipo de Campo:**
- **Nearby Reference:** `distance` - Float → Select (con opciones en español)

### **Nuevos Campos Agregados:**
- **Access Point Detail:** 6 nuevos campos para control de acceso y horarios
- **Condominium Information:** `gps_coordinates` con descripción detallada

### **Traducciones de Opciones:**
- **Sync Data Type:** Todas las opciones traducidas al español
- **Nearby Reference:** Opciones de distancia completamente en español

### **Correcciones de Referencias:**
- **Service Management Contract:** `payment_terms` corregido de "Payment Terms" a "Payment Term"

### **Modificaciones Estructurales:**
- **Condominium Information:** Eliminación de pestaña "Contacto y Servicios" y reorganización en 3 pestañas principales

---

## 🔍 **IMPACTO EN OTROS MÓDULOS**

### **Para futuros desarrollos:**

1. **Nearby Reference:** El cambio de Float a Select en `distance` afecta:
   - ✅ Formularios de captura (más intuitivo)
   - ✅ Reportes y filtros (opciones predefinidas)
   - ✅ Validaciones (opciones controladas)

2. **Access Point Detail:** Los nuevos campos permiten:
   - ✅ Control granular de accesos
   - ✅ Gestión de horarios operativos
   - ✅ Clasificación por tipos de vehículos
   - ✅ Métodos de autenticación

3. **Condominium Information:** Las mejoras incluyen:
   - ✅ Integración con sistemas GPS
   - ✅ Mejor organización de información
   - ✅ Interfaz más clara y funcional

4. **Sync Data Type:** Opciones en español mejoran:
   - ✅ Usabilidad para usuarios finales
   - ✅ Configuración de sincronización
   - ✅ Mantenimiento del sistema

---

## ⚠️ **CONSIDERACIONES TÉCNICAS**

### **Compatibilidad:**
- ✅ Todos los cambios son retrocompatibles
- ✅ Datos existentes se mantienen intactos
- ✅ No requiere migración de datos

### **Validaciones:**
- ✅ Campos requeridos mantienen validación
- ✅ Tipos de dato apropiados para cada uso
- ✅ Referencias corregidas funcionan correctamente

### **Performance:**
- ✅ Select fields mejoran rendimiento vs Float
- ✅ MultiSelectPills optimizados para UI
- ✅ Time fields con validación nativa

---

**Documento generado:** 28 de junio de 2025  
**Estado:** Implementado y activo en domika.dev  
**Próxima revisión:** Al agregar nuevos DocTypes al módulo Companies