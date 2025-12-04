# 🎥 YouTube Twin - AI-Powered Video Chat Assistant

<div align="center">

![YouTube Twin](https://img.shields.io/badge/YouTube-Twin-red?style=for-the-badge&logo=youtube)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green?style=for-the-badge&logo=openai)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Chat with any YouTube video using AI. Get answers with precise timestamp references that link directly to relevant moments.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints)

</div>

---

## 📖 About

YouTube Twin transforms how you interact with video content. Simply paste a YouTube URL, and our AI processes the entire transcript, allowing you to ask questions and receive intelligent answers with exact timestamp links to relevant video segments.

### 🎯 Perfect For
- 📚 **Students** - Studying video lectures and finding specific topics
- 🎬 **Content Creators** - Analyzing competitor videos and extracting insights
- 📊 **Researchers** - Extracting information from interviews and presentations
- 💼 **Professionals** - Quickly finding information in training videos and webinars

---

## ✨ Features

### 🚀 Core Capabilities

- **🤖 AI-Powered Chat** - Natural language conversations powered by GPT-4 Turbo
- **⏱️ Timestamp Navigation** - Click timestamps to jump to exact video moments
- **🔍 Semantic Search** - Find content using natural language, not keywords
- **📝 Interactive Transcript** - Browse full transcript with clickable timestamps
- **🎯 Smart Chunking** - Intelligent 30-second segments with contextual overlap
- **💡 Source Attribution** - See which video segments generated each answer
- **🎨 Modern UI** - Clean, responsive dark-themed interface
- **⚡ Fast Processing** - Efficient embedding creation and retrieval

### 🔬 Technical Features

- **Vector Embeddings** - OpenAI `text-embedding-3-small` for semantic understanding
- **Cosine Similarity** - Accurate context retrieval using scikit-learn
- **YouTube Integration** - Embedded player with synchronized navigation
- **Real-time Chat** - Instant AI responses with streaming support
- **RESTful API** - Clean backend API for extensibility

---

## 🛠️ Tech Stack

**Backend:**
- Flask (Python web framework)
- OpenAI API (GPT-4 & Embeddings)
- youtube-transcript-api (Transcript fetching)
- scikit-learn (Vector similarity search)
- NumPy (Numerical operations)

**Frontend:**
- Vanilla JavaScript (No frameworks needed)
- YouTube IFrame API (Video player)
- Modern CSS (Responsive design)
- Google Fonts (Inter typography)

**AI Models:**
- `text-embedding-3-small` - Fast, accurate embeddings (1536 dimensions)
- `gpt-4-turbo-preview` - Intelligent chat responses

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Internet connection** for YouTube transcript fetching
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

---

## 🚀 Installation

### Quick Start (Windows)

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/youtube-twin.git
cd youtube-twin
```

2. **Configure Environment**

Create a `.env` file in the `backend` folder:

```bash
cd backend
copy .env.example .env
notepad .env
```

Add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. **Run the Application**

```bash
cd ..
run.bat
```

The script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Start backend server (port 5000)
- ✅ Start frontend server (port 8000)
- ✅ Open the app in your browser

### Manual Installation

If you prefer manual setup:

**Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start server
python app.py
```

**Frontend Setup (new terminal):**
```bash
cd frontend
python -m http.server 8000
```

**Access the app:** http://localhost:8000

---

## 📁 Project Structure

```
youtube-twin/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Your API keys (create this)
│   ├── .env.example             # Environment template
│   └── utils/
│       ├── __init__.py
│       ├── transcript_fetcher.py # YouTube transcript handling
│       ├── embeddings_manager.py # OpenAI embeddings
│       └── chat_handler.py       # Chat logic with GPT-4
├── frontend/
│   ├── index.html               # Main HTML structure
│   ├── style.css                # Styles and animations
│   └── script.js                # Frontend logic
├── run.bat                      # Windows startup script
├── run.sh                       # Linux/Mac startup script
└── README.md                    # This file
```

---

## 💡 Usage

### 1️⃣ Process a Video

1. Open http://localhost:8000 in your browser
2. Paste any YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click **"Process Video"**
4. Wait 10-30 seconds while the AI analyzes the transcript

### 2️⃣ Chat with the Video

Once processed, you can:

**Ask Questions:**
```
"What are the main topics discussed?"
"Explain the concept mentioned at 5:30"
"What does the speaker say about AI?"
```

**Use Suggested Questions:**
- Click pre-built questions for instant insights
- Perfect for getting started quickly

**View Sources:**
- See which video segments were used for each answer
- Click source timestamps to verify information

### 3️⃣ Navigate the Video

**Click Timestamps:**
- In chat responses: `[02:30]` links jump to that moment
- In transcript: Click any segment to navigate
- In sources: Click to see the exact context

**Search Transcript:**
- Use semantic search to find specific topics
- Results ranked by relevance
- Click to jump to that moment

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "YouTube Twin API is running"
}
```

### 2. Process Video
```http
POST /api/process-video
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "message": "Video processed successfully",
  "video_id": "VIDEO_ID",
  "video_info": {
    "video_id": "VIDEO_ID",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
  },
  "chunks_count": 42
}
```

### 3. Chat with Video
```http
POST /api/chat
Content-Type: application/json

