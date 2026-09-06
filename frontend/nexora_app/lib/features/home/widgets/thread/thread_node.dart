import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import 'thread_segment.dart';

class ThreadNode extends StatelessWidget {
  final ThreadNodeType type;
  final String title;
  final bool isFirst;
  final bool isLast;

  const ThreadNode({
    super.key,
    required this.type,
    required this.title,
    this.isFirst = false,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return ThreadSegment(
      type: type,
      isFirst: isFirst,
      isLast: isLast,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 24.0),
        child: Center(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(width: 48), // Padding to balance the title on right
              _buildMarker(),
              const SizedBox(width: 24),
              SizedBox(
                width: 140, // Fixed width for alignment
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: type == ThreadNodeType.past ? FontWeight.w600 : FontWeight.w400,
                    color: type == ThreadNodeType.past 
                        ? AppColors.success 
                        : AppColors.mutedText,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMarker() {
    final bool isPast = type == ThreadNodeType.past;
    
    return Container(
      width: 16,
      height: 16,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: isPast ? AppColors.success : Colors.white,
        border: Border.all(
          color: isPast ? AppColors.success : AppColors.mutedText.withValues(alpha: 0.5),
          width: 3,
        ),
      ),
    );
  }
}
