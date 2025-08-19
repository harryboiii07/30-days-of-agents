from fastapi import FastAPI, Request, UploadFile, File, WebSocket, WebSocketDisconnect
import json
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
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
from google import genai
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import List
from datetime import datetime
import asyncio
import subprocess
import threading
import queue

# Load environment variables
load_dotenv()

# Configure AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "e6136224990d49f494f6bcf658569b7c")

# Configure MongoDB with detailed debugging
mongodb_url = os.getenv("MONGODB_URL")
if not mongodb_url:
    raise ValueError("MONGODB_URL environment variable not set")

print("🔍 MongoDB Debug Information:")
print(f"📍 MongoDB URL: {mongodb_url[:50]}...{mongodb_url[-10:] if len(mongodb_url) > 60 else mongodb_url}")
print(f"🔗 URL Type: {'SRV' if '+srv' in mongodb_url else 'Standard'}")
print(f"📊 URL Length: {len(mongodb_url)} characters")

try:
    print("🔄 Creating MongoDB client (lazy connection)...")
    # Create client with lazy connection - don't test immediately to avoid DNS issues during reload
    client = MongoClient(
        mongodb_url,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=30000,  # 30 seconds for DNS resolution
        connectTimeoutMS=20000,          # 20 seconds for connection
        socketTimeoutMS=20000,           # 20 seconds for socket operations  
        maxPoolSize=1,                   # Single connection for startup
        retryWrites=True,
        # Additional settings for DNS stability
        maxIdleTimeMS=45000,
        waitQueueTimeoutMS=10000,
        # Lazy connection - don't connect immediately
        connect=False,  # This prevents immediate DNS resolution
    )
    
    print("✅ MongoClient created successfully (lazy connection)")
    
    # Set up database and collection references (no actual connection yet)
    db = client.voiceforge_chat_history
    chat_collection = db.chat_sessions
    
    # Only test connection if we're not in a reload scenario
    import __main__
    if hasattr(__main__, '__file__') and not hasattr(__main__, '_called_from_test'):
        try:
            print("🧪 Testing database connection...")
            client.admin.command('ping')
            print("✅ MongoDB ping successful!")
            
            # Test collection access
            print("🧪 Testing collection access...")
            collection_count = chat_collection.count_documents({})
            print(f"✅ Collection accessible, current document count: {collection_count}")
            
            print("🎉 MongoDB setup completed successfully!")
        except Exception as conn_test_error:
            print(f"⚠️ Initial connection test failed (will retry on first use): {conn_test_error}")
    else:
        print("🔄 Skipping connection test during reload - will connect on first use")
    
except Exception as e:
    print("❌ MongoDB Connection Failed!")
    print(f"🔍 Error Type: {type(e).__name__}")
    print(f"🔍 Error Message: {str(e)}")
    
    # Additional debug info for different error types
    if "DNS" in str(e) or "resolution" in str(e):
        print("\n🌐 DNS Resolution Debug:")
        print("- This appears to be a DNS resolution issue")
        print("- Check if you're using mongodb+srv:// format")
        print("- Verify your internet connection")
        print("- Try using a direct connection string instead of SRV")
        
    elif "timeout" in str(e).lower():
        print("\n⏱️ Timeout Debug:")
        print("- Connection is timing out")
        print("- Check if MongoDB Atlas IP whitelist includes your current IP")
        print("- Verify firewall settings")
        
    elif "authentication" in str(e).lower():
        print("\n🔐 Authentication Debug:")
        print("- Check username and password in connection string")
        print("- Verify database user permissions")
        
    print(f"\n🔍 Full MongoDB URL for debugging: {mongodb_url}")
    print("💡 Possible solutions:")
    print("1. Check your internet connection")
    print("2. Verify MongoDB Atlas cluster is running")
    print("3. Check IP whitelist in MongoDB Atlas")
    print("4. Try a different network connection")
    print("5. Use a direct connection string instead of SRV")
    
    # Don't fallback - raise the error to stop startup
    raise RuntimeError(f"MongoDB connection required but failed: {str(e)}") from e

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

# Pydantic models for Chat History
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None

class ChatSession(BaseModel):
    session_id: str
    chats: List[ChatMessage] = []
    created_at: datetime = None
    updated_at: datetime = None

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

