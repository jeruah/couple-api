# Couple API

Simple FastAPI backend for an application named **Couple Box**. It stores users, albums and images and now includes a basic chat system.

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements
```

2. Copy the example environment file and edit the values as needed:

```bash
cp .env.example .env
# edit .env and set SECRET_KEY
```

3. Initialize the database and run the server:

```bash
uvicorn app.main:app --reload
```

Visit `/initdb` once to create the SQLite database.

## Tests

Run `pytest` to execute the test suite (no tests yet, but the command should succeed).
