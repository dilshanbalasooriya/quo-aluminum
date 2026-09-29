# Quo Aluminum Project Context

Use this document as a starting point when an AI assistant is asked to understand or modify this repository. Treat the source code as authoritative if it differs from this summary or other documentation.

## What the project does

Quo Aluminum is an internal quotation-estimation tool for an aluminum workshop. Workers select a window/door design and an aluminum profile, enter dimensions and quantity, add customer details and a worker fee, then issue a quotation and view, print, download, or share its PDF. Administrators manage users and the catalog and review dashboard statistics.

## Architecture

- `backend/` is a Python FastAPI application. It uses SQLModel/SQLAlchemy for database access, JWT bearer authentication, and Jinja2 plus xhtml2pdf to render quotation PDFs.
- `frontend/` is a Vue 3 + TypeScript single-page application built with Vite. Pinia holds authentication and catalog state; Vue Router controls role-aware navigation; Axios communicates with the API.
- `docker-compose.yml` defines PostgreSQL, backend, and frontend services. The configured ports are 5432, 8000, and 5000 respectively.
- The backend creates SQLModel tables on startup. `backend/seed.py` is a separate script for creating initial users; it is not invoked by the app startup handler.

## Main user flows

### Worker

1. Logs in and is directed to the workshop dashboard.
2. Chooses active window/door types and aluminum profiles from the authenticated catalog API.
3. Enters width, height, and quantity. The frontend requests a server-side price preview; it does not calculate prices itself.
4. Adds one or more priced items to the in-memory draft, enters customer details and a worker fee, then submits the quotation.
5. The backend stores the customer, quotation, and items, then returns the issued quotation. The frontend fetches the authenticated PDF as a blob for preview and related actions.
6. Can inspect quotation history.

### Administrator

Administrators can access dashboard statistics, manage worker accounts, and create/update/soft-delete aluminum profiles and window/door types. Catalog reads are exposed separately so any authenticated worker or administrator can use them.

## Backend structure and ownership

- `backend/app.py`: creates the FastAPI app, initializes database tables on startup, configures CORS from `ORIGIN`, and mounts routers.
- `backend/configs/config.py`: loads `backend/.env`; reads `SECRET_KEY`, `DATABASE_URL`, company details, and comma-separated `ORIGIN` values.
- `backend/database/connection.py`: creates the database engine and provides SQLModel sessions.
- `backend/database/models.py`: persistence models and enums.
- `backend/routers/auth.py`: login, current-user details, and admin-only user operations.
- `backend/routers/admin.py`: admin-only dashboard, user, profile, and window/door-type management.
- `backend/routers/catalog.py`: authenticated read-only profiles, types, and settings.
- `backend/routers/quotation.py`: price preview, quotation listing/creation, and PDF generation.
- `backend/services/security.py`: password/JWT and current-user authorization helpers.
- `backend/services/calulate_service.py`: shared price calculation. The filename is spelled `calulate_service.py`; preserve that import path unless intentionally renaming all references.
- `backend/templates/quotation.html`: quotation PDF HTML template; `template.html` is another backend template.

## Data model

The main SQLModel tables are:

- `User`: username, password hash, role (`ADMIN` or `WORKER`), active/deleted flags, and creation time.
- `AluminiumProfile`: profile name, brand, gauge, weight per meter, rate per kilogram, active/deleted flags.
- `WindowDoorType`: name, category (`WINDOW` or `DOOR`), counts of internal vertical/horizontal bars, active/deleted flags.
- `Customer`: name and phone, with optional email.
- `Quotation`: unique quotation number, worker/customer references, worker fee, subtotal, total, status (`DRAFT` or `ISSUED`), and creation time.
- `QuotationItem`: quotation/profile/type references, dimensions in millimeters, quantity, calculated weight, frame cost, and item total.
- `Setting`: string key/value configuration records, including the optional `default_worker_fee` used when a request omits its fee.

Profile and type deletes are soft deletes: records are marked inactive and deleted rather than removed from the database. User deletion follows the same pattern and changes the username to preserve its uniqueness.

## Pricing rules and invariants

The single source of truth is `backend/services/calulate_service.py`. The quotation preview and quotation creation both call `calculate_item_price`; keep them consistent by reusing this service rather than reproducing pricing math in Vue or in a route.

For dimensions converted from millimeters to meters:

