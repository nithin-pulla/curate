import 'package:flutter/material.dart';
import 'models.dart';
import 'restaurant_menu_screen.dart';
import 'screens/onboarding_screen.dart';

void main() {
  runApp(CurateApp());
}

class CurateApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Curate',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: OnboardingScreen(),
    );
  }
}
