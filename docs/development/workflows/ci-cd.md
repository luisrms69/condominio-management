# CI/CD Workflow

Pipeline de integración y despliegue continuo.

---

## GitHub Actions Pipeline

### Configuración Básica

Archivo `.github/workflows/tests.yml`:

```yaml
name: Testing Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          pip install frappe-bench
          bench init frappe-bench --skip-assets
          cd frappe-bench
          bench get-app ${{ github.workspace }}
          bench new-site test-site --admin-password admin
          bench --site test-site install-app condominium_management

      - name: Run Tests
        run: |
          cd frappe-bench
          bench --site test-site run-tests --app condominium_management

      - name: Run Linting
        run: |
          pip install ruff
          ruff check .
```

---

## Pre-commit Hooks (Local)

### Tests Críticos Pre-commit

No ejecutamos TODOS los tests en pre-commit (demasiado lento), solo checks rápidos:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: ruff check --fix
        language: system
        types: [python]

      - id: check-yaml
        name: Check YAML
        entry: check-yaml
        language: system
        types: [yaml]
```

---

## Pipeline Stages

### Stage 1: Linting (Rápido)

```bash
# Ejecuta en cada commit
ruff check --fix .
```

**Criterio de paso:** 0 errores linting

---

### Stage 2: Tests Unitarios (Medio)

```bash
# Ejecuta en cada push
bench --site test-site run-tests --app condominium_management
```

**Criterio de paso:** 100% tests pasando

---

### Stage 3: Tests Performance (Lento)

```bash
# Ejecuta solo en PRs a main
bench --site test-site run-tests \
  --module "condominium_management.*.test_*_l4b_performance"
```

**Criterio de paso:** Benchmarks < thresholds

---

## Ambientes

### Development (Local)

```bash
SITE: admin1.dev
COMANDOS: bench --site admin1.dev [comando]
```

### CI/CD (GitHub Actions)

```bash
SITE: test-site (efímero)
COMANDOS: Automatizados en workflow
```

### Staging (Futuro)

```bash
SITE: staging.admin1.dev
COMANDOS: Deploy automático desde main
```

---

## Debugging CI Failures

### Tests Fallan en CI pero Pasan Local

**Causas comunes:**

1. **Environment Differences**
   ```bash
   # Verificar versiones
   python --version
   frappe --version
   ```

2. **Database State**
   ```bash
   # CI usa DB limpia siempre
   # Local puede tener datos residuales
   bench --site admin1.dev reinstall
   ```

3. **Permisos**
   ```bash
   # CI puede tener permisos diferentes
   # Usar ignore_permissions=True en tests
   ```

### Linting Falla en CI

```bash
# Ejecutar exactamente lo mismo que CI
ruff check .

# Auto-fix
ruff check --fix .

# Commit fixes
git add .
git commit -m "fix: resolver linting issues"
```

---

## Secrets Management

### Variables de Entorno en CI

GitHub repository settings → Secrets:

```yaml
# En workflow
env:
  ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

**⚠️ NUNCA** commitear secrets en código.

---

## Build Artifacts

### Guardar Reports de Tests

```yaml
- name: Upload Test Reports
  if: always()
  uses: actions/upload-artifact@v2
  with:
    name: test-reports
    path: frappe-bench/sites/test-site/logs/
```

### Coverage Reports

```yaml
- name: Generate Coverage
  run: |
    bench --site test-site run-tests --coverage \
      --app condominium_management

- name: Upload Coverage
  uses: codecov/codecov-action@v2
  with:
    files: ./coverage.xml
```

---

## Deploy Automation (Futuro)

### Deploy a Staging

```yaml
deploy-staging:
  needs: test
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest

  steps:
    - name: Deploy to Staging
      run: |
        ssh user@staging.server 'cd /path/to/bench && \
          git pull origin main && \
          bench --site staging.admin1.dev migrate && \
          bench --site staging.admin1.dev build'
```

---

## Health Checks

### Post-Deploy Verification

```bash
# Smoke tests básicos
curl https://staging.admin1.dev/api/method/ping
curl https://staging.admin1.dev/desk

# Verificar migración exitosa
bench --site staging.admin1.dev migrate --dry-run
```

---

## Rollback Strategy

### Si Deploy Falla

```bash
# 1. Revert a commit anterior
git revert HEAD
git push origin main

# 2. O rollback manual
bench --site staging.admin1.dev restore [backup-file]

# 3. Verificar estado
bench --site staging.admin1.dev doctor
```

---

## Performance Monitoring

### Benchmark Tracking

```yaml
- name: Run Performance Tests
  run: |
    bench --site test-site run-tests \
      --module "...test_l4b_performance" \
      --profile > performance.txt

- name: Compare with Baseline
  run: |
    python scripts/compare_performance.py \
      performance.txt baseline.txt
```

---

## Notifications

### Slack/Email on Failure

```yaml
- name: Notify on Failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Tests failed on ${{ github.ref }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Best Practices

### ✅ DO

- Ejecutar tests localmente antes de push
- Mantener pipeline rápido (< 10 min ideal)
- Usar caching para dependencies
- Tests deterministas (sin flakiness)
- Logs claros de failures

### ❌ DON'T

- Commit sin verificar tests locales
- Ignorar CI failures ("pasará en segundo intento")
- Hardcodear secrets
- Tests que dependen de orden de ejecución
- Pipeline > 30 minutos

---

## Troubleshooting Commands

```bash
# Ver logs de CI run
gh run list
gh run view [run-id] --log

# Re-run failed jobs
gh run rerun [run-id]

# Download artifacts
gh run download [run-id]
```

---

## Recursos Adicionales

- [Git Workflow](git-workflow.md) - Estrategia branching
- [Testing Best Practices](../testing/best-practices.md) - Metodología testing
- [Troubleshooting](troubleshooting.md) - Solución problemas

---

**Actualizado:** 2025-10-17
**Basado en:** CLAUDE.md RG-002 + RG-003
