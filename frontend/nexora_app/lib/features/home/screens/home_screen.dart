import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/local_storage_service.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/models/progress_model.dart';

import '../widgets/home_header.dart';
import '../widgets/ask_nexora_bar.dart';
import '../widgets/stats_row.dart';
import '../widgets/core_actions_grid.dart';
import '../widgets/recent_materials_list.dart';
import '../widgets/empty_learning_hero.dart';
import '../../../core/widgets/nexora_shapes.dart';
import '../../../core/theme/app_colors.dart';
import '../../study/screens/study_screen.dart';

// Old imports kept in the project directory but not imported here.

class HomeScreen extends StatefulWidget {
  final VoidCallback? onNavigateToLibrary;

  const HomeScreen({super.key, this.onNavigateToLibrary});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiClient _apiClient = ApiClient();
  final LocalStorageService _storage = LocalStorageService();
  final ImagePicker _imagePicker = ImagePicker();
  
  bool _isLoading = false;
  
  List<DocumentMetadata> _documents = [];
  DocumentMetadata? _activeDocument;
  UserProgress? _progress;
  
  // Dummy user ID for this implementation
  final int _userId = 1;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    
    try {
      final docs = await _storage.getDocuments();
      final active = await _storage.getLastAccessedDocument();
      
      UserProgress? prog;
      
      try {
        final progData = await _apiClient.getUserProgress(_userId);
        prog = UserProgress.fromJson(progData);
      } catch (_) {}
      
      try {
        final weakData = await _apiClient.getWeakTopics(_userId);
        if (weakData is List && weakData.isNotEmpty) {
          // Keep fetch to not break api expectations but don't store
        }
      } catch (_) {}

      if (mounted) {
        setState(() {
          _documents = docs;
          _activeDocument = active;
          _progress = prog;
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _handleUpload(bool isCamera) async {
    String? filePath;
    String? filename;
    String? fileType;

    if (isCamera) {
      final XFile? photo = await _imagePicker.pickImage(source: ImageSource.camera);
      if (photo != null) {
        filePath = photo.path;
        filename = photo.name;
        fileType = 'image/jpeg';
      }
    } else {
      final result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'txt', 'md', 'jpg', 'jpeg', 'png'],
      );
      if (result.isNotEmpty && result.first.path != null) {
        filePath = result.first.path!;
        filename = result.first.name;
        fileType = result.first.extension ?? 'unknown';
      }
    }

    if (filePath == null || filename == null) return;

    setState(() => _isLoading = true);

    try {
      final response = await _apiClient.uploadDocument(filePath, filename: filename);
      if (response['success'] == true) {
        final newDoc = DocumentMetadata(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          filename: filename,
          type: fileType ?? 'unknown',
          uploadDate: DateTime.now(),
        );
        
        await _storage.saveDocument(newDoc);
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Material added successfully')),
          );
        }
        await _loadDashboardData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to upload material: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showAddMaterialOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: NexoraIcon(NexoraIcons.upload),
                title: const Text('Upload File'),
                onTap: () {
                  Navigator.pop(context);
                  _handleUpload(false);
                },
              ),
              ListTile(
                leading: NexoraIcon(NexoraIcons.camera),
                title: const Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  _handleUpload(true);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      body: NexoraBackground(
        variant: _documents.isEmpty ? NexoraBackgroundVariant.homeEmpty : NexoraBackgroundVariant.homeActive,
        child: SafeArea(
          bottom: false, // AppShell handles bottom padding
          child: _isLoading && _documents.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _loadDashboardData,
                  child: ListView(
                    physics: const ClampingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
                    children: [
                      const HomeHeader(),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 4.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Stack(
                                        clipBehavior: Clip.none,
                                        children: [
                                          const Text(
                                            'Hey there,',
                                            style: TextStyle(
                                              fontFamily: 'BricolageGrotesque',
                                              fontSize: 36,
                                              fontWeight: FontWeight.w900,
                                              color: AppColors.nexoraInk,
                                              letterSpacing: -0.5,
                                              height: 1.1,
                                            ),
                                          ),
                                          Positioned(
                                            bottom: 4, // Fixed collision (was 2)
                                            left: 0,
                                            width: 120,
                                            child: Container(
                                              height: 8,
                                              decoration: BoxDecoration(
                                                color: AppColors.nexoraYellow,
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                      const Text(
                                        'Ready to learn?',
                                        style: TextStyle(
                                          fontFamily: 'BricolageGrotesque',
                                          fontSize: 36,
                                          fontWeight: FontWeight.w900,
                                          color: AppColors.nexoraInk,
                                          letterSpacing: -0.5,
                                          height: 1.1,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                // Cleaned up text block
                                Transform.rotate(
                                  angle: 0.05,
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: AppColors.nexoraCyan,
                                      borderRadius: BorderRadius.circular(12),
                                      border: Border.all(color: AppColors.nexoraInk, width: 2),
                                      boxShadow: const [
                                        BoxShadow(
                                          color: AppColors.nexoraInk,
                                          offset: Offset(2, 2),
                                        ),
                                      ],
                                    ),
                                    child: const Text(
                                      'Better\nLearning\nBrighter\nYou',
                                      textAlign: TextAlign.center,
                                      style: TextStyle(
                                        fontFamily: 'DMSans',
                                        fontSize: 10,
                                        fontWeight: FontWeight.w800,
                                        color: AppColors.nexoraInk,
                                        height: 1.1,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Turn your study materials into interactive\nquizzes, notes and AI-powered insights.',
                              style: TextStyle(
                                fontFamily: 'DMSans',
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: AppColors.nexoraInk.withOpacity(0.8),
                              ),
                            ),
                          ],
                        ),
                      ),
                        const SizedBox(height: 16),
                        AskNexoraBar(
                          onTap: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Ask NEXORA clicked')),
                            );
                          },
                        ),
                        const SizedBox(height: 8),
                        if (_documents.isEmpty)
                          EmptyLearningHero(
                            onAddMaterial: _showAddMaterialOptions,
                          )
                        else
                          StatsRow(progress: _progress),
                        const SizedBox(height: 8),
                        CoreActionsGrid(
                          isEmptyState: _documents.isEmpty,
                          onAddMaterial: _showAddMaterialOptions,
                          onAskAiTutor: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Ask AI Tutor clicked')),
                            );
                          },
                          onContinueStudy: _activeDocument != null
                              ? () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => StudyScreen(document: _activeDocument!),
                                    ),
                                  );
                                }
                              : null,
                        ),
                        if (_documents.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          RecentMaterialsList(
                            documents: _documents,
                            onViewLibrary: () {
                              if (widget.onNavigateToLibrary != null) {
                                widget.onNavigateToLibrary!();
                              }
                            },
                          ),
                        ],
                        const SizedBox(height: 120), // Breathing room above nav bar
                      ],
                    ),
                  ),
        ),
      ),
    );
  }
}
