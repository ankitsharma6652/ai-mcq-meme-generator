# 🎯 Complete Analytics & User Journey Tracking System

## 📊 Database Architecture - Normalized for Maximum Analytics

### **Key Improvement: Normalized Structure**
Instead of storing questions as JSON blobs, each question and answer is now a separate row. This enables:
- ✅ Question-level analytics
- ✅ Answer pattern analysis
- ✅ Difficulty scoring per question
- ✅ Time-to-answer metrics
- ✅ Success rate per question
- ✅ User performance trends

---

## 🗄️ New Table Structure

### 1. **MCQ Generation Tables**

#### `mcq_generations`
**Purpose:** Track MCQ generation metadata
```sql
- id, user_id, input_type, content_type, difficulty
- num_questions, source_content, model_name
- generation_time_seconds, created_at
- ip_address, user_agent
```

#### `mcq_questions` ⭐ NEW - Normalized
**Purpose:** Each question as a separate row
```sql
- id, generation_id, question_number
- question_text, option_a, option_b, option_c, option_d
- correct_answer, explanation
- times_attempted, times_correct, times_wrong
- average_time_to_answer
```

**Analytics Enabled:**
- Which questions are hardest? (lowest success rate)
- Which questions take longest to answer?
- Question difficulty calibration
- Content quality analysis

---

### 2. **Quiz Session Tables**

#### `quiz_sessions`
**Purpose:** Track each quiz attempt
```sql
- id, user_id, mcq_generation_id
- total_questions, questions_answered
- correct_answers, wrong_answers, score_percentage
- started_at, completed_at, time_taken_seconds
- is_completed, content_type, difficulty
- device_type, ip_address
```

#### `question_answers` ⭐ NEW - Normalized
**Purpose:** Each answer as a separate row
```sql
- id, quiz_session_id, question_id
- user_answer, is_correct
- time_spent_seconds, answered_at
```

**Analytics Enabled:**
- Answer patterns per user
- Time spent per question
- Question skip patterns
- Performance by question type
- Learning curve analysis

---

### 3. **Meme Generation Tables**

#### `meme_generations`
**Purpose:** Track meme generation metadata
```sql
- id, user_id, input_type, topic
- meme_type, num_memes, model_name
- total_generated, successful_generations
- generation_time_seconds, created_at
```

#### `generated_memes` ⭐ NEW - Normalized
**Purpose:** Each meme as a separate row
```sql
- id, generation_id, meme_url
- meme_type, source, note
- views, downloads, created_at
```

**Analytics Enabled:**
- Meme popularity (views/downloads)
- Success rate by meme type
- Model performance comparison
- Topic trend analysis

---

### 4. **User Journey & Event Tracking** ⭐ NEW

#### `user_events`
**Purpose:** Track EVERY user interaction
```sql
- id, user_id, session_id
- event_type, event_category, event_action
- event_label, event_value
- page_url, page_title, referrer
- device_type, browser, os
- timestamp, time_on_page
- metadata (JSON for additional data)
```

**Event Types to Track:**
```javascript
// Navigation
- page_view
- page_exit
- scroll_depth

// Engagement
- button_click
- input_focus
- tab_switch
- theme_toggle

// Conversions
- mcq_generate_start
- mcq_generate_complete
- quiz_start
- quiz_complete
- meme_generate_start
- meme_generate_complete

// User Actions
- login
- logout
- signup
- profile_update
- settings_change

// Errors
- generation_error
- api_error
- validation_error
```

#### `user_sessions`
**Purpose:** Track user sessions for retention
```sql
- id, user_id, session_id
- started_at, ended_at, duration_seconds
- pages_viewed, mcqs_generated
- quizzes_taken, memes_generated
- device_type, browser, os
- referrer, utm_source, utm_medium, utm_campaign
```

---

## 📈 Analytics You Can Now Track

### **User Performance Analytics**
```sql
-- User's average score over time
SELECT 
    DATE(completed_at) as date,
    AVG(score_percentage) as avg_score
FROM quiz_sessions
WHERE user_id = ? AND is_completed = TRUE
GROUP BY DATE(completed_at);

-- User's improvement rate
SELECT 
    user_id,
    FIRST_VALUE(score_percentage) OVER (ORDER BY completed_at) as first_score,
    LAST_VALUE(score_percentage) OVER (ORDER BY completed_at) as latest_score,
    (LAST_VALUE(score_percentage) - FIRST_VALUE(score_percentage)) as improvement
FROM quiz_sessions
WHERE user_id = ? AND is_completed = TRUE;
```

### **Question Analytics**
```sql
-- Hardest questions (lowest success rate)
SELECT 
    q.question_text,
    q.times_attempted,
    q.times_correct,
    (q.times_correct * 100.0 / q.times_attempted) as success_rate
FROM mcq_questions q
WHERE q.times_attempted > 10
ORDER BY success_rate ASC
LIMIT 10;

-- Questions that take longest to answer
SELECT 
    question_text,
    average_time_to_answer
FROM mcq_questions
WHERE average_time_to_answer IS NOT NULL
ORDER BY average_time_to_answer DESC
LIMIT 10;
```

