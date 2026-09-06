import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/storage/local_storage_service.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_shapes.dart';
import '../widgets/library_header.dart';
import '../widgets/library_search_bar.dart';
import '../widgets/library_empty_state.dart';
import '../widgets/document_list_item.dart';
import '../widgets/library_filter_row.dart';
import '../../study/screens/study_screen.dart';
import '../../../core/utils/upload_helper.dart';

class LibraryScreen extends StatefulWidget {
  const LibraryScreen({super.key});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  final LocalStorageService _storage = LocalStorageService();
  
  bool _isLoading = false;
  List<DocumentMetadata> _documents = [];
  
  String _searchQuery = '';
  String _activeFilter = 'All';
  final List<String> _filters = ['All', 'PDFs', 'Notes', 'Images'];

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    setState(() => _isLoading = true);
    try {
      final docs = await _storage.getDocuments();
      // Sort recently uploaded first
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

  Future<void> _handleUpload(bool isCamera) async {
    if (_isLoading) return;

    final newDoc = await UploadHelper.handleUpload(context, isCamera, (loading) {
      if (mounted) {
        setState(() => _isLoading = loading);
      }
    });

    if (newDoc != null && mounted) {
      await _loadDocuments();
    }
  }

  void _showAddMaterialOptions() {
    UploadHelper.showAddMaterialOptions(context, onSelect: (isCamera) {
      _handleUpload(isCamera);
    });
  }

  List<DocumentMetadata> get _filteredDocuments {
    return _documents.where((doc) {
      final matchesQuery = doc.filename.toLowerCase().contains(_searchQuery.toLowerCase());
      if (!matchesQuery) return false;

      switch (_activeFilter) {
        case 'PDFs':
          return doc.type.toLowerCase() == 'pdf';
        case 'Notes':
          return ['txt', 'md'].contains(doc.type.toLowerCase());
        case 'Images':
          return ['jpg', 'jpeg', 'png'].contains(doc.type.toLowerCase());
        case 'All':
        default:
          return true;
      }
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final displayDocs = _filteredDocuments;

    return Scaffold(
      extendBody: true,
      backgroundColor: AppColors.nexoraCream,
      body: NexoraBackground(
        variant: NexoraBackgroundVariant.library,
        child: SafeArea(
          bottom: false,
          child: _isLoading && _documents.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _loadDocuments,
                  child: ListView(
                    physics: const ClampingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
                    children: [
                      const LibraryHeader(),
                      if (_documents.isNotEmpty) ...[
                        LibrarySearchBar(
                          query: _searchQuery,
                          onChanged: (q) => setState(() => _searchQuery = q),
                          onClear: () => setState(() => _searchQuery = ''),
                        ),
                        LibraryFilterRow(
                          filters: _filters,
                          activeFilter: _activeFilter,
                          onFilterChanged: (f) => setState(() => _activeFilter = f),
                        ),
                        const SizedBox(height: 8),
                      ],
                      if (_documents.isEmpty)
                        LibraryEmptyState(onAddMaterial: _showAddMaterialOptions)
                      else if (displayDocs.isEmpty)
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
                          child: Center(
                            child: Text(
                              'No materials match your search.',
                              style: TextStyle(
                                fontFamily: 'DMSans',
                                fontSize: 16,
                                color: AppColors.mutedText,
                              ),
                            ),
                          ),
                        )
                      else
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 24.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Recent Materials Header
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'Recent Materials',
                                    style: TextStyle(
                                      fontFamily: 'BricolageGrotesque',
                                      fontSize: 18,
                                      fontWeight: FontWeight.w800,
                                      color: AppColors.nexoraInk,
                                    ),
                                  ),
                                  Text(
                                    '${displayDocs.length} material${displayDocs.length == 1 ? '' : 's'}',
                                    style: TextStyle(
                                      fontFamily: 'DMSans',
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: AppColors.nexoraInk.withValues(alpha: 0.6),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              // Document List
                              ...displayDocs.map((doc) => DocumentListItem(
                                document: doc,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => StudyScreen(document: doc),
                                    ),
                                  );
                                },
                              )),
                            ],
                          ),
                        ),
                      
                      // Footer actions when populated
                      if (_documents.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                          child: Column(
                            children: [
                              // Upload more materials button
                              GestureDetector(
                                onTap: _showAddMaterialOptions,
                                child: Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(16),
                                    border: Border.all(color: AppColors.nexoraInk, width: 1.5, style: BorderStyle.none),
                                  ),
                                  child: CustomPaint(
                                    painter: DashedRectPainter(color: AppColors.nexoraInk, strokeWidth: 1.5, radius: 16),
                                    child: const Row(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        NexoraIcon(NexoraIcons.add, color: AppColors.nexoraInk),
                                        SizedBox(width: 8),
                                        Text(
                                          'Upload more materials to keep learning!',
                                          style: TextStyle(
                                            fontFamily: 'DMSans',
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                            color: AppColors.nexoraInk,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 24),
                              // Motivational info pill
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                                decoration: BoxDecoration(
                                  color: AppColors.nexoraLavender,
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                                  boxShadow: const [
                                    BoxShadow(
                                      color: AppColors.nexoraInk,
                                      offset: Offset(4, 4),
                                      blurRadius: 0,
                                    ),
                                  ],
                                ),
                                child: Row(
                                  children: [
                                    NexoraIcon(NexoraIcons.quote, color: AppColors.nexoraInk),
                                    const SizedBox(width: 12),
                                    const Expanded(
                                      child: Text(
                                        'A well-organized library builds a focused mind.',
                                        style: TextStyle(
                                          fontFamily: 'DMSans',
                                          fontSize: 12,
                                          fontWeight: FontWeight.w600,
                                          color: AppColors.nexoraInk,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    const Text(
                                      'Keep Growing',
                                      style: TextStyle(
                                        fontFamily: 'BricolageGrotesque',
                                        fontSize: 12,
                                        fontWeight: FontWeight.w800,
                                        color: AppColors.nexoraInk,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    NexoraIcon(NexoraIcons.forward, color: AppColors.nexoraInk, size: 14),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      const SizedBox(height: 120), // Large breathing room above nav bar
                    ],
                  ),
                ),
        ),
      ),
    );
  }
}
