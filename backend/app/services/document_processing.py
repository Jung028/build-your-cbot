
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_chunk(file_path: str):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    return chunks
