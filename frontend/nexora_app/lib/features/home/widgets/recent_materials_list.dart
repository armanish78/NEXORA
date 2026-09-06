import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../../core/models/document_metadata.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/nexora_container.dart';
import '../../study/screens/study_screen.dart';

class RecentMaterialsList extends StatelessWidget {
  final List<DocumentMetadata> documents;
  final VoidCallback onViewLibrary;

  const RecentMaterialsList({
    super.key,
    required this.documents,
    required this.onViewLibrary,
  });

  @override
  Widget build(BuildContext context) {
    if (documents.isEmpty) {
      return const SizedBox.shrink(); // Hide if empty
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              const Text(
                'Recent Study Materials',
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: AppColors.nexoraInk,
                ),
              ),
              GestureDetector(
                onTap: onViewLibrary,
                child: const Row(
                  children: [
                    Text(
                      'View Library',
                      style: TextStyle(
                        fontFamily: 'BricolageGrotesque',
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: AppColors.nexoraCyan,
                      ),
                    ),
                    SizedBox(width: 4),
                    NexoraIcon(NexoraIcons.forward, color: AppColors.nexoraCyan, size: 14),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...documents.take(3).map((doc) => _buildDocumentItem(context, doc)),
        ],
      ),
    );
  }

  Widget _buildDocumentItem(BuildContext context, DocumentMetadata doc) {
    String typeText = 'DOC';
    Color typeColor = AppColors.nexoraMutedInk;

    if (doc.type.toLowerCase().contains('pdf')) {
      typeText = 'PDF';
      typeColor = AppColors.nexoraCoral; // Red
    } else if (doc.type.toLowerCase().contains('image') || doc.type.toLowerCase().contains('jpg') || doc.type.toLowerCase().contains('png')) {
      typeText = 'IMG';
      typeColor = AppColors.nexoraCyan; // Cyan
    }

    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => StudyScreen(document: doc),
          ),
        );
      },
      child: NexoraContainer(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        borderRadius: BorderRadius.circular(100),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.nexoraCream, // Very light tint
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.nexoraInk, width: 1.5),
              ),
              child: Text(
                typeText,
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  color: typeColor,
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    doc.filename,
                    style: const TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                      color: AppColors.nexoraInk,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Uploaded ${doc.uploadDate.toLocal().toString().split(' ')[0]}',
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: AppColors.nexoraMutedInk,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
              child: NexoraIcon(NexoraIcons.forward, color: AppColors.nexoraInk, size: 18),
            ),
          ],
        ),
      ),
    );
  }
}
