class QuizQuestion {
  final String question;
  final String questionType;
  final String difficulty;
  final List<String> options;
  final String correctAnswer;
  final String explanation;
  final String topic;

  QuizQuestion({
    required this.question,
    required this.questionType,
    required this.difficulty,
    required this.options,
    required this.correctAnswer,
    required this.explanation,
    required this.topic,
  });

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    return QuizQuestion(
      question: json['question'] ?? json['question_text'] ?? '',
      questionType: json['question_type'] ?? 'MCQ',
      difficulty: json['difficulty'] ?? 'medium',
      options: List<String>.from(json['options'] ?? []),
      correctAnswer: json['correct_answer'] ?? '',
      explanation: json['explanation'] ?? '',
      topic: json['topic'] ?? '',
    );
  }
}

class QuizResponse {
  final bool success;
  final int? quizId;
  final List<QuizQuestion> questions;
  final String? reason;
  final String? message;
  final bool personalized;
  final String? selectedTopic;

  QuizResponse({
    required this.success,
    this.quizId,
    required this.questions,
    this.reason,
    this.message,
    this.personalized = false,
    this.selectedTopic,
  });

  factory QuizResponse.fromJson(Map<String, dynamic> json) {
    return QuizResponse(
      success: json['success'] ?? false,
      quizId: json['quiz_id'],
      questions: (json['questions'] as List<dynamic>?)
              ?.map((q) => QuizQuestion.fromJson(q))
              .toList() ??
          [],
      reason: json['reason'],
      message: json['message'],
      personalized: json['personalized'] ?? false,
      selectedTopic: json['selected_topic'],
    );
  }
}

class AnswerSubmissionResponse {
  final bool isCorrect;
  final String explanation;
  final String topic;

  AnswerSubmissionResponse({
    required this.isCorrect,
    required this.explanation,
    required this.topic,
  });

  factory AnswerSubmissionResponse.fromJson(Map<String, dynamic> json) {
    return AnswerSubmissionResponse(
      isCorrect: json['is_correct'] ?? false,
      explanation: json['explanation'] ?? '',
      topic: json['topic'] ?? '',
    );
  }
}
