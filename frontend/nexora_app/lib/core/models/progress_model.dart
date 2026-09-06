class UserProgress {
  final double totalMastery;
  final int quizzesTaken;
  final double accuracy;
  final int? streak;
  final int? xp;

  UserProgress({
    required this.totalMastery,
    required this.quizzesTaken,
    required this.accuracy,
    this.streak,
    this.xp,
  });

  factory UserProgress.fromJson(Map<String, dynamic> json) {
    return UserProgress(
      totalMastery: (json['overall_mastery'] ?? json['totalMastery'] ?? 0.0).toDouble(),
      quizzesTaken: json['quizzes_taken'] ?? json['quizzesTaken'] ?? 0,
      accuracy: (json['accuracy'] ?? 0.0).toDouble(),
      streak: json['streak'],
      xp: json['xp'],
    );
  }
}
