# docs_new/ — Documentación validada de condominium_management

**Creado:** 2026-05-26
**Estado:** En construcción — se puebla tarea por tarea

---

## Qué es este directorio

`docs_new/` es el destino de documentación validada del app `condominium_management`.

No es una reorganización de `docs/`. Es una estructura nueva que se construye
progresivamente, documento por documento, a medida que cada fragmento de
documentación existente es revisado, verificado contra el estado real del app
y confirmado durante una tarea real.

**`docs/` permanece intacta** hasta que cada sección sea procesada.

---

## Workflow documental obligatorio

Para cada tarea real del app:

1. **Buscar** en `docs/` todas las referencias relacionadas con la tarea.
2. **Clasificar** cada fragmento encontrado como:
   - ✅ Vigente — coincide con el estado real del app
   - ⚠️ Parcialmente vigente — información correcta pero con detalles obsoletos
   - ❌ Obsoleto — el problema que documenta ya está resuelto, o la información es incorrecta
   - ❓ Faltante — el tema no está documentado en ningún lugar
3. **Ejecutar** la tarea con instrucciones basadas en evidencia documental.
4. **Documentar** en `docs_new/` únicamente lo confirmado durante la ejecución.
5. **No mover** lo no confirmado.

### Regla de movimiento

Un fragmento pasa a `docs_new/` solo cuando cumple las tres condiciones:
- Fue encontrado en `docs/` (o identificado como faltante).
- Fue revisado contra el estado real del app.
- Fue validado durante una tarea real ejecutada.

Si no cumple las tres: se queda donde está.

---

## Estructura destino

```
docs_new/
├── README.md                          ← este archivo
├── usuario/
│   ├── index.md
│   ├── instalacion-y-configuracion.md ← en construcción
│   ├── flujo-operativo.md
│   ├── condominios.md
│   └── espacios-fisicos.md
├── tecnico/
│   ├── index.md
│   ├── desarrollo-local.md
│   ├── arquitectura.md
│   ├── testing.md
│   ├── fixtures.md
│   ├── hooks.md
│   └── deuda-tecnica.md
├── adr/
│   └── (copias de adr/ vigentes, cuando se revisen)
└── archive/
    └── (documentos descartados con nota de por qué)
```

Los archivos marcados como "en construcción" se crean vacíos o con el primer
fragmento validado al completar la primera tarea que los requiera.

---

## Estado de construcción

| Archivo | Estado | Tarea que lo crea |
|---|---|---|
| `usuario/instalacion-y-configuracion.md` | ✅ En construcción | Configuración inicial condo-v16.dev (wizard + company_type) |
| `tecnico/hooks.md` | ✅ En construcción | Configuración inicial condo-v16.dev (wizard — Company hooks) |
| `tecnico/fixtures.md` | ✅ En construcción | Fix Company Type IDs (bug depends_on + insert_after) |
| `tecnico/desarrollo-local.md` | Pendiente | Configuración inicial condo-v16.dev |
| `tecnico/deuda-tecnica.md` | Pendiente | Próxima tarea: ISSUE #7 |
| Resto | Pendiente | Tareas futuras |

---

## Fuentes de autoridad para poblar docs_new/

En orden de precedencia:

1. Estado real observado durante ejecución de la tarea.
2. `CONTINUITY.md` — estado actual del proyecto.
3. `CLAUDE.md` (app) — reglas operativas vigentes.
4. `docs/adr/` — decisiones arquitectónicas.
5. `docs/` — documentación existente (revisar vigencia antes de copiar).
6. Frappe/ERPNext docs oficiales v16 — para comportamiento del framework.

---

## Lo que NO va en docs_new/

- Reportes de sesiones de desarrollo (REPORTE-*, DIAGNOSTICO-*, PLAN-*).
- Auditorías de PRs específicos (pr-24-*, pr-21-*).
- Resultados de campañas de testing (testing/resultados/).
- Placeholders sin contenido real.
- Instrucciones que referencian sites v15 (admin1.dev) sin actualizar a v16.
