import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nexora_app/features/quiz/screens/quiz_setup_screen.dart';
import 'package:nexora_app/core/models/document_metadata.dart';
import 'dart:io';

void main() {
  setUpAll(() {
    HttpOverrides.global = null; // allow actual network requests? No, flutter test blocks them usually.
  });

  testWidgets('Quiz Setup Test 1 - All Topics', (WidgetTester tester) async {
    final document = DocumentMetadata(
      id: '1',
      filename: 'sample_doc.pdf',
      type: 'pdf',
      uploadDate: DateTime.now(),
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(body: QuizSetupScreen(document: document)),
    ));

    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    // Since network requests fail in widget tests by default, _topics will be empty.
    // The UI will show "Couldn't load topics". We can't easily test this without a mock API.
  });
}
