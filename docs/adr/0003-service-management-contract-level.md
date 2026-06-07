# ADR-0003: Service Management Contract — DocType Nivel 1/2 (Domika↔Condominio)

**Fecha:** 2026-06-06
**Estado:** Aceptado
**Autor:** Luis Montanaro / Claude Code
**Contexto:** Auditoría Companies/Property Registry — Fase 3

---

## Contexto

`Service Management Contract` usa `client_condominium (Link → Company)` como campo de aislamiento, en lugar del campo convencional `company` que usan todos los DocTypes operativos del módulo Companies. Esta desviación fue detectada durante la auditoría y requería una decisión explícita.

En la arquitectura Domika, el sistema opera en tres niveles:
- **Nivel 1:** HQ / Domika (la empresa administradora)
- **Nivel 2:** Condominio cliente (la Company que representa el edificio)
- **Nivel 3:** Unidades y personas del condominio

---

## Decisión

`Service Management Contract` es un DocType de **Nivel 1/2**: modela el contrato entre Domika (administradora) y el condominio cliente. No es un DocType operativo interno del condominio.

Por tanto, usar `client_condominium` en lugar de `company` es correcto y no debe cambiarse. Este DocType representa la relación comercial entre empresas, no un documento de operación del condominio.

---

## Consecuencias

- `Service Management Contract` no debe seguir la convención de campo `company` que aplica a DocTypes operativos.
- Filtros automáticos de Frappe por `company` no aplican a este DocType — es intencional.
- Los informes y dashboards que filtran por `company` no deben incluir `Service Management Contract` como DocType operativo del condominio.
- Si en el futuro se necesita un contrato interno de servicios dentro de un condominio, se crea un DocType nuevo separado que sí sigue la convención `company`.

---

## Alternativas consideradas

**Renombrar a `company`:** haría que SMC se comporte como DocType operativo del condominio. Descartado — semánticamente incorrecto. SMC modela la relación entre dos companies (Domika y el cliente), no un documento interno del condominio.
