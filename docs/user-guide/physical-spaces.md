# Physical Spaces - Guía de Usuario

Guía completa para gestionar los espacios físicos de tu condominio.

---

## ¿Qué son los Physical Spaces?

Los Physical Spaces (Espacios Físicos) representan todas las ubicaciones dentro de tu condominio que necesitas administrar. Desde torres completas hasta departamentos individuales, estacionamientos, o áreas comunes.

### Características Principales

- **Jerarquía ilimitada**: Crea estructuras tan profundas como necesites
- **Categorización flexible**: Define tus propias categorías de espacios
- **Componentes personalizables**: Registra los componentes de cada espacio
- **Integración completa**: Vincula con residentes, mantenimiento, y accesos

---

## Configuración Inicial

### Paso 1: Crear Categorías de Espacios

Antes de crear espacios, define las categorías que usarás.

**Ir a:** Condominium Management > Physical Spaces > Space Category > New

**Categorías comunes:**

| Categoría | Descripción | Ejemplo de Uso |
|-----------|-------------|----------------|
| Torre | Edificios del condominio | Torre A, Torre B, Torre Norte |
| Piso | Niveles dentro de torres | Piso 1, Piso 2, Nivel PB |
| Departamento | Unidades habitacionales | Depto 101, Casa 5, Loft 201 |
| Estacionamiento | Espacios para vehículos | Cajón 15, Garage A-23 |
| Área Común | Espacios compartidos | Alberca, Gimnasio, Salón de Eventos |
| Bodega | Almacenamiento | Bodega 101, Storage A-5 |

**Ejemplo - Crear categoría "Torre":**

1. Nombre: `Torre`
2. Descripción: `Edificios principales del condominio`
3. Guardar

---

### Paso 2: Crear Tipos de Componentes

Define los componentes que pueden tener tus espacios.

**Ir a:** Condominium Management > Physical Spaces > Component Type > New

**Tipos comunes:**

| Tipo de Componente | Aplica a | Ejemplos |
|-------------------|----------|----------|
| Ventana | Departamentos | Ventana sala, Ventana recámara principal |
| Puerta | Todos | Puerta principal, Puerta de servicio |
| Instalación Eléctrica | Todos | Tablero principal, Contactos, Iluminación |
| Instalación Hidráulica | Todos | Tinaco, Calentador, Tuberías |
| Acabado | Todos | Pintura, Piso, Azulejo |
| Equipo | Áreas Comunes | Bomba alberca, Caminadora, Caldera |

**Ejemplo - Crear tipo "Ventana":**

1. Nombre: `Ventana`
2. Descripción: `Aberturas con cristal para iluminación y ventilación`
3. Requiere Mantenimiento: ✓ (opcional)
4. Guardar

---

## Crear Estructura de Espacios

### Ejemplo 1: Condominio Vertical (Torres y Departamentos)

**Estructura objetivo:**
```
Condominio Ejemplo
├── Torre A
│   ├── Piso 1
│   │   ├── Depto 101
│   │   ├── Depto 102
│   │   └── Depto 103
│   └── Piso 2
│       ├── Depto 201
│       └── Depto 202
└── Torre B
    └── Piso 1
        ├── Depto 101
        └── Depto 102
```

**Paso a paso:**

#### 1. Crear Torre A

**Ir a:** Physical Space > New

- **Nombre del Espacio**: `Torre A`
- **Categoría**: Torre
- **Espacio Superior**: (vacío - es el nivel más alto)
- **Estado**: Activo
- **Descripción**: `Edificio principal del condominio`
- **Guardar**

#### 2. Crear Piso 1 de Torre A

**Ir a:** Physical Space > New

- **Nombre del Espacio**: `Piso 1`
- **Categoría**: Piso
- **Espacio Superior**: Torre A
- **Estado**: Activo
- **Guardar**

#### 3. Crear Departamento 101

**Ir a:** Physical Space > New

