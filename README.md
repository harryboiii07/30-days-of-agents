# 🎤 VoiceForge - AI Voice Assistant Platform

**Complete AI voice interaction platform with natural conversations, speech recognition, and intelligent responses.**

VoiceForge is an advanced AI voice assistant platform that enables natural conversations through voice. It combines speech-to-text transcription, large language model intelligence, text-to-speech synthesis, persistent chat history, and real-time WebSocket communication. Perfect for creating conversational AI applications, voice interfaces, and intelligent chatbots.

![VoiceForge Platform](https://img.shields.io/badge/Platform-Text--to--Speech-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)

## ✨ Features

### 🎙️ **Voice Interaction**
- **🎤 Speech Recognition** - AssemblyAI-powered transcription with high accuracy
- **🗣️ Natural Conversations** - Google Gemini LLM for intelligent responses
- **🔊 Voice Synthesis** - Murf AI for professional-quality text-to-speech
- **💬 Session-based Chat** - Persistent conversation history with MongoDB

### 🌐 **Real-time Communication**
- **⚡ WebSocket Support** - Real-time bidirectional communication (`/ws`)
- **📡 JSON & Text Messaging** - Structured and plain text message handling
- **🔄 Connection Management** - Multi-client support with connection tracking

### 🤖 **AI & Intelligence**
- **🧠 LLM Integration** - Google Gemini 2.0 Flash for contextual responses
- **📚 Context Awareness** - Chat history integration for natural conversations
- **🎯 Smart Fallbacks** - Graceful error handling with alternative responses
- **⚙️ Auto Text Trimming** - Intelligent text processing for TTS limits

### 🏗️ **Platform Features**
- **📱 Responsive Design** - Modern, mobile-first interface
- **🔒 Secure API** - Environment-based configuration and validation
- **🎨 Professional UI** - Smooth animations and intuitive user experience
- **♿ Accessibility** - Built with accessibility best practices
- **📊 Health Monitoring** - System status and service health checks

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- **API Keys Required:**
  - Murf AI API key (for text-to-speech generation)
  - AssemblyAI API key (for speech recognition)
  - Google Gemini API key (for LLM responses)
  - MongoDB connection string (for chat history persistence)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/voiceforge.git
   cd voiceforge
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create environment file
   cp .env.example .env
   
   # Edit .env and add your API keys:
   MURF_API_KEY=your_murf_api_key_here
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URL=your_mongodb_connection_string_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access VoiceForge**
   - **Main Platform**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health
   - **WebSocket Endpoint**: ws://localhost:8000/ws

## 🏗️ Architecture

VoiceForge is built with modern web technologies:

```
voiceforge/
├── main.py                 # FastAPI backend server with AI voice assistant
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (API keys & configuration)
├── templates/
│   └── index.html         # AI Voice Assistant web interface
├── static/
│   ├── script.js          # Voice chat functionality with WebRTC
│   └── style.css          # Modern responsive design
├── uploads/               # Temporary audio file storage
└── README.md              # This documentation
```

### Technology Stack

- **Backend**: FastAPI + Python 3.11+ with async/await
- **Frontend**: Modern HTML5, CSS3, JavaScript ES6+ with WebRTC
- **AI Services**: 
  - Google Gemini 2.0 Flash (LLM)
  - Murf AI (Text-to-Speech)
  - AssemblyAI (Speech-to-Text)
- **Database**: MongoDB Atlas (Chat History)
- **Real-time**: WebSocket communication
- **Styling**: Custom CSS with animations and responsive design
- **Fonts**: Google Fonts (Inter)
- **Deployment**: Production-ready ASGI server with Uvicorn

## 🔧 API Reference

### Core Endpoints

#### `GET /`
Serves the main VoiceForge AI Voice Assistant web application

#### `GET /api/health`
System health check endpoint with service status

**Response:**
```json
{
  "status": "healthy",
  "message": "30 Days of Voice Agents - Day 10: Chat History Ready!",
  "services": {
    "mongodb": {
      "status": "connected",
      "database": "voiceforge_chat_history",
      "collection": "chat_sessions",
      "document_count": 42
    }
  }
}
```

### Voice Assistant Endpoints

#### `POST /agent/chat/{session_id}`
Complete voice interaction with AI assistant

**Parameters:**
- `session_id`: Unique session identifier for chat history persistence

**Request:** (Form Data)
- `audio_file`: Audio file (WebM, WAV, MP3, OGG) - max 25MB

**Response:**
```json
{
  "success": true,
  "session_id": "sess_1642123456_abc123",
  "user_message": "What's the weather like today?",
  "ai_response": "I'd be happy to help, but I don't have access to current weather data...",
  "audio_file": "https://murf-audio-url.mp3",
  "chat_history_length": 4,
  "complete_response": {
    "model": "gemini-2.0-flash-exp",
    "text": "Full AI response text",
    "context_used": true
  },
  "message": "Agent chat processed successfully with history. The audio link will be available for 72 hours."
}
```

#### `POST /transcribe/file`
Speech-to-text transcription service

**Request:** (Form Data)
- `audio_file`: Audio file to transcribe

**Response:**
```json
{
  "success": true,
  "transcription": "Hello, how are you today?",
  "confidence": 0.95,
  "language": "en",
  "processing_time": 2.3,
  "message": "Audio transcribed successfully"
}
```

#### `POST /api/tts`
Text-to-speech generation service

**Request:**
```json
{
  "text": "Welcome to VoiceForge AI Assistant!",
  "voice_id": "en-US-terrell"
}
```

**Response:**
```json
{
  "success": true,
  "audio_file": "https://murf-audio-url.mp3",
  "message": "Audio file generated successfully. The link will be available for 72 hours."
}
```

### Real-time Communication

#### `WebSocket /ws`
Real-time bidirectional communication

**Connection:** `ws://localhost:8000/ws`

**Text Message:**
```
Send: "Hello WebSocket!"
Receive: "Echo: Hello WebSocket!"
```

**JSON Message:**
```json
Send: {"type": "greeting", "content": "Hello AI!"}
Receive: {
  "type": "echo",
  "original_type": "greeting",
  "content": "Echo: Hello AI!",
  "timestamp": "2025-01-06T12:00:00Z",
  "connection_count": 1
}
```

### Error Handling

The API provides comprehensive error handling with user-friendly messages:

**Standard Error Response:**
```json
{
  "success": false,
  "error": "error_type",
  "message": "User-friendly error description",
  "fallback_audio": null
}
```

**Common Error Types:**
- `validation_error` - Invalid input (empty text, file too large, unsupported format)
- `configuration_error` - Missing API keys or service configuration
- `transcription_error` - Speech recognition failed
- `no_speech` - No speech detected in audio
- `service_error` - External service unavailable
- `api_error` - API response validation failed

**WebSocket Errors:**
- Connection drops are handled gracefully with automatic cleanup
- Invalid JSON messages fallback to text processing
- Connection state tracking prevents message loss

## 🎨 Frontend Features

### AI Voice Assistant Interface
- **Voice Chat UI**: Intuitive conversation interface with chat bubbles
- **Real-time Status**: Live recording indicator and processing progress
- **Session Management**: Persistent chat sessions with unique identifiers
- **Audio Controls**: Professional microphone button with visual feedback

### Voice Interaction Features
- **WebRTC Recording**: High-quality audio capture with noise suppression
- **Progress Tracking**: Step-by-step visual feedback during processing
- **Auto-play Responses**: AI voice responses play automatically
- **Recording Timer**: Visual recording duration display
- **Smart Fallbacks**: Browser TTS when server TTS fails

### User Experience Enhancements
- **Responsive Design**: Optimized for desktop and mobile devices
- **Smooth Animations**: Professional micro-interactions and transitions
- **Visual Feedback**: Recording indicators, pulse animations, and status updates
- **Error Handling**: User-friendly error messages with retry options
- **Accessibility**: Keyboard navigation and screen reader support
- **Auto-scroll**: Messages automatically scroll into view

## 🔐 Security & Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Required API Keys
MURF_API_KEY=your_murf_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here

# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/voiceforge_chat_history

# Optional Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000
USE_MOCK_LLM=false
```

### Security Best Practices
- ✅ Environment variables for sensitive data (API keys, DB credentials)
- ✅ API key validation and graceful error handling
- ✅ Request validation with Pydantic models
- ✅ File upload validation (type, size limits)
- ✅ Input sanitization and text length limits
- ✅ MongoDB connection with authentication
- ✅ WebSocket connection management and cleanup
- ✅ Timeout configurations to prevent hanging requests

## 🧪 Testing

### Voice Assistant Testing
1. **Voice Chat Interface**: Open http://localhost:8000
2. **Start Conversation**: Click the microphone button
3. **Speak**: Record your voice message (browser will request microphone permission)
4. **AI Response**: Watch the processing steps and listen to the AI response
5. **Continue Chat**: Continue the conversation with context awareness
6. **Clear Chat**: Start a new session with the clear button

### WebSocket Testing
Use Postman or a WebSocket client:
1. **Connect**: ws://localhost:8000/ws
2. **Send Text**: `Hello WebSocket!`
3. **Send JSON**: `{"type": "test", "content": "Hello AI!"}`
4. **Observe**: Structured responses with timestamps and connection count

### API Testing
Use the interactive API documentation at http://localhost:8000/docs to:
- Test voice assistant endpoints (`/agent/chat/{session_id}`)
- Test transcription service (`/transcribe/file`)
- Test text-to-speech (`/api/tts`)
- View request/response schemas
- Upload audio files and test voice interactions

### Service Health Checks
```bash
# Overall system health
curl http://localhost:8000/api/health

# Test individual services
curl -X POST -F "audio_file=@test.wav" http://localhost:8000/transcribe/file
curl -X POST -H "Content-Type: application/json" -d '{"text":"Test"}' http://localhost:8000/api/tts
```

## 🚀 Deployment

### Production Deployment

1. **Install production server**:
   ```bash
   pip install uvicorn[standard] gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:8000
   ```

3. **Or with Uvicorn**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

We welcome contributions to VoiceForge! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Test your changes thoroughly
- Update documentation as needed

## 📊 Performance

VoiceForge is optimized for high-performance voice interactions:
- **Async Processing**: FastAPI with async/await for concurrent request handling
- **Persistent Connections**: HTTP session reuse for faster API calls
- **WebSocket Efficiency**: Real-time communication with minimal overhead
- **Database Optimization**: MongoDB with connection pooling and retry logic
- **Smart Caching**: Audio file caching and intelligent text trimming
- **Error Recovery**: Graceful fallbacks and retry mechanisms
- **Resource Management**: Automatic cleanup of WebSocket connections and file uploads

## 🛠️ Troubleshooting

### Common Issues

**API Key Configuration:**
```bash
# Check if all required environment variables are loaded
python -c "
import os
keys = ['MURF_API_KEY', 'ASSEMBLYAI_API_KEY', 'GEMINI_API_KEY', 'MONGODB_URL']
for key in keys:
    value = os.getenv(key)
    print(f'{key}: {\"✅ Set\" if value else \"❌ Missing\"}')
"
```

**MongoDB Connection Issues:**
```bash
# Test MongoDB connection
python -c "
from pymongo import MongoClient
import os
try:
    client = MongoClient(os.getenv('MONGODB_URL'))
    client.admin.command('ping')
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"
```

**Microphone Permission Issues:**
- Browser blocks microphone access → Check site permissions
- HTTPS required for microphone in production → Use SSL certificates
- Multiple tabs accessing microphone → Close other audio applications

**WebSocket Connection Issues:**
```bash
# Test WebSocket connection
pip install websockets
python -c "
import asyncio
import websockets
async def test():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as ws:
            await ws.send('test')
            response = await ws.recv()
            print(f'✅ WebSocket test: {response}')
    except Exception as e:
        print(f'❌ WebSocket failed: {e}')
asyncio.run(test())
"
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Module Installation Issues:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Getting Help

- **Check API Documentation**: http://localhost:8000/docs
- **Review Logs**: Check console output for detailed error messages
- **System Health**: Monitor http://localhost:8000/api/health for service status
- **Test Individual Services**: Use API docs to test transcription, TTS, and voice chat
- **WebSocket Testing**: Use Postman or browser developer tools for WebSocket debugging
- **Database Status**: Check MongoDB Atlas dashboard for connection issues

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for providing advanced large language model capabilities
- **Murf AI** for high-quality text-to-speech synthesis
- **AssemblyAI** for accurate speech recognition technology
- **MongoDB Atlas** for reliable cloud database services
- **FastAPI** for the excellent async Python web framework
- **WebRTC** community for enabling browser-based audio recording
- **Inter Font** by Google Fonts for beautiful typography
- **Open Source Community** for amazing tools and libraries

## 📞 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **System Health**: [Health Check](http://localhost:8000/api/health)
- **WebSocket Testing**: ws://localhost:8000/ws
- **Issues**: [GitHub Issues](https://github.com/your-username/voiceforge/issues)
- **Contact**: [Your Contact Information]

---

**VoiceForge AI Assistant** - *Natural voice conversations with AI intelligence* 🤖🎤✨