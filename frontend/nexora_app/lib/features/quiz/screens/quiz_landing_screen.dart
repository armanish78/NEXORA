import 'package:flutter/material.dart';
import '../../../core/storage/local_storage_service.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_icons.dart';
import '../../../core/widgets/nexora_shapes.dart';
import '../../documents/widgets/document_list_item.dart';
import 'quiz_setup_screen.dart';

class QuizLandingScreen extends StatefulWidget {
  const QuizLandingScreen({super.key});

  @override
  State<QuizLandingScreen> createState() => _QuizLandingScreenState();
}

class _QuizLandingScreenState extends State<QuizLandingScreen> {
  final LocalStorageService _storage = LocalStorageService();
  bool _isLoading = false;
  List<DocumentMetadata> _documents = [];

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    setState(() => _isLoading = true);
    try {
      final docs = await _storage.getDocuments();
      docs.sort((a, b) => b.uploadDate.compareTo(a.uploadDate));
      if (mounted) {
        setState(() {
          _documents = docs;
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _navigateToSetup(DocumentMetadata document) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizSetupScreen(document: document),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      backgroundColor: AppColors.nexoraCream,
      body: NexoraBackground(
        variant: NexoraBackgroundVariant.quiz,
        child: SafeArea(
          bottom: false,
          child: _isLoading && _documents.isEmpty
              ? const Center(child: CircularProgressIndicator(color: AppColors.nexoraYellow))
              : RefreshIndicator(
                  onRefresh: _loadDocuments,
                  child: ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
                    physics: const ClampingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
                    children: [
                      _buildHeader(),
                      const SizedBox(height: 32),
                      _buildPersonalizedBanner(),
                      const SizedBox(height: 32),
                      _buildDocumentSelection(),
                      const SizedBox(height: 120), // Breathing room for bottom nav
                    ],
                  ),
                ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'QUIZ',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 32,
                fontWeight: FontWeight.w900,
                color: AppColors.nexoraInk,
              ),
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.nexoraYellow,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.nexoraInk, width: 2),
                boxShadow: const [
                  BoxShadow(
                    color: AppColors.nexoraInk,
                    offset: Offset(2, 2),
                  ),
                ],
              ),
              child: NexoraIcon(NexoraIcons.quiz, color: AppColors.nexoraInk),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Test your knowledge and master your study materials.',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 16,
            color: AppColors.nexoraInk.withValues(alpha: 0.8),
          ),
        ),
      ],
    );
  }

  Widget _buildPersonalizedBanner() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.nexoraCoral,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.nexoraInk, width: 3),
        boxShadow: const [
          BoxShadow(
            color: AppColors.nexoraInk,
            offset: Offset(6, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                child: NexoraIcon(NexoraIcons.profile, color: AppColors.nexoraInk),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Text(
                  'Personalized Quiz',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Focus on your weaknesses and get tested on what matters most.',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppColors.nexoraInk.withValues(alpha: 0.9),
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Select a document below, then choose "Take Personalized Quiz" in the setup.',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 12,
              fontStyle: FontStyle.italic,
              color: AppColors.nexoraInk,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDocumentSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Select Document',
          style: TextStyle(
            fontFamily: 'BricolageGrotesque',
            fontSize: 24,
            fontWeight: FontWeight.w800,
            color: AppColors.nexoraInk,
          ),
        ),
        const SizedBox(height: 16),
        if (_documents.isEmpty)
          Container(
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
              children: [
                NexoraIcon(NexoraIcons.library, size: 48, color: AppColors.nexoraLavender),
                const SizedBox(height: 16),
                const Text(
                  'No materials yet',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.nexoraInk,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Head over to the Library to add some study materials before taking a quiz.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 14,
                    color: AppColors.nexoraInk.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ),
          )
        else
          ..._documents.map((doc) => DocumentListItem(
                document: doc,
                onTap: () => _navigateToSetup(doc),
              )),
      ],
    );
  }
}
