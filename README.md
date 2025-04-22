# Unix-Inspired Task Manager API

## Overview

This API simulates Unix-style process/task management. It allows you to create, list, and manage tasks, mimicking Unix commands like `ls` for listing tasks and `fork` for creating tasks. The tasks have a **process ID (PID)**, a **status**, and a **command** associated with them.

### Features
- **Create Tasks** (`POST /tasks`)
- **List Tasks** (`GET /tasks`)
- **Filter Tasks by Status** (`GET /tasks?status=running`)
- **Simulate Task Completion** (`PATCH /tasks/{id}`)
- **Task Details** (`GET /tasks/{id}`)

## Setup

### Requirements

- Python 3.8 or higher
- FastAPI
- SQLAlchemy
- SQLite (or another DB of your choice)

### Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. Open the interactive documentation in your browser:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Database Setup

The project uses SQLite as the default database. When you first run the application, it will create a file called `tasks.db` to store task information. If you want to use another database (e.g., PostgreSQL, MySQL), you can modify the `DATABASE_URL` in the code.

## API Endpoints

### 1. Create a Task (`POST /tasks`)

Create a new task by providing the following details in the body:

- `name` (str): Task name (e.g., "Daily backup")
- `priority` (int): Task priority (0–5)
- `owner` (str): User who initiated the task
- `command` (str): Simulated command or operation (e.g., "rsync -avz /data /backup")

**Example Request:**

```bash
POST /tasks
{
  "name": "Backup",
  "priority": 3,
  "owner": "admin",
  "command": "rsync -avz /data /backup"
}
```

### 2. List All Tasks (`GET /tasks`)

Get a list of all tasks. Optionally filter tasks by status using `?status=running` or `?status=completed`.

**Example Request:**

```bash
GET /tasks?status=running
```

### 3. Get Task Details (`GET /tasks/{id}`)

Get detailed information for a single task using its ID.

**Example Request:**

```bash
GET /tasks/12345
```

### 4. Simulate Task Completion (`PATCH /tasks/{id}`)

Update the status of a task to `completed`. This mimics the task finishing or being terminated.

**Example Request:**

```bash
PATCH /tasks/12345
```

This will update the task with the specified ID to `completed`.

## Models

### Task

- `id`: The unique process ID (PID), auto-generated randomly between 1000 and 99999.
- `name`: The name of the task.
- `priority`: The priority of the task (0–5).
- `owner`: The user who initiated the task.
- `command`: The command or operation that the task is performing.
- `status`: The current status of the task (e.g., `running`, `completed`).
- `created_at`: Timestamp when the task was created.
- `updated_at`: Timestamp when the task was last updated.

### Run  Tests
To run the tests with detailed output, use the following command:
```bash
pytest --tb=short -v test_task_manager.py
```

