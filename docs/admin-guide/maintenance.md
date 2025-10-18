# Mantenimiento del Sistema

Guía de tareas de mantenimiento para mantener el sistema funcionando óptimamente.

---

## Mantenimiento Diario

### 1. Verificar Backups

**Comando:**
```bash
ls -lh /home/erpnext/frappe-bench/sites/admin1.dev/private/backups/
```

**Verificar:**
- ✅ Backup generado en últimas 24 horas
- ✅ Tamaño razonable (comparar con backups anteriores)
- ✅ Sin errores en log de backup

**Si falla backup:**
```bash
bench --site admin1.dev backup --with-files
```

---

### 2. Revisar Error Logs

**Ir a:** Error Log > List View

**Filtrar:**
- Creation: Últimas 24 horas
- Status: Open

**Acciones:**
- Revisar errores críticos
- Documentar errores recurrentes
- Crear tickets para resolución

---

## Mantenimiento Semanal

### 1. Limpiar Logs Antiguos

**Comando:**
```bash
bench --site admin1.dev clear-cache
bench --site admin1.dev clear-website-cache
```

**Limpiar Error Logs resueltos:**
- Ir a Error Log > List View
- Filtrar: Status = Resolved, Más de 30 días
- Eliminar en batch

---

### 2. Verificar Uso de Disco

**Comando:**
```bash
df -h
du -sh /home/erpnext/frappe-bench/sites/admin1.dev/
```

**Acciones si uso > 80%:**
- Limpiar backups antiguos (más de 30 días)
- Comprimir archivos grandes
- Mover archivos a storage externo

---

### 3. Revisar Performance

**Ir a:** System Settings > Database

**Verificar:**
- Query execution times
- Slow queries (> 1 segundo)

**Optimizar si necesario:**
```bash
bench --site admin1.dev mariadb
> ANALYZE TABLE `tabPhysical Space`;
> OPTIMIZE TABLE `tabPhysical Space`;
```

---

## Mantenimiento Mensual

### 1. Actualizar Sistema

**Verificar actualizaciones disponibles:**
```bash
cd /home/erpnext/frappe-bench/apps/condominium_management
git fetch origin
git log HEAD..origin/main --oneline
```

**Aplicar actualizaciones (con precaución):**
```bash
# Backup primero
bench --site admin1.dev backup --with-files

# Actualizar app
cd /home/erpnext/frappe-bench
bench get-app condominium_management --branch main

# Migrar
bench --site admin1.dev migrate

# Verificar
bench --site admin1.dev console
>>> frappe.get_installed_apps()
```

---

### 2. Auditoría de Usuarios y Permisos

**Revisar usuarios activos:**

**Ir a:** User > List View

**Verificar:**
- Usuarios inactivos > 90 días → Deshabilitar
- Roles asignados correctamente
- Usuarios con permisos excesivos

**Acciones:**
- Deshabilitar usuarios que ya no trabajan
- Revisar y actualizar roles
- Documentar cambios de permisos

---

### 3. Limpieza de Datos de Prueba

**Identificar datos de prueba:**

```bash
bench --site admin1.dev console
```

```python
# Buscar datos de prueba (naming convention TEST-)
test_spaces = frappe.get_all("Physical Space",
    filters={"space_name": ["like", "%TEST%"]})

print(f"Found {len(test_spaces)} test spaces")

# Eliminar si confirmado
# for space in test_spaces:
#     frappe.delete_doc("Physical Space", space.name)
# frappe.db.commit()
```

---

## Mantenimiento Trimestral

### 1. Revisar Índices de Base de Datos

**Verificar índices:**
```bash
bench --site admin1.dev mariadb
```

```sql
SHOW INDEX FROM `tabPhysical Space`;
SHOW INDEX FROM `tabService Management Contract`;
```

**Agregar índices si necesario** (consultar con desarrollo)

---

### 2. Análisis de Uso de Recursos

**CPU y Memoria:**
```bash
top
htop  # si disponible
```

**Conexiones de Base de Datos:**
```bash
bench --site admin1.dev mariadb
> SHOW PROCESSLIST;
> SHOW STATUS LIKE 'Threads_connected';
```

**Acciones si recursos altos:**
- Identificar queries lentas
- Optimizar código/queries
- Considerar upgrade de hardware

---

### 3. Pruebas de Restauración de Backup

