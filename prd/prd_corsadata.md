# PRD — Director Hub PRO
### Product Requirements Document · SaaS Platform

> **Versión:** 1.0 · **Fecha:** Abril 2026 · **Estado:** BORRADOR  
> **Clasificación:** Confidencial · **Stack:** Next.js 14 + FastAPI + Supabase

---

## Índice

1. [Introducción y Contexto](#1-introducción-y-contexto)
2. [Objetivos del Producto](#2-objetivos-del-producto)
3. [Usuarios y Roles](#3-usuarios-y-roles)
4. [Arquitectura y Stack](#4-arquitectura-y-stack)
5. [Esquema de Base de Datos](#5-esquema-de-base-de-datos)
6. [Fases de Desarrollo](#6-fases-de-desarrollo)
   - [Fase 0 — Infraestructura Base](#fase-0--infraestructura-base)
   - [Fase 1 — Analizador GPX](#fase-1--analizador-gpx)
   - [Fase 2 — CRM de Ciclistas](#fase-2--crm-de-ciclistas)
   - [Fase 3 — Calendario y Carreras](#fase-3--calendario-y-carreras)
   - [Fase 4 — Dashboard de Rendimiento](#fase-4--dashboard-de-rendimiento)
   - [Fase 5 — Multi-tenant y SaaS](#fase-5--multi-tenant-y-saas)
7. [Requisitos No Funcionales](#7-requisitos-no-funcionales)
8. [Criterios Globales de Seguridad](#8-criterios-globales-de-seguridad)
9. [Convenciones y Definiciones](#9-convenciones-y-definiciones)

---

## 1. Introducción y Contexto

### 1.1 Visión del Producto

Director Hub PRO es una plataforma **SaaS B2B** para directores deportivos y equipos de ciclismo profesional. Integra análisis táctico de etapas GPX, gestión de plantilla y planificación competitiva en un único sistema con persistencia real, aislamiento multi-tenant y acceso desde cualquier dispositivo.

Parte de un prototipo funcional (monolito Flask) con análisis GPX, visualización Plotly, meteorología en tiempo real y roadbook táctico automatizado. La migración construye sobre ese núcleo sin perder ninguna funcionalidad.

### 1.2 Problema que Resuelve

Los directores deportivos trabajan actualmente con:
- Análisis de etapas en herramientas genéricas (RideWithGPS, Strava) sin capacidades tácticas.
- Plantilla gestionada en hojas de cálculo Excel no integradas con el análisis.
- Información meteorológica consultada manualmente, sin vinculación al perfil de la etapa.
- Roadbook táctico construido a mano sin datos de pavimento, índice de peligro ni waypoints exportables.
- Rendimiento de atletas disperso en Garmin, TrainingPeaks y sistemas propios.

### 1.3 Propuesta de Valor

- Análisis táctico automatizado con meteorología real, pendientes, pavimento e índice de peligro.
- Roadbook generado automáticamente, clasificado por prioridad táctica y exportable.
- CRM de atletas integrado con los análisis para personalizar por ciclista (peso, FTP).
- Multi-tenant con aislamiento total mediante RLS en PostgreSQL.
- Sin instalación: plataforma web accesible desde cualquier dispositivo.

### 1.4 Fuera de Alcance (v1.0)

- Integración nativa Garmin Connect / Strava API.
- Aplicación móvil nativa (iOS/Android).
- Transmisión de datos en tiempo real desde ciclistas durante carrera.
- Análisis de vídeo o IA generativa para scouting.
- Módulo financiero o gestión de nóminas.

---

## 2. Objetivos del Producto

### 2.1 Objetivos de Negocio

| ID | Prioridad | Objetivo | Métrica de Éxito |
|----|-----------|----------|-----------------|
| OBJ-01 | CRÍTICO | MVP demostrable (Fases 0–2) en 8 semanas | Primer equipo externo usando la plataforma |
| OBJ-02 | CRÍTICO | SaaS completo (Fases 0–5) en 15 semanas | 5 equipos suscritos al finalizar |
| OBJ-03 | ALTO | Retención de usuarios >80% al mes 3 | Tasa de uso semanal activa por equipo |
| OBJ-04 | ALTO | Tiempo de análisis GPX <90 segundos | P95 del pipeline completo |
| OBJ-05 | MEDIO | NPS >50 entre directores beta | Encuesta post-onboarding |
| OBJ-06 | MEDIO | MRR de €5.000 en mes 6 post-lanzamiento | Revenue por suscripciones |

### 2.2 Objetivos Técnicos

- Migrar monolito Flask → Next.js + FastAPI + Supabase sin pérdida de funcionalidad.
- Garantizar aislamiento de datos entre equipos mediante RLS en todas las tablas.
- Reemplazar el sistema de threading manual (Flask) por asyncio nativo (FastAPI).
- Persistir todos los datos en Supabase (DB + Storage), eliminando el estado en memoria.
- Cobertura de tests unitarios >70% en los servicios de análisis críticos.

---

## 3. Usuarios y Roles

### 3.1 Roles y Permisos

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `director` | Responsable táctico del equipo en carrera | Acceso total al equipo |
| `coach` | Coordinador de entrenamiento | Lectura + edición de rendimiento |
| `analyst` | Especialista en análisis de datos | Lectura + análisis de etapas |
| `rider` | Ciclista del equipo | Solo sus propios datos |

### 3.2 Jerarquía de Acceso

- Cada usuario pertenece a exactamente un `team_id`.
- Los datos de cada tabla se filtran automáticamente por `team_id` mediante RLS.
- No existe acceso cross-team bajo ninguna circunstancia.

---

## 4. Arquitectura y Stack

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND                                                   │
│  Next.js 14 (App Router) + TypeScript + Tailwind CSS       │
│  Plotly.js · shadcn/ui · Zustand · @supabase/ssr           │
│  Deploy: Vercel                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS / REST + SSE
┌───────────────────────────▼─────────────────────────────────┐
│  BACKEND                                                    │
│  FastAPI + Python 3.11 + uvicorn                           │
│  gpxpy · plotly · numpy · httpx · pydantic v2              │
│  Deploy: Railway                                            │
└──────────┬────────────────┬────────────────────────────────┘
           │                │
┌──────────▼──────┐  ┌──────▼──────────────────────────────┐
│   Supabase DB   │  │   Supabase Storage                  │
│   PostgreSQL    │  │   GPX files · PDF exports           │
│   + Auth + RLS  │  └─────────────────────────────────────┘
└─────────────────┘
```

### 4.1 Estructura de Carpetas

```
director-hub/
├── frontend/                    # Next.js app
│   ├── app/
│   │   ├── (auth)/login · register
│   │   ├── (dashboard)/
│   │   │   ├── stages/          # analizador GPX
│   │   │   ├── riders/          # CRM ciclistas
│   │   │   ├── races/           # calendario
│   │   │   └── performance/     # rendimiento
│   │   └── middleware.ts        # protección de rutas
│   ├── components/analysis · riders · ui/
│   ├── lib/supabase/ · api.ts
│   └── types/database.ts
├── backend/
│   ├── routers/analysis · stages · riders · races
│   ├── services/gpx_analyzer · weather · surface
│   ├── middleware/auth.py
│   ├── models/schemas.py
│   └── core/config.py
├── supabase/migrations/ · seed.sql
└── docker-compose.yml
```

---

## 5. Esquema de Base de Datos

> Todas las tablas tienen RLS activado con la política `team_isolation`.

```sql
teams         (id, name, slug, logo_url, created_at)
profiles      (id → auth.users, team_id, full_name, role, avatar_url)
riders        (id, team_id, full_name, birth_date, nationality,
               weight_kg, height_cm, ftp_w, ftp_wkg, vo2max,
               contract_end, status, notes, avatar_url)
stages        (id, team_id, name, race_name, stage_number,
               distance_km, d_pos_m, gpx_url, thumbnail_url, created_by)
stage_analyses(id, stage_id, team_id, analysis_date, start_hour,
               rider_weight_kg, ftp_wkg, analysis_json, fig_json,
               roadbook, stats)
waypoints     (id, analysis_id, team_id, name, type, km, lat, lon, alt)
performance_entries (id, rider_id, team_id, date, type,
               distance_km, duration_min, avg_power_w,
               normalized_power_w, tss, ftp_tested, notes)
races         (id, team_id, name, start_date, end_date,
               category, country, status)
race_entries  (id, race_id, rider_id, team_id, role, result)
```

**Política RLS base (aplica a todas las tablas):**
```sql
CREATE POLICY "team_isolation" ON <tabla>
  FOR ALL USING (
    team_id = (SELECT team_id FROM profiles WHERE id = auth.uid())
  );
```

---

## 6. Fases de Desarrollo

> **Convención de prioridades:** 🔴 CRÍTICO · 🟠 ALTO · 🟡 MEDIO · 🟢 BAJO

> **Cada fase tiene:**  
> - Subfases con requisitos funcionales detallados  
> - Checklist de testing funcional por subfase  
> - Test de seguridad obligatorio antes de avanzar a la siguiente fase

---

### FASE 0 — Infraestructura Base

**Duración estimada:** 2 semanas  
**Objetivo:** Cimientos de infraestructura. App vacía donde un usuario puede registrarse, hacer login y ver un dashboard en blanco.

---

#### 0.1 Supabase — Proyecto y Base de Datos

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F0.1-01 | 🔴 | Crear proyecto Supabase en entornos `dev` y `prod` separados |
| F0.1-02 | 🔴 | Ejecutar migrations SQL con el esquema completo de tablas |
| F0.1-03 | 🔴 | Activar RLS en todas las tablas con política `team_isolation` |
| F0.1-04 | 🔴 | Configurar Supabase Auth: email/password, magic link, OAuth Google |
| F0.1-05 | 🟠 | Crear datos de seed para entorno de desarrollo (`seed.sql`) |
| F0.1-06 | 🟠 | Configurar Supabase Storage: bucket `gpx-files` (privado) y `avatars` (público) |

**Checklist de testing — subfase 0.1:**

- [ ] Todas las tablas existen en el esquema público de Supabase.
- [ ] RLS activado: una consulta directa sin JWT devuelve 0 filas en cada tabla.
- [ ] Seed ejecutado sin errores; datos de prueba visibles en el dashboard de Supabase.
- [ ] Storage: buckets creados con políticas correctas (gpx-files privado, avatars público).
- [ ] Auth: registro con email funciona y envía email de verificación.

**🔒 Test de seguridad — subfase 0.1:**

- [ ] Consulta SQL directa (sin JWT) a `riders` devuelve `[]` → RLS activo.
- [ ] Usuario del equipo A no puede ver filas del equipo B (test con dos usuarios de seed).
- [ ] Bucket `gpx-files` devuelve 403 sin signed URL al intentar acceso público.
- [ ] Las claves `service_role` de Supabase NO están en variables de entorno del frontend.

---

#### 0.2 Next.js — Setup y Autenticación

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F0.2-01 | 🔴 | Setup Next.js 14 con TypeScript, Tailwind CSS y shadcn/ui |
| F0.2-02 | 🔴 | Configurar `@supabase/ssr` con cliente browser (`client.ts`) y servidor (`server.ts`) |
| F0.2-03 | 🔴 | Middleware Next.js en `middleware.ts`: protección de rutas `/dashboard/**` con JWT |
| F0.2-04 | 🔴 | Página `/login`: formulario email + password, enlace magic link, botón Google OAuth |
| F0.2-05 | 🔴 | Página `/register`: formulario con nombre, email, contraseña; email de verificación |
| F0.2-06 | 🔴 | Página `/dashboard`: placeholder autenticado con topbar y sidebar |
| F0.2-07 | 🟠 | Página `/forgot-password`: flujo de reset por email |
| F0.2-08 | 🟠 | Redirección automática: usuario autenticado en `/login` → `/dashboard` |
| F0.2-09 | 🟠 | Persistencia de sesión: al recargar el dashboard, el usuario sigue autenticado (SSR sin flicker) |

**Checklist de testing — subfase 0.2:**

- [ ] Acceder a `/dashboard` sin estar autenticado redirige a `/login`.
- [ ] Registro con email inválido muestra error de validación.
- [ ] Registro con email válido envía email de verificación; antes de confirmar no puede hacer login.
- [ ] Login correcto redirige a `/dashboard`.
- [ ] Google OAuth completa el flujo y crea perfil en la tabla `profiles`.
- [ ] Magic link llega en <5 segundos y permite login en un clic.
- [ ] Al recargar `/dashboard` con sesión activa, el usuario permanece logueado (sin flicker).
- [ ] Logout elimina la cookie y redirige a `/login`.

**🔒 Test de seguridad — subfase 0.2:**

- [ ] JWT almacenado en cookie `httpOnly`, `SameSite=Strict`, `Secure`. No accesible desde `document.cookie`.
- [ ] Manipular manualmente la cookie con un JWT forjado devuelve 401/redirect.
- [ ] 10 intentos de login fallido desde la misma IP activan rate limiting de Supabase Auth (bloqueo temporal).
- [ ] Ruta `/dashboard` responde 307 redirect (no 200) cuando el JWT es inválido o ha expirado.
- [ ] Headers de respuesta incluyen `X-Frame-Options: DENY` y `X-Content-Type-Options: nosniff`.

---

#### 0.3 FastAPI — Setup y Middleware JWT

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F0.3-01 | 🔴 | Setup FastAPI + uvicorn con estructura de carpetas (`routers/`, `services/`, `middleware/`, `models/`) |
| F0.3-02 | 🔴 | Middleware de verificación JWT de Supabase en todos los endpoints protegidos (`python-jose`) |
| F0.3-03 | 🔴 | Endpoint `GET /health` público que devuelve `{"status": "ok"}` |
| F0.3-04 | 🔴 | CORS configurado para aceptar solo el dominio del frontend (Vercel URL + localhost) |
| F0.3-05 | 🟠 | Documentación OpenAPI disponible en `/docs` (solo en entorno `dev`) |
| F0.3-06 | 🟠 | Variables de entorno cargadas con `python-dotenv`; fichero `.env.example` documentado |
| F0.3-07 | 🟡 | Logs estructurados en JSON con nivel `INFO` en producción, `DEBUG` en dev |

**Checklist de testing — subfase 0.3:**

- [ ] `GET /health` devuelve 200 `{"status": "ok"}`.
- [ ] `GET /docs` disponible en dev; devuelve 404 en producción.
- [ ] Request a endpoint protegido sin `Authorization: Bearer <token>` devuelve 401.
- [ ] Request con JWT de otro proyecto Supabase (JWKS diferente) devuelve 401.
- [ ] CORS: request desde dominio no autorizado devuelve 403.

**🔒 Test de seguridad — subfase 0.3:**

- [ ] JWT expirado (modificar `exp` en payload) devuelve 401.
- [ ] JWT con firma alterada devuelve 401.
- [ ] `SUPABASE_SERVICE_KEY` y `SUPABASE_JWT_SECRET` nunca aparecen en logs ni en respuestas de error.
- [ ] `/docs` devuelve 404 en producción (variable `ENV=production`).
- [ ] CORS no permite `*`; cabecera `Access-Control-Allow-Origin` es exactamente el dominio del frontend.

---

#### 0.4 CI/CD y Docker

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F0.4-01 | 🟠 | GitHub Actions: lint + typecheck en cada PR (frontend: `eslint`, `tsc`; backend: `ruff`, `mypy`) |
| F0.4-02 | 🟠 | `docker-compose.yml` para desarrollo local: backend + Supabase local |
| F0.4-03 | 🟡 | Variables de entorno de producción configuradas en Railway (backend) y Vercel (frontend) |

**Checklist de testing — subfase 0.4:**

- [ ] `docker-compose up` levanta el backend y el Supabase local sin errores.
- [ ] CI pipeline pasa en verde en un PR limpio.
- [ ] CI falla correctamente al introducir un error de tipos en TypeScript.

**🔒 Test de seguridad — subfase 0.4:**

- [ ] El fichero `.env` NO está en el repositorio (`.gitignore` configurado).
- [ ] `.env.example` no contiene valores reales, solo placeholders.
- [ ] Secrets de Railway/Vercel no visibles en los logs del pipeline de CI.

---

#### ✅ Gate de Seguridad — Fase 0

> **Obligatorio superar TODOS los puntos antes de iniciar la Fase 1.**

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS0-01 | RLS test: usuario A no ve datos de equipo B | 0 filas devueltas |
| GS0-02 | JWT forjado en frontend devuelve 401 en FastAPI | HTTP 401 |
| GS0-03 | Cookie JWT es `httpOnly` y no accesible desde JS | `document.cookie` no la contiene |
| GS0-04 | `/docs` FastAPI no accesible en producción | HTTP 404 |
| GS0-05 | Ninguna clave secreta en variables de entorno del frontend | Audit de `NEXT_PUBLIC_*` vars |
| GS0-06 | `.env` no en repositorio Git | `git log --all -- .env` vacío |
| GS0-07 | Supabase Storage `gpx-files` no accesible públicamente | HTTP 403 sin signed URL |

---

### FASE 1 — Analizador GPX

**Duración estimada:** 3 semanas  
**Objetivo:** El Director Hub actual funcionando dentro del nuevo stack con persistencia real en Supabase.  
**Prerequisito:** Fase 0 completada y Gate de Seguridad GS0 superado.

---

#### 1.1 Pipeline de Análisis (FastAPI)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F1.1-01 | 🔴 | Migrar `analyze_gpx()` a `services/gpx_analyzer.py` con tests unitarios |
| F1.1-02 | 🔴 | Reescribir `Hub` con `asyncio.Queue` y `asyncio.create_task` (eliminar `threading.Thread`) |
| F1.1-03 | 🔴 | SSE reescrito con `StreamingResponse` en FastAPI: eventos `job_update`, `analysis_ready`, `error` |
| F1.1-04 | 🔴 | `POST /api/analysis/upload`: acepta GPX (máx 50MB), lo sube a Supabase Storage y lanza job |
| F1.1-05 | 🔴 | `GET /api/analysis/sse/{stage_id}`: stream SSE de progreso del job |
| F1.1-06 | 🔴 | `GET /api/analysis/data/{stage_id}`: devuelve `analysis_json` y `stats` desde Supabase |
| F1.1-07 | 🔴 | `GET /api/analysis/fig/{stage_id}`: devuelve `fig_json` (figura Plotly) desde Supabase |
| F1.1-08 | 🔴 | Persistir resultado completo en tabla `stage_analyses` antes de emitir `analysis_ready` |
| F1.1-09 | 🟠 | Migrar `services/weather.py` (Tomorrow.io + fallback Open-Meteo) con degradación graciosa |
| F1.1-10 | 🟠 | Migrar `services/surface.py` (OpenRouteService) con degradación graciosa (fallback `asphalt`) |
| F1.1-11 | 🟠 | Timeout de 30 segundos en el parsing de GPX para protección contra archivos maliciosos |
| F1.1-12 | 🟡 | Rate limiting: máximo 20 análisis por hora por `team_id` |

**Checklist de testing — subfase 1.1:**

- [ ] Upload de GPX válido (600 puntos) completa análisis en <90 segundos.
- [ ] SSE envía al menos 5 eventos de progreso durante el análisis.
- [ ] Tras `analysis_ready`, `GET /api/analysis/data/{id}` devuelve JSON con `roadbook`, `stats`, `dists`, `alts`.
- [ ] Análisis persiste en Supabase: visible en tabla `stage_analyses` tras cerrar el job.
- [ ] Análisis con Tomorrow.io no disponible (mock) completa usando Open-Meteo.
- [ ] Análisis con ORS no disponible (mock) completa asumiendo `surface='asphalt'`.
- [ ] GPX con menos de 10 puntos devuelve error `{"error": "GPX < 10 puntos"}`.
- [ ] GPX de 50MB se procesa (o rechaza limpiamente si excede el límite).
- [ ] Con asyncio: 3 análisis lanzados simultáneamente completan sin errores ni race conditions.

**🔒 Test de seguridad — subfase 1.1:**

- [ ] Subir un archivo GPX manipulado con XML bomb (entidad recursiva) no bloquea el proceso.
- [ ] GPX con coordenadas extremas (lat/lon fuera de rango) no provoca crash; devuelve error controlado.
- [ ] URL del fichero en Supabase Storage solo accesible con signed URL (1h expiración); URL directa devuelve 403.
- [ ] Endpoint `POST /api/analysis/upload` devuelve 401 sin JWT válido.
- [ ] Con rate limiting activo: el 21º análisis en 1h devuelve 429 con mensaje claro.
- [ ] Las claves de Tomorrow.io, ORS y Google Maps no aparecen en ninguna respuesta de la API ni logs de frontend.

---

#### 1.2 Librería de Etapas (FastAPI + Supabase)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F1.2-01 | 🔴 | `GET /api/stages`: listado de etapas del equipo desde tabla `stages` |
| F1.2-02 | 🔴 | `POST /api/stages/save`: guarda metadatos + GPX en Supabase (reemplaza `tracks_library/`) |
| F1.2-03 | 🔴 | `POST /api/stages/{id}/analyze`: lanza análisis usando el GPX almacenado en Storage |
| F1.2-04 | 🟠 | `DELETE /api/stages/{id}`: elimina registro en DB y fichero en Storage |
| F1.2-05 | 🟠 | Auto-guardado: tras análisis con GPX nuevo, guardarlo automáticamente en la librería del equipo |

**Checklist de testing — subfase 1.2:**

- [ ] `GET /api/stages` devuelve solo las etapas del team del usuario autenticado.
- [ ] `POST /api/stages/save` persiste el GPX en Storage y los metadatos en `stages`.
- [ ] Tras DELETE, el fichero GPX en Storage ya no existe (signed URL da 404).
- [ ] Equipo B no puede acceder ni borrar etapas del Equipo A.
- [ ] Auto-guardado: tras analizar un nuevo GPX, aparece en el listado de etapas.

**🔒 Test de seguridad — subfase 1.2:**

- [ ] `DELETE /api/stages/{id}` con `id` de otro equipo devuelve 403 o 404 (no 200).
- [ ] `POST /api/stages/{id}/analyze` con `id` de otro equipo devuelve 403.
- [ ] Inyección en el nombre de la etapa (e.g. `<script>alert(1)</script>`) es escapada al renderizar.

---

#### 1.3 Waypoints (FastAPI + Supabase)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F1.3-01 | 🔴 | `POST /api/waypoints`: persiste waypoint en tabla `waypoints` vinculado al `analysis_id` |
| F1.3-02 | 🔴 | `DELETE /api/waypoints/{id}`: elimina waypoint del equipo autenticado |
| F1.3-03 | 🟠 | `GET /api/waypoints/{analysis_id}`: listado de waypoints de un análisis |
| F1.3-04 | 🟠 | `GET /api/analysis/{id}/export/gpx`: genera fichero GPX con todos los waypoints del análisis |
| F1.3-05 | 🟡 | `GET /api/analysis/{id}/export/pdf`: genera informe PDF con estadísticas y roadbook |

**Checklist de testing — subfase 1.3:**

- [ ] Añadir waypoint y recargar la página lo muestra correctamente (persistencia real).
- [ ] DELETE de waypoint propio devuelve 200 y desaparece del listado.
- [ ] Export GPX contiene todos los waypoints en formato válido (parseable por Garmin/Wahoo).
- [ ] Export PDF contiene la tabla del roadbook con todos los eventos.

**🔒 Test de seguridad — subfase 1.3:**

- [ ] `DELETE /api/waypoints/{id}` con `id` de waypoint de otro equipo devuelve 403.
- [ ] `GET /api/waypoints/{analysis_id}` con `analysis_id` de otro equipo devuelve `[]`.

---

#### 1.4 Frontend Next.js — Componentes del Analizador

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F1.4-01 | 🔴 | Migrar `index.html` completo a componentes React con TypeScript |
| F1.4-02 | 🔴 | `<ProfileChart />`: Plotly bar chart VeloViewer con 6 tabs de coloración |
| F1.4-03 | 🔴 | `<StageLibrary />`: sidebar con etapas del equipo desde API |
| F1.4-04 | 🔴 | `<RoadbookPanel />`: panel lateral con eventos tácticos del roadbook |
| F1.4-05 | 🔴 | `<MapView />`: Google Maps con trayecto + Street View + marcador de posición sincronizado |
| F1.4-06 | 🔴 | Estado global migrado de objeto `S{}` a Zustand store |
| F1.4-07 | 🟠 | Indicador de progreso SSE en tiempo real durante el análisis |
| F1.4-08 | 🟠 | Panel de waypoints: añadir, ver y eliminar; sincronizado con Supabase |
| F1.4-09 | 🟠 | Botones de exportación GPX y PDF funcionales |
| F1.4-10 | 🟡 | Tipos TypeScript generados automáticamente desde esquema Supabase (`supabase gen types`) |

**Checklist de testing — subfase 1.4:**

- [ ] Flujo completo: subir GPX → ver progreso SSE → ver perfil → ver roadbook → ver mapa.
- [ ] Hover sobre el perfil mueve el marcador en Google Maps y actualiza Street View.
- [ ] Los 6 tabs de coloración cambian los colores del perfil correctamente.
- [ ] Añadir un waypoint en el perfil lo persiste y aparece tras recargar.
- [ ] Dashboard funcionalmente idéntico al prototipo Flask original.
- [ ] TypeScript: `npm run build` sin errores de tipos.

**🔒 Test de seguridad — subfase 1.4:**

- [ ] Las variables `NEXT_PUBLIC_*` no contienen `SUPABASE_SERVICE_KEY`, `TOMORROW_IO_KEY`, `ORS_KEY`.
- [ ] El token JWT nunca se loguea en `console.log` ni aparece en Network requests al backend (solo en headers `Authorization`).
- [ ] Zustand store no persiste datos sensibles en `localStorage` (solo memoria de sesión).

---

#### ✅ Gate de Seguridad — Fase 1

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS1-01 | Acceso a análisis de otro equipo via API | HTTP 403 o 404 |
| GS1-02 | XML bomb en GPX | Error controlado, proceso no bloqueado |
| GS1-03 | 21 análisis en 1h desde mismo team | HTTP 429 en el 21º |
| GS1-04 | URL directa a fichero GPX en Storage | HTTP 403 sin signed URL |
| GS1-05 | Claves API externas en respuesta del frontend | No presentes en Network tab |
| GS1-06 | JWT en `console.log` del frontend | No presente |
| GS1-07 | Delete waypoint de otro equipo | HTTP 403 |
| GS1-08 | XSS en nombre de etapa | Texto escapado, sin ejecución de script |

---

### FASE 2 — CRM de Ciclistas

**Duración estimada:** 3 semanas  
**Objetivo:** Gestión completa del roster del equipo con vinculación a análisis de etapas.  
**Prerequisito:** Fase 1 completada y Gate de Seguridad GS1 superado.

---

#### 2.1 API de Ciclistas (FastAPI)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F2.1-01 | 🔴 | `GET /api/riders`: listado del equipo con filtros opcionales (`status`, `role`, `nationality`) |
| F2.1-02 | 🔴 | `POST /api/riders`: crear ciclista con validación Pydantic de todos los campos |
| F2.1-03 | 🔴 | `GET /api/riders/{id}`: ficha completa del ciclista |
| F2.1-04 | 🔴 | `PATCH /api/riders/{id}`: actualización parcial de campos |
| F2.1-05 | 🔴 | `DELETE /api/riders/{id}`: archivado lógico (status = `inactive`), no borrado físico |
| F2.1-06 | 🟠 | `POST /api/riders/{id}/avatar`: subir foto a Supabase Storage bucket `avatars` |
| F2.1-07 | 🟠 | `GET /api/riders/{id}/analyses`: listado de análisis vinculados al ciclista |
| F2.1-08 | 🟠 | `POST /api/riders/{id}/ftp-entry`: registrar nuevo valor de FTP con fecha |

**Checklist de testing — subfase 2.1:**

- [ ] CRUD completo: crear → leer → editar → archivar un ciclista.
- [ ] Filtros: `GET /api/riders?status=active&nationality=ES` devuelve solo los coincidentes.
- [ ] Avatar: subida de imagen JPG/PNG ≤5MB; rechazo de PDF.
- [ ] `GET /api/riders/{id}` de ciclista de otro equipo devuelve 404.
- [ ] Histórico FTP: `GET /api/riders/{id}` incluye todos los valores de FTP ordenados por fecha.
- [ ] `DELETE` no borra físicamente: el registro existe con `status='inactive'`.

**🔒 Test de seguridad — subfase 2.1:**

- [ ] `PATCH /api/riders/{id}` con `id` de otro equipo devuelve 403.
- [ ] Avatar: subir un SVG con contenido malicioso es rechazado (solo `image/jpeg`, `image/png`, `image/webp`).
- [ ] `POST /api/riders` con campos extra desconocidos (ej. `team_id` hardcodeado) ignora el campo; usa el `team_id` del JWT.
- [ ] SQL injection en campo `nationality` es neutralizada por Pydantic + ORM paramétrico.

---

#### 2.2 Vinculación Ciclista ↔ Análisis

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F2.2-01 | 🔴 | Al lanzar análisis, campo opcional `rider_id` vincula el análisis al ciclista |
| F2.2-02 | 🔴 | Si `rider_id` está presente, `rider_weight_kg` y `ftp_wkg` se cargan automáticamente desde la ficha |
| F2.2-03 | 🟠 | `PATCH /api/analysis/{id}`: permite actualizar el `rider_id` de un análisis existente |
| F2.2-04 | 🟠 | La ficha del ciclista muestra todos sus análisis asociados con enlace directo |

**Checklist de testing — subfase 2.2:**

- [ ] Seleccionar ciclista en el formulario de análisis carga peso y FTP correctamente.
- [ ] El análisis aparece en la ficha del ciclista seleccionado.
- [ ] Cambiar el `rider_id` de un análisis actualiza la asociación en ambas fichas.

---

#### 2.3 Frontend — CRM de Ciclistas

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F2.3-01 | 🔴 | Página `/riders`: tabla/grid del roster completo con filtros y búsqueda |
| F2.3-02 | 🔴 | Página `/riders/[id]`: ficha de ciclista con todos los datos y gráfica de evolución FTP |
| F2.3-03 | 🔴 | `<RiderForm />`: formulario de creación/edición con validación client-side |
| F2.3-04 | 🟠 | `<RiderCard />`: tarjeta en el roster con avatar, nombre, estado y métricas clave |
| F2.3-05 | 🟠 | Gráfica de evolución de FTP (Recharts) en la ficha del ciclista |
| F2.3-06 | 🟠 | Campo de notas con guardado automático al perder foco (debounce 1s) |
| F2.3-07 | 🟠 | Selector de ciclista en el formulario de análisis (carga peso/FTP automáticamente) |
| F2.3-08 | 🟡 | Badge de alerta en ficha si `contract_end` < 90 días |

**Checklist de testing — subfase 2.3:**

- [ ] Crear ciclista desde la UI y verlo en el roster sin recargar.
- [ ] Filtrar por `status=injured` muestra solo los lesionados.
- [ ] Ficha de ciclista muestra gráfica de FTP con al menos 2 puntos.
- [ ] Notas guardadas automáticamente (verificar en Supabase tras 1 segundo sin escribir).
- [ ] Badge de alerta visible si el contrato vence en <90 días.
- [ ] TypeScript: `npm run build` sin errores.

**🔒 Test de seguridad — subfase 2.3:**

- [ ] XSS en campo `full_name` del ciclista: el nombre se renderiza como texto, no como HTML.
- [ ] La URL `/riders/[id]` de un ciclista de otro equipo devuelve 404, no la ficha.
- [ ] El formulario de edición no permite modificar el `team_id` del ciclista.

---

#### ✅ Gate de Seguridad — Fase 2

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS2-01 | `GET /api/riders/{id}` de otro equipo | HTTP 404 |
| GS2-02 | `PATCH /api/riders/{id}` de otro equipo | HTTP 403 |
| GS2-03 | `POST /api/riders` con `team_id` hardcodeado en body | Campo ignorado; usa team_id del JWT |
| GS2-04 | XSS en nombre de ciclista | Texto escapado en UI |
| GS2-05 | Subir SVG como avatar | HTTP 422 (tipo no permitido) |
| GS2-06 | URL `/riders/[id]` de otro equipo en frontend | Página 404, sin datos |

---

### FASE 3 — Calendario y Carreras

**Duración estimada:** 2 semanas  
**Objetivo:** Gestión del calendario competitivo con vinculación de ciclistas y análisis de etapas.  
**Prerequisito:** Fase 2 completada y Gate de Seguridad GS2 superado.

---

#### 3.1 API de Carreras (FastAPI)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F3.1-01 | 🔴 | CRUD completo: `GET/POST/PATCH/DELETE /api/races` |
| F3.1-02 | 🔴 | `GET /api/races?status=upcoming`: filtro por estado |
| F3.1-03 | 🟠 | `POST /api/races/{id}/entries`: asignar ciclista a una carrera con su rol táctico |
| F3.1-04 | 🟠 | `DELETE /api/races/{id}/entries/{entry_id}`: desasignar ciclista |
| F3.1-05 | 🟠 | `GET /api/races/{id}/stages`: listado de etapas analizadas vinculadas a la carrera |
| F3.1-06 | 🟠 | `POST /api/races/{id}/stages/{stage_id}`: vincular etapa analizada a una carrera |
| F3.1-07 | 🟡 | `PATCH /api/races/{id}/entries/{entry_id}/result`: registrar resultado post-carrera |

**Checklist de testing — subfase 3.1:**

- [ ] CRUD completo de carrera sin errores.
- [ ] Asignar un ciclista a una carrera con rol `leader`; aparece en `GET /api/races/{id}/entries`.
- [ ] Vincular una etapa analizada a la carrera; aparece en `GET /api/races/{id}/stages`.
- [ ] Carrera de otro equipo no accesible.

**🔒 Test de seguridad — subfase 3.1:**

- [ ] `POST /api/races/{id}/entries` con `race_id` de otro equipo devuelve 403.
- [ ] `POST /api/races/{id}/stages/{stage_id}` con `stage_id` de otro equipo devuelve 403.

---

#### 3.2 Frontend — Calendario y Preparación de Carrera

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F3.2-01 | 🟠 | Página `/races`: calendario visual mensual con carreras del equipo |
| F3.2-02 | 🟠 | Formulario de creación/edición de carrera |
| F3.2-03 | 🟠 | Página `/races/[id]`: vista de preparación — ciclistas convocados + etapas analizadas |
| F3.2-04 | 🟠 | Asignación de ciclistas a la carrera con selector de rol |
| F3.2-05 | 🟡 | Registro de resultados post-carrera por ciclista |

**Checklist de testing — subfase 3.2:**

- [ ] Carrera creada aparece en el calendario en la fecha correcta.
- [ ] Vista de preparación muestra los ciclistas convocados y sus roles.
- [ ] Vista de preparación muestra las etapas analizadas con enlace al análisis.
- [ ] Resultado post-carrera guardado aparece en la ficha del ciclista.

---

#### ✅ Gate de Seguridad — Fase 3

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS3-01 | Carrera de otro equipo via API | HTTP 403/404 |
| GS3-02 | Vincular etapa de otro equipo a carrera propia | HTTP 403 |
| GS3-03 | XSS en nombre de carrera | Texto escapado |

---

### FASE 4 — Dashboard de Rendimiento

**Duración estimada:** 3 semanas  
**Objetivo:** Centro de mando con KPIs del equipo, evolución de rendimiento y alertas.  
**Prerequisito:** Fase 3 completada y Gate de Seguridad GS3 superado.

---

#### 4.1 API de Rendimiento (FastAPI)

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F4.1-01 | 🟠 | `GET/POST /api/performance`: listado y creación de entradas de rendimiento |
| F4.1-02 | 🟠 | `GET /api/performance?rider_id={id}&from={date}&to={date}`: histórico filtrado |
| F4.1-03 | 🟠 | `POST /api/performance/import`: importación desde CSV con validación fila a fila |
| F4.1-04 | 🟠 | `GET /api/dashboard/kpis`: resumen del equipo (activos/lesionados, próximas carreras, alertas) |
| F4.1-05 | 🟡 | `GET /api/dashboard/alerts`: alertas activas (FTP >30 días sin actualizar, contratos próximos) |

**Checklist de testing — subfase 4.1:**

- [ ] Crear entrada de rendimiento manual; aparece en histórico del ciclista.
- [ ] Import CSV con 50 filas: 48 correctas + 2 erróneas → devuelve resumen de errores por fila.
- [ ] `GET /api/dashboard/kpis` devuelve los números correctos según los datos de seed.
- [ ] Alerta generada si un ciclista no tiene FTP registrado en los últimos 30 días.

**🔒 Test de seguridad — subfase 4.1:**

- [ ] Import CSV: fichero con fórmulas Excel (`=CMD`, `=HYPERLINK`) es tratado como texto puro.
- [ ] Import CSV: más de 10.000 filas es rechazado con 422 (límite de importación).
- [ ] `GET /api/performance?rider_id={id}` con `rider_id` de otro equipo devuelve `[]`.

---

#### 4.2 Frontend — Dashboard y Gráficas

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F4.2-01 | 🟠 | Dashboard home `/dashboard`: KPIs del equipo (ciclistas activos/lesionados, próximas carreras, alertas) |
| F4.2-02 | 🟠 | Gráficas de evolución por ciclista en la ficha: FTP, TSS, potencia media (Recharts) |
| F4.2-03 | 🟠 | Página `/performance`: comparativa multi-ciclista (hasta 4) con selector |
| F4.2-04 | 🟠 | Alertas in-app visibles en el dashboard (FTP desactualizado, contratos próximos) |
| F4.2-05 | 🟡 | Importación CSV desde la UI con feedback de errores por fila |

**Checklist de testing — subfase 4.2:**

- [ ] Dashboard carga KPIs correctos sin errores de consola.
- [ ] Gráfica de evolución FTP muestra los puntos ordenados cronológicamente.
- [ ] Comparativa: seleccionar 4 ciclistas muestra 4 series en la misma gráfica.
- [ ] Alerta de FTP desactualizado visible en el dashboard de prueba.

---

#### ✅ Gate de Seguridad — Fase 4

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS4-01 | CSV con fórmulas Excel en import | Tratado como texto, sin ejecución |
| GS4-02 | `GET /api/performance?rider_id` de otro equipo | `[]` vacío |
| GS4-03 | Import de >10.000 filas | HTTP 422 |
| GS4-04 | Dashboard KPIs de otro equipo | HTTP 403/404 |

---

### FASE 5 — Multi-tenant y SaaS

**Duración estimada:** 2 semanas  
**Objetivo:** Plataforma lista para múltiples equipos como clientes independientes.  
**Prerequisito:** Fase 4 completada y Gate de Seguridad GS4 superado.

---

#### 5.1 Onboarding y Gestión de Equipos

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F5.1-01 | 🔴 | Wizard de onboarding para nuevo equipo: nombre, slug, logo, importar ciclistas CSV (opcional) |
| F5.1-02 | 🔴 | Sistema de invitaciones por email: envío de link con token de invitación (72h de validez) |
| F5.1-03 | 🔴 | Aceptar invitación: el invitado crea cuenta y queda vinculado al equipo |
| F5.1-04 | 🟠 | Gestión de miembros del equipo: ver, cambiar rol, revocar acceso |
| F5.1-05 | 🟠 | Página de perfil del equipo: nombre, logo, miembros activos |

**Checklist de testing — subfase 5.1:**

- [ ] Wizard completo: equipo creado, logo subido, 3 ciclistas importados desde CSV.
- [ ] Invitación enviada; link recibido en <30 segundos.
- [ ] Aceptar invitación vincula el usuario al equipo correcto.
- [ ] Link de invitación expirado (>72h) devuelve error claro.
- [ ] Link de invitación ya usado no permite un segundo registro.

**🔒 Test de seguridad — subfase 5.1:**

- [ ] Token de invitación es criptográficamente aleatorio (≥32 bytes).
- [ ] Token de invitación es de un solo uso: segundo uso devuelve error.
- [ ] No es posible cambiar el `team_id` de un token de invitación (firmado o verificado en DB).

---

#### 5.2 Planes y Límites

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F5.2-01 | 🟠 | Sistema de quotas: límites por plan (ciclistas, análisis/mes, usuarios del equipo) |
| F5.2-02 | 🟠 | Al alcanzar un límite, la acción es bloqueada con mensaje de upgrade claro |
| F5.2-03 | 🟠 | Página de pricing con mínimo 3 planes y comparativa de características |
| F5.2-04 | 🟡 | Integración Stripe: suscripción mensual/anual; webhook actualiza el plan en DB |
| F5.2-05 | 🟡 | Portal de facturación de Stripe accesible desde configuración del equipo |

**Checklist de testing — subfase 5.2:**

- [ ] Equipo en plan gratuito: superar el límite de ciclistas bloquea la creación con mensaje de upgrade.
- [ ] Webhook de Stripe en test mode: pago correcto sube el plan; pago fallido lo baja.
- [ ] Dos equipos distintos tienen contadores de quota completamente independientes.

**🔒 Test de seguridad — subfase 5.2:**

- [ ] El webhook de Stripe verifica la firma (`stripe-signature` header); request sin firma válida devuelve 400.
- [ ] No es posible modificar el plan del equipo via API sin pasar por Stripe (endpoint de plan solo acepto llamadas del webhook verificado).

---

#### 5.3 Roles y Permisos Granulares

**Requisitos funcionales:**

| ID | Prioridad | Requisito |
|----|-----------|-----------|
| F5.3-01 | 🔴 | Enforcement de permisos por rol en todos los endpoints de FastAPI |
| F5.3-02 | 🔴 | `director`: acceso total. `coach`: sin acceso a facturación ni gestión de equipo. `analyst`: solo lectura de carreras y ciclistas. `rider`: solo sus propios datos |
| F5.3-03 | 🟠 | UI oculta o desactiva acciones no permitidas según el rol del usuario |

**Checklist de testing — subfase 5.3:**

- [ ] Usuario con rol `analyst` no puede crear ciclistas (POST /api/riders → 403).
- [ ] Usuario con rol `coach` no puede acceder a facturación.
- [ ] Usuario con rol `rider` solo puede ver su propia ficha.
- [ ] UI: botones de crear/editar no visibles para `analyst`.

**🔒 Test de seguridad — subfase 5.3:**

- [ ] El enforcement de roles ocurre en el backend (FastAPI), no solo en la UI.
- [ ] Manipular la UI para mostrar botones ocultos no permite realizar la acción si el backend la deniega.

---

#### ✅ Gate de Seguridad — Fase 5

| # | Check | Resultado esperado |
|---|-------|--------------------|
| GS5-01 | Token de invitación reutilizado | Error de token ya usado |
| GS5-02 | Webhook Stripe sin firma | HTTP 400 |
| GS5-03 | Analyst intenta crear ciclista via API | HTTP 403 |
| GS5-04 | Rider accede a ciclista de compañero | HTTP 403/404 |
| GS5-05 | Modificar plan via API sin Stripe | HTTP 403 |
| GS5-06 | Equipo A accede a datos de Equipo B (regresión completa) | HTTP 403/404 en todos los endpoints |

---

## 7. Requisitos No Funcionales

### 7.1 Rendimiento

| ID | Requisito | Target |
|----|-----------|--------|
| RNF-01 | Tiempo total pipeline análisis GPX | <90s P95 (GPX 600 puntos) |
| RNF-02 | Tiempo de respuesta endpoints CRUD | <300ms P95 |
| RNF-03 | LCP del dashboard | <2.5s en 10Mbps |
| RNF-04 | TTI tras carga inicial | <4s |
| RNF-05 | Latencia SSE (evento → frontend) | <500ms |
| RNF-06 | Consultas DB frecuentes | <50ms P95 con índices |
| RNF-07 | Análisis simultáneos sin degradación | ≥10 concurrentes por instancia |

### 7.2 Disponibilidad

| ID | Requisito | Target |
|----|-----------|--------|
| RNF-08 | Uptime mensual | ≥99.5% |
| RNF-09 | Análisis con datos meteorológicos reales | ≥90% (fallback Open-Meteo) |
| RNF-10 | Análisis sin datos de superficie | 100% (fallback `asphalt`) |
| RNF-11 | Recuperación ante crash de job | SSE envía error en <5s |
| RNF-12 | Persistencia ante restart del servidor | Análisis guardado antes de `analysis_ready` |

### 7.3 Compatibilidad

| Componente | Requisito |
|-----------|-----------|
| Navegadores | Chrome 110+, Firefox 115+, Safari 16+, Edge 110+ |
| Formato GPX | GPX 1.0 y 1.1; tracks con y sin elevación |
| Export GPX | Compatible con Garmin, Wahoo, RideWithGPS, Komoot |
| Resolución mínima | 1024×768px |

### 7.4 Mantenibilidad

- Separación estricta: `gpx_analyzer.py`, `weather.py`, `surface.py` son servicios independientes.
- OpenAPI/Swagger automático en FastAPI.
- Tipos TypeScript generados desde Supabase (`supabase gen types`).
- Logs estructurados en JSON.
- `docker-compose` para entorno de desarrollo local.

---

## 8. Criterios Globales de Seguridad

> Estos criterios se verifican **en cada Gate de Seguridad** de cada fase (regresión completa).

### 8.1 Autenticación y Sesión

- JWT en cookie `httpOnly`, `SameSite=Strict`, `Secure`.
- Verificación JWT en FastAPI en **cada** request protegido.
- Rate limiting en login: 10 intentos / 15 min por IP.
- Rate limiting en análisis: 20 / hora por `team_id`.
- Tokens de invitación: ≥32 bytes aleatorios, un solo uso, TTL 72h.

### 8.2 Autorización y Aislamiento

- RLS activo en **todas** las tablas de Supabase.
- `team_id` nunca tomado del body del request; siempre del JWT.
- Enforcement de roles en el backend, no solo en la UI.
- Acceso cross-team en cualquier endpoint → 403 o 404 (nunca 200).

### 8.3 Inputs y Uploads

- Validación con Pydantic v2 en todos los endpoints.
- GPX parseado con timeout de 30s; XML bomb neutralizado.
- Avatares: solo `image/jpeg`, `image/png`, `image/webp`; máx 5MB.
- Import CSV: máx 10.000 filas; fórmulas tratadas como texto puro.
- Todos los outputs de usuario escapados en la UI (sin innerHTML con datos del usuario).

### 8.4 Secretos y Variables de Entorno

- Claves API externas (Tomorrow.io, ORS, Google Maps, Stripe) **solo en backend**.
- `SUPABASE_SERVICE_KEY` **nunca** en variables `NEXT_PUBLIC_*`.
- `.env` en `.gitignore`; `.env.example` sin valores reales.
- `/docs` de FastAPI deshabilitado en producción.

### 8.5 Storage

- Bucket `gpx-files` privado; acceso solo con signed URL (TTL 1h).
- Signed URLs generadas en el backend, no en el frontend.

### 8.6 Infraestructura

- HTTPS/TLS 1.2+ en toda comunicación client-server.
- CORS: solo dominios del frontend explícitamente permitidos.
- Headers de seguridad: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
- Webhook de Stripe: verificación de firma en cada request.

---

## 9. Convenciones y Definiciones

### 9.1 Prioridades de Requisitos

| Símbolo | Nivel | Descripción |
|---------|-------|-------------|
| 🔴 | CRÍTICO | Bloqueante. Sin esto la fase no puede cerrarse. |
| 🟠 | ALTO | Debe estar en la fase. Puede entregarse al final de la misma. |
| 🟡 | MEDIO | Deseable en la fase. Puede moverse a la siguiente si hay presión de tiempo. |
| 🟢 | BAJO | Nice-to-have. Backlog para versiones futuras. |

### 9.2 Definición de Done por Subfase

Una subfase está **Done** cuando:
1. Todos los requisitos 🔴 están implementados y testeados.
2. El checklist de testing de la subfase está completo al 100%.
3. El test de seguridad de la subfase no tiene fallos abiertos.
4. `npm run build` (frontend) y `pytest` (backend) pasan sin errores.
5. El código ha pasado por revisión (PR aprobado).

### 9.3 Definición de Done por Fase

Una fase está **Done** cuando:
1. Todas las subfases están Done.
2. El Gate de Seguridad de la fase está superado al 100%.
3. El entregable descrito en el objetivo de la fase es demostrable end-to-end.
4. No hay issues de seguridad abiertos de prioridad CRÍTICA o ALTA.

### 9.4 Glosario

| Término | Definición |
|---------|-----------|
| GPX | GPS Exchange Format. Formato XML para rutas GPS. |
| FTP | Functional Threshold Power. Potencia umbral funcional en vatios. |
| W/kg | Vatios por kilogramo. Métrica de rendimiento relativo. |
| TSS | Training Stress Score. Carga de entrenamiento acumulada. |
| RLS | Row Level Security. Política de acceso a nivel de fila en PostgreSQL. |
| SSE | Server-Sent Events. Protocolo de streaming unidireccional HTTP. |
| D+ | Desnivel positivo acumulado en metros. |
| Roadbook | Guía táctica de eventos clave de una etapa. |
| JWT | JSON Web Token. Token de autenticación firmado. |
| MRR | Monthly Recurring Revenue. Ingresos recurrentes mensuales. |
| P95 | Percentil 95. El 95% de los casos están por debajo de este valor. |

---

*Director Hub PRO — PRD v1.0 · Confidencial · Abril 2026*
