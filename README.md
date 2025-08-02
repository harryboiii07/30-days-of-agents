# 🎙️ 30 Days of Voice Agents

Welcome to the "30 Days of Voice Agents" challenge by Murf AI! This repository contains the progressive development of a voice agent project over 30 days.

## 📅 Day 1: Project Setup ✅

**Task**: Initialize a Python backend using FastAPI, create a basic HTML file and JavaScript file, and serve the HTML page from the Python server.

### 🚀 What's Implemented

- ✅ **FastAPI Backend**: Modern Python web framework with automatic API documentation
- ✅ **HTML Template**: Responsive web page served by the backend
- ✅ **JavaScript Frontend**: Interactive functionality with API integration
- ✅ **Static File Serving**: CSS and JS files served efficiently
- ✅ **Health Check API**: Basic API endpoint for testing

### 🏗️ Project Structure

```
30-days-of-agents/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── script.js          # JavaScript functionality
│   └── style.css          # Styling
└── README.md              # This file
```

### 🛠️ Setup Instructions

1. **Clone/Navigate to the project directory**
   ```bash
   cd 30-days-of-agents
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open your browser**
   - Main page: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/health

### 🎯 Features

- **Interactive Frontend**: Click buttons to test JavaScript functionality
- **API Integration**: Frontend communicates with backend API
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, gradient-based design with smooth animations
- **Health Monitoring**: Built-in health check endpoint

### 🔮 What's Next

This is just Day 1! Over the next 29 days, we'll be adding:
- Voice recording and processing
- AI/ML integration
- Real-time communication
- Advanced voice agent capabilities
- And much more!

### 🐛 Troubleshooting

**Port already in use?**
```bash
# Change the port in main.py or run with:
uvicorn main:app --reload --port 8001
```

**Dependencies not installing?**
```bash
# Upgrade pip first:
pip install --upgrade pip
pip install -r requirements.txt
```

---

**Day 1 Status**: ✅ Complete
**Next**: Day 2 - Coming soon!

Happy coding! 🚀