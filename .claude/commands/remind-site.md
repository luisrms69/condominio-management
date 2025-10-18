# ⚠️ RECORDATORIO: SITE CORRECTO

**Este workspace usa:** `admin1.dev`
**App:** `condominium_management`

## Comandos correctos para este proyecto:

```bash
bench --site admin1.dev migrate
bench --site admin1.dev export-fixtures --apps condominium_management
bench --site admin1.dev run-tests --app condominium_management
bench build --apps condominium_management
```

## ❌ NUNCA ejecutar:

```bash
bench start                   # Ya corre en tmux global
bench migrate                 # Sin --site (afectaría otros sites)
bench --site facturacion.dev  # Site de OTRA app
bench --site llantascs.dev    # Site de OTRA app
```

## Sites en este bench:

- **admin1.dev** ← ESTE workspace (condominium_management)
- facturacion.dev (facturacion_mexico - OTRO workspace)
- llantascs.dev (llantascs_customs - OTRO workspace)

## URLs Desarrollo:

- **Principal:** http://admin1.dev:8000
- **Secundarios (opcionales):** http://condo1.dev:8000, http://condo2.dev:8000
