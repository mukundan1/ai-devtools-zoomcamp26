# Mini Kanban Application Specification

## 1. Purpose

Mini Kanban is a small task-management application with a browser frontend and a FastAPI backend.

The application uses an OpenAPI-described HTTP API and SQLAlchemy for database access. SQLite is used by default for local development, while the application remains database-agnostic for a future PostgreSQL migration.

## 2. Implemented Features

### 2.1 Board columns

The board contains three task statuses:

- `todo` — To do
- `doing` — In progress
- `done` — Done

Every task must belong to exactly one column.

### 2.2 Task properties

Each task contains:

| Property | Type | Required | Description |
|---|---|---:|---|
| `id` | integer | Yes | Unique task identifier |
| `title` | string | Yes | Task title, 1–200 characters |
| `description` | string | No | Task details, up to 2,000 characters |
| `status` | enum | Yes | `todo`, `doing`, or `done` |
| `position` | integer | Yes | Ordering within a column |
| `created_at` | datetime | Yes | Creation timestamp |

### 2.3 Task operations

The frontend supports:

- Creating tasks
- Editing tasks
- Deleting tasks
- Moving tasks between columns
- Dragging tasks to another column
- Displaying task counts per column
- Displaying an empty-column message

### 2.4 HTTP API

#### Health check

```http
GET /api/health
```

Returns:

```json
{
  "status": "ok"
}
```

#### List tasks

```http
GET /api/tasks
```

Returns all tasks ordered by status and position.

#### Create a task

```http
POST /api/tasks
Content-Type: application/json
```

Example request:

```json
{
  "title": "Write documentation",
  "description": "Document the API",
  "status": "todo"
}
```

Returns HTTP `201`.

#### Update a task

```http
PATCH /api/tasks/{task_id}
Content-Type: application/json
```

Any of the following properties may be updated:

- `title`
- `description`
- `status`
- `position`

Returns HTTP `200`.

#### Delete a task

```http
DELETE /api/tasks/{task_id}
```

Returns HTTP `204`.

### 2.5 Validation

The API rejects:

- Empty task titles
- Titles longer than 200 characters
- Descriptions longer than 2,000 characters
- Unknown statuses
- Negative positions
- Requests for nonexistent task IDs

FastAPI returns HTTP `422` for validation failures and HTTP `404` for nonexistent tasks.

### 2.6 Persistence

The default database is SQLite:

```text
sqlite:///kanban.db
```

The database is created automatically at application startup.

Initial sample tasks are inserted only when the database is empty.

### 2.7 Database portability

The application uses SQLAlchemy rather than SQLite-specific SQL.

A PostgreSQL database can be configured with:

```bash
DATABASE_URL="postgresql+psycopg://user:password@localhost/kanban"
```

The route and API layers do not directly depend on SQLite.

### 2.8 OpenAPI

FastAPI exposes the generated contract at:

```text
/docs
/openapi.json
```

A checked-in contract summary is also stored at:

```text
openapi.yaml
```

## 3. Deliberately Avoided Features

The following features are not implemented:

- User accounts
- Authentication or authorization
- Multi-user boards
- Multiple boards
- Team membership
- Comments
- Attachments
- Labels or tags
- Due dates
- Priorities
- Search
- Filtering
- Pagination
- Server-sent events
- WebSockets
- Offline synchronization
- Conflict resolution
- Audit history
- Soft deletion
- Database migrations
- Production deployment configuration
- PostgreSQL-specific optimizations
- External object storage
- Email or notification delivery
- Automated browser testing

## 4. Non-functional Requirements

- The backend must expose valid OpenAPI metadata.
- The API must return JSON for successful operations.
- The API must return appropriate HTTP status codes.
- The frontend must communicate with the backend using HTTP.
- Database access must remain isolated from route handlers through SQLAlchemy.
- The application must work with SQLite without manual schema setup.
- The application must be testable using an isolated test database.

## 5. Acceptance Criteria

The application is considered functional when:

1. The server starts without manual database setup.
2. The health endpoint returns `{"status": "ok"}`.
3. Tasks can be created, listed, updated, moved, and deleted.
4. Invalid task data is rejected.
5. Missing tasks return HTTP `404`.
6. Task positions and statuses persist between requests.
7. The generated OpenAPI document contains all implemented task endpoints.
8. Tests pass against an isolated SQLite database.
