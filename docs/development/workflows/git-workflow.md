# Git Workflow

Estrategia de branching y commits para el proyecto.

---

## Branching Strategy

### Feature Branches Obligatorias

```bash
# SIEMPRE crear feature branch, NUNCA trabajar en main
git checkout main
git pull origin main
git checkout -b feature/[modulo]-[descripcion]
```

**Convención naming:**
- `feature/physical-spaces-jerarquia`
- `feature/companies-sync-config`
- `fix/test-fallo-validacion`
- `docs/actualizar-arquitectura`

---

## Conventional Commits

### Formato Obligatorio

```
tipo(alcance): descripción en español

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Tipos Permitidos

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat(physical-spaces): agregar jerarquía nested set` |
| `fix` | Bug fix | `fix(companies): validación empresas diferentes` |
| `docs` | Documentación | `docs(testing): actualizar guía Layer 3` |
| `style` | Formato código | `style: aplicar ruff formatting` |
| `refactor` | Refactorización | `refactor(sync): simplificar lógica conflictos` |
| `test` | Tests | `test(companies): agregar tests validaciones` |
| `chore` | Mantenimiento | `chore: actualizar dependencias` |

### Alcances Específicos

- `companies`, `physical-spaces`, `residents`, `access-control`
- `tests`, `docs`, `config`, `api`, `ui`
- `database`, `sync`, `validation`

---

## Workflow Completo

### 1. Crear Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/companies-validaciones
```

### 2. Desarrollo y Commits

```bash
# Hacer cambios
git add .
git commit -m "feat(companies): agregar validación empresas diferentes

Implementa validación que previene que empresa se contrate a sí misma.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3. Pre-commit Hooks

```bash
# Hooks se ejecutan automáticamente
# Si fallan, corregir y volver a commit
git commit -m "..."
# Hook ejecuta: ruff check, tests críticos
```

**❌ PROHIBIDO ABSOLUTO:**
```bash
git commit --no-verify  # NUNCA usar
```

### 4. Push y Pull Request

```bash
# Push branch
git push origin feature/companies-validaciones

# Verificar que no existe PR
gh pr list --state open --head feature/companies-validaciones

# Crear PR
gh pr create --base main --title "feat(companies): Validaciones empresas diferentes" --body "
## Resumen
Implementa validaciones para prevenir configuraciones inválidas.

## Cambios
- Validación empresa origen ≠ destino
- Tests para validaciones
- Mensajes error en español

## Testing
- ✅ Tests unitarios pasando
- ✅ Validaciones funcionando

🤖 Generated with [Claude Code](https://claude.ai/code)
"
```

---

## Commits de Emergencia

### Git Crisis Recovery

**Si cometiste error (código perdido, etc):**

```bash
# 1. NO ENTRAR EN PÁNICO
# 2. NO hacer git reset/checkout precipitadamente
# 3. Crear backup inmediato
git stash save "EMERGENCY_BACKUP_$(date +%Y%m%d_%H%M%S)"

# 4. Revisar git log para entender qué pasó
git log --oneline -20

# 5. Si código está en working directory, hacer backup manual
cp -r . ../backup-$(date +%Y%m%d_%H%M%S)

# 6. SOLO ENTONCES considerar recovery
```

**Ver:** [CLAUDE.md RG-002](../../CLAUDE.md) para procedimientos completos

---

## Pre-commit Hooks

### Configuración Automática

Archivo `.pre-commit-config.yaml` en raíz:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
```

### Instalación

```bash
pip install pre-commit
pre-commit install
```

### Ejecución Manual

```bash
# Ejecutar en todos los archivos
pre-commit run --all-files

# Ejecutar en staged files
pre-commit run
```

---

## Verificaciones Pre-PR

### Checklist Obligatorio

Antes de crear PR, verificar:

```bash
# 1. Tests pasando
bench --site admin1.dev run-tests --app condominium_management

# 2. Linting OK
ruff check .

# 3. No conflictos con main
git fetch origin main
git merge-base --is-ancestor origin/main HEAD

# 4. Commits limpios
git log --oneline origin/main..HEAD

# 5. Sin archivos no deseados
git status
```

---

## Comandos Prohibidos

### ❌ NUNCA USAR:

```bash
git commit --no-verify          # Bypass hooks
git push --force origin main    # Force push a main
git checkout [archivo]          # Puede perder cambios
git reset --hard [sin backup]   # Pérdida datos
```

### ✅ ALTERNATIVAS CORRECTAS:

```bash
# En lugar de git checkout file (pérdida cambios)
git stash save "backup antes de revert"
git checkout file

# En lugar de force push
git pull --rebase origin main
git push origin feature-branch

# En lugar de --no-verify
# Corregir el problema que causa el hook failure
```

---

## Backup Antes de Cambios Mayores

```bash
# Backup automático (ya implementado en hooks)
bench --site admin1.dev backup --with-files

# Renombrar para identificación
cd sites/admin1.dev/private/backups
cp [timestamp]-admin1_dev-database.sql.gz \
   backup-pre-feature-companies-$(date +%Y%m%d).sql.gz
```

---

## Resolución de Conflictos

### Merge Conflicts

```bash
# Si hay conflictos al mergear
git fetch origin main
git merge origin/main

# Resolver conflictos manualmente
# Luego:
git add [archivos resueltos]
git commit -m "merge: resolver conflictos con main"
```

### Rebase (Avanzado)

```bash
# Si necesitas rebase (usar con cuidado)
git fetch origin main
git rebase origin/main

# Si hay conflictos, resolver y:
git add [archivos]
git rebase --continue
```

---

## GitHub CLI Shortcuts

### Comandos Útiles

```bash
# Ver PRs abiertos
gh pr list --state open

# Ver status checks de PR
gh pr checks

# Ver diff de PR
gh pr diff 123

# Mergear PR (si tienes permisos)
gh pr merge 123 --squash
```

---

## Recursos Adicionales

- [CLAUDE.md RG-002](../../CLAUDE.md) - Reglas git completas
- [CI/CD](ci-cd.md) - Integración continua
- [Troubleshooting](troubleshooting.md) - Solución problemas comunes

---

**Actualizado:** 2025-10-17
**Basado en:** CLAUDE.md RG-002 + lessons learned
