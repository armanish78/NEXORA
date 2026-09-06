from typing import List, Dict, Any
from collections import defaultdict
from app.database import get_user_answers
from app.config import DB_PATH

MIN_ATTEMPTS_FOR_WEAKNESS = 2

def _calculate_accuracy(correct: int, attempts: int) -> float:
    if attempts == 0:
        return 0.0
    return round((correct / attempts) * 100, 1)

def get_overall_progress(user_id: int, db_path: str = DB_PATH) -> Dict[str, Any]:
    answers = get_user_answers(user_id, db_path=db_path)
    
    total_questions = len(answers)
    correct = sum(1 for a in answers if a["is_correct"])
    incorrect = total_questions - correct
    accuracy = _calculate_accuracy(correct, total_questions)
    
    quizzes_attempted = len(set(a["quiz_id"] for a in answers if "quiz_id" in a))
    
    return {
        "user_id": user_id,
        "total_questions": total_questions,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
        "quizzes_attempted": quizzes_attempted
    }

def get_topic_performance(user_id: int, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    answers = get_user_answers(user_id, db_path=db_path)
    
    topic_stats = defaultdict(lambda: {"attempts": 0, "correct": 0, "incorrect": 0})
    
    for a in answers:
        topic = a.get("topic", "Unknown")
        topic_stats[topic]["attempts"] += 1
        if a["is_correct"]:
            topic_stats[topic]["correct"] += 1
        else:
            topic_stats[topic]["incorrect"] += 1
            
    result = []
    for topic, stats in topic_stats.items():
        acc = _calculate_accuracy(stats["correct"], stats["attempts"])
        result.append({
            "topic": topic,
            "attempts": stats["attempts"],
            "correct": stats["correct"],
            "incorrect": stats["incorrect"],
            "accuracy": acc
        })
        
    # Sort deterministically by accuracy descending, then attempts descending, then alphabetically
    result.sort(key=lambda x: (-x["accuracy"], -x["attempts"], x["topic"]))
    return result

def get_difficulty_performance(user_id: int, db_path: str = DB_PATH) -> Dict[str, Any]:
    answers = get_user_answers(user_id, db_path=db_path)
    
    diff_stats = defaultdict(lambda: {"attempts": 0, "correct": 0, "incorrect": 0})
    
    for a in answers:
        diff = a.get("difficulty", "unknown")
        diff_stats[diff]["attempts"] += 1
        if a["is_correct"]:
            diff_stats[diff]["correct"] += 1
        else:
            diff_stats[diff]["incorrect"] += 1
            
    result = {}
    for diff, stats in diff_stats.items():
        acc = _calculate_accuracy(stats["correct"], stats["attempts"])
        result[diff] = {
            "attempts": stats["attempts"],
            "correct": stats["correct"],
            "incorrect": stats["incorrect"],
            "accuracy": acc
        }
        
    return result

def get_weak_topics(user_id: int, limit: int = 3, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    topics = get_topic_performance(user_id, db_path=db_path)
    
    # Filter by minimum attempts
    qualified = [t for t in topics if t["attempts"] >= MIN_ATTEMPTS_FOR_WEAKNESS]
    
    # Sort by accuracy ASCENDING (weakest first), then attempts descending, then topic name
    qualified.sort(key=lambda x: (x["accuracy"], -x["attempts"], x["topic"]))
    
    # Strip correct/incorrect fields to match expected simpler output
    result = [
        {
            "topic": t["topic"],
            "attempts": t["attempts"],
            "accuracy": t["accuracy"]
        } for t in qualified
    ]
    
    return result[:limit]

def get_strong_topics(user_id: int, limit: int = 3, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    topics = get_topic_performance(user_id, db_path=db_path)
    
    # Filter by minimum attempts
    qualified = [t for t in topics if t["attempts"] >= MIN_ATTEMPTS_FOR_WEAKNESS]
    
    # Sort by accuracy DESCENDING (strongest first), then attempts descending, then topic name
    qualified.sort(key=lambda x: (-x["accuracy"], -x["attempts"], x["topic"]))
    
    result = [
        {
            "topic": t["topic"],
            "attempts": t["attempts"],
            "accuracy": t["accuracy"]
        } for t in qualified
    ]
    
    return result[:limit]

def get_progress_over_time(user_id: int, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    answers = get_user_answers(user_id, db_path=db_path)
    
    # Sort answers by timestamp
    answers.sort(key=lambda x: x["timestamp"])
    
    # Group by date (YYYY-MM-DD)
    date_stats = defaultdict(lambda: {"attempts": 0, "correct": 0})
    
    for a in answers:
        date = a["timestamp"][:10]
        date_stats[date]["attempts"] += 1
        if a["is_correct"]:
            date_stats[date]["correct"] += 1
            
    result = []
    for date in sorted(date_stats.keys()):
        stats = date_stats[date]
        acc = _calculate_accuracy(stats["correct"], stats["attempts"])
        result.append({
            "date": date,
            "attempts": stats["attempts"],
            "accuracy": acc
        })
        
    return result
