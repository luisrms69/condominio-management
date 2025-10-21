# Configuración del Sistema

Guía de configuración para administradores del sistema.

---

## Configuración Inicial Post-Instalación

### 1. Verificar Instalación

**Ir a:** About

**Verificar:**
- ✅ Condominium Management aparece en Installed Apps
- ✅ Versión correcta instalada
- ✅ Frappe/ERPNext v15+

---

### 2. Configurar Roles y Permisos

**Roles incluidos por defecto:**

| Rol | Propósito | Permisos Principales |
|-----|-----------|---------------------|
| Property Manager | Administrador de condominios | Full access a todos los módulos |
| Committee Member | Miembros del comité | Read access, Limited write |
| Maintenance Staff | Personal de mantenimiento | Access a Physical Spaces, Maintenance |
| Resident | Residentes | Read-only access a información propia |

**Asignar roles a usuarios:**

**Ir a:** User > [seleccionar usuario] > Roles

**Agregar roles** según responsabilidades

---

### 3. Configurar Master Data

#### Space Categories

**Ir a:** Space Category > New

**Crear categorías base:**
- Torre
- Piso
- Departamento
- Estacionamiento
- Área Común
- Bodega

#### Component Types

**Ir a:** Component Type > New

**Crear tipos base:**
- Ventana
- Puerta
- Instalación Eléctrica
- Instalación Hidráulica
- Acabados
- Equipos

---

## Configuración Multi-Company

### Separación Financiera

**Para cada condominio:**

1. **Crear Company separada**
   - Setup > Company > New
   - Configurar Chart of Accounts independiente

2. **Configurar Cuentas Bancarias**
   - Setup > Bank Account
   - Vincular a Company específica

3. **Configurar Cost Centers**
   - Setup > Cost Center
   - Crear estructura por condominio

---

## Configuración de Seguridad

### Roles y Permisos

**Ver:** [Security Guide](security.md) para detalles completos

**Principios:**
- Least privilege access
- Separation of duties
- Regular permission audits

---

## Configuración de Fixtures

### ¿Qué son Fixtures?

Datos maestros que se instalan automáticamente con la app.

**Ubicación:** `condominium_management/fixtures/`

**Fixtures incluidos:**
- Space Category (categorías de espacios)
- Roles personalizados
- Permission templates

**Exportar fixtures modificados:**

```bash
bench --site admin1.dev export-fixtures --app condominium_management
```

---

## Configuración de Backups

### Backup Automático

**Ir a:** Setup > System Settings

**Configurar:**
- Backup Frequency: Daily
- Backup Hour: 02:00 (madrugada)
- Keep Backups: 7 days

**Comando manual:**

```bash
bench --site admin1.dev backup --with-files
```

---

## Configuración de Email

### SMTP Settings

**Ir a:** Setup > Email Domain

**Configurar cuenta de email del sistema:**
- Email Server: smtp.gmail.com (ejemplo)
- Port: 587
- Use TLS: Yes
- Login: admin@tucondominio.mx
- Password: [contraseña de aplicación]

**Test:** Enviar email de prueba

---

## Configuración Regional

### Zona Horaria y Moneda

**Ir a:** Setup > System Settings

**Configurar:**
- Time Zone: America/Mexico_City
- Currency: MXN
- Date Format: DD-MM-YYYY
- Time Format: HH:mm

---

## Optimización de Performance

### Cache Configuration

**Ir a:** Setup > System Settings > Cache

**Configurar:**
- Redis Cache: Enabled
- Cache Timeout: 3600 seconds

### Database Indexing

Los índices se crean automáticamente en campos con `search_index: 1`

**Verificar índices importantes:**
- Physical Space: space_name, parent_space
- Service Management Contract: managed_company, end_date

---

## Mantenimiento Regular

**Tareas mensuales:**
- ✅ Verificar backups exitosos
- ✅ Revisar error logs
- ✅ Actualizar roles/permisos si necesario
- ✅ Limpiar datos de prueba

**Tareas trimestrales:**
- ✅ Revisar performance queries lentas
- ✅ Optimizar índices si necesario
- ✅ Actualizar documentación de configuración

---

## Recursos Adicionales

- [Maintenance Guide](maintenance.md) - Tareas de mantenimiento
- [Security Guide](security.md) - Seguridad del sistema
- [Frappe Setup Guide](https://frappeframework.com/docs/v15/user/en/basics/setup)

---

**Actualizado:** 2025-10-17
**Para:** System Administrators
