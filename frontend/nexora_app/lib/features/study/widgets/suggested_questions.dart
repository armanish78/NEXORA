import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/network/api_client.dart';

class SuggestedQuestions extends StatefulWidget {
  final String filename;
  final Function(String) onQuestionSelected;

  const SuggestedQuestions({super.key, required this.filename, required this.onQuestionSelected});

  @override
  State<SuggestedQuestions> createState() => _SuggestedQuestionsState();
}

class _SuggestedQuestionsState extends State<SuggestedQuestions> {
  final ApiClient _apiClient = ApiClient();
  bool _isLoading = true;
  List<String> _topics = [];
  int _currentTopicOffset = 0;
  int _currentFallbackIndex = 0;

  String _cleanTopic(String topic) {
    // Strip leading structural numbering like "4.4.1 " or "1. "
    final regex = RegExp(r'^(\d+\.)+\d*\s+|^(\d+\.)+\s+');
    return topic.replaceAll(regex, '').trim();
  }

  String _generateQuestionForTopic(String rawTopic, int index) {
    final cleanTopic = _cleanTopic(rawTopic);
    final lowerTopic = cleanTopic.toLowerCase();
    
    if (lowerTopic.contains('architecture') || lowerTopic.contains('component') || lowerTopic.contains('layer')) {
      return "What are the main components of $cleanTopic?";
    }
    if (lowerTopic.contains('design')) {
      return "How is $cleanTopic designed according to the document?";
    }
    if (lowerTopic.contains('model') || lowerTopic.contains('type')) {
      return "What models or types of $cleanTopic are described?";
    }
    if (lowerTopic.contains('management') || lowerTopic.contains('process')) {
      return "How does the document describe $cleanTopic?";
    }
    if (lowerTopic.contains('advantage') || lowerTopic.contains('benefit')) {
      return "What are the advantages of $cleanTopic?";
    }
    if (lowerTopic.contains('challenge') || lowerTopic.contains('issue') || lowerTopic.contains('problem') || lowerTopic.contains('limitation')) {
      return "What challenges or limitations are associated with $cleanTopic?";
    }
    if (lowerTopic.contains('difference') || lowerTopic.contains('compare') || lowerTopic.contains('vs')) {
      return "What are the key differences discussed regarding $cleanTopic?";
    }
    if (lowerTopic.contains('application') || lowerTopic.contains('use case')) {
      return "What are the applications or use cases of $cleanTopic?";
    }
    
    // Varied templates for generic concepts
    final genericTemplates = [
      "Explain the concept of $cleanTopic.",
      "What are the main characteristics of $cleanTopic?",
      "How does $cleanTopic work?",
      "What does the document say about $cleanTopic?",
    ];
    
    return genericTemplates[index % genericTemplates.length];
  }

  static const List<List<String>> _fallbackSets = [
    [
      "What are the main concepts discussed in this document?",
      "How do the main processes or architectures described here work?",
      "What are the key advantages and limitations mentioned?",
      "What important definitions are introduced?"
    ],
    [
      "What are the key characteristics of the topics covered?",
      "What relationships or differences between concepts are explained?",
      "What challenges or issues does the document identify?",
      "Explain one of the major concepts covered in the document."
    ],
    [
      "What is the primary goal or thesis of this material?",
      "How are the different components or models categorized?",
      "What are the practical applications or use cases described?",
      "Summarize the most important takeaways from this text."
    ],
  ];

  @override
  void initState() {
    super.initState();
    _fetchTopics();
  }

  Future<void> _fetchTopics() async {
    try {
      final topics = await _apiClient.getDocumentTopics(widget.filename);
      // Filter out overly short or meaningless headings
      final validTopics = topics.where((t) => t.length > 3).toList();
      print('[Suggestions] fallback: ${validTopics.isEmpty}');
      if (mounted) {
        setState(() {
          _topics = validTopics;
          _isLoading = false;
        });
      }
    } catch (e) {
      print('[Suggestions] TOPIC FETCH FAILED -> FALLBACK USED');
      print(e);
      if (mounted) {
        setState(() {
          _topics = [];
          _isLoading = false;
        });
      }
    }
  }

  void _rotateQuestions() {
    setState(() {
      if (_topics.isNotEmpty) {
        _currentTopicOffset = (_currentTopicOffset + 4) % _topics.length;
      }
      _currentFallbackIndex = (_currentFallbackIndex + 1) % _fallbackSets.length;
    });
  }

  List<String> _generateCurrentQuestions() {
    if (_isLoading) {
      return ["Loading study topics..."];
    }

    if (_topics.isEmpty) {
      return _fallbackSets[_currentFallbackIndex];
    }

    List<String> questions = [];
    int numTopicsToPick = _topics.length < 4 ? _topics.length : 4;
    
    for (int i = 0; i < numTopicsToPick; i++) {
      int idx = (_currentTopicOffset + i) % _topics.length;
      String topic = _topics[idx];
      
      questions.add(_generateQuestionForTopic(topic, idx));
    }
    
    return questions;
  }

  @override
  Widget build(BuildContext context) {
    final currentQuestions = _generateCurrentQuestions();

    return Container(
      decoration: BoxDecoration(
        color: AppColors.nexoraLavender.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.nexoraInk, width: 2),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              NexoraIcon(NexoraIcons.sparkle, color: AppColors.nexoraInk, size: 20),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'Suggested questions',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ),
              if (!_isLoading)
                GestureDetector(
                  onTap: _rotateQuestions,
                  behavior: HitTestBehavior.opaque,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'ASK SOMETHING ELSE',
                        style: TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: AppColors.nexoraInk.withValues(alpha: 0.6),
                          letterSpacing: 1,
                        ),
                      ),
                      const SizedBox(width: 4),
                      NexoraIcon(NexoraIcons.retry,
                        size: 14,
                        color: AppColors.nexoraInk.withValues(alpha: 0.6),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          if (_isLoading)
            const Center(
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.nexoraInk),
              ),
            )
          else
            ...currentQuestions.map((q) => Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: _buildQuestionButton(q),
            )),
        ],
      ),
    );
  }

  Widget _buildQuestionButton(String question) {
    return InkWell(
      onTap: () => widget.onQuestionSelected(question),
      borderRadius: BorderRadius.circular(24),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.nexoraInk, width: 1.5),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                question,
                style: const TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.nexoraInk,
                ),
              ),
            ),
            NexoraIcon(NexoraIcons.forward, size: 16, color: AppColors.nexoraInk),
          ],
        ),
      ),
    );
  }
}
