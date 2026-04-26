from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_text_from_pdf, extract_policy_metadata
from app.services.nlp_service import extract_countries
from app.services.recommender import get_recommendations_for_text
import json

router = APIRouter()

@router.post("/pdf")
async def upload_policy_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read file bytes
    file_bytes = await file.read()
    
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    
    # Extract text
    text = extract_text_from_pdf(file_bytes)
    
    if len(text) < 100:
        raise HTTPException(status_code=400, detail="Could not extract enough text from PDF.")
    
    # Extract metadata
    metadata = extract_policy_metadata(text)
    
    # NLP — extract countries mentioned
    extracted_countries = extract_countries(text)
    
    # Get recommendations
    recommendations = get_recommendations_for_text(
        text=text,
        tags=metadata["tags"],
        title=metadata["title"]
    )
    
    return {
        "filename": file.filename,
        "title": metadata["title"],
        "year": metadata["year"],
        "tags": metadata["tags"],
        "extracted_countries": extracted_countries,
        "content_preview": text[:500] + "..." if len(text) > 500 else text,
        "word_count": len(text.split()),
        "recommendations": recommendations["recommendations"],
        "similar_policies": recommendations["similar_policies"],
        "ml_method": recommendations["ml_method"]
    }