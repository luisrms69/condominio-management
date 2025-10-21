# Companies – Recreación de Journey

**Módulo:** Companies
**Journey:** Crear Primer Condominio (Setup Inicial)
**Rol:** Super Admin / Administrador IT
**Fecha ejecución:** 2025-10-18 (Día 1 - Planificación)

---

## Journey 1: Crear Primer Condominio

### Contexto/Objetivo del Usuario

**Persona:** María González - Administradora IT de empresa de gestión de condominios

**Objetivo:** Configurar el primer condominio en el sistema para empezar a operar

**Motivación:** La empresa acaba de instalar condominium_management y necesita empezar a usarlo para gestionar "Condominio Torres del Sol"

**Experiencia previa:** Conoce ERPNext básico, primera vez usando condominium_management

---

### Precondiciones

**Rol/Permisos:**
- [x] Usuario con rol System Manager
- [x] Permisos de creación en Company
- [x] Permisos de creación en Condominium Information
- [x] App condominium_management instalada

**Datos necesarios:**
- Nombre del condominio: "Torres del Sol"
- RFC: TSO1234567ABC
- Dirección física completa
- Información de contacto

**Estado del sistema:**
- [x] Fresh install (bench install-app ejecutado)
- [x] Fixtures cargados
- [ ] ¿Wizard de setup inicial disponible? (TBD - evaluar)

---

### Pasos Secuenciales

| # | Paso | Acción del Usuario | Resultado Esperado | Resultado Real | Fricción |
|---|------|-------------------|-------------------|----------------|----------|
| 1 | Acceso inicial | Login al sistema y ver dashboard | Dashboard con módulos visibles | (TBD - ejecutar en admin1.dev) | TBD |
| 2 | Buscar módulo | Buscar "Companies" o "Condominio" en awesome bar | Encontrar Company o Condominium Information | (TBD) | TBD |
| 3 | ¿Crear Company o Condominium Information? | **Decisión:** ¿Qué crear primero? | Debe ser obvio: Company primero | (TBD) | **FRICCIÓN ESPERADA:** No está claro cuál crear primero |
| 4 | Crear Company | Click en "New Company", llenar formulario básico | Company creado con campos obligatorios claros | (TBD) | TBD |
| 5 | Configurar Company | Llenar: Company Name, Abbr, Default Currency (MXN), Country (Mexico) | Guardado exitoso | (TBD) | TBD |
| 6 | Crear Condominium Information | Buscar y crear Condominium Information, enlazar a Company | Relación Company ↔ Condominium clara | (TBD) | **FRICCIÓN ESPERADA:** Relación no obvia |
| 7 | Configurar información específica | Llenar campos específicos del condominium (dirección, contacto, etc.) | Campos organizados lógicamente | (TBD) | TBD |
| 8 | Crear Service Management Contract | Crear contrato de gestión entre administradora y condominio | Relación con Company clara | (TBD) | TBD |
| 9 | Verificación | Revisar que todo quedó configurado correctamente | Dashboard muestra condominio activo | (TBD) | TBD |

**Tiempo esperado:** 10-15 minutos para usuario experimentado

**Tiempo real:** (TBD - medir en ejecución real)

---

### Resultados

#### Esperado
- Company creado y configurado
- Condominium Information enlazado
- Service Management Contract creado
- Usuario puede continuar con configuración de Physical Spaces

#### Observado
(Pendiente ejecución en admin1.dev - Día 2)

**Evidencias:**
- `evidencias/screenshots/journey1-step*.png`
- `evidencias/videos/journey1-full-flow.mp4`

---

### Puntos de Fricción Identificados

| Paso | Fricción | Severidad | Impacto | Evidencia |
|------|----------|-----------|---------|-----------|
| 3 | No está claro qué crear primero (Company vs Condominium Information) | Alta | Usuario pierde tiempo buscando documentación o prueba/error | (Capturar en Día 2) |
| 6 | Relación Company ↔ Condominium Information no es obvia | Media | Usuario puede crear Condominium sin enlazar correctamente | (Capturar en Día 2) |
| - | ¿Falta wizard de setup? | Alta (si no existe) | Sin guía, setup inicial es confuso | (Verificar en Día 2) |

---

### Notas de Observación

**Hipótesis a validar en ejecución real:**

1. ¿Existe un wizard de setup inicial que guíe el proceso?
   - Si NO: **Alta fricción** - crear propuesta de wizard

2. ¿Los campos obligatorios están claramente marcados?
   - Verificar asteriscos rojos, mensajes claros

3. ¿La documentación (user-guide/companies.md) es accesible desde el formulario?
   - ¿Hay links de ayuda contextuales?

4. ¿Los custom fields (cm_*) son visibles y confusos?
   - Evaluar si deben ocultarse o tener mejor labeling

5. ¿Hay validaciones que fallan sin mensaje claro?
   - Capturar screenshots de cualquier error

---

## Journey 2: Editar Información de Condominio (Planeado para Día 2)

**Contexto:** Usuario necesita actualizar dirección del condominio

**Pasos:** (TBD)

---

## Journey 3: Consultar Contratos de Gestión (Planeado para Día 3)

**Contexto:** Usuario quiere revisar términos del contrato

**Pasos:** (TBD)

---

**Actualizado:** 2025-10-18
**Estado:** Planificado - Pendiente ejecución en admin1.dev
**Próximo paso:** Ejecutar Journey 1 en entorno real y documentar resultados
