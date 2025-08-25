# Data Store Service

FastAPI service that manages document metadata storage in PostgreSQL with multi-tenant support.

## Endpoints

### POST /clients/{client_id}/documents

Stores document metadata in the database for a specific client.

**Request:**

```json
{
  "filename": "example.txt",
  "file_size": 1024,
  "file_type": "text/plain",
  "content_type": "text/plain",
  "file_path": "/app/uploads/example.txt"
}
```

**Response:**

```json
{
  "id": 1,
  "client_id": "test-client-123",
  "filename": "example.txt",
  "file_size": 1024,
  "file_type": "text/plain",
  "content_type": "text/plain",
  "upload_timestamp": "2024-01-01T12:00:00Z",
  "file_path": "/app/uploads/example.txt"
}
```

### GET /clients/{client_id}/documents/{document_id}

Retrieves document metadata by client ID and document ID.

**Response:**

```json
{
  "id": 1,
  "client_id": "test-client-123",
  "filename": "example.txt",
  "file_size": 1024,
  "file_type": "text/plain",
  "content_type": "text/plain",
  "upload_timestamp": "2024-01-01T12:00:00Z",
  "file_path": "/app/uploads/example.txt"
}
```

### GET /health

Health check endpoint.

## Database Schema

The service uses PostgreSQL with the following table structure:

```sql
CREATE TABLE document_metadata (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR NOT NULL,
    filename VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR NOT NULL,
    content_type VARCHAR,
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_path VARCHAR
);

CREATE INDEX ix_document_metadata_client_id ON document_metadata (client_id);
CREATE INDEX ix_document_metadata_filename ON document_metadata (filename);
CREATE INDEX ix_document_metadata_id ON document_metadata (id);
```

## Configuration

Environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `OTEL_SERVICE_NAME`: OpenTelemetry service name (default: "data-store")
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OpenTelemetry collector endpoint

## Development

```bash
# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Run in development mode
poetry run uvicorn main:app --reload --port 8001
```
