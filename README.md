# 🎤 VoiceForge - Professional Text-to-Speech Platform

**Transform your text into natural-sounding speech with cutting-edge AI technology.**

VoiceForge is a modern, professional text-to-speech platform that converts your written content into high-quality audio using advanced AI voices. Perfect for creating voiceovers, audiobooks, podcasts, and accessibility solutions.

![VoiceForge Platform](https://img.shields.io/badge/Platform-Text--to--Speech-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)

## ✨ Features

- **🎯 Professional Interface** - Modern, responsive web application
- **⚡ Lightning Fast** - Generate high-quality audio in seconds
- **🎭 Multiple Voices** - Choose from various natural-sounding AI voices
- **🔊 Studio Quality** - Professional-grade audio output
- **📱 Responsive Design** - Works seamlessly on desktop and mobile
- **🔒 Secure API** - RESTful API with proper error handling
- **🎨 Smooth Animations** - Engaging user experience with modern animations
- **♿ Accessible** - Built with accessibility best practices

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- Murf AI API key (for text-to-speech generation)

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
   
   # Edit .env and add your Murf API key:
   MURF_API_KEY=your_actual_murf_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access VoiceForge**
   - **Main Platform**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health

## 🏗️ Architecture

VoiceForge is built with modern web technologies:

```
voiceforge/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── templates/
│   └── index.html         # Professional SPA frontend
├── static/
│   ├── script.js          # Modern JavaScript with animations
│   └── style.css          # Professional CSS with responsive design
└── README.md              # This documentation
```

### Technology Stack

- **Backend**: FastAPI + Python 3.11+
- **Frontend**: Modern HTML5, CSS3, JavaScript ES6+
- **AI/TTS**: Murf AI API integration
- **Styling**: Custom CSS with CSS Grid, Flexbox, and animations
- **Fonts**: Google Fonts (Inter)
- **Deployment**: Production-ready ASGI server

## 🔧 API Reference

### Core Endpoints

#### `GET /`
Serves the main VoiceForge web application

#### `GET /api/health`
System health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "30 Days of Voice Agents - Day 2: TTS Ready!"
}
```

#### `POST /api/tts`
Convert text to speech using AI voices

**Request:**
```json
{
  "text": "Welcome to VoiceForge, where your words come to life!",
  "voice_id": "en-US-terrell"
}
```

**Response:**
```json
{
  "success": true,
  "audio_file": "https://generated-audio-url.mp3",
  "message": "Audio file generated successfully. The link will be available for 72 hours."
}
```

**Available Voices:**
- `en-US-terrell` - Professional Male Voice
- `en-US-sarah` - Warm Female Voice (if configured)
- `en-US-mike` - Friendly Male Voice (if configured)

### Error Handling

The API provides comprehensive error handling:

```json
{
  "detail": "Error description here"
}
```

Common error codes:
- `400` - Bad Request (empty text, invalid parameters)
- `500` - Internal Server Error (API issues, network problems)

## 🎨 Frontend Features

### Modern User Interface
- **Responsive Design**: Works on all screen sizes
- **Smooth Animations**: Professional hover effects and transitions
- **Interactive Elements**: Real-time feedback and loading states
- **Accessibility**: Keyboard navigation and screen reader support

### Animation System
- **Sound Wave Visualization**: Animated sound bars in hero section
- **Scroll Animations**: Elements animate in as you scroll
- **Hover Effects**: Interactive buttons and cards
- **Smooth Scrolling**: Navigation with smooth scroll behavior

### User Experience
- **Professional Branding**: Modern VoiceForge identity
- **Intuitive Interface**: Clean, focused design
- **Real-time Feedback**: Status messages and loading indicators
- **Auto-play Audio**: Generated audio plays automatically (when permitted)

## 🔐 Security & Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Murf AI Configuration
MURF_API_KEY=your_murf_api_key_here
MURF_API_BASE_URL=https://api.murf.ai/v1

# Application Configuration (optional)
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Security Best Practices
- ✅ Environment variables for sensitive data
- ✅ API key validation and error handling
- ✅ Request validation with Pydantic models
- ✅ CORS configuration for production
- ✅ Input sanitization and length limits

## 🧪 Testing

### Manual Testing
1. **Web Interface**: Open http://localhost:8000
2. **Enter Text**: Type or paste text in the textarea
3. **Select Voice**: Choose from available voice options
4. **Generate Audio**: Click "Generate Speech" button
5. **Listen**: Audio will play automatically or click play button

### API Testing
Use the interactive API documentation at http://localhost:8000/docs to:
- Test all endpoints
- View request/response schemas
- Try different voice options and text inputs

### Health Check
```bash
curl http://localhost:8000/api/health
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

VoiceForge is optimized for performance:
- **Fast API responses** with efficient request handling
- **Optimized frontend** with modern CSS and JavaScript
- **Minimal dependencies** for quick startup
- **Responsive design** that works on all devices
- **Progressive enhancement** for better accessibility

## 🛠️ Troubleshooting

### Common Issues

**API Key Issues:**
```bash
# Check if environment variables are loaded
python -c "import os; print(os.getenv('MURF_API_KEY'))"
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Module Not Found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Getting Help

- **Check API Documentation**: http://localhost:8000/docs
- **Review Logs**: Check console output for error messages
- **Verify Configuration**: Ensure `.env` file is properly configured
- **Test API Endpoints**: Use the interactive API docs for testing

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Murf AI** for providing the advanced text-to-speech API
- **FastAPI** for the excellent Python web framework
- **Inter Font** by Google Fonts for beautiful typography
- **Open Source Community** for amazing tools and libraries

## 📞 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/voiceforge/issues)
- **Contact**: [Your Contact Information]

---

**VoiceForge** - *Transform your words into beautiful, natural-sounding speech* 🎤✨