from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv
from murf import Murf
import assemblyai as aai
from google import genai

# Load environment variables
load_dotenv()

# Configure AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "e6136224990d49f494f6bcf658569b7c")

# Create FastAPI app instance
app = FastAPI(title="VoiceForge - Text-to-Speech Platform", version="1.0.0")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models for TTS API
class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-terrell"

# Pydantic model for LLM API
class LLMRequest(BaseModel):
    text: str

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

def trim_text_for_tts(text: str, max_chars: int = 3000) -> str:
    """
    Trim text to fit within Murf TTS character limits while preserving sentence structure
    
    - **text**: The text to trim
    - **max_chars**: Maximum character limit (default: 3000 for Murf)
    
    Returns trimmed text that ends at a complete sentence when possible
    """
    if len(text) <= max_chars:
        return text
    
    # Find the last complete sentence within the limit
    # Look for sentence endings: . ! ?
    sentence_endings = ['.', '!', '?']
    
    # Start from the max_chars position and work backwards
    for i in range(max_chars - 1, max_chars // 2, -1):
        if text[i] in sentence_endings:
            # Check if this is actually the end of a sentence (not an abbreviation)
            # Simple heuristic: if followed by space and capital letter, it's likely a sentence end
            if i + 1 < len(text) and (i + 1 == len(text) or (text[i + 1] == ' ' and i + 2 < len(text) and text[i + 2].isupper())):
                trimmed = text[:i + 1].strip()
                if len(trimmed) > 50:  # Ensure we have a reasonable amount of text
                    return trimmed
    
    # If no good sentence break found, look for paragraph breaks
    for i in range(max_chars - 1, max_chars // 2, -1):
        if text[i] == '\n':
            trimmed = text[:i].strip()
            if len(trimmed) > 50:
                return trimmed
    
    # If no good break found, just cut at word boundary
    # Find the last space before the limit
    for i in range(max_chars - 1, max_chars // 2, -1):
        if text[i] == ' ':
            trimmed = text[:i].strip()
            if len(trimmed) > 50:
                return trimmed + "..."
    
    # Last resort: hard cut with ellipsis
    return text[:max_chars - 3].strip() + "..."

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main index page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "30 Days of Voice Agents - Day 2: TTS Ready!"}

@app.post("/api/tts")
async def generate_speech(request: TTSRequest):
    """
    Generate speech from text using Murf's TTS API
    
    - **text**: The text to convert to speech
    - **voice_id**: Voice ID to use (default: en-US-terrell)
    
    Returns the audio file URL from Murf's API
    """
    try:
        # Get API key from environment - not required if MURF_API_KEY is set
        api_key = os.getenv("MURF_API_KEY")
        
        # Validate input
        if len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Initialize Murf client
        client = Murf(api_key=api_key) if api_key else Murf()
        
        # Generate speech using Murf SDK
        res = client.text_to_speech.generate(
            text=request.text,
            voice_id=request.voice_id,
        )
        
        # Return the audio file URL
        return {
            "success": True,
            "audio_file": res.audio_file,
            "message": "Audio file generated successfully. The link will be available for 72 hours."
        }
        
    except Exception as e:
        # Handle any errors from the SDK
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}") from e

@app.post("/transcribe/file")
async def transcribe_file(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file using AssemblyAI
    
    - **audio_file**: The audio file to transcribe (WebM, WAV, MP3, etc.)
    
    Returns the transcription text
    """
    try:
        # Validate file type
        allowed_types = ["audio/webm", "audio/wav", "audio/mp3", "audio/mpeg", "audio/ogg"]
        if audio_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {audio_file.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read the file content directly into memory
        audio_data = await audio_file.read()
        
        # Configure transcription settings
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_detection=True,
            punctuate=True,
            format_text=True
        )
        
        # Create transcriber and transcribe the audio data
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_data)
        
        # Check for transcription errors
        if transcript.status == "error":
            raise HTTPException(
                status_code=500, 
                detail=f"Transcription failed: {transcript.error}"
            )
        
        # Return successful response
        return {
            "success": True,
            "transcription": transcript.text,
            "confidence": getattr(transcript, 'confidence', None),
            "language": getattr(transcript, 'language_code', None),
            "processing_time": getattr(transcript, 'audio_duration', None),
            "message": "Audio transcribed successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}") from e

@app.post("/tts/echo")
async def echo_with_tts(audio_file: UploadFile = File(...)):
    """
    Echo Bot v2: Transcribe audio and generate speech using Murf TTS
    
    - **audio_file**: The audio file to transcribe and echo back with Murf voice
    
    Returns the Murf-generated audio URL
    """
    try:
        print("🎤 Starting Echo Bot v2 processing...")
        
        # Step 1: Use existing transcription endpoint
        print("🎤 Transcribing audio using existing /transcribe/file endpoint...")
        transcription_result = await transcribe_file(audio_file)
        
        # Check if transcription was successful
        if not transcription_result.get("success") or not transcription_result.get("transcription"):
            raise HTTPException(
                status_code=400,
                detail="Transcription failed or no speech detected. Please try speaking more clearly."
            )
        
        transcription_text = transcription_result["transcription"]
        print(f"✅ Transcription successful: {transcription_text}")
        
        # Step 2: Use existing TTS endpoint to generate speech
        print("🎵 Generating speech using existing /api/tts endpoint...")
        
        # Create TTS request object
        tts_request = TTSRequest(
            text=transcription_text,
            voice_id="en-US-terrell"  # Default voice for echo
        )
        
        # Use existing TTS function
        tts_result = await generate_speech(tts_request)
        
        print(f"✅ Murf TTS successful: {tts_result['audio_file']}")
        
        # Return the response with both transcription and audio URL
        return {
            "success": True,
            "transcription": transcription_text,
            "audio_file": tts_result["audio_file"],
            "confidence": transcription_result.get("confidence"),
            "language": transcription_result.get("language"),
            "message": "Audio transcribed and converted to speech successfully. The audio link will be available for 72 hours."
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        print(f"❌ Echo TTS Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}") from e

@app.post("/llm/query")
async def llm_query(audio_file: UploadFile = File(None), request: LLMRequest = None):
    """
    Query the Gemini LLM API with text or audio input
    
    - **audio_file**: Optional audio file to transcribe and send to LLM
    - **request**: Optional text input to send to the LLM (for backward compatibility)
    
    Returns the LLM response along with Murf-generated audio
    """
    try:
        input_text = ""
        
        # Handle audio input
        if audio_file:
            print("🎤 Processing audio input for AI Voice Chatbot...")
            
            # Step 1: Transcribe the audio
            print("🎤 Transcribing audio using existing transcribe_file function...")
            transcription_result = await transcribe_file(audio_file)
            
            # Check if transcription was successful
            if not transcription_result.get("success") or not transcription_result.get("transcription"):
                raise HTTPException(
                    status_code=400,
                    detail="Transcription failed or no speech detected. Please try speaking more clearly."
                )
            
            input_text = transcription_result["transcription"]
            print(f"✅ Transcription successful: {input_text}")
            
        # Handle text input (for backward compatibility)
        elif request and request.text:
            input_text = request.text.strip()
            
        # Validate we have input
        if not input_text:
            raise HTTPException(status_code=400, detail="No text or audio input provided")
        
        print(f"🤖 Sending to LLM: {input_text}")
        
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Generate response using Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=input_text
        )
        
        # Extract response text
        response_text = response.text if hasattr(response, 'text') else str(response)
        print(f"🤖 LLM Response: {response_text}")
        
        # If audio input was provided, generate audio response using Murf
        audio_file_url = None
        if audio_file:
            print("🎵 Generating speech response using Murf TTS...")
            
            # Trim response text for Murf TTS (3,000 character limit)
            original_length = len(response_text)
            trimmed_response = trim_text_for_tts(response_text)
            
            if len(trimmed_response) < original_length:
                print(f"⚠️ AI response trimmed from {original_length} to {len(trimmed_response)} characters for TTS")
            
            # Create TTS request object with trimmed text
            tts_request = TTSRequest(
                text=trimmed_response,
                voice_id="en-US-terrell"  # Default voice for AI responses
            )
            
            # Use existing TTS function (echo_with_tts logic)
            tts_result = await generate_speech(tts_request)
            audio_file_url = tts_result["audio_file"]
            print(f"✅ Murf TTS successful: {audio_file_url}")
            
            # Update response_text to reflect what was actually spoken
            response_text = trimmed_response
        
        # Return comprehensive response
        response_data = {
            "success": True,
            "response_text": response_text,
            "input_text": input_text,
            "complete_response": {
                "model": "gemini-2.0-flash-exp",
                "text": response_text,
                "raw_response": str(response)  # Full response for debugging
            },
            "message": "LLM query processed successfully"
        }
        
        # Add audio file URL if audio was processed
        if audio_file_url:
            response_data["audio_file"] = audio_file_url
            response_data["message"] = "Audio transcribed, processed by LLM, and converted to speech successfully. The audio link will be available for 72 hours."
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any errors from the SDK or processing
        print(f"❌ LLM Query Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing LLM query: {str(e)}") from e

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)