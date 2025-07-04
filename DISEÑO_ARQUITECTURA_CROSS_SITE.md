# 🌐 DISEÑO ARQUITECTÓNICO CROSS-SITE PARA COMMUNITY CONTRIBUTIONS

**Fecha:** 2025-07-04  
**Propósito:** Definir arquitectura completa para integración cross-site entre administradoras y domika.dev  
**Estado:** 📋 DISEÑO - Pendiente aprobación e implementación  

---

## 🎯 **OBJETIVO Y CONTEXTO**

### **Requerimiento Central:**
Permitir que administradoras de condominios (en sites independientes) puedan enviar contribuciones de templates al pool universal en domika.dev, y recibir actualizaciones mediante `bench update`.

### **Flujo Target:**
```
[Site Administradora] → [API Cross-Site] → [domika.dev Review] → [App Release] → [bench update en todos los sites]
```

---

## 🏗️ **DECISIÓN DE MÓDULO**

### **✅ MÓDULO PROPUESTO: `site_integration`**

**Razones para módulo independiente:**
1. **Separación de responsabilidades** - Cross-site vs Community Contributions local
2. **Reutilizable** - Puede servir para otros tipos de integraciones futuras
3. **Seguridad centralizada** - Toda la lógica de autenticación en un lugar
4. **Mantenimiento independiente** - No afecta otros módulos

### **📁 Estructura del Módulo:**
```
condominium_management/site_integration/
├── __init__.py
├── doctype/
│   ├── registered_site/
│   │   ├── registered_site.json
│   │   ├── registered_site.py  
│   │   └── test_registered_site.py
│   ├── site_api_key/
│   │   ├── site_api_key.json
│   │   ├── site_api_key.py
│   │   └── test_site_api_key.py
│   ├── cross_site_request_log/
│   │   ├── cross_site_request_log.json
│   │   ├── cross_site_request_log.py
│   │   └── test_cross_site_request_log.py
│   └── contribution_sync_status/
│       ├── contribution_sync_status.json
│       ├── contribution_sync_status.py
│       └── test_contribution_sync_status.py
├── api/
│   ├── __init__.py
│   ├── cross_site_sender.py      # APIs para enviar desde administradora
│   ├── cross_site_receiver.py    # APIs para recibir en domika.dev
│   ├── authentication.py         # Sistema de auth cross-site
│   └── sync_manager.py           # Gestión de sincronización
├── utils/
│   ├── __init__.py
│   ├── encryption.py             # Utilidades de encriptación
│   ├── signature.py              # Validación de firmas
│   └── rate_limiting.py          # Control de tasa de requests
└── hooks_handlers/
    ├── __init__.py
    ├── site_registration.py      # Hooks para registro de sites
    └── sync_monitoring.py        # Hooks para monitoreo
```

---

## 📊 **DISEÑO DE DOCTYPES**

### **1. Registered Site (Maestro en domika.dev)**
```json
{
    "doctype": "DocType",
    "name": "Registered Site",
    "label": "Sitio Registrado",
    "module": "Site Integration",
    "fields": [
        {
            "fieldname": "site_name",
            "fieldtype": "Data",
            "label": "Nombre del Sitio",
            "reqd": 1,
            "unique": 1
        },
        {
            "fieldname": "site_url",
            "fieldtype": "Data", 
            "label": "URL del Sitio",
            "reqd": 1,
            "description": "https://admin1.ejemplo.com"
        },
        {
            "fieldname": "company_name",
            "fieldtype": "Link",
            "label": "Empresa Administradora",
            "options": "Company",
            "reqd": 1
        },
        {
            "fieldname": "contact_email",
            "fieldtype": "Data",
            "label": "Email de Contacto",
            "reqd": 1
        },
        {
            "fieldname": "registration_status",
            "fieldtype": "Select",
            "label": "Estado de Registro",
            "options": "Pending\nActive\nSuspended\nRevoked",
            "default": "Pending"
        },
        {
            "fieldname": "api_key_reference",
            "fieldtype": "Link",
            "label": "API Key Reference", 
            "options": "Site API Key",
            "read_only": 1
        },
        {
            "fieldname": "registration_date",
            "fieldtype": "Datetime",
            "label": "Fecha de Registro",
            "read_only": 1
        },
        {
            "fieldname": "last_active",
            "fieldtype": "Datetime", 
            "label": "Última Actividad",
            "read_only": 1
        },
        {
            "fieldname": "total_contributions",
            "fieldtype": "Int",
            "label": "Total de Contribuciones",
            "read_only": 1,
            "default": 0
        },
        {
            "fieldname": "allowed_modules",
            "fieldtype": "Table",
            "label": "Módulos Permitidos",
            "options": "Site Allowed Module"
        },
        {
            "fieldname": "rate_limit_per_hour",
            "fieldtype": "Int",
            "label": "Límite por Hora",
            "default": 10
        },
        {
            "fieldname": "notes",
            "fieldtype": "Text",
            "label": "Notas"
        }
    ]
}
```

