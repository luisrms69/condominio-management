# Physical Spaces – Recreación de Journey

**Módulo:** Physical Spaces
**Journey:** Configurar Estructura Física de Condominio
**Rol:** Administrador de Condominio
**Fecha ejecución:** Pendiente (Día 2+)

---

## Journey 1: Configurar Estructura Física Completa

### Contexto/Objetivo del Usuario

**Persona:** Carlos Ramírez - Administrador de Condominio Torres del Sol

**Objetivo:** Configurar la estructura física completa del condominio en el sistema (Torre A: 5 pisos, 4 deptos por piso; Torre B: 3 pisos, 2 deptos por piso)

**Motivación:** Necesita tener todos los espacios registrados para asignar propietarios, calcular cuotas de mantenimiento y gestionar accesos

**Experiencia previa:** Ya configuró Company y Condominium Information, primera vez usando Physical Spaces

---

### Precondiciones

**Rol/Permisos:**
- [x] Usuario con rol Condominium Administrator
- [x] Permisos creación en Physical Space
- [x] Permisos creación en Space Category
- [x] Company y Condominium Information ya creados

**Datos necesarios:**
- Estructura física completa:
  - Torre A: 5 pisos, 4 departamentos por piso (A-101, A-102, A-201, etc.)
  - Torre B: 3 pisos, 2 departamentos por piso (B-101, B-102, B-201, etc.)
  - Áreas comunes: Lobby, Gimnasio, Alberca, Estacionamiento
- Categorías de espacios: Departamento, Local Comercial, Estacionamiento, Área Común

**Estado del sistema:**
- [x] Company "Torres del Sol" creado
- [x] Condominium Information configurado
- [ ] Physical Spaces vacío (primera configuración)

---

### Pasos Secuenciales

| # | Paso | Acción del Usuario | Resultado Esperado | Resultado Real | Fricción |
|---|------|-------------------|-------------------|----------------|----------|
| 1 | Acceso módulo | Buscar "Physical Spaces" en awesome bar | Encontrar opción fácilmente | (TBD) | TBD |
| 2 | Ver estructura existente | Abrir tree view de espacios | Ver estructura jerárquica vacía o raíz | (TBD) | **FRICCIÓN ESPERADA:** No obvio cómo iniciar estructura |
| 3 | Crear nodo raíz | Crear Physical Space raíz "Torres del Sol" | Creación exitosa, level=0 | (TBD) | **FRICCIÓN ESPERADA:** ¿Qué es parent_physical_space=None? |
| 4 | Crear Torre A | Crear hijo "Torre A" bajo "Torres del Sol" | Relación padre-hijo correcta, level=1 | (TBD) | TBD |
| 5 | Crear Piso 1 Torre A | Crear hijo "Piso 1" bajo "Torre A" | Relación correcta, level=2 | (TBD) | TBD |
| 6 | Crear departamentos | Crear 4 deptos: A-101, A-102, A-103, A-104 | 4 nodos level=3 bajo "Piso 1" | (TBD) | **FRICCIÓN ESPERADA:** Tedioso crear uno por uno (20 deptos solo Torre A) |
| 7 | Repetir para otros pisos | Crear Pisos 2-5 con sus deptos | Estructura completa Torre A | (TBD) | **FRICCIÓN ESPERADA:** Sin bulk create, muy manual |
| 8 | Crear Torre B | Repetir proceso para Torre B | Estructura Torre B completa | (TBD) | **FRICCIÓN ESPERADA:** Sin templates, re-trabajo manual |
| 9 | Asignar categorías | Asignar Space Category a cada espacio | Categorización correcta | (TBD) | **FRICCIÓN ESPERADA:** Asignación individual vs bulk |
| 10 | Verificar estructura | Revisar tree view completo | Estructura jerárquica correcta, fácil navegar | (TBD) | TBD |

**Tiempo esperado:** 15-20 minutos (si hay bulk operations)

**Tiempo real estimado sin bulk:** 60-90 minutos (30+ espacios individuales)

---

### Resultados

#### Esperado
- Estructura jerárquica completa: Condominio → Torres → Pisos → Departamentos
- Categorías asignadas correctamente
- Tree view navegable y claro
- Usuario puede proceder a asignar propietarios

#### Observado
(Pendiente ejecución en admin1.dev - Día 2+)

**Evidencias:**
- `evidencias/screenshots/journey1-step*.png`
- `evidencias/videos/journey1-full-setup.mp4`

---

### Puntos de Fricción Identificados

| Paso | Fricción | Severidad | Impacto | Evidencia |
|------|----------|-----------|---------|-----------|
| 2 | No obvio cómo iniciar estructura (crear raíz primero) | Media | Usuario pierde 5-10 min o crea estructura incorrecta | (TBD) |
| 3 | Concepto "parent_physical_space=None" técnico, no user-friendly | Media | Confusión inicial | (TBD) |
| 6-8 | Sin bulk create - creación manual uno por uno | Alta | 60-90 min vs 15-20 min esperado | (TBD) |
| 8 | Sin templates para estructuras comunes (Torre con N pisos, M deptos) | Alta | Re-trabajo manual, propenso a errores | (TBD) |
| 9 | Asignación categorías individual vs bulk | Media | Tiempo adicional, clicks innecesarios | (TBD) |

---

### Notas de Observación

**Hipótesis a validar en ejecución real:**

1. **¿Existe wizard o bulk operations?**
   - Si NO: **Alta fricción** - crear 30+ espacios uno por uno inviable
   - Si SÍ: Documentar usabilidad del wizard

2. **¿Tree view es intuitivo?**
   - ¿Expand/collapse obvio?
   - ¿Indicadores visuales de nivel (iconos, indentación)?
   - ¿Acciones rápidas (edit, delete, add child) accesibles?

3. **¿Validaciones Nested Set son claras?**
   - ¿Mensajes error comprensibles si intenta operación inválida?
   - ¿Previene eliminar nodo con hijos sin confirmación?

4. **¿Puede corregir errores fácilmente?**
   - ¿Mover espacio a otro parent?
   - ¿Renombrar espacios?
   - ¿Deshacer operaciones?

5. **¿Documentación accesible?**
   - ¿Help text explica Nested Set en términos simples?
   - ¿Ejemplos visuales de estructuras típicas?

---

## Journey 2: Editar Estructura Existente (Planeado para Día 2+)

**Contexto:** Administrador necesita agregar nueva Torre C al condominio existente

**Pasos:** (TBD)

**Hipótesis fricción:**
- ¿Puede agregar torre sin afectar estructura existente?
- ¿Validaciones Nested Set permiten inserciones mid-tree?

---

## Journey 3: Búsqueda y Navegación (Planeado para Día 3+)

**Contexto:** Administrador necesita encontrar departamento A-304 rápidamente

**Pasos:** (TBD)

**Hipótesis fricción:**
- ¿Search bar funciona en tree view?
- ¿Filtros por Space Category disponibles?
- ¿Navegación breadcrumbs clara?

---

**Actualizado:** 2025-10-18
**Estado:** Planificado - Pendiente ejecución en admin1.dev
**Próximo paso:** Ejecutar Journey 1 en entorno real y documentar resultados
