# Instalación

## Requisitos Previos

- Frappe/ERPNext v15+
- Python 3.8+
- MariaDB/MySQL
- Node.js (para compilación de assets)

## Instalación en Frappe Bench

```bash
# En tu frappe-bench
cd /path/to/frappe-bench

# Obtener la aplicación
bench get-app https://github.com/buzola-tm/condominium_management

# Instalar en tu sitio
bench --site [tu-sitio] install-app condominium_management

# Migrar base de datos
bench --site [tu-sitio] migrate

# Compilar assets
bench build --app condominium_management
```

## Verificación

```bash
# Verificar que la app está instalada
bench --site [tu-sitio] list-apps

# Debería aparecer: condominium_management
```

## Próximos Pasos

- **[Guía Rápida](quick-start.md)** - Configuración inicial
- **[Arquitectura](architecture-overview.md)** - Entender el sistema

---

**Última actualización:** 2025-10-17
