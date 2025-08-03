from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app instance
app = FastAPI(title="30 Days of Voice Agents", version="1.0.0")

# Pydantic models for TTS API
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-natalie"  # Default voice
    
class TTSResponse(BaseModel):
    success: bool
    audio_url: str = None
    message: str = ""

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main index page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "30 Days of Voice Agents - Day 2: TTS Ready!"}

@app.post("/api/tts", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """
    Generate speech from text using Murf's TTS API
    
    - **text**: The text to convert to speech
    - **voice_id**: Voice ID to use (default: en-US-sarah)
    """
    try:
        # Get API key from environment
        api_key = os.getenv("MURF_API_KEY")
        
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="MURF_API_KEY not configured. Please set up your .env file."
            )
        
        # For Day 2 demonstration: Create endpoint structure for Murf TTS API
        # In production, you would use: from murf import Murf
        # client = Murf(api_key=api_key)
        # response = client.text_to_speech.generate(text=request.text, voice_id=request.voice_id)
        
        # Simulate API call structure for demonstration
        if len(request.text.strip()) == 0:
            return TTSResponse(
                success=False,
                message="Text cannot be empty"
            )
        
        # Demonstrate successful TTS endpoint structure
        # In production, this would be the actual audio URL from Murf
        demo_audio_url = f"https://murf-demo-audio.s3.amazonaws.com/{request.voice_id}/generated_audio.mp3"
        
        return TTSResponse(
            success=True,
            audio_url=demo_audio_url,
            message=f"TTS endpoint ready! Generated speech for {len(request.text)} characters using {request.voice_id}. (Demo response - integrate with actual Murf SDK for production)"
        )
        
    except Exception as e:
        return TTSResponse(
            success=False,
            message=f"Error in TTS endpoint: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)