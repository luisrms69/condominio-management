# Financial Management – Recreación de Journey

**Módulo:** Financial Management
**Journey:** Facturar Cuotas Mantenimiento Mensual
**Rol:** Administrador Financiero / Contador
**Fecha ejecución:** Pendiente (Día 2+)

---

## Journey 1: Crear y Ejecutar Ciclo de Facturación Mensual

### Contexto/Objetivo del Usuario

**Persona:** Ana Martínez - Contadora de Condominio Torres del Sol

**Objetivo:** Generar facturación de cuotas de mantenimiento mensuales para todos los propietarios (30 departamentos) y enviar invoices

**Motivación:** Es inicio de mes, necesita facturar cuotas ordinarias + extraordinarias (reparación elevador). Fecha límite: día 5 de cada mes

**Experiencia previa:** Conoce contabilidad, segunda vez usando sistema (primer mes fue con ayuda)

---

### Precondiciones

**Rol/Permisos:**
- [x] Usuario con rol Financial Manager
- [x] Permisos creación en Billing Cycle
- [x] Permisos creación en Property Account
- [x] Company, Condominium, Physical Spaces ya configurados

**Datos necesarios:**
- 30 departamentos con propietarios asignados
- Cuota ordinaria: $2,500 MXN/mes
- Cuota extraordinaria (reparación): $1,000 MXN (one-time)
- Vencimiento: día 10 del mes
- Método pago: Transferencia bancaria

**Estado del sistema:**
- [x] Physical Spaces completo con propietarios
- [x] Property Accounts creados para cada departamento
- [x] Conceptos facturación definidos (Cuota Ordinaria, Extraordinaria)
- [ ] Billing Cycle mes actual (a crear)

---

### Pasos Secuenciales

| # | Paso | Acción del Usuario | Resultado Esperado | Resultado Real | Fricción |
|---|------|-------------------|-------------------|----------------|----------|
| 1 | Acceso módulo | Buscar "Financial Management" o "Billing Cycle" | Encontrar módulo fácilmente | (TBD) | TBD |
| 2 | Verificar dashboard | Revisar KPIs: saldo mes anterior, pagos pendientes | Dashboard actualizado con info clara | (TBD) | **FRICCIÓN ESPERADA:** Dashboard puede no mostrar KPIs críticos |
| 3 | Crear Billing Cycle | Nuevo Billing Cycle "Octubre 2025" | Form con campos obvios | (TBD) | **FRICCIÓN ESPERADA:** No claro qué campos son obligatorios |
| 4 | Configurar período | Seleccionar período: 01/10/2025 - 31/10/2025 | Fechas validadas correctamente | (TBD) | TBD |
| 5 | Agregar conceptos | Agregar: 1) Cuota Ordinaria $2,500, 2) Extraordinaria $1,000 | Conceptos agregados a billing cycle | (TBD) | **FRICCIÓN ESPERADA:** ¿Se agregan a todos los deptos automáticamente o manual? |
| 6 | Generar invoices | Botón "Generar Facturas" crea 30 invoices automáticamente | 30 Sales Invoice creados enlazados a Property Accounts | (TBD) | **FRICCIÓN ESPERADA:** Sin preview antes de generar (si hay error, 30 invoices incorrectos) |
| 7 | Revisar invoices | Verificar muestreo 3-5 invoices aleatorios | Montos correctos, propietarios correctos, fechas correctas | (TBD) | **FRICCIÓN ESPERADA:** Sin listado consolidado, debe buscar uno por uno |
| 8 | Enviar notificaciones | Enviar emails con invoices a propietarios | 30 emails enviados exitosamente | (TBD) | **FRICCIÓN ESPERADA:** ¿Envío manual uno por uno o bulk? |
| 9 | Cerrar ciclo | Marcar Billing Cycle como "Facturado" | Estado actualizado, no permite modificaciones | (TBD) | TBD |
| 10 | Verificar dashboard | Dashboard muestra facturación completada, pagos pendientes | Info actualizada en tiempo real | (TBD) | TBD |

**Tiempo esperado:** 15-20 minutos para 30 departamentos (con bulk operations)

**Tiempo real estimado sin bulk:** 90-120 minutos (si debe crear invoices uno por uno)

---

### Resultados

#### Esperado
- Billing Cycle creado y cerrado
- 30 Sales Invoice generados correctamente
- Emails enviados a propietarios
- Dashboard actualizado con facturación pendiente de pago
- Usuario puede proceder a registrar pagos conforme lleguen

#### Observado
(Pendiente ejecución en admin1.dev - Día 2+)

**Evidencias:**
- `evidencias/screenshots/journey1-step*.png`
- `evidencias/videos/journey1-billing-cycle.mp4`

---

### Puntos de Fricción Identificados

| Paso | Fricción | Severidad | Impacto | Evidencia |
|------|----------|-----------|---------|-----------|
| 2 | Dashboard no muestra KPIs críticos (saldo, pagos vencidos, proyecciones) | Alta | Información clave requiere navegar múltiples pantallas | (TBD) |
| 3 | Campos obligatorios Billing Cycle no claros | Media | Usuario intenta guardar y recibe errores | (TBD) |
| 5 | No claro si conceptos aplican automáticamente a todos los deptos o manual | Alta | Puede facturar incorrectamente (algunos deptos sin concepto) | (TBD) |
| 6 | Sin preview antes de generar 30 invoices | Alta | Si hay error configuración, debe corregir 30 invoices manualmente | (TBD) |
| 7 | Sin listado consolidado invoices del ciclo | Media | Revisar invoices requiere búsqueda individual | (TBD) |
| 8 | Envío emails manual uno por uno vs bulk | Alta | 30 emails manuales toma 30-60 min vs 1 min bulk | (TBD) |

---

### Notas de Observación

**Hipótesis a validar en ejecución real:**

1. **¿Existe generación automática bulk de invoices?**
   - Si NO: **Alta fricción** - crear 30 invoices manualmente inviable
   - Si SÍ: Documentar usabilidad y validaciones previas

2. **¿Dashboard muestra KPIs relevantes?**
   - Saldo actual, pagos pendientes, pagos vencidos
   - Proyección flujo efectivo
   - Gráficas históricas

3. **¿Validaciones previenen errores contables?**
   - Montos negativos
   - Conceptos sin monto
   - Invoices duplicados mismo período

4. **¿Puede corregir errores después de generar?**
   - Cancelar invoices individuales
   - Cancelar ciclo completo
   - Re-generar con correcciones

5. **¿Integración con Property Accounts es clara?**
   - Relación Physical Space ↔ Property Account ↔ Sales Invoice
   - Usuario entiende flujo contable completo

---

## Journey 2: Registrar Pagos Recibidos (Planeado para Día 2+)

**Contexto:** Propietarios empiezan a pagar cuotas (transferencias bancarias)

**Pasos:** (TBD)

**Hipótesis fricción:**
- ¿Puede registrar pagos bulk (importar desde estado de cuenta)?
- ¿Conciliación automática payment → invoice?
- ¿Qué pasa con pagos parciales?

---

## Journey 3: Generar Reportes Contables (Planeado para Día 3+)

**Contexto:** Fin de mes, necesita reportes para asamblea de propietarios

**Pasos:** (TBD)

**Hipótesis fricción:**
- ¿Reportes estándar disponibles (Estado Resultados, Balance)?
- ¿Puede exportar a Excel/PDF?
- ¿Reportes cumplen normativa contable México?

---

**Actualizado:** 2025-10-18
**Estado:** Planificado - Pendiente ejecución en admin1.dev
**Próximo paso:** Ejecutar Journey 1 en entorno real y documentar resultados
