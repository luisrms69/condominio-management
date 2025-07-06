# 🌐 Community Contributions Module

## 📋 Resumen

El **Community Contributions Module** permite la colaboración entre múltiples sites administradoras independientes y el servidor central domika.dev para compartir templates, configuraciones y mejoras de forma segura y controlada.

**Estado**: ✅ **100% COMPLETADO** (Julio 2025)  
**Commit**: `feature/community-contributions-cross-site`

## 🏗️ Arquitectura

### Sites y Roles

- **🏢 domika.dev**: RECEPTOR CENTRAL (matriz)
  - Recibe contribuciones de todas las administradoras
  - Centraliza pool de templates universales
  - Maneja review, aprobación e integración

- **🏘️ admin1.dev, admin2.dev, ...**: SITES CONTRIBUYENTES
  - Envían contribuciones a domika.dev
  - Autenticación con API keys únicos
  - Seguimiento de estadísticas

### Flujo de Contribuciones

1. **Administradora crea contribución** en su site local
2. **Envía via API** `submit_contribution_to_domika` con autenticación HMAC
3. **domika.dev recibe** y valida autenticación + payload
4. **Crea Contribution Request** con status "Submitted"
5. **Workflow de review** por equipo domika.dev
6. **Aprobación/Rechazo** con notificación a site originador
7. **Integración** a pool universal si es aprobada

## 🔧 APIs Principales

### 1. Envío de Contribuciones
```python
@frappe.whitelist()
def submit_contribution_to_domika(
    contribution_data: str, 
    target_site_url: str, 
    api_key: str, 
    contribution_title: str | None = None
) -> dict[str, Any]:
```

**Endpoint**: `/api/method/condominium_management.community_contributions.api.cross_site_api.submit_contribution_to_domika`

**Descripción**: Permite a administradoras enviar contribuciones desde sus sites independientes al servidor central.

### 2. Recepción de Contribuciones
```python
@frappe.whitelist(allow_guest=False)
def receive_external_contribution(
    contribution_data: dict,
    source_site: str,
    source_company: str,
    contribution_title: str,
    timestamp: str,
    user_email: str | None = None
) -> dict[str, Any]:
```

**Endpoint**: `/api/method/condominium_management.community_contributions.api.cross_site_api.receive_external_contribution`

**Descripción**: Recibe contribuciones en domika.dev, valida autenticación cross-site y crea Contribution Request.

### 3. Testing de Conectividad
```python
@frappe.whitelist()
def test_cross_site_connection(
    target_site_url: str, 
    api_key: str
) -> dict[str, Any]:
```

**Endpoint**: `/api/method/condominium_management.community_contributions.api.cross_site_api.test_cross_site_connection`

**Descripción**: Verifica conectividad cross-site para troubleshooting.

## 📋 DocTypes

### Registered Contributor Site
**Propósito**: Gestión de sites administradoras autorizadas

**Campos Principales**:
- `site_url`: URL única del site administradora
- `company_name`: Nombre de la empresa administradora
- `api_key`: Clave de autenticación (SHA-256, 64 caracteres)
- `is_active`: Estado activo/inactivo
- `total_contributions`: Contador de contribuciones enviadas
- `security_logs`: Logs de eventos de seguridad (JSON)
- `contribution_stats`: Estadísticas detalladas (JSON)

**Funcionalidades**:
- Generación automática de API keys únicos
- Tracking de estadísticas de contribuciones
- Logs de seguridad y auditoría
- Auto-desactivación tras 100 requests fallidos consecutivos

### Contribution Request (Extended)
**Propósito**: Gestión de contribuciones internas y externas

**Campos Cross-Site Agregados**:
- `source_site`: URL del site que envió la contribución
- `source_user_email`: Email del usuario originador
- `is_external_contribution`: Flag de contribución externa
- `cross_site_auth_verified`: Flag de autenticación verificada

### Contribution Category
**Propósito**: Configuración de validaciones por módulo y tipo

**Campos Principales**:
- `module_name`: Módulo destino (Document Generation, Companies, etc.)
- `contribution_type`: Tipo de contribución (template, workflow, etc.)
- `required_fields`: Campos obligatorios en JSON
- `validation_rules`: Reglas específicas de validación

