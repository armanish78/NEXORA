import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      fontFamily: 'DMSans',
      scaffoldBackgroundColor: AppColors.nexoraCream,
      colorScheme: const ColorScheme.light(
        primary: AppColors.nexoraYellow,
        secondary: AppColors.nexoraCyan,
        surface: Colors.white,
        error: AppColors.nexoraCoral,
        onPrimary: AppColors.nexoraInk,
        onSecondary: AppColors.nexoraInk,
        onSurface: AppColors.nexoraInk,
        onError: Colors.white,
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 36,
          fontWeight: FontWeight.w900,
          color: AppColors.nexoraInk,
        ),
        displayMedium: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 28,
          fontWeight: FontWeight.w800,
          color: AppColors.nexoraInk,
        ),
        displaySmall: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 22,
          fontWeight: FontWeight.w800,
          color: AppColors.nexoraInk,
        ),
        headlineLarge: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 20,
          fontWeight: FontWeight.w800,
          color: AppColors.nexoraInk,
        ),
        headlineMedium: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
        headlineSmall: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 16,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
        titleLarge: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
        titleMedium: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: AppColors.nexoraInk,
        ),
        titleSmall: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppColors.nexoraInk,
        ),
        bodyLarge: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: AppColors.nexoraInk,
        ),
        bodyMedium: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: AppColors.nexoraInk,
        ),
        bodySmall: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: AppColors.nexoraInk,
        ),
        labelLarge: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
        labelMedium: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
        labelSmall: TextStyle(
          fontFamily: 'DMSans',
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: AppColors.nexoraInk,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.nexoraCream,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: AppColors.nexoraInk),
        titleTextStyle: TextStyle(
          fontFamily: 'BricolageGrotesque',
          fontSize: 22,
          fontWeight: FontWeight.w900,
          color: AppColors.nexoraInk,
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: AppColors.nexoraYellow,
        unselectedItemColor: AppColors.nexoraMutedInk,
        elevation: 8,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }
}
