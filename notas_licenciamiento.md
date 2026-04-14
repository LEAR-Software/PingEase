# Notas - Licenciamiento (shareware + premium)

Fecha: 2026-04-13  
Proyecto: `WifiChannelOptimizer`

## Resumen ejecutivo

- Recomendacion principal: modelo **open core**.
- Mantener un nucleo base compatible con MIT y crear una **edicion Premium privativa** (EULA comercial).
- Evitar intentar cerrar retroactivamente versiones MIT ya publicadas.
- Evitar fork/copia de software privativo de terceros sin permiso explicito por escrito.

## Modelo comercial sugerido

### Planes

1. **Free / Shareware**
   - Trial por tiempo (7-14 dias) o features limitadas.
   - Objetivo: adopcion y validacion de mercado.

2. **Premium Personal**
   - 1 usuario, 1-3 dispositivos.
   - Incluye UI completa, automatizacion y actualizaciones menores.

3. **Premium Pro/Business** (opcional)
   - Multiples dispositivos/equipos.
   - Soporte prioritario, politicas de despliegue empresarial.

## Factibilidad

- Factibilidad tecnica: **alta** para Windows desktop + servicio.
- MVP comercial realista: **2 a 6 semanas** (segun alcance de UI y sistema de activacion).
- Dificultad estimada:
  - UI Windows: media
  - Servicio Windows: media
  - Licenciamiento robusto/antifraude: media-alta

## Arquitectura de licencias recomendada

### Enfoque hibrido (recomendado)

1. **Offline-first**
   - Archivo de licencia firmado criptograficamente (ej. Ed25519 o RSA).
   - Validacion local sin internet.

2. **Online opcional**
   - Activacion inicial y control de dispositivos.
   - Revocacion y reemision de licencias.
   - Heartbeat opcional + grace period (3-7 dias).

### Buenas practicas

- El codigo entregado al cliente debe mapear a licencia firmada, no a validaciones triviales.
- No prometer anti-pirateria total; objetivo realista: subir costo de abuso y mejorar conversion legitima.

## Riesgos y compliance

1. **Licencia MIT del proyecto base**
   - Mantener avisos/copyright requeridos.
   - No remover atribuciones exigidas.

2. **Dependencias de terceros**
   - Construir `THIRD_PARTY_LICENSES` y `NOTICE`.
   - Validar redistribucion de binarios/dependencias usadas en el instalador.

3. **Privativo de terceros**
   - No copiar codigo/assets sin permiso contractual.
   - Integrar por API/CLI/plugin cuando sea posible.

4. **Legal comercial**
   - Preparar `EULA`, `Privacy Policy`, `Terms of Sale`.
   - Validar texto final con abogado/licensing counsel.

## Proximos pasos (48h)

1. Definir estrategia final: open core vs cerrado total.
2. Definir planes y limites de cada tier (Free/Premium/Pro).
3. Especificar campos de licencia (cliente, plan, expiracion, dispositivos, firma).
4. Crear backlog MVP de licenciamiento y activacion.
5. Preparar documentos base: `EULA`, `NOTICE`, `THIRD_PARTY_LICENSES`.

## Decision sugerida hoy

- Avanzar con **open core + premium privativo** y activacion hibrida (offline firmado + online opcional).
- Esta via balancea rapidez de salida, menor riesgo legal y buena base para monetizacion en Windows.

e