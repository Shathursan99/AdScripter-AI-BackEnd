# core/gemini.py

import io
from typing import List
from PIL import Image
from google import genai
from google.genai import types

from core.schemas import ContentResponse, ContentRequest 

AI_CLIENT = None
MODEL_NAME = "gemini-2.5-flash" 

def set_ai_client(client: genai.Client.aio):
    global AI_CLIENT
    AI_CLIENT = client

async def generate_content_from_images(
    images: List[Image.Image], 
    user_context: dict
) -> ContentResponse:
    
    if AI_CLIENT is None:
        raise ConnectionError("Gemini client is not initialized. Application startup failed.")

    target_platform = user_context.get('post_medium', '').lower()
    
    if target_platform in ['instagram', 'facebook']:
        description_format_instruction = (
            "Write an attractive and concise product description (25-35 words) tailored to the target platform tone. "
            "Use 1-2 short, impactful bullet points to highlight key features for quick social media reading. Add 1-2 relevant emojis if natural for the platform."
        )
        caption_instruction = (
            "Write a single-sentence social media caption (10-15 words) optimized for the style of the "
            f"Target Platform ({target_platform}). Add 1-2 relevant emojis if natural for the platform."
        )
    else:
        # Marketplace/E-commerce (Daraz, ikman.lk, eBay, Amazon): Detailed, SEO-focused blocks.
        description_format_instruction = (
            "Write a comprehensive, SEO-optimized product description (25-35 words) tailored to the target platform expectations. "
            "Use a brief, easy-to-read paragraph format suitable for a marketplace listing. Avoid emojis unless the platform commonly uses them."
        )
        caption_instruction = (
            "Write a brief, direct summary (10-15 words, single sentence) suitable as a short product headline/summary. Avoid emojis unless the platform commonly uses them."
        )
    # --- END CONDITIONAL LOGIC ---


    system_instruction = (
        "You are an expert e-commerce copywriter, SEO specialist, and market analyst. "
        "Your goal is to analyze the product images and user context to generate a highly accurate, "
        "professional, and persuasive product description, a short social media caption, and 8 SEO-optimized "
        "hashtags. You MUST return the output as a single JSON object that conforms STRICTLY to the required schema."
    )

    main_prompt = f"""
    Generate content for the product shown in the images.
    
    **USER CONTEXT:**
    - Target Platform: {user_context.get('post_medium', 'Not specified')}
    - Company/Store Name: {user_context.get('company_name', 'Not specified')}
    - Offer Status: {"YES, the post should emphasize a special offer/sale." if user_context.get('is_offer') else "NO special offer. Focus on product quality and features."}
    - Contact/Web Info: {user_context.get('contact_info', 'None provided')}
    - Key Selling Points/Keywords: {user_context.get('keywords', 'Analyze the images for key features.')}

    **INSTRUCTIONS:**
    1. **Description (seo_description field):** {description_format_instruction}
    2. **Caption (social_caption field):** {caption_instruction}
    3. **Hashtags:** Generate a list of 8 relevant, trending, and SEO-friendly hashtags.
    4. **Product Summary:** Provide a 1-sentence summary (10-15 words) of the product and its target audience.
    
    Return the result strictly as a JSON object matching the ContentResponse schema.
    """

    contents = images + [main_prompt]
    
    response = await AI_CLIENT.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json", 
            response_schema=ContentResponse,      
        )
    )
    
    return ContentResponse.model_validate_json(response.text)