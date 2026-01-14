# Environment Variables Setup Guide

This guide explains how to set up environment variables for development and production environments.

## Overview

The project uses separate `.env` files for different environments:
- **Development**: `.env.development`
- **Production**: `.env.production`

These files are gitignored for security. Use the `.env.example` files as templates.

## Backend Environment Variables

### Development (`.env.development`)

Create `backend/.env.development`:

```env
# Development Environment Variables
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/netgarde

# Application Configuration
PYTHONUNBUFFERED=1
ENVIRONMENT=development

# Logging
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Production (`.env.production`)

Create `backend/.env.production`:

```env
# Production Environment Variables
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/netgarde

# Application Configuration
PYTHONUNBUFFERED=1
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security (add your production secrets here)
# SECRET_KEY=your-secret-key-here
# ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Frontend Environment Variables

### Development (`.env.development`)

Create `frontend/.env.development`:

```env
# Development Environment Variables
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Enable source maps in development
GENERATE_SOURCEMAP=true
```

### Production (`.env.production`)

Create `frontend/.env.production`:

```env
# Production Environment Variables
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production

# Disable source maps in production for security
GENERATE_SOURCEMAP=false
```

## Quick Setup

### Option 1: Manual Creation

1. Copy the example content above into new files:
   - `backend/.env.development`
   - `backend/.env.production`
   - `frontend/.env.development`
   - `frontend/.env.production`

2. Update the values for your environment, especially:
   - Database passwords
   - API URLs
   - Production secrets

### Option 2: Using Command Line

**Windows (PowerShell):**
```powershell
# Backend development
@"
# Development Environment Variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/netgarde
PYTHONUNBUFFERED=1
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath backend\.env.development -Encoding utf8

# Backend production
@"
# Production Environment Variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/netgarde
PYTHONUNBUFFERED=1
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath backend\.env.production -Encoding utf8

# Frontend development
@"
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true
"@ | Out-File -FilePath frontend\.env.development -Encoding utf8

# Frontend production
@"
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
"@ | Out-File -FilePath frontend\.env.production -Encoding utf8
```

**Linux/Mac:**
```bash
# Backend development
cat > backend/.env.development << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:12345@db:5432/netgarde
PYTHONUNBUFFERED=1
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Backend production
cat > backend/.env.production << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=netgarde
DB_URL=postgresql+psycopg2://postgres:CHANGE_ME_IN_PRODUCTION@db:5432/netgarde
PYTHONUNBUFFERED=1
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Frontend development
cat > frontend/.env.development << EOF
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
GENERATE_SOURCEMAP=true
EOF

# Frontend production
cat > frontend/.env.production << EOF
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
EOF
```

## Docker Compose Configuration

The docker-compose files are already configured to use the appropriate `.env` files:

- **Development**: `docker-compose.dev.yml` uses `.env.development`
- **Production**: `docker-compose.yml` uses `.env.production`

## Important Notes

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Update production passwords** - Change `CHANGE_ME_IN_PRODUCTION` to secure passwords
3. **Update API URLs** - Set correct production API URLs in frontend `.env.production`
4. **Security** - Use strong, unique passwords for production
5. **Secrets** - Store sensitive values in environment variables or secrets management systems

## Environment Variable Reference

### Backend Variables

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `POSTGRES_USER` | PostgreSQL username | `postgres` | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `12345` | **CHANGE** |
| `POSTGRES_DB` | Database name | `netgarde` | `netgarde` |
| `DB_URL` | Full database connection string | Auto-generated | Auto-generated |
| `PYTHONUNBUFFERED` | Python output buffering | `1` | `1` |
| `ENVIRONMENT` | Environment name | `development` | `production` |
| `LOG_LEVEL` | Logging level | `DEBUG` | `INFO` |
| `API_HOST` | API host address | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | API port | `8000` | `8000` |

### Frontend Variables

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `REACT_APP_API_BASE_URL` | Backend API URL | `http://localhost:8000` | `https://api.yourdomain.com` |
| `REACT_APP_ENVIRONMENT` | Environment name | `development` | `production` |
| `GENERATE_SOURCEMAP` | Generate source maps | `true` | `false` |

## Troubleshooting

### Environment variables not loading

1. Check file names match exactly: `.env.development` or `.env.production`
2. Verify docker-compose file references the correct `.env` file
3. Restart containers after changing `.env` files:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Frontend variables not working

- React requires variables to start with `REACT_APP_`
- Restart the dev server after changing `.env` files
- Clear browser cache if needed

### Database connection issues

- Verify `DB_URL` format is correct
- Check PostgreSQL credentials match
- Ensure database container is running
