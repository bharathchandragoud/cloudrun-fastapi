
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, File, UploadFile, HTTPException
from google.cloud import storage
import os
from datetime import datetime
import uuid


app = FastAPI(title="AI Image/Video Generator")

PROJECT_ID="test-fast-api-475508"
REGION="us-central1"
DB_INSTANCE="neuro-ai-postgres-instance"
DB_NAME="neuro_asset_db"
DB_USER="admin_user"
DB_PASS="Aidevgroup@321"
BUCKET="neuro-ai-assets-buckett"


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
async def upload_image(file: UploadFile = File(...)):

    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"generated-images/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Cloud Storage
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(file_content, content_type=file.content_type)
        
        # Make blob publicly readable (optional)
        # blob.make_public()
        
        # Get public URL (if public) or signed URL (if private)
        public_url = blob.public_url
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "filename": unique_filename,
            "url": public_url,
            "size": len(file_content),
            "content_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

