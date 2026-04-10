# Director Hub PRO

Plataforma SaaS para directores deportivos y equipos de ciclismo profesional. Integra analisis tactico de etapas GPX, gestion de plantilla, planificacion competitiva y dashboard de rendimiento.

## Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** FastAPI + Python 3.11 + uvicorn
- **Base de datos:** Supabase (PostgreSQL + Auth + RLS + Storage)
- **Deploy:** Vercel (frontend) + Railway (backend)

## Estructura del proyecto

```
corsadata/
├── frontend/          # Next.js app
├── backend/           # FastAPI API
├── supabase/          # Migrations, seed, config
├── migracion/         # Prototipo Flask original (referencia)
├── prd/               # Product Requirements Document
├── docker-compose.yml
└── .github/workflows/ # CI pipeline
```

## Setup local

### 1. Supabase

```bash
# Instalar Supabase CLI: https://supabase.com/docs/guides/cli
supabase start
supabase db reset  # Ejecuta migrations + seed
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Rellenar con las claves de Supabase
uvicorn main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Rellenar con URL y anon key de Supabase
npm run dev
```

### 4. Docker (solo backend)

```bash
docker-compose up --build
```

## Fases de desarrollo

| Fase | Descripcion | Estado |
|------|-------------|--------|
| 0 | Infraestructura Base | En progreso |
| 1 | Analizador GPX | Pendiente |
| 2 | CRM de Ciclistas | Pendiente |
| 3 | Calendario y Carreras | Pendiente |
| 4 | Dashboard de Rendimiento | Pendiente |
| 5 | Multi-tenant y SaaS | Pendiente |

## Variables de entorno

Ver `backend/.env.example` y `frontend/.env.local.example` para la lista completa.
