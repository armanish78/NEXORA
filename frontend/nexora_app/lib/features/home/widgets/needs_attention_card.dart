import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../../core/models/topic_model.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/nexora_container.dart';

class NeedsAttentionCard extends StatelessWidget {
  final Topic? weakTopic;
  final double? accuracy;
  final VoidCallback onPractice;

  const NeedsAttentionCard({
    super.key,
    this.weakTopic,
    this.accuracy,
    required this.onPractice,
  });

  @override
  Widget build(BuildContext context) {
    if (weakTopic == null) {
      return const SizedBox.shrink(); // Hide if no weak topic
    }

    final double accuracyVal = accuracy ?? 0.0;

    return Padding(
      padding: const EdgeInsets.only(left: 24.0, right: 24.0, top: 16.0, bottom: 8.0),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          NexoraContainer(
            margin: const EdgeInsets.only(top: 16),
            padding: const EdgeInsets.fromLTRB(16, 24, 16, 16),
            backgroundColor: AppColors.nexoraCoral.withOpacity(0.3), // Light Coral tint
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Inner white box for warning
                NexoraContainer(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.white,
                  child: Column(
                    children: [
                      NexoraIcon(NexoraIcons.warning, size: 32, color: AppColors.nexoraCoral),
                      const SizedBox(height: 8),
                      Text(
                        'REVIEW NEEDED',
                        style: const TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          color: AppColors.nexoraCoral,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  weakTopic!.name,
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
                // Accuracy Bar
                Container(
                  height: 12,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(100),
                    border: Border.all(color: AppColors.nexoraInk, width: 2),
                  ),
                  child: accuracyVal > 0
                      ? FractionallySizedBox(
                          alignment: Alignment.centerLeft,
                          widthFactor: accuracyVal.clamp(0.0, 1.0),
                          child: Container(
                            decoration: BoxDecoration(
                              color: AppColors.nexoraCoral, // Red fill
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
                          '${(accuracyVal * 100).toInt()}%',
                          style: const TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 18,
                            fontWeight: FontWeight.w800,
                            color: AppColors.nexoraInk,
                          ),
                        ),
                        Text(
                          'Accuracy',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: AppColors.nexoraInk.withOpacity(0.8),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          // NEEDS ATTENTION Tab
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
                      color: AppColors.nexoraCoral, // Red dot
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text(
                    'NEEDS ATTENTION',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: AppColors.nexoraInk, // Dark text
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
