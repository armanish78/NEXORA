import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class LibrarySearchBar extends StatelessWidget {
  final String query;
  final ValueChanged<String> onChanged;
  final VoidCallback onClear;

  const LibrarySearchBar({
    super.key,
    required this.query,
    required this.onChanged,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
      child: Container(
        height: 56,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: AppColors.nexoraInk, width: 2),
          boxShadow: const [
            BoxShadow(
              color: AppColors.nexoraInk,
              offset: Offset(0, 4),
              blurRadius: 0,
            ),
          ],
        ),
        child: TextField(
          controller: TextEditingController(text: query)..selection = TextSelection.fromPosition(TextPosition(offset: query.length)),
          onChanged: onChanged,
          style: const TextStyle(
            fontFamily: 'DMSans',
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: AppColors.nexoraInk,
          ),
          decoration: InputDecoration(
            hintText: 'Search your materials...',
            hintStyle: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: AppColors.nexoraInk.withValues(alpha: 0.5),
            ),
            prefixIcon: const Padding(
              padding: EdgeInsets.only(left: 16.0, right: 12.0),
              child: NexoraIcon(NexoraIcons.search, color: AppColors.nexoraInk, size: 24),
            ),
            prefixIconConstraints: const BoxConstraints(minWidth: 50),
            suffixIcon: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (query.isNotEmpty)
                  IconButton(
                    icon: NexoraIcon(NexoraIcons.close, color: AppColors.nexoraInk),
                    onPressed: onClear,
                  ),
                const Padding(
                  padding: EdgeInsets.only(right: 16.0, left: 8.0),
                  child: NexoraIcon(NexoraIcons.settings, color: AppColors.nexoraInk, size: 24),
                ),
              ],
            ),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(vertical: 16),
          ),
        ),
      ),
    );
  }
}
