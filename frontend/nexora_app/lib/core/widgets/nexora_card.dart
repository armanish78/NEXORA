import 'package:flutter/material.dart';

class NexoraCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final Color backgroundColor;
  final bool withBorder;

  const NexoraCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.onTap,
    this.backgroundColor = Colors.white,
    this.withBorder = true,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: padding,
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(16),
          border: withBorder
              ? Border.all(color: Colors.black, width: 2.5)
              : null,
          boxShadow: [
            if (withBorder)
              const BoxShadow(
                color: Colors.black,
                blurRadius: 0,
                offset: Offset(4, 4),
              ),
          ],
        ),
        child: child,
      ),
    );
  }
}

