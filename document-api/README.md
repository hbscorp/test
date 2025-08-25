# Document API Service

FastAPI service that handles document uploads and metadata retrieval with multi-tenant support.

## Endpoints

### PUT /clients/{client_id}/upload-document
Uploads a document and stores its metadata for a specific client.

**Request:**
- Method: PUT
- Path parameter: client_id (string)
- Content-Type: multipart/form-data
- Body: file (required)

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "client_id": "test-client-123",
  "document_id": 1,
  "metadata": {
    "id": 1,
    "client_id": "test-client-123",
    "filename": "example.txt",
    "file_size": 1024,
    "file_type": "text/plain",
    "content_type": "text/plain",
    "upload_timestamp": "2024-01-01T12:00:00Z",
    "file_path": "/app/uploads/test-client-123_20240101_120000_example.txt"
  }
}
```

### GET /clients/{client_id}/documents/{document_id}
Retrieves metadata for a specific document belonging to a client.

**Request:**
- Method: GET
- Path parameters: 
  - client_id (string)
  - document_id (integer)

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
  "file_path": "/app/uploads/test-client-123_20240101_120000_example.txt"
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "document-api"
}
```

## Configuration

The service can be configured using environment variables:

- `DATA_STORE_URL`: URL of the data-store service (default: `http://localhost:8001`)

## Development

```bash
# Install dependencies
poetry install

# Run in development mode
poetry run uvicorn main:app --reload --port 8000
```
