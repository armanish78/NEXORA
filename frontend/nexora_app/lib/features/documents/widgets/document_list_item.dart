import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/theme/app_colors.dart';

class DocumentListItem extends StatelessWidget {
  final DocumentMetadata document;
  final VoidCallback onTap;

  const DocumentListItem({
    super.key,
    required this.document,
    required this.onTap,
  });

  Color _getColorForType(String type) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return AppColors.nexoraCoral;
      case 'txt':
      case 'md':
        return AppColors.nexoraYellow;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return AppColors.nexoraCyan;
      default:
        return AppColors.nexoraGreen;
    }
  }

  String _getShortType(String type) {
    if (type.toLowerCase() == 'jpeg') return 'JPG';
    return type.toUpperCase();
  }

  String _formatDate(DateTime date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[date.month - 1]} ${date.day}, ${date.year}';
  }

  @override
  Widget build(BuildContext context) {
    final bgColor = _getColorForType(document.type);
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            color: AppColors.nexoraCream,
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
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: bgColor,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                alignment: Alignment.center,
                child: Text(
                  _getShortType(document.type),
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 14,
                    fontWeight: FontWeight.w900,
                    color: AppColors.nexoraInk,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      document.filename,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontFamily: 'BricolageGrotesque',
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatDate(document.uploadDate),
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.nexoraInk.withValues(alpha: 0.6),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                alignment: Alignment.center,
                child: NexoraIcon(NexoraIcons.forward, size: 16, color: AppColors.nexoraInk),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
