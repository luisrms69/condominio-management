# 🤖 CONFIGURACIÓN PERMANENTE CLAUDE CODE - SISTEMA CONDOMINIUM MANAGEMENT

**ARCHIVO INMUTABLE - NO MODIFICAR SIN APROBACIÓN USUARIO**

## 🎯 **SEPARACIÓN CRÍTICA DE RESPONSABILIDADES**

### **📁 UBICACIONES FÍSICAS DEFINITIVAS:**

#### **A. MEMORIA OPERACIONAL CLAUDE CODE:**
```
CLAUDE.md                              # Índice principal (MAX 300 líneas)
docs/core/                            # Reglas y configuración inmutable
docs/operational/                     # Estado actual del proyecto
docs/workflows/                       # Procesos de desarrollo
```

#### **B. ARQUITECTURA EXTERNA (IMPORT/EXPORT):**
```
project_architecture/requirements/    # Requerimientos de módulos
project_architecture/design/         # Diseños de arquitectura
project_architecture/specifications/ # Especificaciones técnicas
```

#### **C. CÓDIGO FRAPPE:**
```
condominium_management/              # Código fuente del sistema
```

---

## 🔍 **CRITERIOS DE CLASIFICACIÓN AUTOMÁTICA**

### **✅ VA EN CLAUDE.MD/docs/ (OPERACIONAL):**
- **Estado de desarrollo** de módulos (completo/pendiente/en progreso)
- **Configuración de hooks** activa (qué hooks están configurados)
- **Comandos frecuentes** de desarrollo (bench, git, testing)
- **Reglas de desarrollo** (testing, naming, branching)
- **Procesos automáticos** (cómo crear nuevo módulo)
- **Troubleshooting** de problemas comunes
- **Decisiones técnicas** tomadas durante desarrollo

### **❌ VA EN project_architecture/ (EXTERNA):**
- **Requerimientos de negocio** de módulos específicos
- **Diseños de arquitectura** de sistemas
- **Especificaciones técnicas** detalladas
- **Documentación de APIs** para cliente/stakeholders
- **Diagramas de flujo** de procesos de negocio
- **Análisis de casos de uso** específicos
- **Documentación para usuarios finales**

---

## 🤖 **INSTRUCCIONES PARA CLAUDE CODE**

### **CUANDO RECIBAS DOCUMENTOS:**

#### **🔍 CLASIFICACIÓN AUTOMÁTICA:**
```markdown
SI el documento contiene:
- ✅ Estado de módulos → docs/operational/MODULE_STATUS.md
- ✅ Configuración de hooks → docs/operational/HOOKS_CONFIG.md  
- ✅ Proceso de desarrollo → docs/workflows/
- ✅ Reglas de código → docs/core/
- ✅ Comandos de desarrollo → docs/core/COMMANDS.md

SI el documento contiene:
- ❌ Requerimientos de negocio → project_architecture/requirements/
- ❌ Diseño de arquitectura → project_architecture/design/
- ❌ Especificaciones API → project_architecture/specifications/
- ❌ Casos de uso → project_architecture/requirements/
- ❌ Documentación usuario final → project_architecture/specifications/
```

#### **🔄 PROCESO AUTOMÁTICO:**
1. **Al recibir documento**: Clasificar según criterios arriba
2. **Si es operacional**: Integrar en CLAUDE.md/docs/
3. **Si es arquitectura**: Guardar en project_architecture/
4. **Al finalizar**: Actualizar referencias en CLAUDE.md
5. **Commit**: Separar archivos operacionales vs arquitectura

---

## 📋 **PROCESO PARA NUEVOS MÓDULOS**

### **TEMPLATE AUTOMÁTICO:**
```bash
# 1. CREAR ESTRUCTURA OPERACIONAL
echo "- **[MODULO]**: 🔄 EN DESARROLLO - Hooks: ❌ | Tests: ❌" >> docs/operational/MODULE_STATUS.md

# 2. APLICAR TEMPLATE HOOKS
python TEMPLATE_MODULE_HOOKS.py generate_hooks_for_module('[modulo]')

# 3. ACTUALIZAR CONFIGURACIÓN
echo "[MODULO] hooks configurados $(date)" >> docs/operational/HOOKS_CONFIG.md

# 4. COMMIT SEPARADO
git add docs/ condominium_management/[modulo]/
git commit -m "feat([modulo]): setup operacional y hooks framework"
```

### **ACTUALIZACIÓN STATUS:**
```bash
# Al completar módulo:
sed -i 's/[MODULO].*🔄.*/[MODULO]: ✅ COMPLETO - Hooks: ✅ | Tests: ✅/' docs/operational/MODULE_STATUS.md
```

---

## 🚨 **REGLAS INMUTABLES**

### **ESTRUCTURA:**
1. **CLAUDE.md**: Máximo 300 líneas (solo índice + reglas críticas)
2. **docs/core/**: NUNCA modificar sin aprobación usuario
3. **docs/operational/**: Actualizar frecuentemente con estado real
4. **project_architecture/**: SOLO documentos de arquitectura externa

### **SEPARACIÓN:**
1. **Operacional Claude**: Estado, configuración, procesos de desarrollo
2. **Arquitectura Externa**: Diseños, requerimientos, especificaciones
3. **NO MEZCLAR**: Cada archivo tiene propósito específico

### **PROCESO:**
1. **Cada cambio importante**: Actualizar docs/operational/
2. **Cada nuevo módulo**: Aplicar template automático
3. **Cada commit**: Verificar CLAUDE.md < 300 líneas
4. **Cada PR**: Verificar separación correcta

---

## 📞 **INSTRUCCIONES DE USO PARA USUARIO**

### **PARA ARQUITECTURA (project_architecture/):**
```markdown
Usuario dice: "Aquí está el diseño del módulo Physical Spaces..."
Claude debe: Guardar en project_architecture/design/physical_spaces_architecture.md
```

### **PARA OPERACIÓN (docs/):**
```markdown
Usuario dice: "El módulo Physical Spaces está completo..."
Claude debe: Actualizar docs/operational/MODULE_STATUS.md
```

### **PARA DESARROLLO:**
```markdown
Usuario dice: "Implementa el módulo Physical Spaces..."
Claude debe: 
1. Consultar project_architecture/requirements/physical_spaces_req.md
2. Aplicar NEW_MODULE_PROCESS.md
3. Actualizar docs/operational/ con progreso
```

---

**FECHA CREACIÓN:** 2025-07-04  
**ESTADO:** ACTIVO - CONFIGURACIÓN PERMANENTE  
**MODIFICACIÓN:** Solo con aprobación explícita del usuario