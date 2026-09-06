import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class LibraryHeader extends StatelessWidget {
  const LibraryHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              const Text(
                'Your Library',
                style: TextStyle(
                  fontFamily: 'BricolageGrotesque',
                  fontSize: 32,
                  fontWeight: FontWeight.w900,
                  color: AppColors.nexoraInk,
                  letterSpacing: -0.5,
                  height: 1.1,
                ),
              ),
              Positioned(
                bottom: 2,
                left: 0,
                width: 140,
                child: Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: AppColors.nexoraYellow,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
              // Decorative marks
              Positioned(
                top: -8,
                right: -24,
                child: Transform.rotate(
                  angle: 0.2,
                  child: const Text(
                    '//',
                    style: TextStyle(
                      fontFamily: 'BricolageGrotesque',
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: AppColors.nexoraInk,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Everything you\'ve added to NEXORA, in one place.',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.nexoraInk.withValues(alpha: 0.8),
            ),
          ),
        ],
      ),
    );
  }
}
