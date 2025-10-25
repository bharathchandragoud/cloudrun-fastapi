from fastapi import FastAPI
from google.cloud import storage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI(title="AI Image/Video Generator")

PROJECT_ID="test-fast-api-475508"
REGION="us-central1"
DB_INSTANCE="neuro-ai-postgres-instance"
DB_NAME="neuro_asset_db"
DB_USER="admin_user"
DB_PASS="Aidevgroup@321"
BUCKET="neuro-ai-assets-bucket"


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://{DB_USER}:{DB_PASS}@/{DB_NAME}?host=/cloudsql/{PROJECT_ID}:REGION:{DB_INSTANCE}"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cloud Storage client
storage_client = storage.Client()
BUCKET_NAME = os.getenv("BUCKET_NAME", BUCKET)

@app.get("/")
async def root():
    return {"message": "AI Service Running on Cloud Run"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example: Upload generated image to Cloud Storage
@app.post("/upload-image")
async def upload_image(file_name: str, file_data: bytes):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"generated-images/{file_name}")
    blob.upload_from_string(file_data, content_type="image/png")
    
    # Get public URL
    public_url = blob.public_url
    
    return {
        "message": "Image uploaded successfully",
        "url": public_url
    }
