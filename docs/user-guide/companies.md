# Companies - Guía de Usuario

Guía completa para gestionar condominios y contratos de servicio.

---

## ¿Qué son las Companies en el Sistema?

En el sistema de gestión de condominios, cada **Company** representa un condominio independiente con separación financiera completa. Esto permite que una administradora maneje múltiples condominios en una sola instalación.

### Conceptos Clave

**Company (ERPNext):**
- Representa un condominio individual
- Separación financiera completa
- Configuración contable independiente

**Condominium Information:**
- Información específica del condominio
- Vinculada a Company
- Datos legales y operacionales

**Service Management Contract:**
- Contrato entre administradora y condominio
- Define términos de servicio y fees
- Gestión de pagos y renovaciones

---

## Configuración Inicial de Condominio

### Paso 1: Crear Company (Condominio)

**Ir a:** Setup > Company > New

**Datos básicos:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Company Name | Nombre completo del condominio | Condominio Torres del Bosque |
| Abbr | Abreviación (max 5 caracteres) | TDB |
| Default Currency | Moneda | MXN |
| Country | País | Mexico |

**Datos fiscales:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Tax ID | RFC del condominio | TDB850315KL9 |
| Domain | Industria | Real Estate |

**Configuración contable:**

- Chart of Accounts: Standard (creado automáticamente)
- Default Bank Account: (crear después)
- Default Cash Account: (crear después)

**Guardar**

---

### Paso 2: Crear Condominium Information

**Ir a:** Condominium Management > Companies > Condominium Information > New

**Información básica:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Company | Seleccionar Company creada | Condominio Torres del Bosque |
| Legal Name | Razón social completa | Condominio Torres del Bosque A.C. |
| Short Name | Nombre corto | Torres del Bosque |

**Ubicación:**

| Campo | Ejemplo |
|-------|---------|
| Address | Av. Principal 123 |
| City | Ciudad de México |
| State | CDMX |
| Postal Code | 03100 |
| Phone | +52 55 1234 5678 |
| Email | admin@torresdelb osque.mx |

**Información legal:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Registration Number | Folio mercantil | 12345 |
| Constitution Date | Fecha constitución | 2020-01-15 |
| Legal Representative | Representante legal | Juan Pérez Gómez |

**Características del condominio:**

| Campo | Ejemplo |
|-------|---------|
| Total Units | 120 |
| Total Area (m²) | 15000.00 |
| Condominium Type | Vertical |
| Number of Towers | 3 |
| Number of Floors | 8 |

**Guardar**

---

### Paso 3: Crear Service Management Contract

**Ir a:** Condominium Management > Companies > Service Management Contract > New

**Partes del contrato:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Management Company | Administradora | Mi Administradora S.A. de C.V. |
| Managed Company | Condominio | Condominio Torres del Bosque |
| Contract Number | Número único | CONT-2025-001 |

**Vigencia:**

| Campo | Ejemplo |
|-------|---------|
| Start Date | 2025-01-01 |
| End Date | 2026-12-31 |
| Auto-renew | ✓ (opcional) |

**Términos financieros:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Management Fee Type | Tipo de fee | Percentage |
| Fee Percentage | % sobre ingresos | 8.00% |
| Fixed Monthly Fee | Fee fijo mensual | 0.00 (si es percentage) |
| Currency | Moneda | MXN |
| Payment Terms | Términos de pago | Net 15 |

**Servicios incluidos:**

Marcar los servicios que la administradora proporcionará:

- ✓ Accounting Services
- ✓ Legal Compliance
- ✓ Maintenance Coordination
- ✓ Collections Management
- ✓ Vendor Management
- ✓ Resident Communication
- ⬜ Security Services (opcional)
- ⬜ Cleaning Services (opcional)

**Guardar**

---

## Gestión de Contratos

### Renovación de Contrato

**Proceso manual:**

1. Ir a Service Management Contract existente
2. Usar función "Renew Contract" (si disponible)
3. O crear nuevo contrato con:
   - Mismo Management Company y Managed Company
   - Nuevo Contract Number
   - Nuevas fechas Start Date y End Date
   - Actualizar términos si hay cambios

**Auto-renovación:**

Si el campo "Auto-renew" está marcado:
- Sistema genera notificación 60 días antes de vencimiento
- Administrador confirma renovación
- Contrato se extiende automáticamente

---

### Modificación de Términos

**Casos comunes:**

#### 1. Cambio de Fee Percentage

**Escenario:** Incremento de 8% a 9% en renovación anual

**Proceso:**
1. Crear nuevo contrato con nueva fecha de inicio
2. Fee Percentage: 9.00%
3. Guardar
4. Marcar contrato anterior como "Terminado"

#### 2. Cambio de Servicios Incluidos

**Escenario:** Agregar Security Services al contrato

**Proceso:**
1. Editar contrato existente (si dentro de período de gracia)
2. O crear addendum/anexo al contrato
3. Marcar "Security Services"
4. Actualizar fee si aplica

#### 3. Terminación anticipada