### **2. Site API Key (Seguridad)**
```json
{
    "doctype": "DocType", 
    "name": "Site API Key",
    "label": "Clave API de Sitio",
    "module": "Site Integration",
    "fields": [
        {
            "fieldname": "registered_site",
            "fieldtype": "Link",
            "label": "Sitio Registrado",
            "options": "Registered Site",
            "reqd": 1
        },
        {
            "fieldname": "api_key_hash",
            "fieldtype": "Password",
            "label": "Hash de API Key",
            "reqd": 1,
            "read_only": 1
        },
        {
            "fieldname": "public_key",
            "fieldtype": "Text",
            "label": "Clave Pública",
            "read_only": 1
        },
        {
            "fieldname": "key_status",
            "fieldtype": "Select",
            "label": "Estado de la Clave",
            "options": "Active\nExpired\nRevoked\nSuspended",
            "default": "Active"
        },
        {
            "fieldname": "created_date",
            "fieldtype": "Datetime",
            "label": "Fecha de Creación",
            "read_only": 1
        },
        {
            "fieldname": "expiry_date",
            "fieldtype": "Datetime",
            "label": "Fecha de Expiración"
        },
        {
            "fieldname": "last_used",
            "fieldtype": "Datetime",
            "label": "Último Uso",
            "read_only": 1
        },
        {
            "fieldname": "usage_count",
            "fieldtype": "Int",
            "label": "Contador de Uso",
            "read_only": 1,
            "default": 0
        }
    ]
}
```

### **3. Cross Site Request Log (Auditoría)**
```json
{
    "doctype": "DocType",
    "name": "Cross Site Request Log", 
    "label": "Log de Solicitudes Cross-Site",
    "module": "Site Integration",
    "fields": [
        {
            "fieldname": "source_site",
            "fieldtype": "Link",
            "label": "Sitio Origen",
            "options": "Registered Site"
        },
        {
            "fieldname": "request_type",
            "fieldtype": "Select",
            "label": "Tipo de Solicitud",
            "options": "Contribution Submission\nStatus Check\nAuthentication\nSync Request"
        },
        {
            "fieldname": "request_payload_size",
            "fieldtype": "Int",
            "label": "Tamaño del Payload (bytes)"
        },
        {
            "fieldname": "response_status",
            "fieldtype": "Select",
            "label": "Estado de Respuesta",
            "options": "Success\nFailed\nRejected\nTimeout"
        },
        {
            "fieldname": "response_time_ms",
            "fieldtype": "Int",
            "label": "Tiempo de Respuesta (ms)"
        },
        {
            "fieldname": "ip_address",
            "fieldtype": "Data",
            "label": "Dirección IP"
        },
        {
            "fieldname": "user_agent",
            "fieldtype": "Data",
            "label": "User Agent"
        },
        {
            "fieldname": "error_message", 
            "fieldtype": "Text",
            "label": "Mensaje de Error"
        },
        {
            "fieldname": "request_timestamp",
            "fieldtype": "Datetime",
            "label": "Timestamp",
            "reqd": 1
        }
    ]
}
```

