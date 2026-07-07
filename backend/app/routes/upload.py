from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.pdf_service import extract_text_from_pdf, extract_policy_metadata
from app.services.nlp_service import extract_countries
from app.ml.recommender_v2 import get_recommendations_for_text
from app.auth import get_current_user
from app.database import get_connection
import json

router = APIRouter()

@router.post("/pdf")
async def upload_policy_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
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
    
    final_title = recommendations.get("detected_title") or metadata["title"]
    final_tags = recommendations.get("detected_tags") or metadata["tags"]
    
    # Save transaction to database history for profile audit
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO user_uploads (user_id, filename, title, tags, word_count, result_json)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                current_user["id"],
                file.filename,
                final_title,
                json.dumps(final_tags),
                len(text.split()),
                json.dumps({
                    "year": metadata["year"],
                    "extracted_countries": extracted_countries,
                })
            )
        )
        conn.commit()
    except Exception as db_err:
        print(f"Error logging upload history: {db_err}")
    finally:
        conn.close()
    
    return {
        "filename": file.filename,
        "title": final_title,
        "year": metadata["year"],
        "tags": final_tags,
        "extracted_countries": extracted_countries,
        "detected_sector": recommendations.get("detected_sector"),
        "content_preview": text[:500] + "..." if len(text) > 500 else text,
        "word_count": len(text.split()),
        "recommendations": recommendations["recommendations"],
        "similar_policies": recommendations["similar_policies"],
        "ml_method": recommendations["ml_method"],
        "executive_summary": recommendations.get("executive_summary", "")
    }