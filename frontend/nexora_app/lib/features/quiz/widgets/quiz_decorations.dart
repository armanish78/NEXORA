import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class QuizDecorations extends StatelessWidget {
  final Widget child;

  const QuizDecorations({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: CustomPaint(
            painter: _QuizDecorationPainter(),
          ),
        ),
        child,
      ],
    );
  }
}

class _QuizDecorationPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // The previous generic background shapes have been removed.
    // We now use bespoke decoration widgets for precise layout control.
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class BottomQuizDecoration extends StatelessWidget {
  const BottomQuizDecoration({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 140,
      width: double.infinity,
      child: Stack(
        children: [
          // Left Coral Shape
          Positioned(
            left: -40,
            bottom: -20,
            child: Container(
              width: 180,
              height: 180,
              decoration: BoxDecoration(
                color: AppColors.nexoraCoral,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.nexoraInk, width: 2.5),
              ),
              child: Stack(
                children: [
                  Positioned(
                    top: 40,
                    left: 60,
                    child: Transform.rotate(
                      angle: -0.15,
                      child: const Text(
                        'Same\nCuriosity\nBrighter\nResults',
                        style: TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          color: AppColors.nexoraInk,
                          height: 1.1,
                        ),
                      ),
                    ),
                  ),
                  // Motion lines
                  Positioned(
                    top: 20,
                    right: 40,
                    child: Transform.rotate(
                      angle: 0.5,
                      child: Container(
                        width: 20,
                        height: 3,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                  ),
                  Positioned(
                    top: 35,
                    right: 25,
                    child: Transform.rotate(
                      angle: 0.7,
                      child: Container(
                        width: 15,
                        height: 3,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Right Mint Shape
          Positioned(
            right: -20,
            bottom: -20,
            child: CustomPaint(
              size: const Size(120, 120),
              painter: _MintShapePainter(),
            ),
          ),
          
          // Dotted Pattern
          Positioned(
            right: 40,
            top: 20,
            child: CustomPaint(
              size: const Size(40, 40),
              painter: _DotsPainter(),
            ),
          ),
        ],
      ),
    );
  }
}

class _MintShapePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.nexoraInk
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeJoin = StrokeJoin.round;
      
    final fillMint = Paint()
      ..color = AppColors.nexoraCyan
      ..style = PaintingStyle.fill;
      
    final path = Path()
      ..moveTo(size.width * 0.2, size.height)
      ..lineTo(size.width * 0.2, size.height * 0.4)
      ..lineTo(size.width * 0.8, 0)
      ..lineTo(size.width, size.height * 0.2)
      ..lineTo(size.width, size.height)
      ..close();
      
    canvas.drawPath(path, fillMint);
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _DotsPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = AppColors.nexoraInk;
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
        canvas.drawCircle(Offset(i * 12.0, j * 12.0), 2, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class NexoraLogoHeader extends StatelessWidget {
  const NexoraLogoHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'NEXORA',
              style: TextStyle(
                fontFamily: 'BricolageGrotesque',
                fontSize: 24,
                fontWeight: FontWeight.w900,
                color: AppColors.nexoraInk,
                letterSpacing: 2,
              ),
            ),
            Transform.translate(
              offset: const Offset(4, -8),
              child: Container(
                width: 10,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.nexoraYellow,
                  borderRadius: BorderRadius.circular(2),
                ),
                transform: Matrix4.rotationZ(-0.5),
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          'LEARN • THINK • GO FURTHER',
          style: TextStyle(
            fontFamily: 'BricolageGrotesque',
            fontSize: 8,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
            color: AppColors.nexoraInk.withValues(alpha: 0.6),
          ),
        ),
      ],
    );
  }
}
