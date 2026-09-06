import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class HomeHeader extends StatelessWidget {
  const HomeHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              // Logo 'N' Custom
              Stack(
                alignment: Alignment.center,
                children: [
                  // Shadow
                  Transform.translate(
                    offset: const Offset(4, 4),
                    child: const Text(
                      'N',
                      style: TextStyle(
                        fontFamily: 'BricolageGrotesque',
                        fontSize: 48,
                        fontWeight: FontWeight.w900,
                        height: 1,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                  ),
                  // Stroke
                  Text(
                    'N',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 48,
                      fontWeight: FontWeight.w900,
                      height: 1,
                      foreground: Paint()
                        ..style = PaintingStyle.stroke
                        ..strokeWidth = 6
                        ..strokeJoin = StrokeJoin.round
                        ..color = AppColors.nexoraInk,
                    ),
                  ),
                  // Fill
                  const Text(
                    'N',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 48,
                      fontWeight: FontWeight.w900,
                      height: 1,
                      color: AppColors.nexoraCyan,
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'NEXORA',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.2,
                      color: AppColors.nexoraInk,
                      height: 1.1,
                    ),
                  ),
                  Text(
                    'LEARN ANYTHING\nGO FURTHER',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 7,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 2.5,
                      color: AppColors.nexoraInk.withOpacity(0.8),
                      height: 1.2,
                    ),
                  ),
                ],
              ),
            ],
          ),
          // Top right decorative element
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.nexoraYellow,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.nexoraInk, width: 2.5),
              boxShadow: const [
                BoxShadow(
                  color: AppColors.nexoraInk,
                  offset: Offset(2, 2),
                ),
              ],
            ),
            child: const Center(
              child: NexoraIcon(NexoraIcons.sparkle, color: AppColors.nexoraInk, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}
