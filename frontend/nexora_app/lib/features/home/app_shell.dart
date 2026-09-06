import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import 'screens/home_screen.dart';
import '../documents/screens/library_screen.dart';
import '../quiz/screens/quiz_landing_screen.dart';
import '../progress/screens/progress_screen.dart';
import '../profile/screens/profile_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;

  List<Widget> get _screens => [
    HomeScreen(
      onNavigateToLibrary: () => setState(() => _currentIndex = 1),
    ),
    const LibraryScreen(),
    const QuizLandingScreen(),
    const ProgressScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.nexoraCream,
      extendBody: true, // Content flows behind the transparent nav container
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NexoraBottomNav(
        currentIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
      ),
    );
  }
}

class NexoraBottomNav extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onDestinationSelected;

  const NexoraBottomNav({
    super.key,
    required this.currentIndex,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    final bottomPadding = MediaQuery.viewPaddingOf(context).bottom;
    // Provide a small intentional gap between pill and home indicator
    final bottomSpace = bottomPadding > 0 ? bottomPadding + 8.0 : 20.0;

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        bottom: bottomSpace,
      ),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: const Color(0xFFFFFDF8), // Warm off-white/cream
          borderRadius: BorderRadius.circular(100),
          border: Border.all(color: AppColors.nexoraInk, width: 2.5),
          boxShadow: const [
            BoxShadow(
              color: AppColors.nexoraInk,
              offset: Offset(4, 4),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildNavItem(0, 'Home', NexoraIcons.home),
              _buildNavItem(1, 'Library', NexoraIcons.library),
              _buildNavItem(2, 'Quiz', NexoraIcons.quiz),
              _buildNavItem(3, 'Progress', NexoraIcons.progress),
              _buildNavItem(4, 'Profile', NexoraIcons.profile),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, String label, NexoraIcons iconType) {
    final isSelected = currentIndex == index;

    return Expanded(
      child: GestureDetector(
        onTap: () => onDestinationSelected(index),
        behavior: HitTestBehavior.opaque,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon in a fixed-size container to prevent jumping
            SizedBox(
              height: 40,
              width: 40,
              child: Center(
                child: Container(
                  width: 34,
                  height: 34,
                  decoration: BoxDecoration(
                    color: isSelected ? AppColors.nexoraYellow : Colors.transparent,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: NexoraIcon(
                      iconType,
                      isSelected: isSelected,
                      color: AppColors.nexoraInk,
                      size: 30.0, // 28-32 logical pixels requested
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontFamily: 'DMSans',
                color: AppColors.nexoraInk,
                fontSize: 11, // 11-12px requested
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                height: 1.0,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
            ),
            const SizedBox(height: 4),
            // Small yellow active indicator
            Container(
              width: 4,
              height: 4,
              decoration: BoxDecoration(
                color: isSelected ? AppColors.nexoraYellow : Colors.transparent,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
