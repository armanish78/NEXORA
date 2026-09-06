import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

enum NexoraBadgeVariant { primary, success, warning, error, neutral }

class NexoraBadge extends StatelessWidget {
  final String text;
  final NexoraIcons? icon;
  final NexoraBadgeVariant variant;

  const NexoraBadge({
    super.key,
    required this.text,
    this.icon,
    this.variant = NexoraBadgeVariant.primary,
  });

  @override
  Widget build(BuildContext context) {
    final colors = _getColors();
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: colors.backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            NexoraIcon(icon!, size: 14, color: colors.textColor),
            const SizedBox(width: 4),
          ],
          Text(
            text,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: colors.textColor,
            ),
          ),
        ],
      ),
    );
  }

  _BadgeColors _getColors() {
    switch (variant) {
      case NexoraBadgeVariant.primary:
        return _BadgeColors(
          backgroundColor: AppColors.primary.withValues(alpha: 0.1),
          textColor: AppColors.primary,
        );
      case NexoraBadgeVariant.success:
        return _BadgeColors(
          backgroundColor: AppColors.successBackground,
          textColor: AppColors.success,
        );
      case NexoraBadgeVariant.warning:
        return _BadgeColors(
          backgroundColor: AppColors.attention.withValues(alpha: 0.1),
          textColor: AppColors.attention,
        );
      case NexoraBadgeVariant.error:
        return _BadgeColors(
          backgroundColor: AppColors.errorBackground,
          textColor: AppColors.error,
        );
      case NexoraBadgeVariant.neutral:
        return _BadgeColors(
          backgroundColor: AppColors.surface,
          textColor: AppColors.secondaryText,
        );
    }
  }
}

class _BadgeColors {
  final Color backgroundColor;
  final Color textColor;

  _BadgeColors({required this.backgroundColor, required this.textColor});
}
