# Multi-Platform Device API

A Django REST Framework API for managing devices across multiple platforms with platform-specific JWT authentication.

## Features

- **Platform Isolation**: Users can register with the same email on different platforms (e.g., Android, iOS).
- **JWT Authentication**: Secure login returning tokens valid only for the specific platform.
- **Device Management**: CRUD operations for devices, automatically filtered by the authenticated user's platform.
- **Modern Stack**: Built with Django 5.2, DRF, and managed with `uv`.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.14+ and `uv`

## Quick Start with Docker (Recommended)

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **The API will be available at** `http://localhost:8000`

3. **Create test data** (in a new terminal):
   ```bash
   docker-compose exec web /app/.venv/bin/python manage.py setup_test_data
   ```
   
   This creates:
   - 3 platforms: Android, iOS, Web
   - User `user@example.com` with password `password123` on each platform
   - 2 devices per user/platform

4. **Create a superuser** (optional, for Django admin):
   ```bash
   docker-compose exec web /app/.venv/bin/python manage.py createsuperuser
   ```

5. **Stop the server**:
   ```bash
   docker-compose down
   ```

## Manual Installation (Without Docker)

### Using uv (Recommended)

1. **Install uv** (if not installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create test data** (optional):
   ```bash
   python manage.py setup_test_data
   ```

5. **Run server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

## API Usage

### 1. Login and Obtain JWT Token

**Endpoint:** `POST /api/auth/login/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "platform": "Android"
  }'
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "email": "user@example.com",
  "platform": "Android"
}
```

### 2. List Devices

**Endpoint:** `GET /api/devices/`

**Request:**
```bash
curl -X GET http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Android Device 1",
    "ip_address": "192.168.1.101",
    "is_active": true,
    "created_at": "2025-11-30T20:00:00Z",
    "updated_at": "2025-11-30T20:00:00Z"
  },
  {
    "id": 2,
    "name": "Android Device 2",
    "ip_address": "10.0.0.5",
    "is_active": false,
    "created_at": "2025-11-30T20:00:00Z",
    "updated_at": "2025-11-30T20:00:00Z"
  }
]
```

### 3. Create Device

**Endpoint:** `POST /api/devices/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Device",
    "ip_address": "192.168.1.50",
    "is_active": true
  }'
```

**Response:**
```json
{
  "id": 3,
  "name": "My New Device",
  "ip_address": "192.168.1.50",
  "is_active": true,
  "created_at": "2025-11-30T21:00:00Z",
  "updated_at": "2025-11-30T21:00:00Z"
}
```

### 4. Update Device

**Endpoint:** `PUT /api/devices/{id}/` or `PATCH /api/devices/{id}/`

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/devices/3/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### 5. Delete Device

**Endpoint:** `DELETE /api/devices/{id}/`

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/devices/3/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 6. Refresh Token

**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<REFRESH_TOKEN>"
  }'
```

## Testing

### With Docker:

```bash
docker-compose exec web /app/.venv/bin/python manage.py test
```

### Without Docker:

```bash
python manage.py test
```

Run with coverage:

```bash
coverage run --source='api' manage.py test api
coverage report
```

## Platform Isolation

The key feature of this API is **platform isolation**:

- Same email can exist on multiple platforms (Android, iOS, Web)
- Each login is platform-specific
- JWT tokens contain `platform_id` claim
- Users can only access devices from their authenticated platform
- Cross-platform access is automatically blocked

**Example:**
```bash
# Login as Android user
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "platform": "Android"}'

# This token will ONLY see Android devices
# The same email on iOS platform will have different devices

# Login as the same user on iOS platform
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "platform": "iOS"}'

# This is a different user account with different devices
```

## Project Structure

```
multi-platform-device-api/
├── api/
│   ├── models.py              # Platform, User, Device models
│   ├── serializers.py         # DRF serializers with custom JWT
│   ├── views.py               # API views
│   ├── authentication.py      # Custom JWT authentication
│   ├── permissions.py         # Custom permissions
│   ├── urls.py                # API routes
│   ├── tests.py               # Test suite
│   └── management/
│       └── commands/
│           └── setup_test_data.py  # Test data creation
├── config/
│   ├── settings.py            # Django settings
│   └── urls.py                # Main URL config
├── manage.py
├── pyproject.toml             # uv & ruff config
├── requirements.txt           # Dependencies
├── .pre-commit-config.yaml    # Git hooks
├── Dockerfile                 # Docker configuration
└── docker-compose.yml         # Docker Compose
```

## Code Quality

This project uses:
- **ruff** for linting and formatting
- **pre-commit** for git hooks

Run linting:
```bash
ruff check .
ruff format .
```

## Development

### Access Django Admin

1. Create a superuser:
   ```bash
   # With Docker:
   docker-compose exec web /app/.venv/bin/python manage.py createsuperuser
   
   # Without Docker:
   python manage.py createsuperuser
   ```

2. Access admin panel at `http://localhost:8000/admin/`

## Common Issues

### Port 8000 already in use

If you get an error that port 8000 is already in use:

```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change the port in docker-compose.yml:
ports:
  - "8001:8000"  # Access API at http://localhost:8001
```

### Database locked error

If you get a database locked error with SQLite:

```bash
# Stop all containers
docker-compose down

# Remove the database (you'll lose data)
rm db.sqlite3

# Restart
docker-compose up --build
```

## API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | Login and get JWT tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |
| GET | `/api/devices/` | List user's devices | Yes |
| POST | `/api/devices/` | Create new device | Yes |
| GET | `/api/devices/{id}/` | Get device details | Yes |
| PUT/PATCH | `/api/devices/{id}/` | Update device | Yes |
| DELETE | `/api/devices/{id}/` | Delete device | Yes |