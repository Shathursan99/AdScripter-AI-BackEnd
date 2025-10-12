
from pydantic import BaseModel, Field
from typing import List, Optional

class ContentRequest(BaseModel):
    
    post_medium: str = Field(..., description="e.g., 'Instagram', 'Daraz', 'Etsy', 'eBay'.", example="Instagram")
    company_name: Optional[str] = Field(None, description="The name of the company or store.", example="Divelanka")
    is_offer: bool = Field(False, description="True if the post is for a sale or special offer.", example=True)
    contact_info: Optional[str] = Field(None, description="Contact number, website, or social handle.", example="@StylishGoodsSL")
    keywords: Optional[str] = Field(None, description="Specific SEO keywords or selling points to emphasize.", example="waterproof, durable, limited stock")

class ContentResponse(BaseModel):

    product_summary: str = Field(..., description="A short summary of the product, identified from the images.")
    social_caption: str = Field(..., description="A short, engaging caption optimized for the specified social media.")
    seo_description: str = Field(..., description="The main, professional, and SEO-optimized product description.")
    hashtags: List[str] = Field(..., description="A list of 8 relevant, trending, and SEO-friendly hashtags.")


class ErrorResponse(BaseModel):
    detail: str = Field(..., example="AI content generation failed. Please try again later.")