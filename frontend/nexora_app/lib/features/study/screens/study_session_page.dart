import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/local_storage_service.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/upload_helper.dart';
import '../models/study_message.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/suggested_questions.dart';

class StudySessionPage extends StatefulWidget {
  final DocumentMetadata document;
  final Function(DocumentMetadata) onNewDocumentUploaded;

  const StudySessionPage({
    super.key,
    required this.document,
    required this.onNewDocumentUploaded,
  });

  @override
  State<StudySessionPage> createState() => _StudySessionPageState();
}

class _StudySessionPageState extends State<StudySessionPage> with AutomaticKeepAliveClientMixin {
  final ApiClient _apiClient = ApiClient();
  final LocalStorageService _storageService = LocalStorageService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  List<StudyMessage> _messages = [];
  bool _isLoading = false;
  bool _isInit = false;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final history = await _storageService.getConversation(widget.document.id);
    if (mounted) {
      setState(() {
        _messages = history;
        _isInit = true;
      });
      _scrollToBottom();
    }
  }

  Future<void> _saveHistory() async {
    await _storageService.saveConversation(widget.document.id, _messages);
  }

  String _formatDate(DateTime date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }

  static final List<String> _greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you', 'okay', 'ok', 'bye', 'how are you', 'how are you?'];

  bool _isConversational(String text) {
    String lower = text.toLowerCase().trim().replaceAll(RegExp(r'[^\w\s]'), '');
    return _greetings.contains(lower);
  }

  void _sendMessage(String query) async {
    final text = query.trim();
    if (text.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(StudyMessage(text: text, isUser: true));
      _isLoading = true;
    });

    _controller.clear();
    _scrollToBottom();
    await _saveHistory();

    if (_isConversational(text)) {
      await Future.delayed(const Duration(milliseconds: 500));
      if (mounted) {
        setState(() {
          String reply = "Hey! 👋 Ready to study? Ask me something about this document.";
          String lower = text.toLowerCase().trim().replaceAll(RegExp(r'[^\w\s]'), '');
          if (lower.startsWith('thank')) {
            reply = "You're welcome! Keep the questions coming.";
          } else if (lower == 'bye') {
            reply = "Goodbye! Happy studying.";
          } else if (lower.startsWith('how are you')) {
            reply = "I'm ready to help you study. What would you like to explore?";
          }
          _messages.add(StudyMessage(text: reply, isUser: false));
          _isLoading = false;
        });
        _scrollToBottom();
        await _saveHistory();
      }
      return;
    }

    await _performAsk(text);
  }

  void _retryMessage(String originalQuery) async {
    if (_isLoading) return;
    
    setState(() {
      _messages.removeLast();
      _isLoading = true;
    });
    
    _scrollToBottom();
    await _saveHistory();
    await _performAsk(originalQuery);
  }
  
  Future<void> _performAsk(String text) async {
    try {
      final response = await _apiClient.askQuestion(
        query: text,
        filename: widget.document.filename,
      );

      if (mounted) {
        setState(() {
          if (response['success'] == true) {
            List<String> citations = [];
            if (response['citations'] != null && response['citations'] is List) {
              for (var item in response['citations']) {
                if (item is Map) {
                  String citationStr = "Source";
                  final heading = item['heading'];
                  final pageNum = item['page_num'];
                  
                  if (heading != null && heading.toString().trim().isNotEmpty) {
                    citationStr += " · $heading";
                  }
                  if (pageNum != null) {
                    citationStr += " · Page $pageNum";
                  }
                  
                  if (!citations.contains(citationStr)) {
                    citations.add(citationStr);
                  }
                }
              }
            }
            String rawAnswer = response['answer'] ?? 'No answer provided.';
            String cleanedAnswer = rawAnswer.replaceAll(RegExp(r'\[[^\]]+?,\s*Page\s+\d+\]\s*'), '').trim();
            
            _messages.add(StudyMessage(
              text: cleanedAnswer.isEmpty ? rawAnswer : cleanedAnswer,
              isUser: false,
              citations: citations,
            ));
          } else {
            String reason = response['reason'] ?? 'Failed to get answer.';
            if (reason.toLowerCase().contains('citation') || 
                reason.toLowerCase().contains('sufficient information') ||
                reason.toLowerCase().contains('grounding')) {
              reason = "I couldn't find enough grounded evidence in this document to answer that confidently.";
            }

            _messages.add(StudyMessage(
              text: reason,
              isUser: false,
              isError: true,
              originalQuery: text,
            ));
          }
        });
        await _saveHistory();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(StudyMessage(
            text: 'I couldn\'t reach NEXORA right now.\nPlease check that the server is running and try again.',
            isUser: false,
            isError: true,
            originalQuery: text,
          ));
        });
        await _saveHistory();
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _scrollToBottom();
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
      widget.onNewDocumentUploaded(newDoc);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    
    if (!_isInit) {
      return const Center(child: CircularProgressIndicator(color: AppColors.nexoraInk));
    }

    return Column(
      children: [
        Expanded(
          child: ListView(
            controller: _scrollController,
            padding: const EdgeInsets.all(16.0),
            children: [
              _buildDocumentHeader(),
              const SizedBox(height: 24),
              if (_messages.isEmpty) _buildEmptyState(),
              ..._messages.map((message) {
                return ChatBubble(
                  message: message,
                  onRetry: message.isError && message.originalQuery != null 
                      ? () => _retryMessage(message.originalQuery!) 
                      : null,
                );
              }),
              if (_isLoading)
                Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 16, left: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
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
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: AppColors.nexoraYellow,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Searching document...',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 14,
                            color: AppColors.nexoraInk.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
        _buildInputDock(),
      ],
    );
  }

  Widget _buildDocumentHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.nexoraInk,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    NexoraIcon(NexoraIcons.document, color: Colors.white, size: 24),
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppColors.nexoraYellow,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        widget.document.type.toUpperCase(),
                        style: const TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 8,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
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
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Uploaded ${_formatDate(widget.document.uploadDate)}',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 12,
                        color: AppColors.nexoraInk.withValues(alpha: 0.6),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildTag('Study Mode', AppColors.nexoraLavender),
              _buildTag('Document Scoped', AppColors.nexoraCyan),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border, width: 1),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    NexoraIcon(NexoraIcons.lock, size: 12, color: AppColors.nexoraInk),
                    const SizedBox(width: 4),
                    const Text(
                      'Grounded Answers',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.nexoraInk, width: 1),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontFamily: 'DMSans',
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Column(
      children: [
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppColors.nexoraInk, width: 2),
            boxShadow: const [
              BoxShadow(
                color: AppColors.nexoraInk,
                offset: Offset(4, 4),
                blurRadius: 0,
              ),
            ],
          ),
          child: Column(
            children: [
              NexoraIcon(NexoraIcons.school, size: 48, color: AppColors.nexoraYellow),
              const SizedBox(height: 16),
              const Text(
                "Let's start studying!",
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppColors.nexoraInk,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                "Ask questions about this document and get clear, grounded answers with citations.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 14,
                  color: AppColors.nexoraInk.withValues(alpha: 0.7),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        SuggestedQuestions(
          filename: widget.document.filename,
          onQuestionSelected: (q) => _sendMessage(q),
        ),
      ],
    );
  }

  Widget _buildInputDock() {
    return Container(
      padding: const EdgeInsets.only(left: 16.0, right: 16.0, top: 12.0, bottom: 24.0),
      decoration: const BoxDecoration(
        color: AppColors.nexoraCream,
      ),
      child: SafeArea(
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(32),
            border: Border.all(color: AppColors.nexoraInk, width: 2),
            boxShadow: const [
              BoxShadow(
                color: AppColors.nexoraInk,
                offset: Offset(0, 4),
                blurRadius: 0,
              ),
            ],
          ),
          child: Row(
            children: [
              const SizedBox(width: 16),
              GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: _isLoading ? null : () {
                  UploadHelper.showAddMaterialOptions(context, onSelect: (isCamera) {
                    _handleUpload(isCamera);
                  });
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0, vertical: 8.0),
                  child: Opacity(
                    opacity: _isLoading ? 0.3 : 1.0,
                    child: NexoraIcon(NexoraIcons.add, color: AppColors.nexoraInk),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  controller: _controller,
                  enabled: !_isLoading,
                  decoration: InputDecoration(
                    hintText: 'Ask a question about this document...',
                    hintStyle: TextStyle(
                      fontFamily: 'DMSans',
                      color: AppColors.nexoraInk.withValues(alpha: 0.4),
                      fontSize: 14,
                    ),
                    border: InputBorder.none,
                  ),
                  onSubmitted: _sendMessage,
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: GestureDetector(
                  onTap: _isLoading ? null : () => _sendMessage(_controller.text),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _isLoading ? Colors.grey : AppColors.nexoraYellow,
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.nexoraInk, width: 2),
                    ),
                    child: NexoraIcon(NexoraIcons.send, color: AppColors.nexoraInk, size: 20),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
