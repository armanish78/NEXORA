import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../../core/models/document_metadata.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/nexora_container.dart';
import '../../../../core/models/progress_model.dart';

class CurrentLearningCard extends StatelessWidget {
  final DocumentMetadata? activeDocument;
  final UserProgress? progress;

  const CurrentLearningCard({
    super.key,
    this.activeDocument,
    this.progress,
  });

  @override
  Widget build(BuildContext context) {
    if (activeDocument == null) {
      return const SizedBox.shrink();
    }

    final double mastery = progress?.totalMastery ?? 0.0;

    return Padding(
      padding: const EdgeInsets.only(left: 24.0, right: 24.0, top: 16.0, bottom: 8.0),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          NexoraContainer(
            margin: const EdgeInsets.only(top: 16),
            padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
            backgroundColor: AppColors.nexoraCyan.withOpacity(0.3), // Light Cyan tint
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Inner white box for document icon
                NexoraContainer(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.white,
                  child: Column(
                    children: [
                      NexoraIcon(NexoraIcons.document, size: 32, color: AppColors.nexoraInk),
                      const SizedBox(height: 8),
                      Text(
                        activeDocument!.type.toUpperCase(),
                        style: const TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          color: AppColors.nexoraInk,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  activeDocument!.filename,
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: AppColors.nexoraInk,
                    height: 1.2,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 16),
                // Progress Bar
                Container(
                  height: 12,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(100),
                    border: Border.all(color: AppColors.nexoraInk, width: 2),
                  ),
                  child: mastery > 0 
                      ? FractionallySizedBox(
                          alignment: Alignment.centerLeft,
                          widthFactor: mastery.clamp(0.0, 1.0),
                          child: Container(
                            decoration: BoxDecoration(
                              color: AppColors.nexoraCyan,
                              borderRadius: BorderRadius.circular(100),
                              border: const Border(
                                right: BorderSide(color: AppColors.nexoraInk, width: 2),
                              ),
                            ),
                          ),
                        )
                      : null,
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${(mastery * 100).toInt()}%',
                          style: const TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                        Text(
                          'Mastered',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: AppColors.nexoraInk.withOpacity(0.8),
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: AppColors.nexoraInk,
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: const Row(
                        children: [
                          NexoraIcon(NexoraIcons.play, color: Colors.white, size: 16),
                          SizedBox(width: 4),
                          Text(
                            'Continue',
                            style: TextStyle(
                              fontFamily: 'BricolageGrotesque',
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // ACTIVE DOCUMENT Tab
          Positioned(
            top: 0,
            left: 24,
            child: NexoraContainer(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              backgroundColor: Colors.white,
              borderRadius: BorderRadius.circular(100),
              borderWidth: 2,
              shadow: false,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: AppColors.nexoraCyan,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text(
                    'ACTIVE DOCUMENT',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: AppColors.nexoraInk,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
