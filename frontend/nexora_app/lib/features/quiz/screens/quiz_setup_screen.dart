import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/network/api_client.dart';
import '../../../core/theme/app_colors.dart';
import '../widgets/quiz_decorations.dart';
import 'quiz_session_screen.dart';
import '../models/quiz_models.dart';

class QuizSetupScreen extends StatefulWidget {
  final DocumentMetadata document;

  const QuizSetupScreen({super.key, required this.document});

  @override
  State<QuizSetupScreen> createState() => _QuizSetupScreenState();
}

class _QuizSetupScreenState extends State<QuizSetupScreen> {
  final ApiClient _apiClient = ApiClient();
  
  bool _isLoadingTopics = true;
  List<String> _topics = [];
  String? _selectedTopic;
  String _difficulty = 'medium';
  int _numQuestions = 5;
  
  bool _isGenerating = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchTopics();
  }

  Future<void> _fetchTopics() async {
    try {
      final topics = await _apiClient.getDocumentTopics(widget.document.filename);
      if (mounted) {
        setState(() {
          _topics = topics.where((t) => t.trim().isNotEmpty).toList();
          if (_topics.isNotEmpty) {
            _selectedTopic = _topics.first;
          }
          _isLoadingTopics = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _topics = [];
          _isLoadingTopics = false;
        });
      }
    }
  }

  Future<void> _startQuiz({bool personalized = false}) async {
    if (!personalized && _selectedTopic == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a topic first.')),
      );
      return;
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
    });

    try {
      Map<String, dynamic> responseData;
      if (personalized) {
        responseData = await _apiClient.createPersonalizedQuiz({
          'difficulty': _difficulty,
          'num_questions': _numQuestions,
          'filename': widget.document.filename,
        });
      } else {
        responseData = await _apiClient.createQuiz({
          'topic': _selectedTopic!,
          'difficulty': _difficulty,
          'num_questions': _numQuestions,
          'filename': widget.document.filename,
        });
      }

      final quizResponse = QuizResponse.fromJson(responseData);

      if (quizResponse.success && quizResponse.questions.isNotEmpty) {
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => QuizSessionScreen(
                quizId: quizResponse.quizId ?? 0,
                questions: quizResponse.questions,
                document: widget.document,
                isPersonalized: personalized,
                selectedTopic: quizResponse.selectedTopic,
              ),
            ),
          );
        }
      } else {
        setState(() {
          if (quizResponse.reason == 'INSUFFICIENT_SOURCE_CONTEXT') {
            _errorMessage = 'insufficient_context';
          } else {
            _errorMessage = quizResponse.message ?? 'Could not generate quiz.';
          }
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to connect to the server.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isGenerating = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      body: Stack(
        children: [
          const Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: IgnorePointer(child: BottomQuizDecoration()),
          ),
          SafeArea(
            child: Column(
              children: [
                _buildAppBar(),
                Expanded(
                  child: _isGenerating
                      ? _buildLoadingState()
                      : _errorMessage == 'insufficient_context'
                          ? _buildUnavailableState()
                          : _buildSetupForm(),
                ),
              ],
            ),
          ),
        ],
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

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(color: AppColors.nexoraYellow),
          const SizedBox(height: 24),
          const Text(
            'Generating your quiz...',
            style: TextStyle(
              fontFamily: 'BricolageGrotesque',
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppColors.nexoraInk,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Analyzing ${widget.document.filename}',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 14,
              color: AppColors.nexoraInk.withValues(alpha: 0.6),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUnavailableState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.nexoraInk, width: 2),
            boxShadow: const [
              BoxShadow(
                color: AppColors.nexoraInk,
                offset: Offset(4, 4),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              NexoraIcon(NexoraIcons.document, size: 48, color: AppColors.nexoraCoral),
              const SizedBox(height: 16),
              const Text(
                'Quiz Unavailable',
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.nexoraInk,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                "I couldn't find enough information in this document about the selected topic to generate a high-quality quiz.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 14,
                  color: AppColors.nexoraInk.withValues(alpha: 0.7),
                ),
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _errorMessage = null;
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.nexoraYellow,
                    foregroundColor: AppColors.nexoraInk,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: const BorderSide(color: AppColors.nexoraInk, width: 2),
                    ),
                  ),
                  child: const Text(
                    'Choose Another Topic',
                    style: TextStyle(fontFamily: 'BricolageGrotesque', fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppColors.nexoraInk,
                    side: const BorderSide(color: AppColors.nexoraInk, width: 2),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'Back to Quiz Hub',
                    style: TextStyle(fontFamily: 'BricolageGrotesque', fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSetupForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeroSection(),
          const SizedBox(height: 32),
          _buildCurrentDocumentCard(),
          const SizedBox(height: 32),
          
          if (_errorMessage != null && _errorMessage != 'insufficient_context')
            Container(
              margin: const EdgeInsets.only(bottom: 24),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.nexoraCoral.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.nexoraCoral, width: 2),
              ),
              child: Row(
                children: [
                  const NexoraIcon(NexoraIcons.warning),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        color: AppColors.nexoraInk,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          _buildTopicSelector(),
          const SizedBox(height: 32),
          _buildDifficultySection(),
          const SizedBox(height: 32),
          _buildQuestionCountSection(),
          const SizedBox(height: 40),
          _buildActionButtons(),
          const SizedBox(height: 120),
        ],
      ),
    );
  }

  Widget _buildHeroSection() {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'QUIZ SETUP',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 12,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.5,
                color: AppColors.nexoraInk,
              ),
            ),
            const SizedBox(height: 12),
            Stack(
              clipBehavior: Clip.none,
              children: [
                const Text(
                  'Ready to test\nyour knowledge?',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 32,
                    fontWeight: FontWeight.w900,
                    height: 1.1,
                    color: AppColors.nexoraInk,
                  ),
                ),
                Positioned(
                  bottom: 2,
                  left: 0,
                  child: Container(
                    width: 180,
                    height: 10,
                    color: AppColors.nexoraYellow.withValues(alpha: 0.6),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Turn what you\'ve studied into lasting\nunderstanding.',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 15,
                height: 1.4,
                color: AppColors.nexoraInk.withValues(alpha: 0.8),
              ),
            ),
          ],
        ),
        Positioned(
          right: 0,
          top: 0,
          child: IgnorePointer(child: _buildTopRightIllustration()),
        ),
      ],
    );
  }

  Widget _buildTopRightIllustration() {
    return SizedBox(
      width: 130,
      height: 130,
      child: Stack(
        children: [
          // Yellow geometric bg
          Positioned(
            top: 20,
            right: 0,
            child: Transform.rotate(
              angle: 0.3,
              child: Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: AppColors.nexoraYellow,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
              ),
            ),
          ),
          // Cyan circular accent
          Positioned(
            top: 0,
            right: 40,
            child: Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: AppColors.nexoraCyan,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
            ),
          ),
          // Purple secondary layer
          Positioned(
            top: 15,
            right: 20,
            child: Transform.rotate(
              angle: 0.15,
              child: Container(
                width: 70,
                height: 90,
                decoration: BoxDecoration(
                  color: const Color(0xFFC7B9FF),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
              ),
            ),
          ),
          // Tilted quiz sheet
          Positioned(
            top: 5,
            right: 30,
            child: Transform.rotate(
              angle: -0.1,
              child: Container(
                width: 70,
                height: 90,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const NexoraIcon(NexoraIcons.check, size: 16),
                        const SizedBox(width: 4),
                        Container(width: 20, height: 2, color: AppColors.nexoraInk),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const NexoraIcon(NexoraIcons.check, size: 16),
                        const SizedBox(width: 4),
                        Container(width: 20, height: 2, color: AppColors.nexoraInk),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Handwritten text
          Positioned(
            bottom: -5,
            left: -10,
            child: Transform.rotate(
              angle: -0.15,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Turn\nKnowledge\nInto Progress',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      height: 1.1,
                      color: AppColors.nexoraInk,
                    ),
                  ),
                  Container(
                    width: 60,
                    height: 2,
                    color: AppColors.nexoraInk,
                    margin: const EdgeInsets.only(top: 2),
                  ),
                ],
              ),
            ),
          ),
          // Motion lines
          Positioned(
            top: 40,
            left: 0,
            child: Transform.rotate(
              angle: -0.4,
              child: Container(width: 15, height: 2, color: AppColors.nexoraInk),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentDocumentCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.nexoraCyan,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.nexoraInk, width: 2.5),
        boxShadow: const [
          BoxShadow(
            color: AppColors.nexoraInk,
            offset: Offset(4, 4),
          )
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.nexoraInk, width: 2),
            ),
            child: const NexoraIcon(NexoraIcons.document, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.document.filename,
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.nexoraInk,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                const Text(
                  'Current Document',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: () => Navigator.pop(context),
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
              child: const Text(
                'Change',
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: AppColors.nexoraInk,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopicSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'PICK A TOPIC',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 12,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.5,
                color: AppColors.nexoraInk,
              ),
            ),
            Text(
              'Suggested from this document',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 12,
                color: AppColors.nexoraInk.withValues(alpha: 0.6),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (_isLoadingTopics)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.nexoraInk, width: 2.5),
              boxShadow: const [BoxShadow(color: AppColors.nexoraInk, offset: Offset(4, 4))],
            ),
            child: const Center(child: CircularProgressIndicator(color: AppColors.nexoraInk)),
          )
        else
          GestureDetector(
            onTap: _showTopicPicker,
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.nexoraInk, width: 2.5),
                boxShadow: const [BoxShadow(color: AppColors.nexoraInk, offset: Offset(4, 4))],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.nexoraYellow,
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                    ),
                    child: const NexoraIcon(NexoraIcons.document, size: 16),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _selectedTopic ?? (_topics.isNotEmpty ? _topics.first : 'No topics found'),
                          style: const TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppColors.nexoraInk,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          _selectedTopic == 'All Topics' ? 'Cover the entire document' : 'Cover this topic',
                          style: const TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 12,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  const NexoraIcon(NexoraIcons.more, size: 24, color: AppColors.nexoraInk),
                ],
              ),
            ),
          ),
      ],
    );
  }

  void _showTopicPicker() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          minChildSize: 0.4,
          maxChildSize: 0.85,
          builder: (context, scrollController) {
            return Container(
              decoration: const BoxDecoration(
                color: AppColors.nexoraCream,
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                border: Border(
                  top: BorderSide(color: AppColors.nexoraInk, width: 2.5),
                  left: BorderSide(color: AppColors.nexoraInk, width: 2.5),
                  right: BorderSide(color: AppColors.nexoraInk, width: 2.5),
                ),
              ),
              child: Column(
                children: [
                  // Handle indicator
                  Center(
                    child: Container(
                      margin: const EdgeInsets.only(top: 12, bottom: 8),
                      width: 48,
                      height: 6,
                      decoration: BoxDecoration(
                        color: AppColors.nexoraInk.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  ),
                  // Header
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'PICK A TOPIC',
                          style: TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 1.5,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                        IconButton(
                          icon: const NexoraIcon(NexoraIcons.close),
                          onPressed: () => Navigator.pop(context),
                          color: AppColors.nexoraInk,
                        ),
                      ],
                    ),
                  ),
                  const Divider(color: AppColors.nexoraInk, thickness: 2, height: 1),
                  // Topic List
                  Expanded(
                    child: _topics.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const NexoraIcon(NexoraIcons.warning, size: 48, color: AppColors.nexoraCoral),
                                const SizedBox(height: 16),
                                const Text(
                                  "Couldn't load topics",
                                  style: TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: () {
                                    Navigator.pop(context);
                                    setState(() {
                                      _isLoadingTopics = true;
                                    });
                                    _fetchTopics();
                                  },
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppColors.nexoraYellow,
                                    foregroundColor: AppColors.nexoraInk,
                                    elevation: 0,
                                    padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 32),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                      side: const BorderSide(color: AppColors.nexoraInk, width: 2),
                                    ),
                                  ),
                                  child: const Text('Retry', style: TextStyle(fontFamily: 'BricolageGrotesque', fontWeight: FontWeight.bold)),
                                ),
                              ],
                            ),
                          )
                        : ListView.separated(
                      controller: scrollController,
                      padding: const EdgeInsets.all(24),
                      itemCount: _topics.length + 1,
                      separatorBuilder: (context, index) => const SizedBox(height: 16),
                      itemBuilder: (context, index) {
                        final isAllTopics = index == 0;
                        final topic = isAllTopics ? 'All Topics' : _topics[index - 1];
                        final isSelected = _selectedTopic == topic || (_selectedTopic == null && isAllTopics);

                        return GestureDetector(
                          onTap: () {
                            setState(() {
                              _selectedTopic = topic; // 'All Topics' or specific topic
                            });
                            Navigator.pop(context);
                          },
                          child: Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: isSelected ? AppColors.nexoraYellow : Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: AppColors.nexoraInk, width: 2),
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.nexoraInk,
                                  offset: isSelected ? const Offset(4, 4) : const Offset(2, 2),
                                ),
                              ],
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  margin: const EdgeInsets.only(top: 2),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: isSelected ? Colors.white : AppColors.nexoraCyan.withValues(alpha: 0.2),
                                    shape: BoxShape.circle,
                                    border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                                  ),
                                  child: NexoraIcon(
                                    isAllTopics ? NexoraIcons.document : NexoraIcons.stack,
                                    size: 16,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        topic,
                                        style: TextStyle(
                                          fontFamily: 'BricolageGrotesque',
                                          fontSize: 16,
                                          fontWeight: isSelected ? FontWeight.w900 : FontWeight.bold,
                                          color: AppColors.nexoraInk,
                                        ),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        isAllTopics ? 'Cover the entire document' : 'Cover this topic',
                                        style: TextStyle(
                                          fontFamily: 'DMSans',
                                          fontSize: 12,
                                          color: AppColors.nexoraInk.withValues(alpha: 0.8),
                                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                if (isSelected)
                                  const Padding(
                                    padding: EdgeInsets.only(left: 8.0),
                                    child: NexoraIcon(NexoraIcons.check, size: 24, color: AppColors.nexoraInk),
                                  ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildDifficultySection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'DIFFICULTY',
          style: TextStyle(
            fontFamily: 'BricolageGrotesque',
            fontSize: 12,
            fontWeight: FontWeight.w900,
            letterSpacing: 1.5,
            color: AppColors.nexoraInk,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            _buildDifficultyCard('easy', 'Easy', 'Build Confidence', AppColors.nexoraGreen, NexoraIcons.leaf),
            const SizedBox(width: 12),
            _buildDifficultyCard('medium', 'Medium', 'Good Challenge', AppColors.nexoraYellow, NexoraIcons.barChart),
            const SizedBox(width: 12),
            _buildDifficultyCard('hard', 'Hard', 'Push Your Limits', AppColors.nexoraCoral, NexoraIcons.challenge),
          ],
        ),
      ],
    );
  }

  Widget _buildDifficultyCard(String value, String title, String subtitle, Color accentColor, NexoraIcons icon) {
    final isSelected = _difficulty == value;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _difficulty = value),
        behavior: HitTestBehavior.opaque,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? accentColor : Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.nexoraInk, width: 2.5),
            boxShadow: isSelected
                ? const [BoxShadow(color: AppColors.nexoraInk, offset: Offset(4, 4))]
                : const [BoxShadow(color: AppColors.nexoraInk, offset: Offset(2, 2))],
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: isSelected ? Colors.white : accentColor.withValues(alpha: 0.2),
                  shape: BoxShape.circle,
                  border: isSelected ? Border.all(color: AppColors.nexoraInk, width: 1.5) : null,
                ),
                child: NexoraIcon(icon, size: 24, color: AppColors.nexoraInk),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: AppColors.nexoraInk,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 10,
                  color: AppColors.nexoraInk.withValues(alpha: 0.8),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuestionCountSection() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'NUMBER OF QUESTIONS',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 12,
                fontWeight: FontWeight.w900,
                letterSpacing: 1.5,
                color: AppColors.nexoraInk,
              ),
            ),
            SizedBox(height: 4),
            Text(
              '1 – 5 questions',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 12,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.nexoraInk, width: 2.5),
          ),
          child: Row(
            children: [
              GestureDetector(
                onTap: _numQuestions > 1 ? () => setState(() => _numQuestions--) : null,
                behavior: HitTestBehavior.opaque,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: const BoxDecoration(
                    color: Color(0xFFC7B9FF),
                    shape: BoxShape.circle,
                  ),
                  child: const NexoraIcon(NexoraIcons.remove, size: 16),
                ),
              ),
              Container(
                width: 32,
                alignment: Alignment.center,
                child: Text(
                  '$_numQuestions',
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ),
              GestureDetector(
                onTap: _numQuestions < 5 ? () => setState(() => _numQuestions++) : null,
                behavior: HitTestBehavior.opaque,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: const BoxDecoration(
                    color: Color(0xFFC7B9FF),
                    shape: BoxShape.circle,
                  ),
                  child: const NexoraIcon(NexoraIcons.add, size: 16),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: GestureDetector(
            onTap: () => _startQuiz(personalized: false),
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
              decoration: BoxDecoration(
                color: AppColors.nexoraYellow,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.nexoraInk, width: 2.5),
                boxShadow: const [
                  BoxShadow(color: AppColors.nexoraInk, offset: Offset(4, 4))
                ],
              ),
              child: const Row(
                children: [
                  NexoraIcon(NexoraIcons.play, size: 24),
                  Expanded(
                    child: Center(
                      child: Text(
                        'Start Quiz',
                        style: TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                          color: AppColors.nexoraInk,
                        ),
                      ),
                    ),
                  ),
                  NexoraIcon(NexoraIcons.arrowRight, size: 24),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: GestureDetector(
            onTap: () => _startQuiz(personalized: true),
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.nexoraInk, width: 2.5),
              ),
              child: const Row(
                children: [
                  NexoraIcon(NexoraIcons.profile, size: 24),
                  SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Take Personalized Quiz',
                          style: TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'Focus on your weakest topics',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 12,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                      ],
                    ),
                  ),
                  NexoraIcon(NexoraIcons.arrowRight, size: 20),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

