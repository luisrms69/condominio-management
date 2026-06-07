# ADR-0002: Política de catálogos — Maestros HQ vs extensión local

**Fecha:** 2026-06-06
**Estado:** Aceptado
**Autor:** Luis Montanaro / Claude Code
**Contexto:** Auditoría Companies/Property Registry — Fase 4

---

## Contexto

El módulo Companies define una serie de catálogos de referencia (tipos de uso, estados de propiedad, tipos de adquisición, etc.) que se instalan via fixtures. Estos catálogos no tienen campo `company` — aplican a toda la instalación. Se necesitaba una política explícita para saber cuándo un catálogo puede ser modificado por condominio y cuándo no.

---

## Decisión

Los catálogos sin campo `company` son **maestros HQ/globales**. Se instalan via fixtures de la app y aplican a todos los condominios sin excepción. No se modifican por condominio individual.

**Maestros HQ (no modificables por condominio):**

| Catálogo | Descripción |
|---|---|
| `Company Type` | Tipos de empresa (Condominio, Administradora, etc.) |
| `Acquisition Type` | Tipos de adquisición de propiedad |
| `Property Usage Type` | Tipos de uso (Residencial, Comercial, Mixto, etc.) |
| `Property Status Type` | Estados de propiedad (Activo, Inactivo, En Venta, etc.) |
| `Enforcement Level` | Niveles de enforcement |
| `Document Template Type` | Tipos de documento |
| `Jurisdiction Level` | Niveles jurisdiccionales |
| `Compliance Requirement Type` | Tipos de requisito legal |

**Maestros HQ con extensión local posible** (el condominio puede agregar registros propios, pero solo cuando sea explícitamente necesario):

| Catálogo | Razón |
|---|---|
| `Policy Category` | 19 categorías estándar; un condominio puede necesitar categorías propias |
| `Space Category` | 51 categorías base; un condominio puede necesitar categorías adicionales |

---

## Consecuencias

- Los fixtures de catálogos HQ se instalan en cada `bench migrate` y no se sobreescriben con datos locales.
- Si un condominio necesita variantes propias en el futuro, el catálogo migra a un modelo con campo `company` opcional (global = sin company, local = con company). Ese cambio requiere ADR nuevo.
- La extensión local en `Policy Category` y `Space Category` se hace agregando registros nuevos — nunca modificando los HQ existentes.
- Los comentarios en `hooks.py` § POLÍTICA DE CATÁLOGOS documentan esta regla inline.

---

## Alternativas consideradas

**Catálogos configurables por condominio desde el inicio:** cada catálogo con campo `company` opcional. Descartado por complejidad innecesaria — ningún condominio real ha solicitado variantes propias. El modelo puede evolucionar cuando haya caso concreto.
