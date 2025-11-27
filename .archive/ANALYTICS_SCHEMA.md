# 📊 Comprehensive Analytics Database Schema

## Overview
This document describes the new analytics-focused database tables designed to track every user interaction for KPIs, user scoring, and detailed analytics.

---

## 🎯 New Tables Created

### 1. **mcq_generations** - MCQ Generation Tracking
Tracks every MCQ generation with complete details.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users (nullable for anonymous)
- **Input Details:**
  - `input_type` - paste_text, upload_file, url
  - `content_type` - coding, general, auto
  - `difficulty` - easy, medium, hard, auto
  - `num_questions` - Number of questions requested
  - `include_explanation` - Boolean
- **Source Content:**
  - `source_content` - Original text content
  - `source_url` - URL if URL input
  - `source_filename` - Filename if file upload
- **Generation Details:**
  - `model_name` - AI model used (e.g., "llama-3.3-70b-versatile")
  - `generation_time_seconds` - Time taken to generate
  - `questions_data` - JSON array of all generated questions
- **Metadata:**
  - `created_at` - Timestamp
  - `ip_address` - User's IP
  - `user_agent` - Browser/device info

**Use Cases:**
- Track which content types are most popular
- Analyze generation times by model
- See what difficulty levels users prefer
- Content source analysis (text vs file vs URL)

---

### 2. **quiz_attempts** - Quiz Attempt Tracking
Tracks every quiz attempt with detailed performance metrics.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users (nullable)
- `mcq_generation_id` - Links to the MCQ set used
- **Quiz Performance:**
  - `total_questions` - Total questions in quiz
  - `correct_answers` - Number correct
  - `wrong_answers` - Number wrong
  - `score_percentage` - Calculated percentage
- **Timing:**
  - `started_at` - Quiz start time
  - `completed_at` - Quiz end time
  - `time_taken_seconds` - Total time
- **Detailed Answers:**
  - `answers_detail` - JSON: [{question_id, user_answer, correct_answer, is_correct, time_spent}]
- **Source Info:**
  - `content_type` - coding, general
  - `difficulty` - easy, medium, hard
  - `input_type` - paste_text, upload_file, url
- **Analytics Metrics:**
  - `average_time_per_question` - Avg time per Q
  - `fastest_answer_time` - Fastest answer
  - `slowest_answer_time` - Slowest answer
- **Metadata:**
  - `ip_address` - User's IP
  - `user_agent` - Browser/device info

**Use Cases:**
- Calculate user performance scores
- Track improvement over time
- Identify difficult questions
- Time-based analytics
- Leaderboards and rankings
- Question-level analytics

---

### 3. **meme_generations** - Meme Generation Tracking
Tracks every meme generation with full details.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users (nullable)
- **Input Details:**
  - `input_type` - topic, url
  - `topic` - User's topic/prompt
  - `source_url` - URL if URL input
- **Meme Configuration:**
  - `meme_type` - image, gif, video
  - `num_memes` - Number of memes requested
- **Generation Details:**
  - `model_name` - AI model for prompts
  - `image_model` - Image generation model (flux, pollinations)
  - `generation_time_seconds` - Time taken
  - `memes_data` - JSON: [{url, type, source, note}]
- **Success Metrics:**
  - `total_generated` - Total attempted
  - `successful_generations` - Successful count
  - `failed_generations` - Failed count
- **Metadata:**
  - `created_at` - Timestamp
  - `ip_address` - User's IP
  - `user_agent` - Browser/device info

**Use Cases:**
- Track meme generation success rates
- Popular meme types (image vs gif vs video)
- Model performance comparison
- Topic trend analysis
- Generation time optimization

---

## 📈 KPIs You Can Now Track

### User Performance KPIs
1. **Average Score** - Across all quizzes
2. **Improvement Rate** - Score trend over time
3. **Completion Rate** - % of started quizzes completed
4. **Average Time Per Question** - Speed metric
5. **Accuracy by Difficulty** - Performance by level
6. **Accuracy by Content Type** - Coding vs General