### **4. Contribution Sync Status (Estado de Sincronización)**
```json
{
    "doctype": "DocType",
    "name": "Contribution Sync Status",
    "label": "Estado de Sincronización de Contribución", 
    "module": "Site Integration",
    "fields": [
        {
            "fieldname": "contribution_request",
            "fieldtype": "Link",
            "label": "Solicitud de Contribución",
            "options": "Contribution Request",
            "reqd": 1
        },
        {
            "fieldname": "source_site",
            "fieldtype": "Link", 
            "label": "Sitio Origen",
            "options": "Registered Site"
        },
        {
            "fieldname": "sync_status",
            "fieldtype": "Select",
            "label": "Estado de Sincronización",
            "options": "Received\nValidating\nUnder Review\nApproved\nIntegrated\nRejected\nFailed"
        },
        {
            "fieldname": "received_date",
            "fieldtype": "Datetime",
            "label": "Fecha de Recepción",
            "read_only": 1
        },
        {
            "fieldname": "validation_status",
            "fieldtype": "Select",
            "label": "Estado de Validación",
            "options": "Pending\nPassed\nFailed"
        },
        {
            "fieldname": "validation_errors",
            "fieldtype": "JSON",
            "label": "Errores de Validación"
        },
        {
            "fieldname": "reviewer_notes",
            "fieldtype": "Text",
            "label": "Notas del Revisor"
        },
        {
            "fieldname": "integration_date",
            "fieldtype": "Datetime",
            "label": "Fecha de Integración"
        },
        {
            "fieldname": "fixture_path",
            "fieldtype": "Data",
            "label": "Ruta del Fixture"
        }
    ]
}
```

---

## 🔌 **DISEÑO DE APIs**

### **APIs en Site Administradora (Envío)**

#### **1. `/api/method/site_integration.api.cross_site_sender.submit_contribution`**
```python
@frappe.whitelist()
def submit_contribution_to_domika(
    contribution_request_name: str,
    target_domika_url: str,
    api_key: str
) -> dict:
    """
    Enviar contribución desde site administradora a domika.dev
    
    Args:
        contribution_request_name: Nombre local de Contribution Request
        target_domika_url: URL de domika.dev
        api_key: API key del site registrado
        
    Returns:
        dict: Resultado del envío
    """
```

#### **2. `/api/method/site_integration.api.cross_site_sender.check_sync_status`**
```python
@frappe.whitelist()
def check_contribution_status(
    contribution_id: str,
    target_domika_url: str,
    api_key: str
) -> dict:
    """
    Verificar estado de contribución en domika.dev
    """
```

### **APIs en domika.dev (Recepción)**

#### **3. `/api/method/site_integration.api.cross_site_receiver.receive_contribution`**
```python
@frappe.whitelist(allow_guest=True)
def receive_external_contribution(
    source_site_url: str,
    contribution_data: str,  # JSON encriptado
    signature: str,          # Firma digital
    timestamp: str,          # Unix timestamp
    api_key_hash: str       # Hash de API key
) -> dict:
    """
    Recibir contribución desde site externo
    
    Process:
    1. Validar autenticación (API key + signature)
    2. Verificar rate limiting
    3. Validar payload
    4. Crear Contribution Request en domika.dev
    5. Crear Contribution Sync Status
    6. Log request
    
    Returns:
        dict: Confirmation y tracking ID
    """
```

#### **4. `/api/method/site_integration.api.cross_site_receiver.register_site`**
```python
@frappe.whitelist()
def register_new_site(
    site_url: str,
    company_name: str,
    contact_email: str,
    public_key: str
) -> dict:
    """
    Registrar nuevo site administradora
    """
```

#### **5. `/api/method/site_integration.api.cross_site_receiver.get_sync_status`**
```python
@frappe.whitelist(allow_guest=True)
def get_contribution_sync_status(
    tracking_id: str,
    api_key_hash: str
) -> dict:
    """
    Obtener estado de sincronización de contribución
    """
```

