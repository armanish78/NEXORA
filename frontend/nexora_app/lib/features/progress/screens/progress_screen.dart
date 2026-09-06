import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Progress')),
      body: const Center(
        child: Text(
          'Progress Coming Soon',
          style: TextStyle(color: AppColors.mutedText),
        ),
      ),
    );
  }
}