**Importante:** Probar que los backups funcionan

**En environment de prueba:**
```bash
# Crear sitio de prueba
bench new-site test-restore.dev

# Restaurar backup
bench --site test-restore.dev restore \
  /path/to/backup/[timestamp]-admin1_dev-database.sql.gz

# Verificar integridad
bench --site test-restore.dev console
>>> frappe.get_all("Physical Space", limit=5)
```

---

## Mantenimiento Anual

### 1. Migración a Nueva Versión de Frappe/ERPNext

**Planificar con antelación:**
- Revisar release notes
- Probar en environment de desarrollo
- Crear backup completo
- Programar ventana de mantenimiento

**Proceso:**
```bash
# Backup crítico
bench --site admin1.dev backup --with-files

# Switch branch
cd /home/erpnext/frappe-bench/apps/frappe
git checkout version-16

cd /home/erpnext/frappe-bench/apps/erpnext
git checkout version-16

# Migrate
bench --site admin1.dev migrate

# Rebuild
bench build --app condominium_management

# Verificar
bench start
```

---

### 2. Auditoría de Seguridad

**Verificar:**
- SSL certificates actualizados
- Passwords de usuarios fuertes
- Permisos correctos en archivos sistema
- No hay vulnerabilidades conocidas

**Herramientas:**
```bash
# Verificar SSL
openssl s_client -connect admin1.dev:443

# Verificar permisos archivos
find /home/erpnext/frappe-bench -type f -perm 777
```

---

### 3. Limpieza Profunda de Base de Datos

**Eliminar datos obsoletos:**
- Records eliminados hace > 1 año
- Logs antiguos
- Versiones antiguas de documentos

**Consultar con desarrollo antes de ejecutar**

---

## Monitoreo Continuo

### Herramientas Recomendadas

**1. Uptim Robot / Pingdom**
- Monitorear uptime del sitio
- Alertas si sitio cae

**2. New Relic / Datadog (opcional)**
- Performance monitoring
- Database query analysis

**3. Logs Centralizados**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Graylog

---

## Troubleshooting Común

### Sistema Lento

**Diagnóstico:**
```bash
# Ver procesos
top

# Ver queries lentas
bench --site admin1.dev mariadb
> SHOW FULL PROCESSLIST;
```

**Soluciones:**
- Clear cache
- Restart services
- Optimizar queries identificadas

---

### Errores de Base de Datos

**Error: Lost connection to MySQL server**

**Solución:**
```bash
# Restart MariaDB
sudo systemctl restart mariadb

# Verificar logs
sudo journalctl -u mariadb -n 50
```

---

### Disco Lleno

**Solución rápida:**
```bash
# Limpiar backups antiguos
cd /home/erpnext/frappe-bench/sites/admin1.dev/private/backups
rm -f *-database.sql.gz(+30)  # Más de 30 días

# Limpiar logs
sudo journalctl --vacuum-time=7d

# Limpiar archivos temporales
find /tmp -type f -atime +7 -delete
```

---

## Checklist de Mantenimiento

### Diario
- [ ] Verificar backup exitoso
- [ ] Revisar error logs

### Semanal
- [ ] Limpiar cache
- [ ] Verificar uso de disco
- [ ] Revisar performance

### Mensual
- [ ] Actualizar sistema (si aplica)
- [ ] Auditoría usuarios/permisos
- [ ] Limpiar datos de prueba

### Trimestral
- [ ] Revisar índices BD
- [ ] Análisis recursos
- [ ] Prueba restauración backup

### Anual
- [ ] Migración versión Frappe/ERPNext
- [ ] Auditoría seguridad
- [ ] Limpieza profunda BD

---

## Contactos de Soporte

**Frappe Community:**
- Forum: https://discuss.frappe.io
- GitHub Issues: https://github.com/frappe/frappe/issues

**ERPNext:**
- Documentation: https://docs.erpnext.com
- Forum: https://discuss.erpnext.com

**Condominium Management:**
- GitHub: https://github.com/buzola-tm/condominium_management/issues

---

## Recursos Adicionales

- [Configuration Guide](configuration.md) - Configuración del sistema
- [Security Guide](security.md) - Seguridad
- [Troubleshooting](../development/workflows/troubleshooting.md) - Solución de problemas

---

**Actualizado:** 2025-10-17
**Para:** System Administrators y DevOps
