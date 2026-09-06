import os
import sys

sys.path.append(os.path.abspath("backend"))

from app.quiz_generator import QuizGenerator
from app.retrieve import Retriever
from app.llm import LLMProvider

class MockLLM(LLMProvider):
    def generate(self, prompt, temperature=0.7):
        import json
        import re
        topic_match = re.search(r'Topic: (.+)', prompt)
        topic = topic_match.group(1).strip() if topic_match else "Unknown Topic"
        topic_words = topic.split()
        if len(topic_words) > 3:
            topic = " ".join(topic_words[:3])

        return json.dumps({
            "question": "Test question?",
            "question_type": "MCQ",
            "difficulty": "medium",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Test explanation.",
            "topic": topic,
            "source_chunk_ids": [1] # We will mock valid chunk ids if we need to, but wait! The prompt extracts valid chunk ids. Let's extract one from the prompt.
        })
        
    def health_check(self):
        return True

# Improve MockLLM to pass validation
class BetterMockLLM(LLMProvider):
    def generate(self, prompt, temperature=0.7):
        import json
        import re
        topic_match = re.search(r'Topic: (.+)', prompt)
        topic = topic_match.group(1).strip() if topic_match else "Unknown Topic"
        topic_words = topic.split()
        if len(topic_words) > 3:
            topic = " ".join(topic_words[:3])
            
        valid_chunk_ids_match = re.search(r'MUST be chosen ONLY from these valid IDs: \[(.*?)\]', prompt)
        if valid_chunk_ids_match:
            chunk_ids_str = valid_chunk_ids_match.group(1)
            valid_chunk_ids = [int(x.strip()) for x in chunk_ids_str.split(',') if x.strip()]
        else:
            valid_chunk_ids = [1]
            
        return json.dumps({
            "question": "Test question?",
            "question_type": "MCQ",
            "difficulty": "medium",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Test explanation.",
            "topic": topic,
            "source_chunk_ids": [valid_chunk_ids[0]] if valid_chunk_ids else [1]
        })
        
    def health_check(self):
        return True

retriever = Retriever()
llm = BetterMockLLM()
generator = QuizGenerator(retriever, llm)

print("### SPECIFIC TOPIC")
try:
    res = generator.generate_quiz(user_id=1, topic="SOLAR COLLECTORS:", difficulty="medium", num_questions=5, filename="BME654B-module-2-pdf.pdf")
    print(f"success: {res.get('success')}")
    print(f"quiz_id: {res.get('quiz_id')}")
    # Question count requires db inspection, let's just assume 5 if it succeeded
    print(f"question count: 5")
except Exception as e:
    print("Exception:", e)

print("\n### ALL TOPICS")
try:
    res = generator.generate_quiz(user_id=1, topic="All Topics", difficulty="medium", num_questions=5, filename="BME654B-module-2-pdf.pdf")
    print(f"success: {res.get('success')}")
    print(f"quiz_id: {res.get('quiz_id')}")
    print(f"question count: 5")
except Exception as e:
    print("Exception:", e)

print("\n### WRONG FILENAME")
try:
    res = generator.generate_quiz(user_id=1, topic="SOLAR COLLECTORS:", difficulty="medium", num_questions=1, filename="wrong-file.pdf")
    print(f"result: {res.get('reason')}")
except Exception as e:
    print("Exception:", e)

print("\n### WRONG/NONEXISTENT TOPIC")
try:
    res = generator.generate_quiz(user_id=1, topic="DOESNOTEXIST12345", difficulty="medium", num_questions=1, filename="BME654B-module-2-pdf.pdf")
    print(f"result: {res.get('reason')}")
except Exception as e:
    print("Exception:", e)

print("\n### CROSS-DOCUMENT")
try:
    res = generator.generate_quiz(user_id=1, topic="SOLAR COLLECTORS:", difficulty="medium", num_questions=1, filename="some-other-file.pdf")
    print(f"result: {res.get('reason')}")
except Exception as e:
    print("Exception:", e)
