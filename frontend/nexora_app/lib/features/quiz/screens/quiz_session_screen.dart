import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/network/api_client.dart';
import '../../../core/theme/app_colors.dart';
import '../models/quiz_models.dart';
import '../widgets/quiz_option_widget.dart';
import '../widgets/quiz_decorations.dart';
import 'quiz_results_screen.dart';

class QuizSessionScreen extends StatefulWidget {
  final int quizId;
  final List<QuizQuestion> questions;
  final DocumentMetadata document;
  final bool isPersonalized;
  final String? selectedTopic;

  const QuizSessionScreen({
    super.key,
    required this.quizId,
    required this.questions,
    required this.document,
    this.isPersonalized = false,
    this.selectedTopic,
  });

  @override
  State<QuizSessionScreen> createState() => _QuizSessionScreenState();
}

class _QuizSessionScreenState extends State<QuizSessionScreen> {
  final ApiClient _apiClient = ApiClient();
  
  int _currentIndex = 0;
  int _score = 0;
  
  String? _selectedOption;
  bool _isSubmitting = false;
  bool _hasSubmitted = false;
  AnswerSubmissionResponse? _feedback;

  void _selectOption(String option) {
    if (_hasSubmitted || _isSubmitting) return;
    setState(() {
      _selectedOption = option;
    });
  }

  Future<void> _submitAnswer() async {
    if (_selectedOption == null || _hasSubmitted) return;

    setState(() {
      _isSubmitting = true;
    });

    try {
      final response = await _apiClient.submitAnswer({
        'question_id': widget.quizId, 
        'user_answer': _selectedOption,
      });

      final feedback = AnswerSubmissionResponse.fromJson(response);
      
      setState(() {
        _feedback = feedback;
        _hasSubmitted = true;
        if (feedback.isCorrect) {
          _score++;
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to submit answer. Check connection.')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  void _nextQuestion() {
    if (_currentIndex < widget.questions.length - 1) {
      setState(() {
        _currentIndex++;
        _selectedOption = null;
        _hasSubmitted = false;
        _feedback = null;
      });
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => QuizResultsScreen(
            score: _score,
            total: widget.questions.length,
            document: widget.document,
          ),
        ),
      );
    }
  }

  QuizOptionState _getOptionState(String option) {
    if (!_hasSubmitted) {
      return _selectedOption == option ? QuizOptionState.selected : QuizOptionState.unselected;
    }
    
    final currentQ = widget.questions[_currentIndex];
    final isCorrectOption = option == currentQ.correctAnswer;
    
    if (isCorrectOption) {
      return QuizOptionState.correct;
    } else if (option == _selectedOption) {
      return QuizOptionState.incorrect; // user selected the wrong one
    }
    // other options that weren't selected and aren't correct
    return QuizOptionState.muted;
  }

  String _getLetterForIndex(int index) {
    const letters = ['A', 'B', 'C', 'D'];
    if (index >= 0 && index < letters.length) return letters[index];
    return '';
  }

  @override
  Widget build(BuildContext context) {
    if (widget.questions.isEmpty) return const SizedBox.shrink();

    final currentQuestion = widget.questions[_currentIndex];
    
    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      body: QuizDecorations(
        child: SafeArea(
          child: Column(
            children: [
              _buildAppBar(),
              _buildProgressBar(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: AppColors.nexoraYellow,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.nexoraInk, width: 2),
                        ),
                        child: Text(
                          currentQuestion.topic.toUpperCase(),
                          style: const TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Text(
                        currentQuestion.question,
                        style: const TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 26,
                          fontWeight: FontWeight.w900,
                          color: AppColors.nexoraInk,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 32),
                      ...List.generate(currentQuestion.options.length, (index) {
                        final option = currentQuestion.options[index];
                        return AnimatedSwitcher(
                          duration: const Duration(milliseconds: 300),
                          child: QuizOptionWidget(
                            key: ValueKey('${_currentIndex}_$index'),
                            text: option,
                            label: _getLetterForIndex(index),
                            state: _getOptionState(option),
                            onTap: () => _selectOption(option),
                          ),
                        );
                      }),
                      
                      if (_hasSubmitted && _feedback != null) ...[
                        const SizedBox(height: 12),
                        _buildFeedbackSection(),
                      ],
                      const SizedBox(height: 80), 
                    ],
                  ),
                ),
              ),
              _buildBottomBar(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: NexoraIcon(NexoraIcons.back, color: AppColors.nexoraInk),
            onPressed: () => Navigator.pop(context),
          ),
          const Expanded(child: Center(child: NexoraLogoHeader())),
          const SizedBox(width: 48), // Balance for back button
        ],
      ),
    );
  }

  Widget _buildProgressBar() {
    final progress = (_currentIndex) / widget.questions.length;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Row(
        children: [
          Expanded(
            child: Container(
              height: 12,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
              alignment: Alignment.centerLeft,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width: (MediaQuery.of(context).size.width - 48 - 120) * progress, // roughly
                height: 12,
                decoration: BoxDecoration(
                  color: AppColors.nexoraGreen,
                  borderRadius: BorderRadius.circular(4),
                  border: const Border(
                    right: BorderSide(color: AppColors.nexoraInk, width: 2),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Text(
            'Question ${_currentIndex + 1} of ${widget.questions.length}',
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: AppColors.nexoraInk,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackSection() {
    final isCorrect = _feedback!.isCorrect;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isCorrect ? AppColors.nexoraGreen : AppColors.nexoraCoral,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.nexoraInk,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              NexoraIcon(
                isCorrect ? NexoraIcons.check : NexoraIcons.close,
                color: AppColors.nexoraInk,
              ),
              const SizedBox(width: 8),
              Text(
                isCorrect ? 'Correct!' : 'Not quite right.',
                style: const TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppColors.nexoraInk,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _feedback!.explanation,
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: AppColors.nexoraInk,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomBar() {
    final isFinalQuestion = _currentIndex == widget.questions.length - 1;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: Colors.transparent,
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: (_selectedOption == null)
                ? null
                : (_hasSubmitted ? _nextQuestion : _submitAnswer),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.nexoraYellow,
              foregroundColor: AppColors.nexoraInk,
              disabledBackgroundColor: AppColors.nexoraInk.withValues(alpha: 0.1),
              elevation: 0,
              padding: const EdgeInsets.symmetric(vertical: 20),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(
                  color: _selectedOption == null ? Colors.transparent : AppColors.nexoraInk,
                  width: 3,
                ),
              ),
            ),
            child: _isSubmitting
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(color: AppColors.nexoraInk, strokeWidth: 3),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _hasSubmitted
                            ? (isFinalQuestion ? 'SEE RESULTS' : 'NEXT QUESTION')
                            : 'CHECK ANSWER',
                        style: TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1,
                          color: _selectedOption == null 
                              ? AppColors.nexoraInk.withValues(alpha: 0.4)
                              : AppColors.nexoraInk,
                        ),
                      ),
                      if (_hasSubmitted) ...[
                        const SizedBox(width: 8),
                        NexoraIcon(NexoraIcons.forward,
                          color: _selectedOption == null 
                              ? AppColors.nexoraInk.withValues(alpha: 0.4)
                              : AppColors.nexoraInk,
                        ),
                      ],
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
