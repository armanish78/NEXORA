import re

with open('lib/features/quiz/screens/quiz_setup_screen.dart', 'r') as f:
    content = f.read()

# 1. Wrap top-right illustration in IgnorePointer and fix position
content = content.replace('''        Positioned(
          right: -10,
          top: -10,
          child: _buildTopRightIllustration(),
        ),''', '''        Positioned(
          right: 0,
          top: 0,
          child: IgnorePointer(child: _buildTopRightIllustration()),
        ),''')

# 2. Add GestureDetector to Change button
change_target = """          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.nexoraInk, width: 2),
            ),
            child: const Text(
              'Change',"""

change_replacement = """          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.nexoraInk, width: 2),
              ),
              child: const Text(
                'Change',"""
content = content.replace(change_target, change_replacement)
# don't forget to close the GestureDetector parenthesis. 
# Wait, let's just do it cleanly with python regex

