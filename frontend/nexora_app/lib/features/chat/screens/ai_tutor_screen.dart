import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class AiTutorScreen extends StatelessWidget {
  const AiTutorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Tutor')),
      body: const Center(
        child: Text(
          'AI Tutor Coming Soon',
          style: TextStyle(color: AppColors.mutedText),
        ),
      ),
    );
  }
}
