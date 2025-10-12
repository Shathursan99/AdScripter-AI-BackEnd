# api/router.py

import json
import io
from typing import List
import asyncio  

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request
from PIL import Image

from core.schemas import ContentRequest, ContentResponse, ErrorResponse
from core.gemini import generate_content_from_images 

router = APIRouter(
    prefix="/content",
    tags=["Content Generation"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Input or Missing File"},
        422: {"model": ErrorResponse, "description": "Validation Error (e.g., Invalid JSON)"},
        500: {"model": ErrorResponse, "description": "Internal Server or AI Error"},
        503: {"model": ErrorResponse, "description": "AI Service Unavailable"}
    }
)

async def process_images(files: List[UploadFile], request: Request) -> List[Image.Image]:
    
    if not files:
        raise HTTPException(status_code=400, detail="No product images uploaded. At least one image is required.")
    
    images = []
    for file in files:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid image type.")
            
        content = await file.read()
        
        try:
            image = await asyncio.to_thread(Image.open, io.BytesIO(content))
            images.append(image)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=400, 
                detail=f"Could not process image file: {file.filename}. Reason: {type(e).__name__}: {str(e)}"
            )
            
    return images


@router.post(
    "/generate", 
    response_model=ContentResponse,
    status_code=status.HTTP_200_OK,
)
async def generateProductContent(
    request: Request, 
    files: List[UploadFile] = File(..., description="One or more images of the product."),
    context_data: str = Form(..., description="JSON string of the required ContentRequest data.")
):
    
    try:
        user_context_model = ContentRequest.model_validate_json(context_data)
        user_context_dict = user_context_model.model_dump()
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid JSON format for context_data or missing required fields.")

    processed_images = await process_images(files, request) 


    try:
        ai_response = await generate_content_from_images(processed_images, user_context_dict)
        return ai_response
    
    except ConnectionError:
        raise HTTPException(status_code=503, detail="AI Service connection failed. Check API key and service status.")
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise HTTPException(status_code=500, detail="AI content generation failed due to an unexpected server error.")