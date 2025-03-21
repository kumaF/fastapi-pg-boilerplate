# FastAPI Microservice Setup

## Prerequisites

Ensure you have Python 3.10 or above installed. Additionally, you need `uv`, a Python package manager. If you don't have `uv` installed, you can install it with:

```sh
pip install uv
```

## Setup and Run

Follow these steps to set up and run the project:

1. **Prepare the environment**
   
   Run the `prepare.sh` script to handle prerequisites before starting Docker services:

   ```sh
   bash prepare.sh
   ```

2. **Start PostgreSQL and pgAdmin**
   
   Use Docker Compose to spin up PostgreSQL and pgAdmin:

   ```sh
   docker compose up -d
   ```

3. **Generate Database Migration Script**
   
   Create the initial database migration script using Alembic:

   ```sh
   uv run alembic revision --autogenerate -m "init"
   ```

4. **Apply Database Migrations**
   
   Apply the generated migrations to set up the database schema:

   ```sh
   uv run alembic upgrade head
   ```

5. **Run the FastAPI Server**
   
   Start the FastAPI application in development mode:

   ```sh
   uv run fastapi dev app/main.py
   ```

## Notes

- Ensure Docker is installed and running before executing the commands.
- The `prepare.sh` script handles necessary setup before launching the database services.
- Use `uv` as an alternative to `pip` for package management and environment handling.

Now your FastAPI microservice should be up and running!

