# Roadmap

## Phase 1 — Core backend + Ludus wrapper (MVP)

- [ ] FastAPI project scaffold (`pyproject.toml`, `main.py`, settings)
- [ ] SQLite + SQLAlchemy models (users, lab_templates, sessions, students, events)
- [ ] Auth (single instructor, JWT in httpOnly cookie)
- [ ] `services/ludus.py` — HTTP client wrapping Ludus API
  - [ ] `user_add(userid, name, email, password) -> User`
  - [ ] `user_rm(userid) -> None`
  - [ ] `range_assign(userid, range_id) -> None`
  - [ ] `user_wireguard(userid) -> str`  (returns .conf text)
  - [ ] `snapshot_revert(userid, name) -> None`
  - [ ] `range_deploy(userid, config_yaml) -> None`  (for dedicated mode)
- [ ] Endpoints:
  - [ ] `POST /api/auth/login`
  - [ ] `GET/POST /api/labs`
  - [ ] `GET/POST /api/sessions`
  - [ ] `POST /api/sessions/{id}/provision`
  - [ ] `POST /api/sessions/{id}/students`
  - [ ] `POST /api/students/{id}/reset`
  - [ ] `DELETE /api/students/{id}`
  - [ ] `GET /invite/{token}` (public, HTML)
  - [ ] `GET /invite/{token}/config` (public, .conf download)

**Exit criteria:** Replace `add_player.sh` end-to-end via curl/HTTP.

## Phase 2 — Stitch design + frontend

- [ ] Stitch design for 4 screens (Login, Dashboard, Session Detail, Invite)
- [ ] Export React + Tailwind into `frontend/`
- [ ] Wire pages to backend API
- [ ] Auth flow (login → dashboard → logout)
- [ ] Create session → add students → provision flow
- [ ] Live student table with status polling

**Exit criteria:** Click-through from login to inviting a student in the browser.

## Phase 3 — Polish

- [ ] CSV bulk import for students
- [ ] Provisioning progress indicator (SSE or polling)
- [ ] Rate-limited reset button
- [ ] Session teardown confirmation modal
- [ ] Audit log view
- [ ] Basic error handling + toast notifications

**Exit criteria:** Run first real training on the platform.

## Phase 4 — v2 (post-MVP)

- [ ] SMTP email delivery of invites
- [ ] Student portal (view lab info, submit challenge completions)
- [ ] Multi-instructor / RBAC
- [ ] Postgres migration
- [ ] Background job queue (Celery + Redis)
- [ ] Multi-Ludus-server support (lab1, lab2, etc. selectable per session)
- [ ] Public signup / landing page for insec.ml
