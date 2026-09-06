import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

enum NexoraBackgroundVariant {
  homeEmpty,
  homeActive,
  library,
  tutor,
  progress,
  profile,
  quiz,
}

class NexoraBackground extends StatelessWidget {
  final Widget child;
  final NexoraBackgroundVariant variant;

  const NexoraBackground({
    super.key,
    required this.child,
    this.variant = NexoraBackgroundVariant.homeEmpty,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.nexoraCream,
      child: Stack(
        children: [
          // Background decorations for Home
          if (variant == NexoraBackgroundVariant.homeEmpty || variant == NexoraBackgroundVariant.homeActive) ...[
            // Top Left Coral Rectangle
            Positioned(
              left: -40,
              top: 100,
              child: Transform.rotate(
                angle: -0.2,
                child: Container(
                  width: 80,
                  height: 120,
                  decoration: BoxDecoration(
                    color: AppColors.nexoraCoral,
                    border: Border.all(color: AppColors.nexoraInk, width: 2),
                  ),
                ),
              ),
            ),
            // Top Right Yellow Circle
            Positioned(
              right: -60,
              top: -40,
              child: Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  color: AppColors.nexoraYellow,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
              ),
            ),
            // Bottom Right Cyan Triangle
            Positioned(
              right: -40,
              bottom: 40,
              child: CustomPaint(
                size: const Size(120, 120),
                painter: TrianglePainter(color: AppColors.nexoraCyan),
              ),
            ),
            // Bottom Left Coral Circle with Text
            Positioned(
              left: -40,
              bottom: 80,
              child: Container(
                width: 140,
                height: 140,
                decoration: BoxDecoration(
                  color: AppColors.nexoraCoral,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                alignment: Alignment.centerRight,
                padding: const EdgeInsets.only(right: 20, top: 20),
                child: Transform.rotate(
                  angle: -0.2,
                  child: const Text(
                    'Same\nCuriosity\nBrighter\nTomorrows',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontStyle: FontStyle.italic,
                      fontWeight: FontWeight.w800,
                      fontSize: 10,
                      height: 1.1,
                      color: AppColors.nexoraInk,
                    ),
                  ),
                ),
              ),
            ),
            // Dot Grids
            Positioned(
              left: 30,
              top: 120,
              child: CustomPaint(
                size: const Size(20, 40),
                painter: DotGridPainter(rows: 4, columns: 2),
              ),
            ),
            Positioned(
              right: 20,
              top: 360,
              child: CustomPaint(
                size: const Size(20, 100),
                painter: DotGridPainter(rows: 10, columns: 2),
              ),
            ),
            Positioned(
              left: 20,
              bottom: 240,
              child: CustomPaint(
                size: const Size(20, 60),
                painter: DotGridPainter(rows: 6, columns: 2),
              ),
            ),
            Positioned(
              right: 40,
              bottom: 20,
              child: CustomPaint(
                size: const Size(60, 40),
                painter: DotGridPainter(rows: 4, columns: 6),
              ),
            ),
            // Floating Plus Signs
            Positioned(
              left: 20,
              bottom: 20,
              child: CustomPaint(
                size: const Size(30, 30),
                painter: CrossPainter(color: Colors.transparent, strokeWidth: 2),
              ),
            ),
          ],
          
          // Background decorations for Library and Quiz
          if (variant == NexoraBackgroundVariant.library || variant == NexoraBackgroundVariant.quiz) ...[
            // Top Right Mint Document Shape
            Positioned(
              right: -30,
              top: -20,
              child: Transform.rotate(
                angle: 0.15,
                child: Container(
                  width: 140,
                  height: 180,
                  decoration: BoxDecoration(
                    color: AppColors.nexoraGreen,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.nexoraInk, width: 2),
                  ),
                ),
              ),
            ),
            // Middle Left Lavender Circle
            Positioned(
              left: -50,
              top: 300,
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: AppColors.nexoraLavender,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
              ),
            ),
            // Bottom Right Cyan Dot Grid
            Positioned(
              right: 24,
              bottom: 140,
              child: CustomPaint(
                size: const Size(60, 60),
                painter: DotGridPainter(rows: 6, columns: 6),
              ),
            ),
            // Floating Cross
            Positioned(
              left: 40,
              top: 140,
              child: CustomPaint(
                size: const Size(20, 20),
                painter: CrossPainter(color: Colors.transparent, strokeWidth: 2),
              ),
            ),
            // Bottom Left Yellow Corner
            Positioned(
              left: -20,
              bottom: -20,
              child: Transform.rotate(
                angle: -0.1,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: AppColors.nexoraYellow,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppColors.nexoraInk, width: 2),
                  ),
                ),
              ),
            ),
          ],
          
          // Foreground content
          Positioned.fill(
            child: child, // SafeArea should be handled by the screen if needed
          ),
        ],
      ),
    );
  }
}

class TrianglePainter extends CustomPainter {
  final Color color;

  TrianglePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;
      
    final path = Path()
      ..moveTo(size.width, 0)
      ..lineTo(0, size.height)
      ..lineTo(size.width, size.height)
      ..close();
      
    canvas.drawPath(path, paint);
    
    final borderPaint = Paint()
      ..color = AppColors.nexoraInk
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
      
    canvas.drawPath(path, borderPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class CrossPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;

  CrossPainter({required this.color, this.strokeWidth = 2});

  @override
  void paint(Canvas canvas, Size size) {
    if (color != Colors.transparent) {
      final fillPaint = Paint()
        ..color = color
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.square;
      canvas.drawLine(Offset(size.width / 2, 0), Offset(size.width / 2, size.height), fillPaint);
      canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), fillPaint);
    }
    
    final outlinePaint = Paint()
      ..color = AppColors.nexoraInk
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;
    
    canvas.drawLine(Offset(size.width / 2, 0), Offset(size.width / 2, size.height), outlinePaint);
    canvas.drawLine(Offset(0, size.height / 2), Offset(size.width, size.height / 2), outlinePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class DotGridPainter extends CustomPainter {
  final int rows;
  final int columns;

  DotGridPainter({this.rows = 5, this.columns = 3});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.nexoraInk.withOpacity(0.5)
      ..style = PaintingStyle.fill;

    final double dx = size.width / (columns > 1 ? columns - 1 : 1);
    final double dy = size.height / (rows > 1 ? rows - 1 : 1);

    for (int i = 0; i < columns; i++) {
      for (int j = 0; j < rows; j++) {
        canvas.drawCircle(Offset(i * dx, j * dy), 1.5, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class DashedRectPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;
  final double radius;

  DashedRectPainter({
    required this.color,
    required this.strokeWidth,
    required this.radius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final Paint paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke;

    final RRect rrect = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, size.width, size.height),
      Radius.circular(radius),
    );

    Path path = Path()..addRRect(rrect);
    
    // Create a dashed path
    const double dashWidth = 10;
    const double dashSpace = 6;
    Path dashedPath = Path();
    for (var measurePath in path.computeMetrics()) {
      double distance = 0.0;
      while (distance < measurePath.length) {
        dashedPath.addPath(
          measurePath.extractPath(distance, distance + dashWidth),
          Offset.zero,
        );
        distance += dashWidth + dashSpace;
      }
    }

    canvas.drawPath(dashedPath, paint);
  }

  @override
  bool shouldRepaint(covariant DashedRectPainter oldDelegate) {
    return oldDelegate.color != color ||
        oldDelegate.strokeWidth != strokeWidth ||
        oldDelegate.radius != radius;
  }
}