- **Nombre del Espacio**: `Depto 101`
- **Categoría**: Departamento
- **Espacio Superior**: Torre A > Piso 1
- **Estado**: Activo
- **Área (m²)**: 85.50
- **Características Adicionales**:
  - Recámaras: 2
  - Baños: 1.5
  - Cajón de estacionamiento: A-15
- **Guardar**

#### 4. Agregar Componentes al Departamento 101

En el mismo formulario de Depto 101, sección **Componentes**:

**Agregar componente:**
- **Tipo de Componente**: Ventana
- **Nombre/Identificador**: Ventana Sala
- **Especificaciones**: `Ventana aluminio 2x1.5m, cristal templado`
- **Fecha Instalación**: 2023-01-15
- **Agregar fila**

**Repetir para:**
- Ventana Recámara Principal
- Ventana Recámara Secundaria
- Puerta Principal
- Puerta de Servicio
- Calentador de Agua

**Guardar** cambios

---

### Ejemplo 2: Condominio Horizontal (Casas)

**Estructura objetivo:**
```
Privada Los Olivos
├── Manzana 1
│   ├── Casa 1
│   ├── Casa 2
│   └── Casa 3
├── Manzana 2
│   ├── Casa 4
│   └── Casa 5
└── Áreas Comunes
    ├── Casa Club
    ├── Alberca
    └── Jardines
```

**Paso a paso:**

#### 1. Crear Manzana 1

- **Nombre del Espacio**: `Manzana 1`
- **Categoría**: Torre (reutilizar categoría o crear "Manzana")
- **Espacio Superior**: (vacío)
- **Guardar**

#### 2. Crear Casa 1

- **Nombre del Espacio**: `Casa 1`
- **Categoría**: Departamento (reutilizar o crear "Casa")
- **Espacio Superior**: Manzana 1
- **Área (m²)**: 120.00
- **Guardar**

#### 3. Crear Áreas Comunes

- **Nombre del Espacio**: `Casa Club`
- **Categoría**: Área Común
- **Espacio Superior**: Privada Los Olivos (opcional - puede ser raíz)
- **Guardar**

---

### Ejemplo 3: Estacionamientos

**Estructura objetivo:**
```
Estacionamientos
├── Sótano 1
│   ├── Cajón A-01
│   ├── Cajón A-02
│   └── ...
└── Sótano 2
    ├── Cajón B-01
    └── ...
```

**Crear Cajón de Estacionamiento:**

- **Nombre del Espacio**: `Cajón A-01`
- **Categoría**: Estacionamiento
- **Espacio Superior**: Sótano 1
- **Área (m²)**: 12.50
- **Características Adicionales**:
  - Número de cajón: A-01
  - Tipo: Cubierto
  - Asignado a: Depto 101
- **Guardar**

---

## Gestión de Componentes

### Agregar Componentes a un Espacio

Los componentes permiten registrar los elementos físicos de cada espacio para mantenimiento y seguimiento.

**Ir a:** Physical Space > [seleccionar espacio] > Editar

**Sección Componentes**, agregar filas:

#### Ejemplo: Departamento con Componentes Completos

| Tipo de Componente | Nombre/Identificador | Especificaciones | Fecha Instalación |
|-------------------|---------------------|------------------|-------------------|
| Ventana | Ventana Sala | Aluminio blanco 2x1.5m | 2023-01-15 |
| Ventana | Ventana Recámara 1 | Aluminio blanco 1.5x1.5m | 2023-01-15 |
| Puerta | Puerta Principal | Madera sólida, cerradura Yale | 2023-01-20 |
| Instalación Hidráulica | Calentador | Bosch 10L gas | 2023-02-01 |
| Instalación Eléctrica | Tablero Eléctrico | 12 circuitos, 220V | 2023-01-10 |
| Acabado | Piso Sala | Porcelanato gris 60x60cm | 2023-03-01 |

**Beneficios:**
- Histórico de componentes para mantenimiento
- Reporte de inventario de equipos
- Planificación de reemplazos
- Integración con módulo de Maintenance (futuro)

---

## Casos de Uso Comunes

