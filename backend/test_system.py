import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg, err=None):
    print(f"❌ FAIL: {msg}")
    if err:
        print(f"   Error: {err}")

def test_health():
    try:
        res = requests.get(f"{BASE_URL}/")
        if res.status_code == 200:
            print_pass("Health Check (Frontend Serve)")
        else:
            print_fail(f"Health Check returned {res.status_code}")
    except Exception as e:
        print_fail("Health Check failed to connect", e)

def test_mcq_generation():
    print("\n--- Testing MCQ Generation ---")
    payload = {
        "text": "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
        "num_questions": 2,
        "difficulty": "Easy",
        "question_type": "multiple_choice"
    }
    try:
        # Note: This might take a few seconds as it calls the LLM (or mock)
        start = time.time()
        res = requests.post(f"{BASE_URL}/api/generate-mcqs", json=payload)
        if res.status_code == 200:
            data = res.json()
            if "questions" in data and len(data["questions"]) > 0:
                print_pass(f"Generated {len(data['questions'])} MCQs in {time.time()-start:.2f}s")
                return data["generation_id"]
            else:
                print_fail("Response missing 'questions' list")
        else:
            print_fail(f"MCQ Generation failed: {res.status_code}", res.text)
    except Exception as e:
        print_fail("MCQ Generation exception", e)
    return None

def test_meme_generation():
    print("\n--- Testing Meme Generation ---")
    payload = {
        "question": "When code works but you don't know why",
        "explanation": "Magic",
        "correct_option": "Option A"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/generate-meme", json=payload)
        if res.status_code == 200:
            data = res.json()
            if "image_url" in data:
                print_pass(f"Meme Generated: {data['image_url']}")
            else:
                print_fail("Response missing 'image_url'")
        else:
            print_fail(f"Meme Generation failed: {res.status_code}", res.text)
    except Exception as e:
        print_fail("Meme Generation exception", e)

def test_quiz_submission(gen_id):
    if not gen_id:
        print("\n--- Skipping Quiz Submission (No Gen ID) ---")
        return

    print("\n--- Testing Quiz Submission ---")
    payload = {
        "user_id": None, # Anonymous
        "score": 100,
        "total_questions": 2,
        "time_taken_seconds": 30,
        "answers": [
            {
                "question_id": 1, # Assuming ID 1 exists
                "user_answer": "Option A",
                "is_correct": True,
                "time_spent_seconds": 15
            }
        ]
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/quiz-session", json=payload)
        if res.status_code == 200:
            print_pass("Quiz Session Saved")
        else:
            print_fail(f"Quiz Submission failed: {res.status_code}", res.text)
    except Exception as e:
        print_fail("Quiz Submission exception", e)

def test_social_feed():
    print("\n--- Testing Social Feed ---")
    try:
        res = requests.get(f"{BASE_URL}/api/social/feed")
        if res.status_code == 200:
            data = res.json()
            print_pass(f"Feed fetched successfully. Items: {len(data)}")
            
            # Verify structure of first item if exists
            if len(data) > 0:
                item = data[0]
                if "user" in item and "type" in item:
                    print_pass(f"Feed Item Structure Valid ({item['type']} by {item['user']})")
                else:
                    print_fail("Feed item missing required fields")
        else:
            print_fail(f"Feed fetch failed: {res.status_code}")
    except Exception as e:
        print_fail("Feed fetch exception", e)

def test_database_integrity():
    print("\n--- Testing Database Integrity (via API) ---")
    # Check trending
    try:
        res = requests.get(f"{BASE_URL}/api/trending")
        if res.status_code == 200:
            print_pass("Trending API working")
        else:
            print_fail(f"Trending API failed: {res.status_code}")
    except Exception as e:
        print_fail("Trending API exception", e)

if __name__ == "__main__":
    print("🚀 Starting System Tests...")
    test_health()
    gen_id = test_mcq_generation()
    test_meme_generation()
    test_quiz_submission(gen_id)
    test_social_feed()
    test_database_integrity()
    print("\n✅ Testing Complete")
