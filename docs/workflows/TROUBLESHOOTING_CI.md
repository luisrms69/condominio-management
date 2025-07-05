# 🚨 TROUBLESHOOTING CI/CD - PROBLEMAS FRECUENTES

## 🎯 **PROBLEMA: YARN INSTALL FAILURES EN GITHUB ACTIONS**

### **Error Identificado (2025-07-04):**
```
error https://registry.yarnpkg.com/esbuild-linux-arm64/-/esbuild-linux-arm64-0.14.54.tgz: Request failed "500 Internal Server Error"
subprocess.CalledProcessError: Command 'yarn install --check-files' returned non-zero exit status 1
```

### **Diagnóstico:**
- **Problema**: Registry npm/yarn intermitente con paquetes ARM64
- **Causa**: GitHub Actions runners tienen problemas con dependencias ARM64 específicas
- **Impacto**: Falla setup de Frappe Framework en CI

### **Metodología AI-ASSISTED DEBUGGING:**

#### **🤖 HERRAMIENTAS DISPONIBLES:**
- **GitHub Copilot**: `gh copilot suggest -t shell "fix yarn install errors"`
- **ChatGPT/Claude**: Análisis de patrones y root cause
- **VS Code Extensions**: GitLens, autoDocstring, Conventional Commits

#### **🔍 PROCESO DE ANÁLISIS:**
1. **Identificar patrón**: Error específico + contexto (CI vs local)
2. **Consultar AI**: GitHub Copilot para soluciones específicas yarn/npm
3. **Comparar con apps oficiales**: Verificar CI configs de apps Frappe exitosas
4. **Implementar fix incremental**: Un cambio a la vez con validación
5. **Documentar solución**: Guardar en troubleshooting para futuros

#### **💡 SOLUCIONES PROBADAS:**

##### **Opción A: Retry Strategy**
```yaml
# .github/workflows/ci.yml
- name: Install Frappe with retry
  run: |
    for i in {1..3}; do
      if bench init --python python3 frappe-bench; then
        break
      else
        echo "Attempt $i failed, retrying..."
        rm -rf frappe-bench
        sleep 30
      fi
    done
```

##### **Opción B: Alternative Registry**
```yaml
- name: Configure yarn registry
  run: |
    yarn config set registry https://registry.npmjs.org/
    yarn config set network-timeout 300000
```

##### **Opción C: Node Version Specific**
```yaml
- name: Use specific node version
  uses: actions/setup-node@v3
  with:
    node-version: '18.x'
    registry-url: 'https://registry.npmjs.org'
```

### **🚨 REGLAS CRÍTICAS CI DEBUGGING:**
1. **NUNCA asumir** que error es por nuestro código - verificar en site limpio
2. **SIEMPRE consultar AI tools** antes de inventar soluciones custom
3. **COMPARAR con apps oficiales** - usar patterns probados
4. **DOCUMENTAR solución** en troubleshooting para futuros

---

## 🔧 **OTROS PROBLEMAS FRECUENTES**

### **Setup Wizard Conflicts:**
- **Error**: `Could not find Parent Department: All Departments`
- **Causa**: ERPNext setup wizard + hooks universales
- **Solución**: Hooks específicos por DocType (ya implementado)

### **Test Failures Post-Hooks:**
- **Comando verificación**: `bench --site domika.dev run-tests --app condominium_management`
- **Regla**: SIEMPRE ejecutar después de modificar hooks.py
- **Rollback**: Si falla, git reset inmediato

### **Contaminated Branches:**
- **Problema**: Múltiples commits mezclados en PR
- **Prevención**: Branch limpio desde main para cada feature
- **Solución**: Cerrar PR, crear branch nuevo desde main

---

**Actualizado**: 2025-07-04 - GitHub Actions yarn failures  
**Metodología**: AI-assisted debugging con Copilot + VS Code tools  
**Próximo**: Aplicar solución yarn registry + retry strategy