{
  "video_id": "VIDEO_ID",
  "message": "What is the main topic?"
}
```

**Response:**
```json
{
  "response": "The main topic discussed is...",
  "sources": [
    {
      "text": "Relevant transcript segment...",
      "timestamp": 120.5,
      "formatted_time": "02:00",
      "similarity": 0.89
    }
  ]
}
```

### 4. Get Full Transcript
```http
POST /api/get-transcript
Content-Type: application/json

{
  "video_id": "VIDEO_ID"
}
```

### 5. Search Transcript
```http
POST /api/search-transcript
Content-Type: application/json

{
  "video_id": "VIDEO_ID",
  "query": "artificial intelligence",
  "top_k": 5
}
```

---

## ⚙️ Configuration

### Environment Variables

Edit `backend/.env` to customize:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional Configuration
PORT=5000
FLASK_ENV=development

# AI Models
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4-turbo-preview

# Chunking Strategy (in seconds)
CHUNK_DURATION=30
CHUNK_OVERLAP=5
```

### Customization Options

**Adjust Chunk Size:**
```env
CHUNK_DURATION=60  # 60-second chunks for longer context
CHUNK_OVERLAP=10   # 10-second overlap
```

**Change AI Models:**
```env
EMBEDDING_MODEL=text-embedding-3-large    # Higher quality
CHAT_MODEL=gpt-3.5-turbo                  # Faster & cheaper
```

**Retrieve More Context:**

In `backend/app.py`, line 81:
```python
relevant_chunks = embeddings_manager.find_relevant_chunks(
    message,
    video_store[video_id]['chunks'],
    top_k=10  # Increase for more context (default: 5)
)
```

---

## 🐛 Troubleshooting

### Problem: "Python not recognized"

**Solution:** Add Python to PATH
1. Search "Environment Variables" in Windows
2. Edit "Path" under System Variables
3. Add Python installation directory
4. Restart terminal

### Problem: "Could not fetch transcript"

**Causes:**
- Video doesn't have captions/subtitles
- Video is private or age-restricted
- Auto-generated captions are disabled

**Solution:** Try a different video with captions enabled

### Problem: "Invalid API key"

**Solution:**
1. Verify key in `backend/.env`
2. Remove any quotes or spaces
3. Check OpenAI account has credits
4. Generate new key if needed

### Problem: "Port already in use"

**Windows:**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

### Problem: Dependencies fail to install

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# If numpy/scikit-learn fail, try:
pip install numpy scikit-learn --only-binary :all:
```

### Problem: Frontend shows "File not found" errors

**Solution:**
1. Ensure you're in the `frontend` directory
2. Check that `index.html`, `style.css`, and `script.js` exist
3. Hard refresh browser: `Ctrl + Shift + R`

---

## 💰 Cost Estimation

Approximate OpenAI API costs:

| Operation | Cost per Video (20 min) |
|-----------|------------------------|
| Processing (embeddings) | ~$0.02-0.05 |
| Chat (per message) | ~$0.01-0.03 |
| **Total Session** | **~$0.10** |

**Cost-Saving Tips:**
- Use `gpt-3.5-turbo` for development ($0.001 vs $0.03 per 1K tokens)
- Process shorter videos during testing
- Cache processed videos to avoid reprocessing
- Reduce `top_k` parameter to retrieve fewer chunks

---

## 🔒 Security Best Practices

- ✅ Never commit `.env` files to Git
- ✅ Use environment variables in production
- ✅ Rotate API keys regularly
- ✅ Add rate limiting for production
- ✅ Implement user authentication
- ✅ Use HTTPS in production
- ✅ Validate all user inputs
- ✅ Store video data in database (not in-memory)

---

## 🚀 Deployment

### Backend (Heroku)

```bash
# Install Heroku CLI and login
heroku login
heroku create youtube-twin-api

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key-here

# Deploy
git push heroku main
```

### Frontend (Netlify)

1. Update `API_URL` in `frontend/script.js`:
```javascript
const API_URL = 'https://your-backend.herokuapp.com';
```

2. Deploy:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

### Docker Deployment

*Coming soon - Docker Compose configuration*

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Test all changes locally
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 and Embeddings API
- **YouTube Transcript API** for transcript fetching
- **Flask** for the robust web framework
- **Google Fonts** for Inter typography
- Community contributors and testers

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Multi-video support in one session
- [ ] Conversation history persistence
- [ ] Video summarization endpoint
- [ ] Playlist batch processing
- [ ] Export chat transcripts as PDF
- [ ] Browser extension for Chrome/Firefox

### Version 3.0 (Future)
- [ ] Support for Vimeo and other platforms
- [ ] Real-time collaborative watching
- [ ] Mobile app (iOS & Android)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Voice input for questions

---

## 📧 Support & Contact

**Found a bug?** [Open an issue](https://github.com/dhruv-gautam16/youtube-twin/issues)

**Have a question?** [Start a discussion](https://github.com/dhruv-gautam16/youtube-twin/discussions)

**Want to contribute?** Check out our [Contributing Guidelines](#-contributing)

**Email:** dhrvgautam@gmail.com


---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star!**

**Made with ❤️ using OpenAI GPT-4**

[⬆ Back to Top](#-youtube-twin---ai-powered-video-chat-assistant)

</div>