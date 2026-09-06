class StudyMessage {
  final String text;
  final bool isUser;
  final List<String>? citations;
  final bool isError;
  final String? originalQuery;

  StudyMessage({
    required this.text,
    required this.isUser,
    this.citations,
    this.isError = false,
    this.originalQuery,
  });

  factory StudyMessage.fromJson(Map<String, dynamic> json) {
    return StudyMessage(
      text: json['text'] as String,
      isUser: json['isUser'] as bool,
      citations: json['citations'] != null ? List<String>.from(json['citations']) : null,
      isError: json['isError'] as bool? ?? false,
      originalQuery: json['originalQuery'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'text': text,
      'isUser': isUser,
      'citations': citations,
      'isError': isError,
      'originalQuery': originalQuery,
    };
  }
}
