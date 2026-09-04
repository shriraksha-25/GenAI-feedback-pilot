# MongoDB Database Module

This folder contains the MongoDB configuration, data models, connection
management, and index initialization for the AI Product Manager Copilot.

## Database

- Database name: `product_assistant`
- Database service: MongoDB Atlas
- Python driver: PyMongo Async

## Collections

### `users`

Stores application users.

Important fields:

- `name`
- `email`
- `role`
- `is_active`

### `workspaces`

Stores product-management workspaces.

Important fields:

- `name`
- `description`
- `owner_id`
- `members`
- `status`

### `feedback`

Stores normalized customer-feedback records.

Required fields:

- `feedback_id`
- `source`
- `description`

AI-generated results are stored inside the `ai_analysis` sub-document.

### `data_imports`

Stores information about imported customer-feedback datasets.

Important fields:

- `workspace_id`
- `file_name`
- `source`
- `status`
- Record counts
- `uploaded_by`
- `uploaded_at`

## File structure

- `config.py`: Loads MongoDB environment settings.
- `connection.py`: Manages the asynchronous MongoDB connection.
- `models.py`: Defines database data models.
- `indexes.py`: Creates application indexes.
- `init_db.py`: Tests the connection and initializes indexes.
- `requirements.txt`: Contains database dependencies.

## Local setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1