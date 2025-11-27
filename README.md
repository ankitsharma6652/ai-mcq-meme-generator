# 🚀 AI MCQ & Meme Generator

> **AI That Makes Learning Fun Again!**  
> Generate coding MCQs, quizzes, and hilarious memes — all from text, files, or URLs.  
> Learn → Laugh → Level Up! 🎓😂

<div align="center">

## 🌐 **[Try it Live: quiz-meme.onrender.com](https://quiz-meme.onrender.com)** 🚀

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge&logo=render)](https://quiz-meme.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)](https://github.com/ankitsharma6652)

</div>

---

## ✨ Features

### 📚 **MCQ Generation**
- **Auto-Detect Content Type**: Automatically detects if your content is coding-related or general knowledge
- **Multiple Input Methods**: Paste text, upload files (PDF, TXT, MD, DOCX), or provide URLs
- **Difficulty Levels**: Easy, Medium, Hard, or Auto
- **Customizable**: Choose number of questions (5-50) and optional explanations
- **Export**: Download as PDF, JSON, or TXT

### 🎮 **Interactive Quiz Mode**
- **Timed Quizzes**: Track your performance with a built-in timer
- **Instant Feedback**: See correct/incorrect answers immediately
- **Detailed Explanations**: Learn from your mistakes
- **Progress Tracking**: View your score and time taken
- **Bookmarking**: Save questions for later review

### 🎨 **Meme Generation**
- **AI-Powered**: Generate hilarious memes from any topic
- **Multiple Formats**: Static images, Animated GIFs (Tenor), or Videos
- **Batch Generation**: Create up to 10 memes at once
- **Quick Actions**: Download, share, or bookmark memes

### 🌐 **Community Features**
- **Social Feed**: Browse and interact with community-generated content
- **Like & Comment**: Engage with other users' MCQs and memes
- **Bookmarks**: Save your favorite content for later
- **User Profiles**: Customize your profile with bio, designation, and social links

### 🔐 **Authentication & User Management**
- **Google OAuth**: Secure login with Google
- **Guest Mode**: Try the app without signing up
- **User Dashboard**: Track your activity and analytics
- **Admin Panel**: Manage users, content, and feedback (for admins)

### 💬 **Feedback System**
- **Guest Feedback**: Share your thoughts without logging in
- **User Feedback**: Quick feedback form for logged-in users
- **Star Ratings**: Rate your experience (1-5 stars)
- **Admin Review**: Admins can view and manage all feedback

### 🎨 **Beautiful UI/UX**
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **Smooth Animations**: Delightful micro-interactions
- **Modern Aesthetics**: Gradient buttons, glassmorphism, and vibrant colors

---

## 📸 Screenshots

### 🏠 **Home Page (Light Mode)**
![Home Page Light](screenshots/home-light.png)
*Clean, modern interface with multiple input options*

### 📝 **MCQ Generated**
![MCQ Generated](screenshots/mcq-generated.png)
*Instant MCQ generation with correct/incorrect indicators*

### 🎯 **Quiz Mode**
![Quiz Mode](screenshots/quiz-mode.png)
*Interactive quiz mode with timer and progress tracking*

### 📁 **File Upload (Dark Mode)**
![File Upload Dark](screenshots/file-upload-dark.png)
*Upload PDFs, TXT, MD, or DOCX files for MCQ generation*

### 🔗 **URL Input (Dark Mode)**
![URL Input Dark](screenshots/url-input-dark.png)
*Generate MCQs from any URL - supports multilingual content*

### 💬 **Feedback Modal (Dark Mode)**
![Feedback Modal](screenshots/feedback-modal-dark.png)
*Beautiful feedback form with star ratings and guest/user modes*

### 🔐 **Login Modal**
![Login Modal](screenshots/login-modal.png)
*Secure Google OAuth authentication*

### 📊 **Analytics Dashboard (Personal)**
![Analytics Personal](screenshots/analytics-personal.png)
*Track your personal performance with beautiful charts*

### 🌍 **Analytics Dashboard (Global)**
![Analytics Global](screenshots/analytics-global.png)
*View global statistics and trends*

### 🏆 **Leaderboard**
![Leaderboard](screenshots/leaderboard.png)
*Compete with top performers - Quiz Champions, Meme Lords, and MCQ Masters*

### 🌐 **Community Feed**
![Community Feed](screenshots/community-feed.png)
*Browse and interact with community-generated memes and quiz results*

### 📚 **Saved Items**
![Saved Items](screenshots/saved-items.png)
*Bookmark and review your favorite MCQs and memes*

### 💬 **Feedback Modal (Light Mode)**
![Feedback Light](screenshots/feedback-modal-light.png)
*User-friendly feedback form for logged-in users*

---

## 🛠️ Tech Stack

### **Frontend**
- **React 18** - UI library
- **Vanilla CSS** - Custom styling with CSS variables
- **Material Icons** - Icon library
- **Prism.js** - Code syntax highlighting

### **Backend**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Production database (Neon)
- **Pydantic** - Data validation

### **AI & APIs**
- **Groq (Llama 3)** - MCQ generation
- **Pollinations.ai** - AI image generation
- **Tenor API** - GIF generation
- **Google OAuth** - Authentication

### **Deployment**
- **Render.com** - Web hosting
- **Neon** - PostgreSQL database (3GB free)
- **GitHub** - Version control

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js (for development)
- PostgreSQL (or use Neon)

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/ankitsharma6652/ai-mcq-meme-generator.git
   cd ai-mcq-meme-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the `backend` directory:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   APP_BASE_URL=http://localhost:8000
   ```

4. **Run the application**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```


5. **Open in browser**
   ```
   http://localhost:8000
   ```
   
   **Or visit the live site:** [https://quiz-meme.onrender.com](https://quiz-meme.onrender.com)

---

## 📚 Documentation

- **[Deployment Guide](docs/RENDER_DEPLOYMENT.md)** - Deploy to Render.com
- **[Feedback System](docs/FEEDBACK_SYSTEM.md)** - User feedback documentation
- **[Trending Features](docs/TRENDING_COMPLETE.md)** - Latest features and updates
- **[PythonAnywhere Deployment](docs/PYTHONANYWHERE_DEPLOYMENT.md)** - Alternative deployment option
- **[API Documentation](https://quiz-meme.onrender.com/docs)** - FastAPI auto-generated docs

---

## 🎯 Use Cases

### **For Students**
- Generate practice MCQs from lecture notes
- Create quizzes from textbooks (upload PDF)
- Test knowledge with timed quizzes
- Learn with detailed explanations

### **For Teachers**
- Create assessments quickly
- Generate coding questions from documentation
- Export MCQs for exams
- Share quizzes with students

### **For Developers**
- Test coding knowledge
- Generate questions from documentation URLs
- Practice for interviews
- Learn new technologies

### **For Fun**
- Generate hilarious memes
- Share with friends
- Engage with community content
- Relax and laugh!

---

## 🌟 Key Highlights

- ✅ **100% Free** - No credit card required
- ✅ **No Limits** - Generate unlimited MCQs and memes
- ✅ **Fast** - Instant generation with AI
- ✅ **Secure** - Google OAuth authentication
- ✅ **Persistent** - All data saved to PostgreSQL
- ✅ **Responsive** - Works on all devices
- ✅ **Open Source** - MIT License

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ankit Sharma**
- GitHub: [@ankitsharma6652](https://github.com/ankitsharma6652)
- Email: digitalaks9@gmail.com

---

## 🙏 Acknowledgments

- **Groq** - For the amazing Llama 3 API
- **Pollinations.ai** - For AI image generation
- **Tenor** - For GIF API
- **Render** - For free hosting
- **Neon** - For free PostgreSQL database

---

## 📊 Stats

- **Lines of Code**: 10,000+
- **Features**: 20+
- **API Endpoints**: 50+
- **Database Tables**: 15+
- **Supported File Formats**: PDF, TXT, MD, DOCX
- **Supported Languages**: Multilingual (auto-detect)

---

## 🔮 Future Enhancements

- [ ] AI-powered quiz recommendations
- [ ] Collaborative quiz creation
- [ ] Leaderboards and achievements
- [ ] Mobile app (React Native)
- [ ] Video meme generation
- [ ] Voice-based quiz mode
- [ ] Integration with LMS platforms

---

<div align="center">

**Made with ❤️ by Ankit Sharma**

*"Why be serious? Let AI make learning fun!"*

[⭐ Star this repo](https://github.com/ankitsharma6652/ai-mcq-meme-generator) • [🐛 Report Bug](https://github.com/ankitsharma6652/ai-mcq-meme-generator/issues) • [✨ Request Feature](https://github.com/ankitsharma6652/ai-mcq-meme-generator/issues)

</div>