### Caso 1: Buscar Todos los Departamentos de una Torre

**Ir a:** Physical Space > List View

**Filtros:**
- Espacio Superior: `Torre A`
- Categoría: `Departamento`

**Resultado:** Lista de todos los departamentos en Torre A

---

### Caso 2: Generar Reporte de Áreas por Torre

**Ir a:** Physical Space > List View

**Filtros:**
- Categoría: `Departamento`

**Exportar** a Excel

**Análisis:** Sumar áreas por Espacio Superior para totales por torre

---

### Caso 3: Identificar Espacios sin Componentes

**Ir a:** Physical Space > List View

**Usar filtro avanzado:**
- Categoría: `Departamento`
- (Verificar manualmente cuáles no tienen componentes registrados)

**Acción:** Actualizar espacios faltantes

---

## Buenas Prácticas

### Naming Convention (Convención de Nombres)

**Consistente y claro:**

✅ **Bueno:**
- `Torre A`, `Torre B`, `Torre C`
- `Piso 1`, `Piso 2`, `Piso 3`
- `Depto 101`, `Depto 102`, `Depto 103`

❌ **Evitar:**
- `Torre uno`, `2da torre`, `TORRE-C`
- `Primer piso`, `P2`, `3er nivel`
- `Dept 101`, `Depto. 102`, `#103`

### Jerarquía Clara

**Mantener estructura lógica:**

```
Nivel 1: Torre/Edificio
  Nivel 2: Piso/Nivel
    Nivel 3: Departamento/Casa
      Nivel 4: Habitación (opcional)
```

### Actualización Regular

**Mantener datos actualizados:**

- ✅ Registrar nuevos componentes instalados
- ✅ Actualizar estado de espacios (Activo, Mantenimiento, Fuera de Servicio)
- ✅ Documentar cambios estructurales
- ✅ Sincronizar con cambios de residentes

---

## Preguntas Frecuentes (FAQ)

### ¿Puedo cambiar un espacio de categoría después de crearlo?

Sí, pero con precaución. Cambiar la categoría puede afectar filtros y reportes existentes.

**Recomendación:** Verificar dependencias antes de cambiar.

---

### ¿Cuántos niveles de jerarquía puedo crear?

Ilimitados. El sistema soporta jerarquías tan profundas como necesites.

**Ejemplo extremo válido:**
```
Torre A > Piso 2 > Depto 201 > Recámara Principal > Clóset > Cajón Superior
```

---

### ¿Cómo elimino un espacio que ya no existe?

**Opción 1 (Recomendada):** Cambiar estado a "Inactivo" o "Fuera de Servicio"

**Opción 2:** Eliminar (solo si no tiene espacios hijos ni referencias)

**Proceso:**
1. Ir a Physical Space > [seleccionar espacio]
2. Verificar que no tenga espacios hijos
3. Eliminar (botón Delete)

---

### ¿Los espacios se pueden mover entre espacios superiores?

Sí, cambiando el campo "Espacio Superior".

**Ejemplo:** Mover "Depto 101" de "Torre A > Piso 1" a "Torre B > Piso 1"

**Advertencia:** Cambios afectan jerarquía completa y pueden impactar reportes.

---

## Integración con Otros Módulos

### Con Residents (Futuro)

- Asignar residentes a departamentos específicos
- Visualizar ocupación de espacios
- Contacto directo por espacio

### Con Maintenance (Futuro)

- Programar mantenimiento por componentes
- Histórico de mantenimientos por espacio
- Alertas de mantenimiento preventivo

### Con Access Control (Futuro)

- Permisos de acceso por espacio
- Generación de QR por departamento
- Registro de visitantes por espacio

---

## Recursos Adicionales

- **Arquitectura Técnica**: [Physical Spaces Architecture](../development/architecture/physical-spaces.md)
- **Guía de Administración**: [Configuration Guide](../admin-guide/configuration.md)
- **Soporte**: Contactar al administrador del sistema

---

**Actualizado:** 2025-10-17
**Para usuarios:** Administradores de condominios y personal operativo