## 🔐 Seguridad

### Sistema de Autenticación HMAC
- **API Keys**: Únicos de 64 caracteres generados con SHA-256
- **Firmas HMAC**: SHA-256 del payload completo
- **Validación de Timestamps**: Ventana de 5 minutos para prevenir replay attacks
- **Headers de Seguridad**: `X-Signature`, `X-Timestamp`, `Authorization`

### Logs y Auditoría
- **Eventos registrados**: Registro de site, regeneración de API key, requests fallidos
- **Información por evento**: Timestamp, usuario, IP, detalles
- **Retención**: Últimos 50 eventos por site
- **Auto-protección**: Desactivación automática tras múltiples fallos

## 🧪 Configuración y Testing

### Scripts de Configuración
- **`configure_central.py`**: Configuración básica de domika.dev como receptor
- **`setup_domika_central.py`**: Setup completo con categorías y sites de prueba

### Sites de Testing Configurados
- **admin1.test.com**: Site administradora real registrado
- **admin2.test.com**: Site adicional para testing
- **Estado**: Activo y funcional para testing

### Comandos de Validación
```bash
# Configurar domika.dev como receptor central
cd ~/frappe-bench
bench --site domika.dev console
>>> exec(open('apps/condominium_management/configure_central.py').read())

# Verificar sites registrados
>>> frappe.get_all('Registered Contributor Site', fields=['site_url', 'company_name', 'is_active'])

# Testing de API
>>> from condominium_management.community_contributions.api.cross_site_api import test_cross_site_connection
>>> test_cross_site_connection('https://domika.dev', 'API_KEY_HERE')
```

## 📊 Estadísticas y Monitoreo

### Por Site Administradora
- Total de contribuciones enviadas
- Contribuciones por estado (Draft, Submitted, Approved, Rejected, Integrated)
- Estadísticas mensuales (últimos 6 meses)
- Última actividad y uso de API

### Globales del Sistema
- Sites registrados activos
- Total de contribuciones externas
- Contribuciones pendientes de review
- Distribución por site originador

## 🚨 Problemas Comunes y Soluciones

### Error: "Campos requeridos faltantes"
**Causa**: Inconsistencia entre Contribution Category y módulo handler  
**Solución**: Verificar que `required_fields` en la categoría coincida con validaciones del handler

### Error: "Site no registrado o inactivo"
**Causa**: Site no existe en Registered Contributor Site o está desactivado  
**Solución**: Registrar site o activar en domika.dev

### Error: "Autenticación cross-site inválida"
**Causa**: API key incorrecto o firma HMAC inválida  
**Solución**: Verificar API key y regenerar si es necesario

### Error de Conectividad
**Causa**: Site destino no accesible o timeout  
**Solución**: Verificar conectividad de red y configuración DNS

## 🔄 Mantenimiento

### Regeneración de API Keys
```python
# En domika.dev
site = frappe.get_doc("Registered Contributor Site", "https://admin1.dev")
site.regenerate_api_key()
```

### Limpieza de Logs
Los logs se limpian automáticamente manteniendo solo los últimos 50 eventos por site.

### Monitoreo de Fallos
Los sites se auto-desactivan tras 100 requests fallidos consecutivos y requieren intervención manual para reactivación.

## 📚 Referencias Técnicas

### Archivos Principales
- `cross_site_api.py`: APIs principales del sistema
- `registered_contributor_site.py`: DocType de sites registrados
- `contribution_request.py`: DocType extendido para cross-site
- `contribution_category.py`: Configuración de validaciones

### Testing
- `test_registered_contributor_site.py`: Unit tests completos
- Tests cubren: creación, validaciones, API keys, estadísticas, seguridad

### Configuración
- `hooks.py`: Configuración de eventos y permisos
- `modules.txt`: Definición del módulo
- Scripts de setup incluidos para configuración inicial

---

**Desarrollado**: Julio 2025  
**Mantenido por**: Equipo Buzola  
**Versión**: 1.0.0 - Sistema Cross-Site Contributions Completo