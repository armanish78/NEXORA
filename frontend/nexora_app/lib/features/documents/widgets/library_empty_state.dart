import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_button.dart';

class LibraryEmptyState extends StatelessWidget {
  final VoidCallback onAddMaterial;

  const LibraryEmptyState({
    super.key,
    required this.onAddMaterial,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Visual Stack of Documents
          SizedBox(
            height: 160,
            width: 160,
            child: Stack(
              alignment: Alignment.center,
              children: [
                Transform.rotate(
                  angle: -0.2,
                  child: Container(
                    width: 100,
                    height: 120,
                    decoration: BoxDecoration(
                      color: AppColors.nexoraYellow,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.nexoraInk, width: 2),
                    ),
                  ),
                ),
                Transform.rotate(
                  angle: 0.1,
                  child: Container(
                    width: 110,
                    height: 130,
                    decoration: BoxDecoration(
                      color: AppColors.nexoraLavender,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.nexoraInk, width: 2),
                    ),
                  ),
                ),
                Transform.rotate(
                  angle: -0.05,
                  child: Container(
                    width: 120,
                    height: 140,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.nexoraInk, width: 2),
                      boxShadow: const [
                        BoxShadow(
                          color: AppColors.nexoraInk,
                          offset: Offset(4, 4),
                          blurRadius: 0,
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(width: 60, height: 4, color: AppColors.nexoraInk.withValues(alpha: 0.2), margin: const EdgeInsets.only(bottom: 8)),
                        Container(width: 80, height: 4, color: AppColors.nexoraInk.withValues(alpha: 0.2), margin: const EdgeInsets.only(bottom: 8)),
                        Container(width: 50, height: 4, color: AppColors.nexoraInk.withValues(alpha: 0.2)),
                      ],
                    ),
                  ),
                ),
                // Decorative marks
                Positioned(
                  top: 0,
                  left: 0,
                  child: Transform.rotate(
                    angle: -0.5,
                    child: const Text('//', style: TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 16, fontWeight: FontWeight.w900)),
                  ),
                ),
                Positioned(
                  bottom: 20,
                  right: -10,
                  child: Transform.rotate(
                    angle: 0.3,
                    child: const Text('//', style: TextStyle(fontFamily: 'BricolageGrotesque', fontSize: 16, fontWeight: FontWeight.w900)),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          const Text(
            'Your library is empty.',
            style: TextStyle(
              fontFamily: 'BricolageGrotesque',
              fontSize: 24,
              fontWeight: FontWeight.w800,
              color: AppColors.nexoraInk,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Add your first study material and NEXORA\nwill turn it into an interactive learning\nexperience.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.nexoraInk.withValues(alpha: 0.8),
            ),
          ),
          const SizedBox(height: 32),
          NexoraButton(
            text: 'Add Material',
            onPressed: onAddMaterial,
            variant: NexoraButtonVariant.primary,
            icon: NexoraIcons.add,
            width: 200,
          ),
          const SizedBox(height: 16),
          NexoraButton(
            text: 'Take Photo',
            onPressed: onAddMaterial,
            variant: NexoraButtonVariant.outline,
            icon: NexoraIcons.camera,
            width: 200,
          ),
          const SizedBox(height: 40),
          // Lavender info pill
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            decoration: BoxDecoration(
              color: AppColors.nexoraLavender,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.nexoraInk, width: 2),
              boxShadow: const [
                BoxShadow(
                  color: AppColors.nexoraInk,
                  offset: Offset(4, 4),
                  blurRadius: 0,
                ),
              ],
            ),
            child: Row(
              children: [
                NexoraIcon(NexoraIcons.idea, color: AppColors.nexoraInk),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Supports PDFs, notes, images and more. Your materials are stored locally and always accessible.',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.nexoraInk,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                NexoraIcon(NexoraIcons.forward, color: AppColors.nexoraInk, size: 20),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
