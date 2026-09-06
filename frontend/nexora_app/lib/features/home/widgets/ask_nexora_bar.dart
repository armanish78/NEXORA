import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/nexora_container.dart';

class AskNexoraBar extends StatelessWidget {
  final VoidCallback onTap;

  const AskNexoraBar({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: NexoraContainer(
        margin: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        borderRadius: BorderRadius.circular(100),
        backgroundColor: Colors.white,
        borderWidth: 2.5,
        child: Row(
          children: [
            NexoraIcon(NexoraIcons.search, color: AppColors.nexoraInk, size: 28),
            const SizedBox(width: 12),
            Text(
              'Ask NEXORA anything...',
              style: TextStyle(
                fontFamily: 'DMSans',
                color: AppColors.nexoraMutedInk,
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
            const Spacer(),
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.nexoraLavender,
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
              child: NexoraIcon(NexoraIcons.sparkle, color: AppColors.nexoraInk, size: 20),
            ),
          ],
        ),
      ),
    );
  }
}
