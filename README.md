# insec-platform

Training lab deployment management platform for [insec.ml](https://insec.ml).

A self-hosted web platform that wraps [Ludus](https://ludus.cloud) to let instructors
provision, monitor, and tear down student lab environments in bulk for security
trainings and workshops.

## Status

**MVP in progress.** See [docs/ROADMAP.md](docs/ROADMAP.md) for current phase.

## What it does

- Define reusable **lab templates** (Ludus range-config YAML + metadata)
- Create a **training session**: select lab, pick mode (shared/dedicated), add students
- **One-click bulk provision**: creates Ludus users, assigns ranges, generates WireGuard configs
- Share per-student **invite links** — students download their VPN config
- **Live dashboard**: student status, range health, snapshot state
- Per-student **lab reset** (triggers Ludus snapshot revert)
- **One-click teardown**: cleanup all Ludus users, configs, and artifacts

## Architecture

```
┌─────────────────────────────┐
│  React UI (Stitch design)   │
│  Instructor dashboard       │
└──────────────┬──────────────┘
               │ REST / JSON
               ▼
┌─────────────────────────────┐
│  FastAPI backend            │
│  - sessions / students      │
│  - ludus wrapper            │
│  - invites                  │
└──────┬──────────────┬───────┘
       │              │
       ▼              ▼
  [SQLite]       [Ludus API]
                 (one or more Ludus servers)
```

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic, httpx
- **Frontend:** React + TypeScript + Tailwind (Stitch-designed)
- **DB:** SQLite (MVP), Postgres (v2+)
- **Auth:** Single instructor account, JWT in httpOnly cookie
- **Deployment:** Docker Compose

## Quick start

*(not implemented yet — see ROADMAP)*

```bash
cp .env.example .env
# edit .env with your Ludus API key and admin password
docker compose up -d
```

## License

Private — all rights reserved (for now).
