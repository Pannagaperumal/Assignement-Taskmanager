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
