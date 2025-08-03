# 🎙️ 30 Days of Voice Agents

Welcome to the "30 Days of Voice Agents" challenge by Murf AI! This repository contains the progressive development of a voice agent project over 30 days.

## 📅 Progress Tracker

- **Day 1**: ✅ Project Setup - FastAPI backend with frontend
- **Day 2**: ✅ Your First REST TTS Call - TTS endpoint with Murf API integration
- **Day 3**: 🔄 Coming soon...

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/30-days-of-agents.git
   cd 30-days-of-agents
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
   # Copy and edit the environment file
   cp .env.example .env
   # Edit .env and add your Murf API key:
   MURF_API_KEY=your_actual_murf_api_key_here
   MURF_API_BASE_URL=https://api.murf.ai/v1
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - Main app: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/health

## 📁 Project Structure

```
30-days-of-agents/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── day2_demo.py           # Day 2 demonstration script
├── test_tts.py            # TTS endpoint testing
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── script.js          # JavaScript functionality
│   └── style.css          # Styling
└── README.md              # This file
```

## 🎯 Features by Day

### Day 1: Project Setup ✅
- ✅ FastAPI backend with auto-documentation
- ✅ HTML template rendering with Jinja2
- ✅ Static file serving (CSS, JS)
- ✅ Interactive frontend with JavaScript
- ✅ Health check API endpoint

### Day 2: REST TTS API ✅
- ✅ TTS endpoint: `POST /api/tts`
- ✅ Secure API key management
- ✅ Request/response validation with Pydantic
- ✅ Error handling and logging
- ✅ Interactive API documentation

## 🔧 API Endpoints

### `GET /`
Serves the main HTML page

### `GET /api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "message": "30 Days of Voice Agents - Day 2: TTS Ready!"
}
```

### `POST /api/tts`
Text-to-Speech conversion endpoint

**Request:**
```json
{
  "text": "Hello! Welcome to Day 2 of voice agents.",
  "voice_id": "en-US-natalie"
}
```

**Response:**
```json
{
  "success": true,
  "audio_url": "https://generated-audio-url.mp3",
  "message": "Successfully generated speech for 42 characters using en-US-natalie"
}
```

## 🧪 Testing

### Run All Tests
```bash
# Test TTS endpoint
python test_tts.py

# Day 2 demonstration
python day2_demo.py
```

### Manual Testing
1. Open http://localhost:8000/docs
2. Try the `/api/tts` endpoint with sample data
3. Verify responses and error handling

## 🔐 Environment Setup

Create a `.env` file with:
```env
MURF_API_KEY=your_murf_api_key_here
MURF_API_BASE_URL=https://api.murf.ai/v1
```

**⚠️ Important:** Never commit your `.env` file to git!

## 🏗️ Development

### Adding New Days
1. Add new endpoints to `main.py`
2. Create corresponding test files
3. Update this README with progress
4. Follow the established patterns for consistency

### Code Style
- Use FastAPI best practices
- Type hints for all functions
- Pydantic models for request/response validation
- Environment variables for configuration
- Comprehensive error handling

## 🤝 Contributing

This is a personal learning project for the "30 Days of Voice Agents" challenge. Feel free to:
- Fork and create your own version
- Share improvements via issues
- Use as reference for your own voice agent projects

## 📝 License

MIT License - feel free to use this code for your own learning and projects.

## 🙏 Acknowledgments

- **Murf AI** for the "30 Days of Voice Agents" challenge
- **FastAPI** for the excellent web framework
- **Python community** for the amazing ecosystem

## 📞 Contact

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)

---

**Current Status**: Day 2 Complete ✅  
**Next**: Day 3 - Stay tuned! 🎙️