**Escenario:** Condominio cambia de administradora

**Proceso:**
1. Ir a contrato activo
2. Cambiar Status a "Terminated"
3. Set End Date a fecha real de terminación
4. Documenten razón en Comments

---

## Multi-Company Operations

### Gestión de Múltiples Condominios

**Estructura recomendada:**

```
Administradora Principal (Management Company)
├── Condominio A
│   ├── Contrato Vigente
│   ├── 80 Unidades
│   └── Fee: 8%
├── Condominio B
│   ├── Contrato Vigente
│   ├── 120 Unidades
│   └── Fee: 7.5%
└── Condominio C
    ├── Contrato Vigente
    ├── 45 Unidades
    └── Fee: 9%
```

**Vista consolidada:**

**Ir a:** Service Management Contract > List View

**Filtros útiles:**
- Management Company: [Tu administradora]
- Status: Active
- Ordenar por: End Date (para ver próximos vencimientos)

---

### Reportes Multi-Company

#### Reporte 1: Contratos por Vencer

**Objetivo:** Identificar contratos que vencen en próximos 90 días

**Filtro:**
- Status: Active
- End Date: < (hoy + 90 días)

**Acción:** Iniciar proceso de renovación

---

#### Reporte 2: Ingresos por Management Fees

**Objetivo:** Proyectar ingresos mensuales de administración

**Proceso:**
1. Export Service Management Contract a Excel
2. Columnas relevantes:
   - Managed Company
   - Fee Percentage o Fixed Monthly Fee
   - Total Units (desde Condominium Information)
3. Calcular: Ingresos proyectados por condominio

---

#### Reporte 3: Comparativa de Servicios

**Objetivo:** Analizar qué servicios son más comunes

**Proceso:**
1. Export Service Management Contract
2. Analizar campos de servicios marcados
3. Identificar servicios con mayor demanda

---

## Master Data Sync Configuration

### ¿Qué es Master Data Sync?

Sistema para sincronizar datos maestros entre condominios contribuyentes y un receptor central.

**Casos de uso:**
- Condominios de la misma zona comparten catálogos de proveedores
- Administradora comparte templates de documentos
- Sincronización de categorías de gastos comunes

---

### Configurar Sincronización

**Ir a:** Condominium Management > Companies > Master Data Sync Configuration > New

**Configuración básica:**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Contributing Company | Condominio que aporta datos | Condominio Torre A |
| Receiving Company | Condominio/Matriz que recibe | Administradora Central |
| Sync Direction | Dirección | One-way (Contributing → Receiving) |

**DocTypes a sincronizar:**

Seleccionar qué tipos de documentos se sincronizan:

| DocType | Ejemplo de Uso |
|---------|----------------|
| Supplier | Catálogo de proveedores |
| Item | Catálogo de productos/servicios |
| Expense Category | Categorías de gastos |
| Cost Center | Centros de costo |

**Frecuencia de sincronización:**

| Campo | Opciones |
|-------|----------|
| Sync Frequency | Manual, Daily, Weekly, Real-time |
| Last Sync | (automático) |
| Next Sync | (calculado automáticamente) |

**Guardar**

---

### Ejecutar Sincronización

**Manual:**
1. Ir a Master Data Sync Configuration
2. Click en "Sync Now" (botón)
3. Verificar Last Sync actualizado
4. Revisar logs de sincronización

**Automática:**
- Se ejecuta según Sync Frequency configurada
- Revisar logs regularmente para detectar errores

---

## Casos de Uso Comunes

### Caso 1: Alta de Nuevo Condominio

**Escenario:** Administradora gana contrato de nuevo condominio

**Checklist:**

1. ✅ Crear Company (condominio)
   - Nombre, RFC, configuración fiscal
   - Chart of Accounts automático

2. ✅ Crear Condominium Information
   - Datos legales y ubicación
   - Características del condominio
   - Contactos principales

3. ✅ Crear Service Management Contract
   - Términos acordados con comité
   - Servicios incluidos
   - Fee structure

4. ✅ Configurar Physical Spaces
   - Estructura de torres/departamentos
   - Categorías de espacios
   - Componentes (si aplica)

5. ✅ Migrar datos existentes
   - Residentes (si módulo disponible)
   - Historial de mantenimiento
   - Proveedores recurrentes

6. ✅ Training a usuarios
   - Comité de administración
   - Personal operativo
   - Residentes (portal)

---

### Caso 2: Renovación Anual de Contratos

**Escenario:** 30 días antes de vencimiento de contrato

**Proceso:**

**Semana 1-2: Preparación**
1. Revisar performance del año anterior
2. Preparar propuesta de renovación
3. Evaluar ajuste de fees
4. Documentar mejoras realizadas

**Semana 3: Presentación a Comité**
1. Presentar resultados del año
2. Proponer términos de renovación
3. Negociar ajustes si hay desacuerdos
4. Obtener aprobación formal

**Semana 4: Formalización**
1. Crear nuevo Service Management Contract
2. Actualizar términos acordados
3. Enviar contrato para firma
4. Activar nuevo contrato
5. Archivar contrato anterior

