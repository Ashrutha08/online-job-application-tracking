# Online Job Application and Tracking System

A Flask and SQLite web application for a DevOps case study. Job seekers can create accounts, browse openings, apply with a cover letter, and track application status. An admin can review submissions and update statuses.

## Features

- Candidate registration and login with hashed passwords
- Searchable seeded job listings
- Apply once per job with a cover letter
- Application tracking
- Admin application review and status updates
- Health endpoint at `/health`
- Pytest tests ready for Jenkins CI

## Requirements

- Python 3.10+
- pip

## Run locally

### 1. Create and activate a virtual environment

**Windows PowerShell**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the application

```bash
python app.py
```

Open http://127.0.0.1:5000.

The database is created automatically on first run and sample jobs are added.

## Create an admin account

Set environment variables before running the command.

**Windows PowerShell**
```powershell
$env:ADMIN_NAME="Portal Admin"
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="change-this-password"
flask --app app create-admin
```

**macOS/Linux**
```bash
export ADMIN_NAME="Portal Admin"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="change-this-password"
flask --app app create-admin
```

Then log in with that email and password and open the Admin page.

## Run tests

```bash
python -m pytest -v
```

## Health check

Visit http://127.0.0.1:5000/health. Expected response:

```json
{"status":"ok"}
```

## Project structure

```text
.
├── app.py
├── schema.sql
├── requirements.txt
├── templates/
├── static/
├── tests/
├── .gitignore
└── README.md
```

## DevOps roadmap

1. Push source code to GitHub.
2. Configure Jenkins to install dependencies and run pytest.
3. Add a Dockerfile and build a container image.
4. Deploy the container with Kubernetes.

## Notes

- The default Flask secret key is for local development only. Set a strong `SECRET_KEY` environment variable before deployment.
- This is an educational case study, not a production-ready recruitment system. Add CSRF protection, rate limiting, stronger admin provisioning, and production database/configuration practices before real-world use.