def get_chat_history(session_id: str) -> List[ChatMessage]:
    """
    Retrieve chat history for a given session ID with connection retry
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Ensure connection is active
            if attempt == 0:
                client.admin.command('ping')  # Test connection
            
            session_doc = chat_collection.find_one({"session_id": session_id})
            if session_doc:
                return [ChatMessage(**chat) for chat in session_doc.get("chats", [])]
            return []
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Error retrieving chat history: {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to retrieve chat history after {max_retries} attempts")
                return []
            # Wait before retry
            import time
            time.sleep(1)
    return []

def save_chat_message(session_id: str, role: str, content: str) -> bool:
    """
    Save a chat message to the database with connection retry
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Ensure connection is active
            if attempt == 0:
                client.admin.command('ping')  # Test connection
                
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            # Try to update existing session, or create new one
            chat_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"chats": message},
                    "$set": {"updated_at": datetime.utcnow()},
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} - Error saving chat message: {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to save chat message after {max_retries} attempts")
                return False
            # Wait before retry
            import time
            time.sleep(1)
    return False

def format_chat_history_for_llm(chat_history: List[ChatMessage]) -> str:
    """
    Format chat history for LLM context
    """
    if not chat_history:
        return ""
    
    formatted_history = "Previous conversation:\n"
    for message in chat_history[-10:]:  # Keep last 10 messages for context
        role = "Human" if message.role == "user" else "Assistant"
        formatted_history += f"{role}: {message.content}\n"
    
    formatted_history += "\nCurrent message:\n"
    return formatted_history

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main index page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check endpoint with MongoDB status"""
    health_status = {
        "status": "healthy",
        "message": "30 Days of Voice Agents - Day 10: Chat History Ready!",
        "services": {}
    }
    
    # Check MongoDB connection
    try:
        client.admin.command('ping')
        collection_count = chat_collection.count_documents({})
        health_status["services"]["mongodb"] = {
            "status": "connected",
            "database": "voiceforge_chat_history",
            "collection": "chat_sessions",
            "document_count": collection_count
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["mongodb"] = {
            "status": "disconnected",
            "error": str(e)
        }
    
    return health_status

# WebSocket Connection Manager
class ConnectionManager:
    """
    WebSocket connection manager for handling multiple concurrent connections.
    
    Provides functionality for connecting, disconnecting, and messaging WebSocket clients.
    Automatically handles broken connections and maintains connection state.
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and add it to the active connections list."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from the active connections list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to all active WebSocket connections.
        
        Automatically removes broken connections during broadcast.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

# Initialize connection manager
manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional communication.
    
    Supports both plain text and structured JSON messages with intelligent response formatting.
    
    **Connection:** ws://localhost:8000/ws
    
    **Supported Message Types:**
    - Plain text: Receives "Hello" → Returns "Echo: Hello"
    - JSON messages: Receives {"type": "test", "content": "Hello"} → Returns structured response
    
    **JSON Response Format:**
    ```json
    {
        "type": "echo",
        "original_type": "test",
        "content": "Echo: Hello",
        "timestamp": "2025-01-06T12:00:00Z",
        "connection_count": 1
    }
    ```
    
    **Features:**
    - Multi-client support with connection tracking
    - Automatic JSON parsing and fallback to text
    - Graceful connection handling and cleanup
    - Real-time connection count in responses
    
    **Testing:**
    Use Postman WebSocket client, browser developer tools, or any WebSocket testing tool.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            
            # Log the received message
            print(f"📨 Received WebSocket message: {data}")
            
            # Try to parse as JSON for structured messages
            try:
                import json
                parsed_data = json.loads(data)
                
                # Handle structured message
                if isinstance(parsed_data, dict):
                    message_type = parsed_data.get("type", "unknown")
                    content = parsed_data.get("content", data)
                    
                    # Create structured response
                    response = {
                        "type": "echo",
                        "original_type": message_type,
                        "content": f"Echo: {content}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "connection_count": len(manager.active_connections)
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    print(f"📤 Sent WebSocket JSON echo: {response}")
                else:
                    # Handle simple JSON values
                    echo_message = f"Echo: {data}"
                    await manager.send_personal_message(echo_message, websocket)
                    print(f"📤 Sent WebSocket simple echo: {echo_message}")
                    
            except json.JSONDecodeError:
                # Handle plain text message
                echo_message = f"Echo: {data}"
                await manager.send_personal_message(echo_message, websocket)
                print(f"📤 Sent WebSocket text echo: {echo_message}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/audio_stream/{session_id}")
async def audio_stream_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time audio streaming.
    
    Receives binary audio chunks from the client and saves them to a file.
    
    **Connection:** ws://localhost:8000/ws/audio_stream/{session_id}
    
    **Features:**
    - Receives binary audio data chunks in real-time
    - Saves received audio to a file in the uploads directory
    - Handles both binary data and JSON control messages
    - Automatic file cleanup and connection management
    """
    await websocket.accept()
    print(f"🎤 Audio WebSocket connected for session: {session_id}")

    # Create file path for this session's raw audio (WebM) for debugging/auditing
    audio_filename = f"audio_stream_{session_id}_{int(datetime.utcnow().timestamp())}.webm"
    audio_filepath = UPLOAD_DIR / audio_filename

    audio_file = None
    total_chunks = 0
    total_bytes = 0

    # Prepare AssemblyAI streaming client
    loop = asyncio.get_event_loop()

    def on_begin(self: type[StreamingClient], event: BeginEvent):
        print(f"🟢 AAI session started: {event.id}")

    def on_turn(self: type[StreamingClient], event: TurnEvent):
        transcript_text = (event.transcript or "").strip()
        # Only mark final if we actually have recognized speech
        is_final = bool(event.end_of_turn and transcript_text)
        print(f"📝 Transcript ({'final' if is_final else 'partial'}): {transcript_text}")
        try:
            asyncio.run_coroutine_threadsafe(
                websocket.send_text(json.dumps({
                    "type": "transcript",
                    "text": transcript_text,
                    "final": is_final,
                })),
                loop,
            )
        except Exception as send_err:
            print(f"⚠️ Failed to send transcript to client: {send_err}")

        if event.end_of_turn and not event.turn_is_formatted:
            params = StreamingSessionParameters(format_turns=True)
            self.set_params(params)

    def on_terminated(self: type[StreamingClient], event: TerminationEvent):
        print(f"🔴 AAI session terminated: {event.audio_duration_seconds} seconds processed")

    def on_error(self: type[StreamingClient], error: StreamingError):
        print(f"❌ AAI streaming error: {error}")

    aai_client = None
    aai_stream_thread = None

    # Queued PCM pipeline fed by ffmpeg
    pcm_queue: "queue.Queue[bytes | None]" = queue.Queue(maxsize=50)
    stop_event = threading.Event()

    # Start ffmpeg to convert WebM/Opus -> PCM s16le mono 16k
    ffmpeg_proc = None
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-fflags",
            "+nobuffer",
            "-flags",
            "low_delay",
            "-f",
            "webm",
            "-i",
            "pipe:0",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "pipe:1",
        ]

        ffmpeg_proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install ffmpeg and ensure it is in PATH.")
        await websocket.close()
        return
    except Exception as e:
        print(f"❌ Failed to start ffmpeg: {e}")
        await websocket.close()
        return

    # Thread reading PCM from ffmpeg stdout and pushing to queue
    def read_pcm_from_ffmpeg():
        try:
            # ~100ms per chunk at 16kHz mono s16le = 16000 samples * 2 bytes * 0.1 = 3200 bytes
            chunk_size = 3200
            stdout = ffmpeg_proc.stdout
            while not stop_event.is_set():
                if stdout is None:
                    break
                data = stdout.read(chunk_size)
                if not data:
                    break
                pcm_queue.put(data)
        except Exception as e:
            print(f"⚠️ PCM reader thread error: {e}")
        finally:
            try:
                pcm_queue.put(None)
            except Exception:
                pass

    pcm_reader_thread = threading.Thread(target=read_pcm_from_ffmpeg, daemon=True)
    pcm_reader_thread.start()

    # Generator yielding PCM to AAI SDK
    def pcm_generator():
        while True:
            item = pcm_queue.get()
            if item is None:
                break
            # AAI expects bytes between ~50ms and 1000ms per chunk
            yield item

    # Start AssemblyAI streaming in a background thread
    def start_aai_streaming():
        nonlocal aai_client
        try:
            aai_client = StreamingClient(
                StreamingClientOptions(
                    api_key=os.getenv("ASSEMBLYAI_API_KEY"),
                    api_host="streaming.assemblyai.com",
                )
            )
            aai_client.on(StreamingEvents.Begin, on_begin)
            aai_client.on(StreamingEvents.Turn, on_turn)
            aai_client.on(StreamingEvents.Termination, on_terminated)
            aai_client.on(StreamingEvents.Error, on_error)

            aai_client.connect(
                StreamingParameters(
                    sample_rate=16000,
                    format_turns=True,
                )
            )

            aai_client.stream(pcm_generator())
        except Exception as e:
            print(f"❌ AAI streaming client error: {e}")
        finally:
            try:
                if aai_client:
                    aai_client.disconnect(terminate=True)
            except Exception:
                pass

    aai_stream_thread = threading.Thread(target=start_aai_streaming, daemon=True)
    aai_stream_thread.start()

    try:
        # Open file for binary writing (raw WebM for debugging)
        audio_file = open(audio_filepath, 'wb')
        print(f"📁 Created audio file: {audio_filepath}")

        while True:
            try:
                # Receive data from client
                message = await websocket.receive()

                if 'bytes' in message:
                    # Handle binary audio data
                    audio_chunk = message['bytes']
                    if audio_chunk:
                        # Save original chunk
                        audio_file.write(audio_chunk)
                        total_chunks += 1
                        total_bytes += len(audio_chunk)
                        # Feed ffmpeg for real-time decode/resample
                        try:
                            if ffmpeg_proc.stdin:
                                ffmpeg_proc.stdin.write(audio_chunk)
                                ffmpeg_proc.stdin.flush()
                        except Exception as pipe_err:
                            print(f"⚠️ ffmpeg stdin write error: {pipe_err}")
                        print(f"📼 Received audio chunk {total_chunks}: {len(audio_chunk)} bytes (total: {total_bytes} bytes)")

                elif 'text' in message:
                    # Handle text/JSON control messages
                    try:
                        control_msg = json.loads(message['text'])
                        if control_msg.get('type') == 'end_recording':
                            print(f"🛑 End of recording signal received for session: {session_id}")
                            break
                    except json.JSONDecodeError:
                        print(f"📝 Received text message: {message['text']}")

            except Exception as chunk_error:
                print(f"❌ Error processing audio chunk: {chunk_error}")
                continue

    except WebSocketDisconnect:
        print(f"🔌 Audio WebSocket client disconnected for session: {session_id}")
    except Exception as e:
        print(f"❌ Audio WebSocket error for session {session_id}: {e}")
    finally:
        # Signal end of input to ffmpeg
        try:
            if ffmpeg_proc and ffmpeg_proc.stdin:
                ffmpeg_proc.stdin.close()
        except Exception:
            pass

        # Wait for ffmpeg to finish flushing
        try:
            if ffmpeg_proc:
                ffmpeg_proc.wait(timeout=5)
        except Exception:
            pass

        # Stop PCM reader and streaming
        stop_event.set()
        try:
            pcm_queue.put(None)
        except Exception:
            pass
        try:
            if aai_stream_thread and aai_stream_thread.is_alive():
                aai_stream_thread.join(timeout=5)
        except Exception:
            pass

        # Clean up file resources
        if audio_file:
            audio_file.close()
            print(f"💾 Audio file saved: {audio_filepath}")
            print(f"📊 Final stats - Chunks: {total_chunks}, Total bytes: {total_bytes}")

            # Send confirmation back to client if connection is still open
            try:
                await websocket.send_text(json.dumps({
                    "type": "recording_complete",
                    "filename": audio_filename,
                    "chunks_received": total_chunks,
                    "total_bytes": total_bytes
                }))
            except Exception:
                pass  # Client may have already disconnected

        try:
            await websocket.close()
        except Exception:
            pass

@app.post("/api/tts")
async def generate_speech(request: TTSRequest):
    """
    Generate speech from text using Murf's TTS API
    
    - **text**: The text to convert to speech
    - **voice_id**: Voice ID to use (default: en-US-terrell)
    
    Returns the audio file URL from Murf's API
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            return {
                "success": False,
                "error": "validation_error",
                "message": "Text cannot be empty",
                "fallback_audio": None
            }
        
        if len(request.text) > 5000:
            return {
                "success": False,
                "error": "validation_error",
                "message": "Text is too long. Please limit to 5000 characters.",
                "fallback_audio": None
            }
        
        # Get API key from environment
        api_key = os.getenv("MURF_API_KEY")
        if not api_key:
            print("❌ TTS Error: MURF_API_KEY not found in environment")
            return {
                "success": False,
                "error": "configuration_error",
                "message": "I'm having trouble with the voice service configuration right now.",
                "fallback_audio": None
            }
        
        # Initialize Murf client
        murf_client = Murf(api_key=api_key)
        
        # Generate speech using Murf SDK
        res = murf_client.text_to_speech.generate(
            text=request.text,
            voice_id=request.voice_id,
        )
        
        # Validate response
        if not res or not hasattr(res, 'audio_file') or not res.audio_file:
            print("❌ TTS Error: Invalid response from Murf API")
            return {
                "success": False,
                "error": "api_error",
                "message": "I'm having trouble generating audio right now. Please try again.",
                "fallback_audio": None
            }
        
        # Return the audio file URL
        return {
            "success": True,
            "audio_file": res.audio_file,
            "message": "Audio file generated successfully. The link will be available for 72 hours."
        }
        
    except Exception as e:
        # Log the error
        print(f"❌ TTS Error: {type(e).__name__}: {str(e)}")
        
        # Return user-friendly error response
        return {
            "success": False,
            "error": "service_error",
            "message": "I'm having trouble connecting to the voice service right now. Please try again in a moment.",
            "fallback_audio": None
        }

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
            return {
                "success": False,
                "error": "validation_error",
                "message": f"Unsupported file type. Please use WebM, WAV, MP3, or OGG format.",
                "transcription": ""
            }
        
        # Check file size (limit to 25MB)
        if audio_file.size and audio_file.size > 25 * 1024 * 1024:
            return {
                "success": False,
                "error": "validation_error",
                "message": "Audio file is too large. Please use files under 25MB.",
                "transcription": ""
            }
        
        # Check if AssemblyAI API key is configured
        if not aai.settings.api_key:
            print("❌ STT Error: AssemblyAI API key not configured")
            return {
                "success": False,
                "error": "configuration_error",
                "message": "I'm having trouble with the speech recognition service configuration.",
                "transcription": ""
            }
        
        # Read the file content directly into memory
        audio_data = await audio_file.read()
        
        if not audio_data or len(audio_data) == 0:
            return {
                "success": False,
                "error": "validation_error",
                "message": "The audio file appears to be empty. Please try recording again.",
                "transcription": ""
            }
        
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
            print(f"❌ STT Error: {transcript.error}")
            return {
                "success": False,
                "error": "transcription_error",
                "message": "I couldn't understand the audio. Please try speaking more clearly or check your microphone.",
                "transcription": ""
            }
        
        # Check if transcription is empty or very short
        if not transcript.text or len(transcript.text.strip()) < 2:
            return {
                "success": False,
                "error": "no_speech",
                "message": "I didn't detect any speech in the audio. Please try speaking louder or closer to the microphone.",
                "transcription": ""
            }
        
        # Return successful response
        return {
            "success": True,
            "transcription": transcript.text,
            "confidence": getattr(transcript, 'confidence', None),
            "language": getattr(transcript, 'language_code', None),
            "processing_time": getattr(transcript, 'audio_duration', None),
            "message": "Audio transcribed successfully"
        }
        
    except Exception as e:
        # Log the error
        print(f"❌ STT Error: {type(e).__name__}: {str(e)}")
        
        # Return user-friendly error response
        return {
            "success": False,
            "error": "service_error",
            "message": "I'm having trouble connecting to the speech recognition service right now. Please try again.",
            "transcription": ""
        }





@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, audio_file: UploadFile = File(...)):
    """
    Chat with AI agent using voice input with persistent chat history
    
    - **session_id**: Unique session identifier for chat history
    - **audio_file**: Audio file containing user's voice message
    
    Returns AI response with audio output and maintains chat history
    """
    fallback_message = "I'm having trouble connecting right now. Please try again in a moment."
    
    try:
        print(f"🎤 Starting Agent Chat for session: {session_id}")
        
        # Step 1: Transcribe the audio
        print("🎤 Transcribing audio with AssemblyAI...")
        transcription_result = await transcribe_file(audio_file)
        
        # Check if transcription was successful
        if not transcription_result.get("success"):
            error_message = transcription_result.get("message", "I couldn't understand the audio. Please try again.")
            return {
                "success": False,
                "error": "transcription_error",
                "message": error_message,
                "fallback_audio": None
            }
        
        user_message = transcription_result["transcription"]
        print(f"✅ Transcription successful: {user_message}")
        
        # Step 2: Retrieve chat history (with fallback)
        print(f"📚 Retrieving chat history for session: {session_id}")
        try:
            chat_history = get_chat_history(session_id)
            print(f"📚 Found {len(chat_history)} previous messages")
        except Exception as db_error:
            print(f"⚠️ Database error retrieving chat history: {db_error}")
            chat_history = []  # Continue without history
        
        # Step 3: Format context for LLM
        context = format_chat_history_for_llm(chat_history)
        llm_input = context + user_message if context else user_message
        
        print(f"🤖 Sending to LLM with context: {llm_input[:200]}...")
        
        # Step 4: Get AI response
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ LLM Error: GEMINI_API_KEY not found in environment")
            return {
                "success": False,
                "error": "configuration_error",
                "message": "I'm having trouble with the AI service configuration right now.",
                "fallback_audio": None
            }
        
        try:
            gemini_client = genai.Client(api_key=api_key)
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=llm_input
            )
            
            ai_response = response.text if hasattr(response, 'text') else str(response)
            
            if not ai_response or len(ai_response.strip()) == 0:
                ai_response = "I'm not sure how to respond to that. Could you please try rephrasing your question?"
            
            print(f"🤖 LLM Response: {ai_response}")
            
        except Exception as llm_error:
            print(f"❌ LLM Error: {type(llm_error).__name__}: {str(llm_error)}")
            ai_response = fallback_message
        
        # Step 5: Save user message to chat history (with error handling)
        try:
            save_chat_message(session_id, "user", user_message)
            print(f"💾 Saved user message to session: {session_id}")
        except Exception as save_error:
            print(f"⚠️ Error saving user message: {save_error}")
        
        # Step 6: Save AI response to chat history (with error handling)
        try:
            save_chat_message(session_id, "assistant", ai_response)
            print(f"💾 Saved AI response to session: {session_id}")
        except Exception as save_error:
            print(f"⚠️ Error saving AI response: {save_error}")
        
        # Step 7: Generate audio response
        print("🎵 Generating speech response using Murf TTS...")
        
        # Trim response text for Murf TTS (3,000 character limit)
        original_length = len(ai_response)
        trimmed_response = trim_text_for_tts(ai_response)
        
        if len(trimmed_response) < original_length:
            print(f"⚠️ AI response trimmed from {original_length} to {len(trimmed_response)} characters for TTS")
        
        # Create TTS request object with trimmed text
        tts_request = TTSRequest(
            text=trimmed_response,
            voice_id="en-US-terrell"
        )
        
        # Generate speech with error handling
        tts_result = await generate_speech(tts_request)
        
        if tts_result.get("success"):
            audio_file_url = tts_result["audio_file"]
            print(f"✅ Murf TTS successful: {audio_file_url}")
        else:
            print(f"⚠️ TTS failed: {tts_result.get('message', 'Unknown error')}")
            audio_file_url = None
        
        # Step 8: Return comprehensive response
        return {
            "success": True,
            "session_id": session_id,
            "user_message": user_message,
            "ai_response": trimmed_response,
            "audio_file": audio_file_url,
            "chat_history_length": len(chat_history) + 2,  # +2 for current exchange
            "complete_response": {
                "model": "gemini-2.0-flash-exp",
                "text": ai_response,
                "context_used": bool(context)
            },
            "message": "Agent chat processed successfully" + (" with history" if chat_history else "") + (". The audio link will be available for 72 hours." if audio_file_url else " (audio generation failed).")
        }
        
    except Exception as e:
        # Handle any unexpected errors
        print(f"❌ Agent Chat Error: {type(e).__name__}: {str(e)}")
        
        return {
            "success": False,
            "error": "service_error",
            "message": fallback_message,
            "fallback_audio": None
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)