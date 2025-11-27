# 📊 Complete Data Capture Breakdown

## ✅ What IS Being Captured (Verified)

### 1. MCQ Generation Data
**Table:** `mcq_generations`

**Your Latest Generation (ID 3):**
```
Source Content: "Python Interview Questions"
Input Type: paste_text
Content Type: auto
Difficulty: auto
Number of Questions: 10
Generation Time: 17.71 seconds
Model Used: llama-3.3-70b-versatile
Created At: 2025-11-24 15:37:15
IP Address: [captured]
User Agent: [captured]
```

**Full Schema Captured:**
- ✅ `source_content` - The text you pasted (first 5000 chars)
- ✅ `source_url` - If you used URL input
- ✅ `source_filename` - If you uploaded a file
- ✅ `input_type` - paste_text, upload_file, or url
- ✅ `content_type` - coding, general, or auto
- ✅ `difficulty` - easy, medium, hard, or auto
- ✅ `num_questions` - How many you requested
- ✅ `include_explanation` - Whether explanations were included
- ✅ `model_name` - Which AI model was used
- ✅ `generation_time_seconds` - Exact time taken
- ✅ `ip_address` - Your IP
- ✅ `user_agent` - Your browser info
- ✅ `created_at` - Timestamp

---

### 2. Individual Questions Data
**Table:** `mcq_questions`

**Example from your generation:**
```
Question 1: "What is the purpose of the 'self' parameter in a Python class?"
Option A: To represent the instance of the class
Option B: To refer to the class itself
Option C: To refer to the parent class
Option D: To refer to a local variable
Correct Answer: A
Explanation: [full explanation captured]

Times Attempted: 1
Times Correct: 1
Times Wrong: 0
Average Time to Answer: 2.167 seconds
```

**All 18 questions** from your 2 generations are stored with full text!

---

### 3. Quiz Session Data
**Table:** `quiz_sessions`

**Your Latest Quiz (ID 2):**
```
MCQ Generation ID: 3 (linked to "Python Interview Questions")
Total Questions: 8
Questions Answered: 8
Correct Answers: 3
Wrong Answers: 5
Score: 38%
Time Taken: 28.0 seconds
Started At: 2025-11-24 15:37:15
Device Type: desktop
IP Address: [captured]
User Agent: [captured]
```

---

### 4. Individual Answer Data
**Table:** `question_answers`

**Your 8 answers captured:**
```
Question 11: Answer A, Correct ✅, Time: 2.167s
Question 12: Answer ?, Correct ✅, Time: 0.524s
Question 13: Answer ?, Wrong ❌, Time: 0.476s
Question 14: Answer ?, Wrong ❌, Time: 0.478s
Question 15: Answer ?, Wrong ❌, Time: 0.457s
Question 16: Answer ?, Wrong ❌, Time: 0.459s
Question 17: Answer ?, Wrong ❌, Time: 0.447s
Question 18: Answer ?, Correct ✅, Time: 0.447s
```

---

### 5. Meme Generation Data (When You Test)
**Table:** `meme_generations`

**Will Capture:**
- ✅ `topic` - "Lord Rama" or whatever you enter
- ✅ `source_url` - If you use URL input
- ✅ `input_type` - topic or url
- ✅ `meme_type` - image, gif, or video
- ✅ `num_memes` - How many requested
- ✅ `model_name` - AI model for prompts
- ✅ `image_model` - flux, fal-ai, etc.
- ✅ `generation_time_seconds` - Exact time
- ✅ `total_generated` - How many attempted
- ✅ `successful_generations` - How many succeeded
- ✅ `failed_generations` - How many failed
- ✅ `ip_address` & `user_agent`
- ✅ `created_at`

**Plus individual memes in `generated_memes`:**
- Meme URL
- Meme type
- Source (pollinations, fal-ai, etc.)
- Views count
- Downloads count

---

### 6. Login History
**Table:** `user_login_history`

**Your Login:**
```
Email: digitalaks9@gmail.com
Login Time: 2025-11-24 15:11:59
Auth Provider: google
IP Address: [captured]
User Agent: [captured]
Device Type: [captured]
```

---

### 7. User Events (Auto-Captured)
**Table:** `user_events`

**Automatically tracking:**
- Every page view
- Every button click
- Scroll depth (25%, 50%, 75%, 100%)
- Time on page (every 30s)
- Form interactions
- JavaScript errors
- Session ID linking

---

## 🔍 How to View This Data

### Admin Panel Queries:

**See what users searched for:**
```sql
SELECT 
    source_content,
    content_type,
    difficulty,
    num_questions,
    created_at
FROM mcq_generations
ORDER BY created_at DESC;
```

**See meme topics:**
```sql
SELECT 
    topic,
    meme_type,
    num_memes,
    successful_generations,
    created_at
FROM meme_generations
ORDER BY created_at DESC;
```

**Popular search terms:**
```sql
SELECT 
    source_content,
    COUNT(*) as times_generated
FROM mcq_generations
GROUP BY source_content
ORDER BY times_generated DESC;
```

---

## ✅ Summary

**YES, I AM capturing:**
- ✅ Input text/content
- ✅ Search queries
- ✅ Topics
- ✅ URLs
- ✅ File names
- ✅ Everything users type or upload

**The data is in the database RIGHT NOW!**
Check `mcq_generations.source_content` to see "Python Interview Questions"