- Outer perimeter = `2 * (height + width)`
- Extra bars = `vertical_bars_count * height + horizontal_bars_count * width`
- Frame length = outer perimeter + extra bars
- Weight per unit = frame length * profile weight per meter
- Frame cost per unit = weight per unit * profile rate per kg
- Item total = frame cost per unit * quantity

Inputs must have positive dimensions and quantity. The service uses `Decimal` and rounds frame length and weight to 0.001 and currency values to 0.01. `worker_fee` is added to the sum of item totals to produce the quotation total. These calculations currently cover frame material only; do not imply that glass, hardware, waste, tax, or other charges are included unless implementing them explicitly.

Quotation numbers use the `QT-YYYYMMDD-NNNN` pattern with the date in `Asia/Colombo`. The PDF includes company fields loaded from environment configuration.

## Frontend structure and conventions

- `frontend/src/main.ts` is the app bootstrap; `App.vue` supplies the authenticated shell and global toast/confirmation dialogs.
- `frontend/src/router/index.ts` defines `/login`, `/admin/...`, and `/workshop/...` routes and guards by authentication/role. Admin users are permitted through worker-role checks in the current guard.
- `frontend/src/api/axios.ts` centralizes the API base URL, attaches bearer tokens, and logs out/redirects on HTTP 401 responses.
- `frontend/src/stores/authStore.ts` decodes JWTs and persists the token in `localStorage`.
- `frontend/src/stores/catalogStore.ts` caches profiles and window/door types; invalidate this cache after admin catalog edits.
- `frontend/src/views/worker/WorkerDashboardView.vue` implements quotation entry, cart/draft state, server-side price preview, submission, and PDF actions.
- `frontend/src/views/worker/QuotationHistoryView.vue` is the worker quotation history surface.
- `frontend/src/views/admin/` contains dashboard, profiles, templates, and users views.
- Shared UI components and global styles live under `frontend/src/components/` and `frontend/src/assets/`.

Use the existing Axios client for authenticated API calls. Keep API payload field names aligned with the Pydantic request/response models. Catalog data is cached, while quotation draft/cart state is currently local to the worker dashboard view rather than persisted as a draft in the API.

## API route groups

All routes require authentication unless noted otherwise.

- `/auth/login`: OAuth2 password-form login; returns a bearer JWT. `/auth/me` returns the current user. User listing/creation/password reset are admin-only.
- `/admin/...`: admin-only dashboard statistics, user management, aluminum profiles, and window/door types.
- `/catalog/aluminium-profiles`, `/catalog/window-door-types`, `/catalog/settings/{key}`: authenticated catalog reads.
- `/quotations/price-preview`: stateless item pricing; saves nothing.
- `/quotations`: list quotations and create/issue one.
- `/quotations/quot-pdf/{quotation_id}/invoice.pdf`: render and return the quotation PDF.

The current quotation list response is a hand-built summary and differs from the detailed response used when creating a quotation. Check the actual route schema/response before assuming the shapes are interchangeable.

## Local development and configuration

- Frontend scripts are in `frontend/package.json`: `npm run dev`, `npm run build`, `npm run type-check`, and `npm run preview`. The frontend expects Node.js `^22.18.0 || >=24.12.0`.
- Docker Compose expects `backend/.env` because both backend and database services load that file. Set the backend connection URL, JWT secret, CORS origin(s), and company PDF details there.
- The frontend API URL is `VITE_API_BASE_URL` and defaults in code to `http://localhost:8000`.
- Backend configuration reads `DATABASE_URL`. The hosting guide currently names `DB_URI` instead, so follow the code or update the documentation/config deliberately; do not assume those names are interchangeable.
- `backend/seed.py` currently seeds `admin/admin123` and `worker/worker123`. These are development credentials only; replace them before deploying or exposing an environment.
- Backend dependencies are listed in `backend/requirements.txt`.

## Guidance for future changes

1. Trace behavior to the owning layer before editing: pricing in the calculation service, persistence in models/routes, auth policy in `services/security.py` and router dependencies, and UI state in Vue views/stores.
2. Preserve existing role protections and active/deleted catalog filtering. Do not rely on frontend route guards as backend authorization.
3. For pricing changes, update the shared calculation service and verify both preview and saved quotation behavior. Keep decimal precision and rounding intentional.
4. For API changes, update the backend Pydantic models and the corresponding TypeScript usage/view together.
5. Keep company-specific PDF content in configuration/template code rather than hard-coding it into unrelated UI or route logic.
6. Check existing instructions, tests, and current source before relying on this document; it is a map, not a substitute for inspecting the implementation.
