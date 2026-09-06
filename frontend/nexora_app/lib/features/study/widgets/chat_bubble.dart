import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../core/theme/app_colors.dart';
import '../models/study_message.dart';

class ChatBubble extends StatelessWidget {
  final StudyMessage message;
  final VoidCallback? onRetry;

  const ChatBubble({super.key, required this.message, this.onRetry});

  @override
  Widget build(BuildContext context) {
    if (message.isError) {
      return _buildErrorBubble(context);
    }

    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16.0),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        decoration: BoxDecoration(
          color: message.isUser ? AppColors.nexoraYellow : Colors.white,
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
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            message.isUser
                ? Text(
                    message.text,
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.nexoraInk,
                      height: 1.5,
                    ),
                  )
                : MarkdownBody(
                    data: message.text.replaceAll(RegExp(r' ?\[[^\]]+,\s*Page[^\]]+\]'), ''),
                    styleSheet: MarkdownStyleSheet(
                      p: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.nexoraInk,
                        height: 1.5,
                      ),
                      h1: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      h2: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      h3: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      h4: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      h5: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      h6: const TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.nexoraInk),
                      listBullet: const TextStyle(color: AppColors.nexoraInk),
                    ),
                  ),
            if (message.citations != null && message.citations!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: message.citations!.map((citation) {
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.nexoraLavender,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        NexoraIcon(NexoraIcons.document, size: 12, color: AppColors.nexoraInk),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Text(
                            citation,
                            style: const TextStyle(
                              fontFamily: 'BricolageGrotesque',
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: AppColors.nexoraInk,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildErrorBubble(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16.0),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        decoration: BoxDecoration(
          color: AppColors.errorBackground,
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
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                NexoraIcon(NexoraIcons.warning, color: AppColors.error),
                const SizedBox(width: 8),
                const Text(
                  'Connection Error',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              message.text,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: AppColors.nexoraInk,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 16),
            if (onRetry != null)
              GestureDetector(
                onTap: onRetry,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: AppColors.nexoraYellow,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      NexoraIcon(NexoraIcons.retry, size: 16, color: AppColors.nexoraInk),
                      const SizedBox(width: 6),
                      const Text(
                        'Try Again',
                        style: TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: AppColors.nexoraInk,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
