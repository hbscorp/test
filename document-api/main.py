import asyncio
import logging
from datetime import datetime
from pathlib import Path

import httpx
import magic
from config import get_settings
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from telemetry import init_observability


app = FastAPI(title="Document API", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOADS_DIR = Path("/app/uploads")
UPLOADS_DIR.mkdir(exist_ok=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "document-api"}


async def summarise_document_using_llm(file_path):
    """Summarise the document using a large language model."""

    # Call to real LLM API would go here - lets simulate with a sleep to fake the expensive LLM call
    await asyncio.sleep(10)
    return "This is a summary of the document."


@app.put("/clients/{client_id}/upload-document")
async def upload_document(
    client_id: str, file: UploadFile = File(...), settings=Depends(get_settings)
):
    """Upload a document and store its metadata for a specific client."""
    file_path = None
    try:
        content = await file.read()
        file_size = len(content)

        file_type = magic.from_buffer(content, mime=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{client_id}_{timestamp}_{file.filename}"
        file_path = UPLOADS_DIR / safe_filename

        with open(file_path, "wb") as f:
            f.write(content)

        metadata = {
            "client_id": client_id,
            "filename": file.filename,
            "file_size": file_size,
            "file_type": file_type,
            "content_type": file.content_type,
            "file_path": str(file_path),
            "summary": await summarise_document_using_llm(file_path),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.data_store_url}/clients/{client_id}/documents",
                json=metadata,
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(f"Failed to store metadata: {response.text}")
                raise HTTPException(
                    status_code=500, detail="Failed to store document metadata"
                )

            stored_metadata = response.json()

        logger.info(
            f"Successfully uploaded document: {file.filename} for client: {client_id}"
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Document uploaded successfully",
                "client_id": client_id,
                "document_id": stored_metadata["id"],
                "metadata": stored_metadata,
            },
        )

    except httpx.RequestError as e:
        logger.error(f"Error communicating with data-store: {str(e)}")
        raise HTTPException(status_code=503, detail="Data store service unavailable")
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")
    finally:
        if file_path and file_path.exists():
            file_path.unlink()

@app.get("/clients/{client_id}/documents/{document_id}")
async def retrieve_document_metadata(
    client_id: str, document_id: int, settings=Depends(get_settings)
):
    """Retrieve document metadata by client ID and document ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.data_store_url}/clients/{client_id}/documents/{document_id}",
                timeout=30.0,
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                logger.error(f"Failed to retrieve metadata: {response.text}")
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve document metadata"
                )

            metadata = response.json()

        logger.info(
            f"Retrieved metadata for document ID: {document_id} (client: {client_id})"
        )
        return metadata

    except httpx.RequestError as e:
        logger.error(f"Error communicating with data-store: {str(e)}")
        raise HTTPException(status_code=503, detail="Data store service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve document metadata"
        )


init_observability()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
