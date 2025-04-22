from fastapi import APIRouter, UploadFile, HTTPException
import shutil
import uuid
import os
import logging

from app.services.document_processing import load_and_chunk
from app.services.embeddings import get_gemini_embeddings
from app.db.vectorstore import store_chunks

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.post("/upload")  # Correct path, without 'api'
async def upload_file(file: UploadFile):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load and chunk the document
        chunks = load_and_chunk(file_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="Document could not be parsed or is empty.")

        logging.info(f"Number of chunks generated: {len(chunks)}")

        # Get embeddings
        embeddings = get_gemini_embeddings()
        if not embeddings:
            raise HTTPException(status_code=500, detail="Embeddings could not be initialized.")

        user_id = "user_" + str(uuid.uuid4())[:8]

        # Store in vectorstore
        msg = store_chunks(chunks, embeddings, user_id)
        return {"message": msg, "user_id": user_id}

    except Exception as e:
        logging.error(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
