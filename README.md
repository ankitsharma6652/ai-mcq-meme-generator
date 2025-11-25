# AI Coding MCQ & Quiz Generator

## 🎯 Overview
An interactive web application that generates AI-powered coding MCQs from any content source and provides an engaging quiz experience.

## ✨ Features

### 1. **Multiple Input Methods**
- **Paste Text**: Directly paste coding content
- **Upload File**: Support for PDF, TXT, and MD files
- **URL Extraction**: Automatically extract content from web pages

### 2. **AI-Powered MCQ Generation**
- Uses **Llama-3.3-70B** via Groq API (free & fast)
- Generates realistic, high-quality coding questions
- Customizable options:
  - Number of questions (5, 10, 20)
  - Difficulty (Easy, Medium, Hard, Auto)
  - Content type (Coding, Non-coding, Auto)
  - Include explanations

### 3. **Interactive Quiz Mode**
- Click to select answers
- Instant feedback (✓ Correct / ✗ Wrong)
- Color-coded results:
  - Green for correct answers
  - Red for incorrect answers
- Detailed explanations for each question
- Difficulty badges (Easy/Medium/Hard)

### 4. **Premium UI/UX**
- Dark mode design
- Smooth animations
- Responsive layout
- Material Icons
- Gradient accents

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Groq API Key (free from https://console.groq.com/keys)

### Installation

1. **Clone/Navigate to the project**
   ```bash
   cd /Users/ankit-sharma/Downloads/ai-mcq-meme-generator
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   - Open `backend/main.py`
   - Replace `GROQ_API_KEY` with your actual key (line ~292)

4. **Run the server**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the app**
   - Open http://localhost:8000 in your browser

## 📁 Project Structure

```
ai-mcq-meme-generator/
├── backend/
│   └── main.py          # FastAPI backend with AI integration
├── frontend/
│   ├── index.html       # Main HTML file
│   ├── app.js          # React application logic
│   └── style.css       # Styling
├── venv/               # Python virtual environment
└── README.md           # This file
```

## 🔧 Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **Groq API**: Free, fast LLM inference (Llama-3.3-70B)
- **BeautifulSoup**: Web scraping for URL content
- **PyPDF**: PDF text extraction

### Frontend
- **React**: UI framework (via CDN)
- **Vanilla CSS**: Custom styling
- **Material Icons**: Icon library

## 🎮 How to Use

1. **Choose Input Method**
   - Paste text directly
   - Upload a file (PDF/TXT/MD)
   - Enter a URL

2. **Configure Options**
   - Select number of questions
   - Choose difficulty level
   - Set content type

3. **Generate MCQs**
   - Click "Generate MCQs"
   - Wait for AI to create questions

4. **Take the Quiz**
   - Click on an option to answer
   - Get instant feedback
   - Read explanations to learn

## 🔑 API Endpoints

- `POST /api/generate-mcqs` - Generate MCQs from text
- `POST /api/extract-url` - Extract text from URL
- `POST /api/extract-file` - Extract text from uploaded file

## 🌟 Key Improvements Made

1. ✅ Removed unnecessary "Search" tab
2. ✅ Replaced meme generation with interactive quiz mode
3. ✅ Added instant answer feedback
4. ✅ Implemented color-coded results
5. ✅ Added difficulty badges
6. ✅ Improved user experience with hints

## 📝 Notes

- The Groq API is free but has rate limits
- First-time generation might take a few seconds
- The AI model is optimized for coding questions
- All processing happens server-side for security

## 🎨 Design Philosophy

- **Clean & Modern**: Dark theme with vibrant accents
- **User-Friendly**: Intuitive interface with clear feedback
- **Interactive**: Engaging quiz experience
- **Fast**: Optimized for quick generation and response

---

**Enjoy learning with AI-powered quizzes! 🚀**
