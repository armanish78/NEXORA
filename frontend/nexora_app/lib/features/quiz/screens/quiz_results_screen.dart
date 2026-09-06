import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/models/document_metadata.dart';
import '../../../core/theme/app_colors.dart';
import '../widgets/quiz_decorations.dart';
import 'quiz_setup_screen.dart';

class QuizResultsScreen extends StatelessWidget {
  final int score;
  final int total;
  final DocumentMetadata document;

  const QuizResultsScreen({
    super.key,
    required this.score,
    required this.total,
    required this.document,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (score / total) * 100;
    
    String message;
    
    if (percentage == 100) {
      message = "Perfect Score!\nYou mastered this topic.";
    } else if (percentage >= 80) {
      message = "Solid work.\nKeep building.";
    } else if (percentage >= 60) {
      message = "Good effort.\nYou're getting there.";
    } else {
      message = "Keep practicing.\nEvery question makes you stronger.";
    }

    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      body: QuizDecorations(
        child: SafeArea(
          child: Column(
            children: [
              _buildAppBar(context),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
                  child: Column(
                    children: [
                      const Text(
                        'QUIZ\nCOMPLETE!',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 48,
                          fontWeight: FontWeight.w900,
                          height: 1.0,
                          color: AppColors.nexoraInk,
                        ),
                      ),
                      const SizedBox(height: 32),
                      
                      // Trophy Composition
                      SizedBox(
                        height: 160,
                        width: double.infinity,
                        child: CustomPaint(
                          painter: _TrophyPainter(),
                        ),
                      ),
                      
                      // Score Card
                      Transform.translate(
                        offset: const Offset(0, -20),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 24),
                          decoration: BoxDecoration(
                            color: AppColors.nexoraYellow,
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(color: AppColors.nexoraInk, width: 3),
                            boxShadow: const [
                              BoxShadow(
                                color: AppColors.nexoraInk,
                                offset: Offset(6, 6),
                              )
                            ],
                          ),
                          child: Column(
                            children: [
                              Text(
                                '$score / $total',
                                style: const TextStyle(
                                  fontFamily: 'BricolageGrotesque',
                                  fontSize: 48,
                                  fontWeight: FontWeight.w900,
                                  color: AppColors.nexoraInk,
                                  height: 1.0,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                '${percentage.toStringAsFixed(0)}%',
                                style: const TextStyle(
                                  fontFamily: 'DMSans',
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.nexoraInk,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      Text(
                        message,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontFamily: 'BricolageGrotesque',
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: AppColors.nexoraInk,
                          height: 1.2,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        "You're really getting the hang of it.\nEvery question makes you stronger.",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 12,
                          color: AppColors.nexoraInk.withValues(alpha: 0.8),
                        ),
                      ),
                      
                      const SizedBox(height: 48),
                      
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (context) => QuizSetupScreen(document: document),
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.nexoraYellow,
                            foregroundColor: AppColors.nexoraInk,
                            elevation: 0,
                            padding: const EdgeInsets.symmetric(vertical: 18),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                              side: const BorderSide(color: AppColors.nexoraInk, width: 3),
                            ),
                          ),
                          child: Container(
                            decoration: const BoxDecoration(
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.nexoraInk,
                                  offset: Offset(4, 4),
                                )
                              ],
                            ),
                            child: const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                NexoraIcon(NexoraIcons.retry),
                                SizedBox(width: 12),
                                Text(
                                  'Retake Quiz',
                                  style: TextStyle(
                                    fontFamily: 'BricolageGrotesque',
                                    fontSize: 18,
                                    fontWeight: FontWeight.w900,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: AppColors.nexoraInk,
                            backgroundColor: Colors.white,
                            side: const BorderSide(color: AppColors.nexoraInk, width: 2),
                            padding: const EdgeInsets.symmetric(vertical: 18),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              NexoraIcon(NexoraIcons.quiz),
                              SizedBox(width: 12),
                              Text(
                                'Back to Quiz Hub',
                                style: TextStyle(
                                  fontFamily: 'BricolageGrotesque',
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 40),
                      Align(
                        alignment: Alignment.bottomRight,
                        child: Transform.rotate(
                          angle: -0.1,
                          child: const Text(
                            'Small\nSteps\nBig Progress',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: 'DMSans', // Using manrope as a fallback for handwritten
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: AppColors.nexoraInk,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: NexoraIcon(NexoraIcons.back, color: AppColors.nexoraInk),
            onPressed: () => Navigator.pop(context),
          ),
          const Expanded(child: Center(child: NexoraLogoHeader())),
          const SizedBox(width: 48), // Balance for back button
        ],
      ),
    );
  }
}

class _TrophyPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final borderPaint = Paint()
      ..color = AppColors.nexoraInk
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeJoin = StrokeJoin.round;

    final fillYellow = Paint()
      ..color = AppColors.nexoraYellow
      ..style = PaintingStyle.fill;
      
    final fillMint = Paint()
      ..color = AppColors.nexoraGreen
      ..style = PaintingStyle.fill;
      
    final center = Offset(size.width / 2, size.height / 2 - 10);

    // Decorative dots grid (left)
    final dotPaint = Paint()..color = AppColors.nexoraInk;
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 4; j++) {
        canvas.drawCircle(Offset(size.width * 0.15 + i * 8, size.height * 0.4 + j * 8), 1.5, dotPaint);
      }
    }

    // Sparkles
    _drawSparkle(canvas, Offset(size.width * 0.75, size.height * 0.3), fillMint, borderPaint);
    _drawSparkle(canvas, Offset(size.width * 0.25, size.height * 0.7), fillYellow, borderPaint);
    _drawSparkle(canvas, Offset(size.width * 0.85, size.height * 0.6), fillMint, borderPaint);

    // Trophy Base
    final baseRect = RRect.fromRectAndRadius(
      Rect.fromCenter(center: Offset(center.dx, center.dy + 60), width: 60, height: 16),
      const Radius.circular(8),
    );
    canvas.drawRRect(baseRect, Paint()..color = AppColors.nexoraGreen);
    canvas.drawRRect(baseRect, borderPaint);
    
    // Trophy Stem
    final stemRect = Rect.fromCenter(center: Offset(center.dx, center.dy + 40), width: 16, height: 24);
    canvas.drawRect(stemRect, fillYellow);
    canvas.drawRect(stemRect, borderPaint);

    // Trophy Handles
    final leftHandle = Path()
      ..moveTo(center.dx - 30, center.dy)
      ..quadraticBezierTo(center.dx - 55, center.dy - 10, center.dx - 45, center.dy - 35)
      ..quadraticBezierTo(center.dx - 30, center.dy - 40, center.dx - 25, center.dy - 20);
    canvas.drawPath(leftHandle, fillYellow);
    canvas.drawPath(leftHandle, borderPaint);
    
    final rightHandle = Path()
      ..moveTo(center.dx + 30, center.dy)
      ..quadraticBezierTo(center.dx + 55, center.dy - 10, center.dx + 45, center.dy - 35)
      ..quadraticBezierTo(center.dx + 30, center.dy - 40, center.dx + 25, center.dy - 20);
    canvas.drawPath(rightHandle, fillYellow);
    canvas.drawPath(rightHandle, borderPaint);

    // Trophy Cup
    final cupPath = Path()
      ..moveTo(center.dx - 40, center.dy - 40)
      ..lineTo(center.dx + 40, center.dy - 40)
      ..quadraticBezierTo(center.dx + 40, center.dy + 20, center.dx, center.dy + 30)
      ..quadraticBezierTo(center.dx - 40, center.dy + 20, center.dx - 40, center.dy - 40)
      ..close();
    canvas.drawPath(cupPath, fillYellow);
    canvas.drawPath(cupPath, borderPaint);
    
    // Cup Lip
    final lipRect = RRect.fromRectAndRadius(
      Rect.fromCenter(center: Offset(center.dx, center.dy - 40), width: 90, height: 12),
      const Radius.circular(6),
    );
    canvas.drawRRect(lipRect, fillYellow);
    canvas.drawRRect(lipRect, borderPaint);

    // Star inside cup
    _drawStar(canvas, Offset(center.dx, center.dy - 10), 12, fillMint, borderPaint);
  }

  void _drawSparkle(Canvas canvas, Offset center, Paint fill, Paint border) {
    final path = Path()
      ..moveTo(center.dx, center.dy - 8)
      ..quadraticBezierTo(center.dx, center.dy, center.dx + 8, center.dy)
      ..quadraticBezierTo(center.dx, center.dy, center.dx, center.dy + 8)
      ..quadraticBezierTo(center.dx, center.dy, center.dx - 8, center.dy)
      ..quadraticBezierTo(center.dx, center.dy, center.dx, center.dy - 8)
      ..close();
    canvas.drawPath(path, fill);
    canvas.drawPath(path, border);
  }

  void _drawStar(Canvas canvas, Offset center, double size, Paint fill, Paint border) {
    // simplified 5 point star
    final path = Path();
    path.moveTo(center.dx, center.dy - size);
    path.lineTo(center.dx + size * 0.3, center.dy - size * 0.3);
    path.lineTo(center.dx + size, center.dy - size * 0.2);
    path.lineTo(center.dx + size * 0.4, center.dy + size * 0.2);
    path.lineTo(center.dx + size * 0.6, center.dy + size);
    path.lineTo(center.dx, center.dy + size * 0.5);
    path.lineTo(center.dx - size * 0.6, center.dy + size);
    path.lineTo(center.dx - size * 0.4, center.dy + size * 0.2);
    path.lineTo(center.dx - size, center.dy - size * 0.2);
    path.lineTo(center.dx - size * 0.3, center.dy - size * 0.3);
    path.close();
    
    canvas.drawPath(path, fill);
    canvas.drawPath(path, border);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
