from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
from typing import List  # Add this import

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for your frontend (React running on localhost:3000)
origins = [
    "http://localhost:3000",  # React frontend URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows CORS for the given origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the path to store uploaded documents
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 1. Load and parse documents ---
def load_documents(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(directory_path, filename))
        elif filename.endswith(".pdf"):
            loader = PDFPlumberLoader(os.path.join(directory_path, filename))
        else:
            continue
        documents.extend(loader.load())
    return documents

# --- 2. Chunk documents ---
def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

# --- 3. Generate embeddings using SentenceTransformers ---
def generate_embeddings(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts, convert_to_tensor=False)
    return texts, embeddings

# --- 4. Store in FAISS vector DB ---
def store_in_faiss(texts, embeddings):
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, texts

# --- 5. Full pipeline ---
def prepare_knowledge_base(path_to_docs):
    docs = load_documents(path_to_docs)
    chunks = chunk_documents(docs)
    texts, embeddings = generate_embeddings(chunks)
    index, texts = store_in_faiss(texts, embeddings)
    return index, texts

# Endpoint to handle document upload
@app.post("/upload")
async def upload_documents(documents: List[UploadFile] = File(...)):
    try:
        # Save uploaded files to the server
        saved_files = []
        for document in documents:
            file_location = os.path.join(UPLOAD_FOLDER, document.filename)
            with open(file_location, "wb") as file:
                file.write(await document.read())  # Save file to the server
            saved_files.append(file_location)

        # Load documents from the saved files
        docs = load_documents(UPLOAD_FOLDER)

        # Chunk documents and generate embeddings
        chunks = chunk_documents(docs)
        texts, embeddings = generate_embeddings(chunks)

        # Store embeddings in FAISS
        index, texts = store_in_faiss(texts, embeddings)

        # Return the stored documents and FAISS index
        return JSONResponse(content={"message": "Documents processed successfully", "files": saved_files})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
