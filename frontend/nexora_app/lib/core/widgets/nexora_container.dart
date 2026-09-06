import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class NexoraContainer extends StatelessWidget {
  final Widget child;
  final Color backgroundColor;
  final double borderWidth;
  final BorderRadiusGeometry? borderRadius;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double? width;
  final double? height;
  final bool shadow;
  final Color? outlineColor;

  const NexoraContainer({
    super.key,
    required this.child,
    this.backgroundColor = Colors.white,
    this.borderWidth = 2.5,
    this.borderRadius,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.shadow = true,
    this.outlineColor,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveBorderRadius = borderRadius ?? BorderRadius.circular(16);
    
    return Container(
      width: width,
      height: height,
      margin: margin,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: effectiveBorderRadius,
        border: Border.all(
          color: outlineColor ?? AppColors.nexoraInk,
          width: borderWidth,
        ),
        boxShadow: shadow
            ? [
                BoxShadow(
                  color: AppColors.nexoraInk.withOpacity(1.0),
                  offset: const Offset(4, 4),
                  blurRadius: 0, // Flat shadow
                  spreadRadius: 0,
                )
              ]
            : null,
      ),
      child: Padding(
        padding: padding ?? EdgeInsets.zero,
        child: child,
      ),
    );
  }
}
