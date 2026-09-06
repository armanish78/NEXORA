import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class NexoraProgressBar extends StatelessWidget {
  final double progress; // 0.0 to 1.0
  final Color color;
  final Color backgroundColor;
  final double height;
  final bool animate;

  const NexoraProgressBar({
    super.key,
    required this.progress,
    this.color = AppColors.success,
    this.backgroundColor = AppColors.border,
    this.height = 12.0,
    this.animate = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(height / 2),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth * progress.clamp(0.0, 1.0);
          return Align(
            alignment: Alignment.centerLeft,
            child: animate
                ? AnimatedContainer(
                    duration: const Duration(milliseconds: 500),
                    curve: Curves.easeOutCubic,
                    width: width,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(height / 2),
                    ),
                  )
                : Container(
                    width: width,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(height / 2),
                    ),
                  ),
          );
        },
      ),
    );
  }
}
