import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_container.dart';

class CoreActionsGrid extends StatelessWidget {
  final VoidCallback onAddMaterial;
  final VoidCallback onAskAiTutor;
  final VoidCallback? onContinueStudy;
  final bool isEmptyState;

  const CoreActionsGrid({
    super.key,
    required this.onAddMaterial,
    required this.onAskAiTutor,
    this.onContinueStudy,
    this.isEmptyState = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 4.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Text(
                'Quick Actions',
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: AppColors.nexoraInk,
                ),
              ),
              Text(
                'LEARN • PRACTICE • IMPROVE',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 8,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.5,
                  color: AppColors.nexoraInk.withOpacity(0.6),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: _buildAction(
                  icon: NexoraIcons.add,
                  label: 'Add\nMaterial',
                  onTap: onAddMaterial,
                  bgColor: AppColors.nexoraYellow,
                ),
              ),
              const SizedBox(width: 12), // Fixed gap
              Expanded(
                child: _buildAction(
                  icon: NexoraIcons.more,
                  label: 'Ask AI\nTutor',
                  onTap: onAskAiTutor,
                  isDisabled: true,
                  bgColor: AppColors.nexoraLavender,
                ),
              ),
              const SizedBox(width: 12), // Fixed gap
              Expanded(
                child: _buildAction(
                  icon: NexoraIcons.bookmark,
                  label: 'Continue\nStudy',
                  onTap: onContinueStudy,
                  isDisabled: isEmptyState || onContinueStudy == null,
                  bgColor: const Color(0xFFC4E8FA), // Light Blue tint
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Motivational Quote Pill
          NexoraContainer(
            backgroundColor: AppColors.nexoraLavender,
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            borderRadius: BorderRadius.circular(100),
            child: Row(
              children: [
                NexoraIcon(NexoraIcons.quote, color: AppColors.nexoraInk, size: 24),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'A little progress each day\nadds up to big results.',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: AppColors.nexoraInk.withOpacity(0.8),
                      height: 1.2,
                    ),
                  ),
                ),
                Text(
                  'Keep Going',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: AppColors.nexoraInk,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                  ),
                  child: NexoraIcon(NexoraIcons.forward, color: AppColors.nexoraInk, size: 14),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAction({
    required NexoraIcons icon,
    required String label,
    required VoidCallback? onTap,
    required Color bgColor,
    bool isDisabled = false,
  }) {
    return GestureDetector(
      onTap: isDisabled ? null : onTap,
      child: Opacity(
        opacity: isDisabled ? 0.4 : 1.0,
        child: AspectRatio(
          aspectRatio: 0.85,
          child: NexoraContainer(
            backgroundColor: bgColor,
            borderRadius: BorderRadius.circular(16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.nexoraInk, width: 1.5),
                  ),
                  child: NexoraIcon(icon, color: AppColors.nexoraInk, size: 20),
                ),
                const SizedBox(height: 8),
                Text(
                  label,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: AppColors.nexoraInk,
                    height: 1.2,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
