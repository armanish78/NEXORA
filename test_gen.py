import sys
import os

sys.path.append(os.path.abspath("backend"))
os.chdir("backend")

from app.quiz_generator import QuizGenerator
from app.retrieve import Retriever
from app.llm import LLMProvider

class MockLLM(LLMProvider):
    def generate(self, prompt, temperature=0.7):
        return "{}"
    def health_check(self):
        return True
        
retriever = Retriever()
llm = MockLLM()
generator = QuizGenerator(retriever, llm)

try:
    res = generator.generate_quiz(user_id=1, topic="SOLAR COLLECTORS:", difficulty="medium", num_questions=1, filename="BME654B-module-2-pdf.pdf")
    print("Result:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
