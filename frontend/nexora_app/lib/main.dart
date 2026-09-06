import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'features/home/app_shell.dart';

void main() {
  runApp(const NexoraApp());
}

class NexoraApp extends StatelessWidget {
  const NexoraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NEXORA',
      theme: AppTheme.lightTheme,
      scrollBehavior: const _NexoraScrollBehavior(),
      home: const AppShell(),
    );
  }
}

class _NexoraScrollBehavior extends ScrollBehavior {
  const _NexoraScrollBehavior();

  @override
  ScrollPhysics getScrollPhysics(BuildContext context) {
    return const ClampingScrollPhysics(parent: AlwaysScrollableScrollPhysics());
  }

  @override
  Widget buildOverscrollIndicator(BuildContext context, Widget child, ScrollableDetails details) {
    // Return child directly to remove any glowing or stretching overscroll effects
    return child;
  }
}


