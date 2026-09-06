import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

enum NexoraButtonVariant { primary, secondary, outline }

class NexoraButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final NexoraButtonVariant variant;
  final bool isLoading;
  final NexoraIcons? icon;
  final double width;

  const NexoraButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.variant = NexoraButtonVariant.primary,
    this.isLoading = false,
    this.icon,
    this.width = double.infinity,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: 52,
      child: ElevatedButton(
        onPressed: isLoading ? () {} : onPressed,
        style: _getButtonStyle(),
        child: isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    NexoraIcon(icon!, size: 22, color: _getTextColor()),
                    const SizedBox(width: 8),
                  ],
                  Flexible(
                    child: Text(
                      text,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                        color: _getTextColor(),
                      ),
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  ButtonStyle _getButtonStyle() {
    Color backgroundColor;

    switch (variant) {
      case NexoraButtonVariant.primary:
        backgroundColor = AppColors.primary;
        break;
      case NexoraButtonVariant.secondary:
        backgroundColor = AppColors.attention;
        break;
      case NexoraButtonVariant.outline:
        backgroundColor = Colors.white;
        break;
    }

    return ElevatedButton.styleFrom(
      backgroundColor: backgroundColor,
      foregroundColor: _getTextColor(),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Colors.black, width: 2.5),
      ),
    ).copyWith(
      shadowColor: const WidgetStatePropertyAll(Colors.black),
      elevation: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.pressed)) return 0;
        return 4;
      }),
    );
  }

  Color _getTextColor() {
    switch (variant) {
      case NexoraButtonVariant.primary:
        return Colors.white;
      case NexoraButtonVariant.secondary:
      case NexoraButtonVariant.outline:
        return Colors.black;
    }
  }
}

