import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

enum QuizOptionState {
  unselected,
  selected,
  correct,
  incorrect,
  muted,
}

class QuizOptionWidget extends StatelessWidget {
  final String text;
  final String label; // A, B, C, D
  final QuizOptionState state;
  final VoidCallback onTap;

  const QuizOptionWidget({
    super.key,
    required this.text,
    required this.label,
    required this.state,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Color bgColor = AppColors.nexoraCream;
    Color borderColor = AppColors.nexoraInk;
    Color textColor = AppColors.nexoraInk;
    Color labelColor = AppColors.nexoraInk;
    Color labelBg = Colors.white;
    bool hasShadow = false;
    NexoraIcons? trailingIcon;
    
    switch (state) {
      case QuizOptionState.selected:
        bgColor = AppColors.nexoraYellow;
        hasShadow = true;
        break;
      case QuizOptionState.correct:
        bgColor = AppColors.nexoraGreen;
        trailingIcon = NexoraIcons.check;
        break;
      case QuizOptionState.incorrect:
        bgColor = AppColors.nexoraCoral;
        trailingIcon = NexoraIcons.close;
        break;
      case QuizOptionState.muted:
        bgColor = AppColors.nexoraInk.withValues(alpha: 0.1);
        borderColor = AppColors.nexoraInk.withValues(alpha: 0.3);
        textColor = AppColors.nexoraInk.withValues(alpha: 0.5);
        labelBg = Colors.white.withValues(alpha: 0.5);
        labelColor = AppColors.nexoraInk.withValues(alpha: 0.5);
        trailingIcon = NexoraIcons.close;
        break;
      case QuizOptionState.unselected:
        break;
    }

    return GestureDetector(
      onTap: state == QuizOptionState.unselected || state == QuizOptionState.selected ? onTap : null,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: borderColor, width: 3),
          boxShadow: hasShadow
              ? [
                  const BoxShadow(
                    color: AppColors.nexoraInk,
                    offset: Offset(4, 4),
                  )
                ]
              : null,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: labelBg,
                shape: BoxShape.circle,
                border: Border.all(color: borderColor, width: 2),
              ),
              alignment: Alignment.center,
              child: Text(
                label,
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: labelColor,
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                text,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
            ),
            if (trailingIcon != null)
              Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: NexoraIcon(
                  trailingIcon,
                  color: state == QuizOptionState.muted 
                      ? AppColors.nexoraInk.withValues(alpha: 0.3)
                      : AppColors.nexoraInk,
                  size: 24,
                ),
              ),
          ],
        ),
      ),
    );
  }
}