### **APIs de Autenticación**

#### **6. `/api/method/site_integration.api.authentication.generate_api_key`**
```python
@frappe.whitelist()
def generate_site_api_key(registered_site: str) -> dict:
    """
    Generar API key para site registrado (solo domika.dev)
    """
```

#### **7. `/api/method/site_integration.api.authentication.validate_cross_site_request`**
```python
def validate_request_signature(
    payload: str,
    signature: str,
    api_key_hash: str,
    timestamp: str
) -> bool:
    """
    Validar firma digital de request cross-site
    """
```

---

## 🔄 **WORKFLOW COMPLETO CROSS-SITE**

### **FASE 1: Registro de Site Administradora**
```
1. [Administradora] → Solicita registro a domika.dev (manual/email)
2. [domika.dev Admin] → Crear Registered Site
3. [domika.dev] → Generar API Key pair (pública/privada) 
4. [domika.dev Admin] → Enviar API key privada a administradora (seguro)
5. [Administradora] → Configurar API key en su site
```

### **FASE 2: Envío de Contribución**
```
1. [Administradora] → Crear Contribution Request local
2. [Administradora] → Validar localmente con handler específico
3. [Administradora] → Encriptar payload con clave pública domika
4. [Administradora] → Firmar request con clave privada  
5. [Administradora] → POST a domika.dev/api/method/.../receive_contribution
6. [domika.dev] → Validar autenticación y rate limiting
7. [domika.dev] → Crear Contribution Request + Sync Status
8. [domika.dev] → Responder con tracking_id
```

### **FASE 3: Review y Aprobación (en domika.dev)**
```
1. [domika.dev Reviewer] → Review Contribution Request
2. [domika.dev Reviewer] → Aprobar/Rechazar con notas
3. [domika.dev] → Actualizar Contribution Sync Status
4. [domika.dev] → Si aprobado → Export to fixtures
5. [domika.dev] → Integrar a app release
```

### **FASE 4: Distribución (bench update)**
```
1. [domika.dev] → Crear app release con nuevos fixtures
2. [Todos los sites] → bench update
3. [Todos los sites] → Nuevos templates disponibles automáticamente
```

### **FASE 5: Monitoreo y Auditoría**
```
1. [Administradora] → Puede check status con tracking_id
2. [domika.dev] → Mantiene logs completos en Cross Site Request Log
3. [domika.dev] → Dashboard de estadísticas de contribuciones
4. [domika.dev] → Rate limiting y security monitoring
```

---

## 🔐 **SISTEMA DE SEGURIDAD**

### **1. Autenticación por API Key**
```python
# Generación de claves asimétricas
private_key, public_key = generate_rsa_key_pair()

# Site administradora firma requests con private key
signature = sign_payload(payload, private_key)

# domika.dev valida con public key almacenada
is_valid = verify_signature(payload, signature, public_key)
```

### **2. Encriptación de Payload**
```python
# Encriptar payload sensible
encrypted_payload = encrypt_with_public_key(contribution_data, domika_public_key)

# domika.dev desencripta con su private key
decrypted_payload = decrypt_with_private_key(encrypted_payload, domika_private_key)
```

### **3. Rate Limiting por Site**
```python
# Configuración por site
rate_limits = {
    "requests_per_hour": 10,
    "payload_size_limit_mb": 5,
    "concurrent_requests_limit": 2
}
```

### **4. Request Validation**
```python
# Validaciones obligatorias
validations = [
    "timestamp_not_older_than_5_minutes",
    "signature_verification", 
    "api_key_active_and_not_expired",
    "rate_limit_not_exceeded",
    "payload_size_within_limits",
    "content_type_validation",
    "ip_whitelist_check"  # Opcional
]
```

---

## 🎯 **HOOKS REQUERIDOS**

