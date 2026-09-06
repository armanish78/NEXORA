class Topic {
  final String name;
  final double masteryLevel;

  Topic({
    required this.name,
    required this.masteryLevel,
  });

  factory Topic.fromJson(Map<String, dynamic> json) {
    return Topic(
      name: json['topic'] ?? json['name'] ?? 'Unknown Topic',
      masteryLevel: (json['mastery'] ?? json['masteryLevel'] ?? 0.0).toDouble(),
    );
  }
}
