# Contacts API

REST API for contact management built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Poetry.

The project includes:

- JWT authentication with `access_token`
- Email verification for registered users
- Private contact operations per authenticated user
- User profile endpoint with rate limiting on `/api/users/me`
- Avatar upload to Cloudinary
- CORS configuration through environment variables
- Docker Compose setup for the API and PostgreSQL

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Poetry
- SlowAPI
- Cloudinary

## Project Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Configure environment variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Required groups of settings:

- Database: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Security: `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- Email verification: `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_SERVER`, `MAIL_PORT`
- Cloudinary: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- CORS: `CORS_ALLOW_ORIGINS`

Notes:

- For Gmail SMTP, use an app password instead of your account password.
- `BACKEND_BASE_URL` is used to build the verification link sent by email.
- `CORS_ALLOW_ORIGINS` should stay in JSON array format, for example `["http://localhost:3000","http://localhost:8000"]`.

### 3. Apply migrations

```bash
poetry run alembic upgrade head
```

### 4. Run the application locally

```bash
poetry run uvicorn main:app --reload
```

The API will be available at:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Compose

Run the full stack:

```bash
docker compose up --build
```

This starts:

- FastAPI application on port `8000`
- PostgreSQL on port `5432`

The container startup command runs migrations automatically before starting Uvicorn.

## Authentication Flow

1. Register a new user with `POST /api/auth/register`.
2. Open the verification link sent to the configured email.
3. Log in with `POST /api/auth/login` to receive an `access_token`.
4. Send the token in the `Authorization` header as `Bearer <token>`.
5. Use authenticated routes for contacts and user profile operations.

## API Endpoints

### Auth

- `POST /api/auth/register` — register a new user
- `POST /api/auth/login` — log in and receive `access_token`
- `GET /api/auth/verify-email?token=...` — verify email
- `POST /api/auth/request-email` — resend verification email

### Users

- `GET /api/users/me` — get the current user profile, limited to `10/minute`
- `PATCH /api/users/avatar` — upload or update the user avatar

### Contacts

- `POST /api/contacts` — create a contact
- `GET /api/contacts` — list contacts with optional filters `first_name`, `last_name`, `email`
- `GET /api/contacts/upcoming-birthdays` — get upcoming birthdays
- `GET /api/contacts/{contact_id}` — get a contact by id
- `PUT /api/contacts/{contact_id}` — update a contact
- `DELETE /api/contacts/{contact_id}` — delete a contact

All contact routes require authentication and return only the current user's data.

## Data Notes

- Contact `birthday` is stored as a `date`
- Contact `email` and `phone` remain globally unique in the current schema
- Passwords are stored only in hashed form
- Duplicate user email returns `409 Conflict`
- Invalid login returns `401 Unauthorized`

## Useful Commands

Install dependencies:

```bash
poetry install
```

Run migrations:

```bash
poetry run alembic upgrade head
```

Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "message"
```

Run the server:

```bash
poetry run uvicorn main:app --reload
```

Run tests:

```bash
poetry run pytest
```