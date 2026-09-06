import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';

enum ThreadNodeType { genesis, past, current, future }

class ThreadSegment extends StatelessWidget {
  final Widget child;
  final ThreadNodeType type;
  final bool isFirst;
  final bool isLast;

  const ThreadSegment({
    super.key,
    required this.child,
    required this.type,
    this.isFirst = false,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _ThreadSegmentPainter(
        type: type,
        isFirst: isFirst,
        isLast: isLast,
      ),
      child: child,
    );
  }
}

class _ThreadSegmentPainter extends CustomPainter {
  final ThreadNodeType type;
  final bool isFirst;
  final bool isLast;

  _ThreadSegmentPainter({
    required this.type,
    required this.isFirst,
    required this.isLast,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..strokeWidth = 4.0
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    switch (type) {
      case ThreadNodeType.past:
        paint.color = AppColors.success;
        break;
      case ThreadNodeType.current:
      case ThreadNodeType.genesis:
        paint.color = AppColors.primary;
        break;
      case ThreadNodeType.future:
        paint.color = AppColors.mutedText.withValues(alpha: 0.3);
        break;
    }

    final startY = isFirst ? size.height / 2 : 0.0;
    final endY = isLast ? size.height / 2 : size.height;
    
    // Draw the thread line exactly down the middle
    canvas.drawLine(
      Offset(size.width / 2, startY),
      Offset(size.width / 2, endY),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _ThreadSegmentPainter oldDelegate) {
    return oldDelegate.type != type ||
           oldDelegate.isFirst != isFirst ||
           oldDelegate.isLast != isLast;
  }
}
