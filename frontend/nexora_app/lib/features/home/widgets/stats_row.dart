import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/models/progress_model.dart';
import '../../../core/widgets/nexora_container.dart';

class StatsRow extends StatelessWidget {
  final UserProgress? progress;

  const StatsRow({super.key, this.progress});

  @override
  Widget build(BuildContext context) {
    if (progress == null) return const SizedBox.shrink();

    List<Widget> stats = [];

    // Streak
    if (progress!.streak != null && progress!.streak! > 0) {
      stats.add(_buildStatPill(
        icon: NexoraIcons.check,
        iconColor: Colors.deepOrange,
        iconBgColor: AppColors.nexoraYellow,
        value: '${progress!.streak} Days',
        label: 'Streak',
      ));
    }

    // XP
    if (progress!.xp != null && progress!.xp! > 0) {
      stats.add(_buildStatPill(
        icon: NexoraIcons.check,
        iconColor: AppColors.nexoraInk,
        iconBgColor: AppColors.nexoraCyan,
        value: '${progress!.xp}',
        label: 'XP Earned',
      ));
    }

    // Mastery
    if (progress!.totalMastery > 0) {
      stats.add(_buildStatPill(
        icon: NexoraIcons.check,
        iconColor: AppColors.nexoraInk,
        iconBgColor: AppColors.nexoraLavender,
        value: '${(progress!.totalMastery * 100).toInt()}%',
        label: 'Mastered',
      ));
    }

    if (stats.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: stats.map((w) => Expanded(child: Padding(
          padding: EdgeInsets.only(right: w == stats.last ? 0 : 8.0),
          child: w,
        ))).toList(),
      ),
    );
  }

  Widget _buildStatPill({
    required NexoraIcons icon,
    required Color iconColor,
    required Color iconBgColor,
    required String value,
    required String label,
  }) {
    return NexoraContainer(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
      borderRadius: BorderRadius.circular(100),
      backgroundColor: Colors.white,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(4.0),
            decoration: BoxDecoration(
              color: iconBgColor,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.nexoraInk, width: 2),
            ),
            child: NexoraIcon(icon, color: iconColor, size: 16),
          ),
          const SizedBox(width: 6),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.nexoraInk,
                    height: 1.1,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  label,
                  style: const TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                    color: AppColors.nexoraMutedInk,
                    height: 1.1,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
