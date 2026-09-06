import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_container.dart';

class EmptyLearningHero extends StatelessWidget {
  final VoidCallback onAddMaterial;

  const EmptyLearningHero({
    super.key,
    required this.onAddMaterial,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
      child: NexoraContainer(
        backgroundColor: AppColors.nexoraYellow,
        padding: const EdgeInsets.all(24.0),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            // Decorative background elements inside the hero
            Positioned(
              right: -10,
              top: -10,
              child: CustomPaint(
                size: const Size(40, 40),
                painter: HeroDotsPainter(),
              ),
            ),
            Positioned(
              right: 80,
              bottom: 40,
              child: CustomPaint(
                size: const Size(20, 30),
                painter: HeroLinesPainter(),
              ),
            ),
            
            // Abstract Document Illustration
            Positioned(
              right: -10,
              top: 20,
              child: Transform.rotate(
                angle: 0.2,
                child: Stack(
                  children: [
                    // Purple background paper
                    Transform.translate(
                      offset: const Offset(-15, 10),
                      child: Transform.rotate(
                        angle: -0.1,
                        child: Container(
                          width: 80,
                          height: 100,
                          decoration: BoxDecoration(
                            color: AppColors.nexoraLavender,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppColors.nexoraInk, width: 2),
                          ),
                        ),
                      ),
                    ),
                    // White foreground paper
                    Container(
                      width: 80,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.nexoraInk, width: 2.5),
                      ),
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(height: 3, width: 50, color: AppColors.nexoraInk),
                          Container(height: 3, width: 40, color: AppColors.nexoraInk),
                          Container(height: 3, width: 45, color: AppColors.nexoraInk),
                          Container(height: 3, width: 30, color: AppColors.nexoraInk),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Main Content
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Transform.rotate(
                      angle: 0.785398, // 45 degrees
                      child: Container(
                        width: 8,
                        height: 8,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'YOUR LEARNING SPACE',
                      style: TextStyle(
                        fontFamily: 'BricolageGrotesque',
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.5,
                        color: AppColors.nexoraInk.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  'Start your\njourney here.',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 32,
                    fontWeight: FontWeight.w900,
                    color: AppColors.nexoraInk,
                    height: 1.0,
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: MediaQuery.of(context).size.width * 0.5,
                  child: const Text(
                    'Upload your first study material and let NEXORA turn it into an interactive learning experience.',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.nexoraInk,
                      height: 1.4,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Primary CTA (Black Pill)
                GestureDetector(
                  onTap: onAddMaterial,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    decoration: BoxDecoration(
                      color: AppColors.nexoraInk,
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        NexoraIcon(NexoraIcons.add, color: Colors.white, size: 20),
                        const SizedBox(width: 8),
                        const Text(
                          'Add Material',
                          style: TextStyle(
                            fontFamily: 'BricolageGrotesque',
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(width: 4),
                        NexoraIcon(NexoraIcons.forward, color: Colors.white, size: 20),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            
            // Decorative handwritten text
            Positioned(
              right: 0,
              bottom: 0,
              child: Transform.rotate(
                angle: -0.1,
                child: Text(
                  'Upload\nLearn\nGrow\nRepeat',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'DMSans', // Use DMSans with italic for handwriting feel
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w800,
                    color: AppColors.nexoraInk.withOpacity(0.8),
                    height: 1.1,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class HeroDotsPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.nexoraInk.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 4; i++) {
      for (int j = 0; j < 4; j++) {
        canvas.drawCircle(Offset(i * 10.0, j * 10.0), 1.5, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class HeroLinesPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.nexoraInk
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(const Offset(0, 0), const Offset(15, 10), paint);
    canvas.drawLine(const Offset(5, 15), const Offset(20, 25), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
