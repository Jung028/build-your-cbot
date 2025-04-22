import os
from dotenv import load_dotenv
from google.auth import exceptions
from googleapiclient.discovery import build

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

def get_gemini_embeddings():
    try:
        service = build('gemini', 'v1', developerKey=gemini_api_key)
        response = service.embeddings().list().execute()  # Replace with correct method
        embeddings = response.get('embeddings', [])
        return embeddings
    except exceptions.DefaultCredentialsError as e:
        print(f"Authentication failed: {e}")
        raise
    except Exception as e:
        print(f"Error during API call: {e}")
        raise