### Engagement KPIs
1. **Total MCQs Generated** - Per user/overall
2. **Total Quizzes Taken** - Per user/overall
3. **Total Memes Generated** - Per user/overall
4. **Daily Active Users** - Based on timestamps
5. **Retention Rate** - Returning users
6. **Feature Usage** - MCQ vs Meme popularity

### Content KPIs
1. **Popular Topics** - Most generated topics
2. **Input Method Preference** - Text vs File vs URL
3. **Difficulty Distribution** - Easy/Medium/Hard split
4. **Question Count Preference** - Avg questions per generation

### Technical KPIs
1. **Average Generation Time** - By model/type
2. **Success Rate** - Especially for memes
3. **Model Performance** - Compare different AI models
4. **Peak Usage Times** - Time-based analytics

---

## 🎮 User Scoring System Ideas

### Basic Score
```
User Score = (Total Correct / Total Attempted) × 100
```

### Weighted Score
```
Score = Σ(Question_Score × Difficulty_Multiplier × Time_Bonus)

Where:
- Easy: 1x multiplier
- Medium: 1.5x multiplier
- Hard: 2x multiplier
- Time_Bonus: 1.2x if answered in < avg_time
```

### Streak Bonus
- Track consecutive correct answers
- Add streak multiplier to score

### Level System
```
Level 1: 0-100 points
Level 2: 101-500 points
Level 3: 501-1000 points
... and so on
```

---

## 📊 Sample Analytics Queries

### Top Performers
```sql
SELECT 
    u.full_name,
    u.email,
    AVG(qa.score_percentage) as avg_score,
    COUNT(qa.id) as total_quizzes,
    SUM(qa.correct_answers) as total_correct
FROM users u
JOIN quiz_attempts qa ON u.id = qa.user_id
GROUP BY u.id
ORDER BY avg_score DESC
LIMIT 10;
```

### Content Type Popularity
```sql
SELECT 
    content_type,
    COUNT(*) as generations,
    AVG(num_questions) as avg_questions
FROM mcq_generations
GROUP BY content_type;
```

### User Improvement Trend
```sql
SELECT 
    DATE(completed_at) as date,
    AVG(score_percentage) as avg_score
FROM quiz_attempts
WHERE user_id = ?
GROUP BY DATE(completed_at)
ORDER BY date;
```

### Meme Success Rate
```sql
SELECT 
    meme_type,
    AVG(successful_generations * 100.0 / total_generated) as success_rate,
    AVG(generation_time_seconds) as avg_time
FROM meme_generations
GROUP BY meme_type;
```

---

## 🔄 Next Steps

1. **Implement Data Collection**
   - Update MCQ generation endpoint to save to `mcq_generations`
   - Update quiz submission to save to `quiz_attempts`
   - Update meme generation to save to `meme_generations`

2. **Build Analytics Dashboard**
   - User performance charts
   - System-wide statistics
   - Leaderboards
   - Trend analysis

3. **User Profile Enhancements**
   - Show user's score/level
   - Display achievement badges
   - Show quiz history
   - Performance graphs

4. **Admin Analytics**
   - Real-time usage stats
   - Model performance comparison
   - User engagement metrics
   - Revenue/usage forecasting

---

## 🎯 Benefits

✅ **Complete Tracking** - Every action is logged
✅ **User Insights** - Understand user behavior
✅ **Performance Metrics** - Optimize AI models
✅ **Gamification Ready** - Scores, levels, achievements
✅ **Business Intelligence** - Make data-driven decisions
✅ **Scalable** - Designed for growth
✅ **Privacy Compliant** - User IDs are nullable for anonymous usage

---

**Created:** 2025-11-24
**Version:** 1.0
**Status:** ✅ Database tables created and ready
