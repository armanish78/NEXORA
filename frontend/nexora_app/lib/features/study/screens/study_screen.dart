import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/storage/local_storage_service.dart';
import '../../../core/theme/app_colors.dart';
import 'study_session_page.dart';

class StudyScreen extends StatefulWidget {
  final DocumentMetadata document;

  const StudyScreen({super.key, required this.document});

  @override
  State<StudyScreen> createState() => _StudyScreenState();
}

class _StudyScreenState extends State<StudyScreen> {
  final LocalStorageService _storageService = LocalStorageService();
  
  List<DocumentMetadata> _documents = [];
  PageController? _pageController;
  int _currentIndex = 0;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    final docs = await _storageService.getDocuments();
    
    // Find the requested document
    int targetIndex = docs.indexWhere((d) => d.id == widget.document.id);
    
    if (targetIndex == -1) {
      // Document is new or not found, insert it at front
      docs.insert(0, widget.document);
      targetIndex = 0;
    }

    if (mounted) {
      setState(() {
        _documents = docs;
        _currentIndex = targetIndex;
        _pageController = PageController(initialPage: _currentIndex);
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _pageController?.dispose();
    super.dispose();
  }

  void _onNewDocumentUploaded(DocumentMetadata newDoc) {
    setState(() {
      _documents.insert(0, newDoc);
      _currentIndex = 0;
    });
    // Jump to the newly inserted document which is now at index 0
    _pageController?.jumpToPage(0);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Container(
            decoration: BoxDecoration(
              color: AppColors.nexoraYellow,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.nexoraInk, width: 2),
            ),
            child: IconButton(
              icon: NexoraIcon(NexoraIcons.back, color: AppColors.nexoraInk, size: 20),
              onPressed: () => Navigator.pop(context),
            ),
          ),
        ),
        title: Column(
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                NexoraIcon(NexoraIcons.sparkle, size: 16, color: AppColors.nexoraInk),
                const SizedBox(width: 8),
                const Text(
                  'NEXORA',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 20,
                    fontWeight: FontWeight.w900,
                    color: AppColors.nexoraInk,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(width: 8),
                NexoraIcon(NexoraIcons.sparkle, size: 16, color: AppColors.nexoraInk),
              ],
            ),
            const Text(
              'STUDY',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 12,
                fontWeight: FontWeight.w900,
                color: AppColors.nexoraInk,
                letterSpacing: 4,
              ),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Container(
              width: 44, // Match size to preserve layout balance without the icon
            ),
          ),
        ],
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator(color: AppColors.nexoraInk))
        : PageView.builder(
            controller: _pageController,
            physics: const BouncingScrollPhysics(),
            onPageChanged: (index) {
              setState(() {
                _currentIndex = index;
              });
            },
            itemCount: _documents.length,
            itemBuilder: (context, index) {
              return StudySessionPage(
                document: _documents[index],
                onNewDocumentUploaded: _onNewDocumentUploaded,
              );
            },
          ),
    );
  }
}