---

### Caso 3: Cambio de Representante Legal

**Escenario:** Condominio elige nuevo presidente que es representante legal

**Proceso:**

1. Ir a Condominium Information del condominio
2. Actualizar campo "Legal Representative"
3. Guardar cambios
4. Actualizar Service Management Contract si requiere firma
5. Notificar a áreas contables/legales
6. Actualizar poderes notariales (fuera del sistema)

---

## Buenas Prácticas

### Naming Convention para Companies

**Formato recomendado:**

✅ **Bueno:**
- `Condominium [Nombre Descriptivo]`
- Ejemplos:
  - `Condominium Torres del Bosque`
  - `Condominium Privada Los Olivos`
  - `Condominium Residencial del Valle`

❌ **Evitar:**
- Nombres muy cortos: `TDB`, `Olivos`
- Sin prefijo: `Torres del Bosque` (confunde con clientes)
- Con abreviaturas inconsistentes

**Razón:** Claridad en reportes multi-company y facturación

---

### Abreviaciones (Abbr)

**Reglas:**
- Máximo 5 caracteres
- Solo letras mayúsculas
- Único en todo el sistema
- Memorable y relacionado con nombre

✅ **Buenos ejemplos:**
- Torres del Bosque → `TDB`
- Privada Los Olivos → `PLO`
- Residencial del Valle → `RDV`

❌ **Evitar:**
- Números: `CON01`, `A123`
- Caracteres especiales: `T&B`, `O.L.`
- Muy genéricos: `ABC`, `XYZ`

**Razón:** Abbr se usa en nombres de cuentas contables y transacciones

---

### Gestión de Contratos

**Mejores prácticas:**

1. **Numeración consistente:**
   - Formato: `CONT-YYYY-###`
   - Ejemplo: `CONT-2025-001`, `CONT-2025-002`

2. **Documentación completa:**
   - Guardar PDF firmado en attachments
   - Documentar términos especiales en Comments
   - Mantener histórico de enmiendas

3. **Alertas de vencimiento:**
   - Revisar contratos mensualmente
   - Iniciar renovación 60-90 días antes
   - Mantener comunicación con comités

4. **Validaciones:**
   - Verificar que Management Company ≠ Managed Company
   - Confirmar que End Date > Start Date
   - Validar que Fee Percentage o Fixed Fee están configurados

---

## Preguntas Frecuentes (FAQ)

### ¿Puedo tener el mismo condominio gestionado por dos administradoras?

No recomendado. El sistema permite separación por Company, pero tener dos contratos activos simultáneos genera conflictos.

**Alternativa:** Crear dos Companies separadas si el condominio está dividido legalmente.

---

### ¿Cómo manejo un cambio de administradora?

**Proceso:**
1. Terminar contrato actual:
   - Status: Terminated
   - End Date: Fecha real de cambio
2. Nueva administradora crea nuevo contrato
3. Transferir datos históricos (export/import)
4. Actualizar permisos y accesos

---

### ¿El sistema calcula automáticamente los management fees?

El módulo Companies gestiona los **términos del contrato**. El cálculo de fees se integra con módulo de Accounting.

**Flujo integrado (futuro):**
- Service Management Contract define % o cantidad fija
- Módulo Accounting genera invoices mensuales
- Basado en ingresos reales del condominio

---

### ¿Puedo tener diferentes fees para diferentes servicios?

El sistema actual maneja un fee global (percentage o fixed).

**Workaround para fees diferenciados:**
1. Crear múltiples contratos por tipo de servicio, O
2. Documentar breakdown de fees en Comments
3. Calcular manualmente distribución

**Desarrollo futuro:** Fee breakdown por servicio

---

## Integración con Otros Módulos

### Con Physical Spaces

**Relación:**
- Company (condominio) contiene múltiples Physical Spaces
- Vinculación automática por campo `company`
- Reportes de espacios por Company

**Uso:**
- Visualizar total de unidades por condominio
- Análisis de ocupación por Company
- Distribución de espacios comunes

---

### Con Accounting (ERPNext)

**Relación:**
- Cada Company tiene Chart of Accounts independiente
- Separación financiera completa
- Multi-company consolidation disponible

**Uso:**
- Facturación de cuotas de mantenimiento
- Pago de proveedores por Company
- Estados financieros por condominio
- Reportes consolidados de administradora

---

### Con Residents (Futuro)

**Integración planificada:**
- Residents vinculados a Company específica
- Directory de residentes por condominio
- Comunicaciones segmentadas por Company

---

## Recursos Adicionales

- **Arquitectura Técnica**: [Companies Architecture](../development/architecture/companies.md)
- **Guía de Administración**: [Configuration Guide](../admin-guide/configuration.md)
- **ERPNext Multi-Company**: [ERPNext Docs](https://docs.erpnext.com/docs/v13/user/manual/en/setting-up/articles/managing-multiple-companies)

---

**Actualizado:** 2025-10-17
**Para usuarios:** Administradores de condominios y personal administrativo
