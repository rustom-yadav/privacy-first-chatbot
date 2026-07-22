import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException, status, BackgroundTasks
from app.config import settings
from app.services.rag_service import rag_service

# Initialize the router component
router = APIRouter()

@router.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Endpoint to receive sensitive PDFs from the frontend.
    Validates the format, streams the file to a secure local path, 
    and prepares it for the RAG ingestion pipeline.
    """
    # 1. Validation: Ensure the uploaded file is strictly a PDF for privacy control
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format! Only secure PDF documents are allowed."
        )
    
    # 2. Setup the target destination storage path using Pathlib
    file_path = settings.UPLOAD_DIR / file.filename
    
    try:
        # 3. Stream write operation to save the file chunks on the disk securely
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save the file locally: {str(e)}"
        )
    finally:
        # Always close the file stream to prevent background memory leaks
        file.file.close()

    # 4. Trigger RAG Ingestion in the background so API returns fast
    background_tasks.add_task(rag_service.ingest_document, file_path)

    # 5. Success Response
    return {
        "status": "success",
        "filename": file.filename,
        "saved_at": str(file_path),
        "message": "File successfully uploaded. Ingestion has started in the background."
    }