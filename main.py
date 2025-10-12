# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from api.router import router as content_router
from fastapi.middleware.cors import CORSMiddleware

from core.gemini import set_ai_client 


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception(
        "FATAL ERROR: GEMINI_API_KEY environment variable not set in .env file. "
        "Please create a .env file and add your key."
    )

try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY).aio
except Exception as e:
    raise RuntimeError(f"Error initializing Gemini Client: {e}") from e

set_ai_client(ai_client)


app = FastAPI(
    title="E-commerce Content Generator AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.include_router(content_router)

origins = [
    "http://localhost:8080",  
    "http://127.0.0.1:3000",
   
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the E-commerce Content Generator AI. Navigate to /docs for the API interface."}
    