### **User Journey Analytics**
```sql
-- User's journey through the site
SELECT 
    event_type,
    event_action,
    page_url,
    timestamp
FROM user_events
WHERE user_id = ?
ORDER BY timestamp;

-- Conversion funnel
SELECT 
    event_type,
    COUNT(DISTINCT user_id) as users,
    COUNT(DISTINCT session_id) as sessions
FROM user_events
WHERE event_type IN ('page_view', 'mcq_generate_start', 'quiz_start', 'quiz_complete')
GROUP BY event_type;
```

### **Retention Analytics**
```sql
-- Daily Active Users (DAU)
SELECT 
    DATE(started_at) as date,
    COUNT(DISTINCT user_id) as dau
FROM user_sessions
GROUP BY DATE(started_at);

-- User retention (Day 1, Day 7, Day 30)
SELECT 
    user_id,
    MIN(DATE(started_at)) as first_visit,
    MAX(DATE(started_at)) as last_visit,
    COUNT(DISTINCT DATE(started_at)) as days_active
FROM user_sessions
GROUP BY user_id;
```

### **Engagement Metrics**
```sql
-- Average session duration
SELECT 
    AVG(duration_seconds) as avg_duration,
    AVG(pages_viewed) as avg_pages,
    AVG(mcqs_generated) as avg_mcqs
FROM user_sessions
WHERE ended_at IS NOT NULL;

-- Most engaged users
SELECT 
    user_id,
    COUNT(*) as sessions,
    SUM(duration_seconds) as total_time,
    SUM(quizzes_taken) as total_quizzes
FROM user_sessions
GROUP BY user_id
ORDER BY total_time DESC
LIMIT 10;
```

### **Content Analytics**
```sql
-- Popular content types
SELECT 
    content_type,
    COUNT(*) as generations,
    AVG(generation_time_seconds) as avg_time
FROM mcq_generations
GROUP BY content_type;

-- Popular difficulty levels
SELECT 
    difficulty,
    COUNT(*) as sessions,
    AVG(score_percentage) as avg_score
FROM quiz_sessions
WHERE is_completed = TRUE
GROUP BY difficulty;
```

---

## 🎯 KPIs You Can Calculate

### **User Lifetime Value (LTV)**
```sql
SELECT 
    user_id,
    COUNT(DISTINCT qs.id) as total_quizzes,
    COUNT(DISTINCT mg.id) as total_mcqs,
    COUNT(DISTINCT mem.id) as total_memes,
    COUNT(DISTINCT us.id) as total_sessions,
    SUM(us.duration_seconds) / 3600.0 as total_hours,
    DATEDIFF(MAX(us.started_at), MIN(us.started_at)) as days_active
FROM users u
LEFT JOIN quiz_sessions qs ON u.id = qs.user_id
LEFT JOIN mcq_generations mg ON u.id = mg.user_id
LEFT JOIN meme_generations mem ON u.id = mem.user_id
LEFT JOIN user_sessions us ON u.id = us.user_id
GROUP BY user_id;
```

### **Retention Rate**
```sql
-- 7-day retention
SELECT 
    COUNT(DISTINCT CASE WHEN days_since_signup <= 7 THEN user_id END) * 100.0 / 
    COUNT(DISTINCT user_id) as retention_7day
FROM (
    SELECT 
        user_id,
        DATEDIFF(started_at, first_session) as days_since_signup
    FROM user_sessions us
    JOIN (
        SELECT user_id, MIN(started_at) as first_session
        FROM user_sessions
        GROUP BY user_id
    ) first ON us.user_id = first.user_id
);
```

### **Engagement Score**
```sql
-- User engagement score (0-100)
SELECT 
    user_id,
    (
        (COUNT(DISTINCT DATE(started_at)) * 10) +  -- Daily activity
        (SUM(quizzes_taken) * 5) +                  -- Quiz engagement
        (SUM(mcqs_generated) * 3) +                 -- MCQ generation
        (SUM(memes_generated) * 2)                  -- Meme generation
    ) as engagement_score
FROM user_sessions
GROUP BY user_id
ORDER BY engagement_score DESC;
```

---

## 🚀 Implementation Checklist

### **Backend (In Progress)**
- ✅ Normalized database tables created
- ⏳ Update MCQ generation to save individual questions
- ⏳ Update quiz submission to save individual answers
- ⏳ Add event tracking endpoint
- ⏳ Add session tracking endpoint

### **Frontend (To Do)**
- ⏳ Implement event tracking SDK
- ⏳ Track page views
- ⏳ Track user interactions
- ⏳ Track quiz progress
- ⏳ Send events to backend

### **Analytics Dashboard (To Do)**
- ⏳ User performance dashboard
- ⏳ Question analytics
- ⏳ User journey visualization
- ⏳ Retention cohort analysis
- ⏳ Engagement metrics

---

## 📊 Sample Dashboards

### **User Profile Dashboard**
- Total quizzes taken
- Average score
- Improvement trend graph
- Strongest/weakest topics
- Time spent learning
- Achievement badges
- Rank/leaderboard position

### **Admin Analytics Dashboard**
- DAU/MAU/WAU
- New user signups
- Retention curves
- Engagement metrics
- Popular content types
- Question difficulty distribution
- Model performance comparison
- Revenue/usage forecasting

---

**Status:** Database structure redesigned ✅
**Next:** Update endpoints to use normalized tables