### **1. Site Registration Hooks**
```python
# site_integration/hooks_handlers/site_registration.py

def on_registered_site_after_insert(doc, method):
    """Generar API key automáticamente después de crear site registrado"""
    
def on_site_api_key_before_save(doc, method):
    """Validar configuración de API key antes de guardar"""
```

### **2. Sync Monitoring Hooks**
```python
# site_integration/hooks_handlers/sync_monitoring.py

def on_contribution_sync_status_on_update(doc, method):
    """Notificar cambios de estado a site origen"""
    
def on_cross_site_request_log_after_insert(doc, method):
    """Alertar sobre patrones de seguridad sospechosos"""
```

### **3. Scheduled Jobs**
```python
# En hooks.py
scheduler_events = {
    "hourly": [
        "site_integration.utils.rate_limiting.reset_hourly_counters"
    ],
    "daily": [
        "site_integration.api.sync_manager.check_expired_api_keys",
        "site_integration.api.sync_manager.cleanup_old_request_logs"
    ],
    "weekly": [
        "site_integration.api.sync_manager.generate_security_report"
    ]
}
```

---

## ⚙️ **CONFIGURACIÓN EN hooks.py**

```python
# Agregar a hooks.py principal
modules.update({
    "site_integration": {
        "color": "orange",
        "icon": "octicon octicon-globe",  
        "type": "module",
        "label": "Site Integration",
    }
})

# DocTypes events específicos
doc_events.update({
    "Registered Site": {
        "after_insert": "site_integration.hooks_handlers.site_registration.on_registered_site_after_insert",
        "validate": "site_integration.hooks_handlers.site_registration.validate_site_registration"
    },
    "Site API Key": {
        "before_save": "site_integration.hooks_handlers.site_registration.on_site_api_key_before_save",
        "on_update": "site_integration.hooks_handlers.sync_monitoring.on_api_key_update"
    },
    "Contribution Sync Status": {
        "on_update": "site_integration.hooks_handlers.sync_monitoring.on_sync_status_update"
    }
})

# Scheduled events
scheduler_events.update({
    "hourly": [
        "site_integration.utils.rate_limiting.reset_hourly_counters"
    ],
    "daily": [
        "site_integration.api.sync_manager.daily_maintenance"
    ]
})
```

---

## 📊 **MÉTRICAS Y MONITOREO**

### **Dashboard de domika.dev:**
- Total sites registrados (activos/suspendidos)
- Contribuciones por mes/site
- Rate limiting violations
- Security incidents log
- Performance metrics (response times)

### **Alertas Automáticas:**
- API key cerca de expiración
- Rate limiting violations repetidas
- Signature validation failures
- Payload size anomalies
- Geographic anomalies (IPs sospechosas)

---

## ✅ **CRITERIOS DE ÉXITO**

### **Funcionales:**
- [ ] Site administradora puede registrarse en domika.dev
- [ ] Site administradora puede enviar contribuciones de manera segura
- [ ] domika.dev valida y procesa contribuciones automáticamente
- [ ] Workflow de review y aprobación funciona
- [ ] bench update distribuye nuevos templates a todos los sites
- [ ] Sistema de tracking permite monitorear estado de contribuciones

### **No Funcionales:**
- [ ] Autenticación robusta con claves asimétricas
- [ ] Rate limiting efectivo previene abuse
- [ ] Logs completos para auditoría
- [ ] Performance < 500ms para requests típicos
- [ ] Payload encryption protege datos sensibles
- [ ] Error handling graceful con rollback

---

## 🚀 **PRÓXIMOS PASOS**

1. **✅ REVISIÓN Y APROBACIÓN** de este diseño
2. **✅ IMPLEMENTACIÓN** de DocTypes del módulo site_integration
3. **✅ IMPLEMENTACIÓN** de APIs cross-site
4. **✅ IMPLEMENTACIÓN** de sistema de seguridad
5. **✅ TESTING** completo del workflow cross-site
6. **✅ DOCUMENTACIÓN** de usuario para administradoras

**¿Apruebas este diseño para proceder con la implementación?**