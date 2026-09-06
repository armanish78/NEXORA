import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class LibraryFilterRow extends StatelessWidget {
  final List<String> filters;
  final String activeFilter;
  final ValueChanged<String> onFilterChanged;

  const LibraryFilterRow({
    super.key,
    required this.filters,
    required this.activeFilter,
    required this.onFilterChanged,
  });

  NexoraIcons _getIconForFilter(String filter) {
    switch (filter) {
      case 'PDFs':
        return NexoraIcons.pdf;
      case 'Notes':
        return NexoraIcons.document;
      case 'Images':
        return NexoraIcons.image;
      case 'All':
      default:
        return NexoraIcons.document;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
      child: Row(
        children: filters.map((filter) {
          final isActive = filter == activeFilter;
          return Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: GestureDetector(
              onTap: () => onFilterChanged(filter),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                decoration: BoxDecoration(
                  color: isActive ? AppColors.nexoraYellow : Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppColors.nexoraInk, width: 2),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    NexoraIcon(
                      _getIconForFilter(filter),
                      size: 16,
                      color: AppColors.nexoraInk,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      filter,
                      style: const TextStyle(
                        fontFamily: 'BricolageGrotesque',
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: AppColors.nexoraInk,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
