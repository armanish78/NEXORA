import 'package:flutter/material.dart';

enum NexoraIcons {
  home, library, quiz, tutor, progress, profile, back, forward, arrowRight, search, upload, camera,
  document, pdf, image, check, close, retry, settings, add, remove, play, lock, bookmark, send, more,
  sparkle, warning, school, idea, quote, leaf, barChart, challenge, stack
}

class NexoraIcon extends StatelessWidget {
  final NexoraIcons icon;
  final bool isSelected;
  final Color? color;
  final double size;

  const NexoraIcon(
    this.icon, {
    super.key,
    this.isSelected = false,
    this.color,
    this.size = 24.0,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveColor = color ?? const Color(0xFF1C1C1E); // nexoraInk

    return CustomPaint(
      size: Size(size, size),
      painter: _getPainterForIcon(icon, isSelected, effectiveColor),
    );
  }

  CustomPainter _getPainterForIcon(NexoraIcons icon, bool isSelected, Color color) {
    switch (icon) {
      case NexoraIcons.home: return _HomeIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.library: return _LibraryIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.quiz: return _QuizIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.tutor: return _TutorIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.progress: return _ProgressIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.profile: return _ProfileIconPainter(isSelected: isSelected, color: color);
      case NexoraIcons.back: return _ArrowBackPainter(color: color);
      case NexoraIcons.forward: return _ArrowForwardPainter(color: color);
      case NexoraIcons.arrowRight: return _ArrowRightPainter(color: color);
      case NexoraIcons.search: return _SearchPainter(color: color);
      case NexoraIcons.upload: return _UploadPainter(color: color);
      case NexoraIcons.camera: return _CameraPainter(color: color);
      case NexoraIcons.document: return _DocumentPainter(color: color);
      case NexoraIcons.pdf: return _DocumentPainter(color: color, isPdf: true);
      case NexoraIcons.image: return _ImagePainter(color: color);
      case NexoraIcons.check: return _CheckPainter(color: color);
      case NexoraIcons.close: return _ClosePainter(color: color);
      case NexoraIcons.retry: return _RetryPainter(color: color);
      case NexoraIcons.settings: return _SettingsPainter(color: color);
      case NexoraIcons.add: return _AddPainter(color: color);
      case NexoraIcons.remove: return _RemovePainter(color: color);
      case NexoraIcons.play: return _PlayPainter(isSelected: isSelected, color: color);
      case NexoraIcons.lock: return _LockPainter(color: color);
      case NexoraIcons.bookmark: return _BookmarkPainter(isSelected: isSelected, color: color);
      case NexoraIcons.send: return _SendPainter(color: color);
      case NexoraIcons.more: return _MorePainter(color: color);
      case NexoraIcons.sparkle: return _SparklePainter(color: color);
      case NexoraIcons.warning: return _WarningPainter(color: color);
      case NexoraIcons.school: return _SchoolPainter(color: color);
      case NexoraIcons.idea: return _IdeaPainter(color: color);
      case NexoraIcons.quote: return _QuotePainter(color: color);
      case NexoraIcons.leaf: return _LeafPainter(color: color);
      case NexoraIcons.barChart: return _BarChartPainter(color: color);
      case NexoraIcons.challenge: return _ChallengePainter(color: color);
      case NexoraIcons.stack: return _StackPainter(color: color);
    }
  }
}

class _HomeIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _HomeIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round;

    final fillCoral = Paint()..color = const Color(0xFFEF476F)..style = PaintingStyle.fill;
    final fillWhite = Paint()..color = Colors.white..style = PaintingStyle.fill;

    // Body (simple rectangle)
    final body = Rect.fromLTRB(size.width * 0.25, size.height * 0.45, size.width * 0.75, size.height * 0.9);
    
    // Doorway
    final door = Path()
      ..moveTo(size.width * 0.4, size.height * 0.9)
      ..lineTo(size.width * 0.4, size.height * 0.6)
      ..lineTo(size.width * 0.6, size.height * 0.6)
      ..lineTo(size.width * 0.6, size.height * 0.9);

    // Roof (simple triangle)
    final roof = Path()
      ..moveTo(size.width * 0.1, size.height * 0.45)
      ..lineTo(size.width * 0.5, size.height * 0.1)
      ..lineTo(size.width * 0.9, size.height * 0.45)
      ..close();

    // Fills
    canvas.drawRect(body, fillWhite);
    canvas.drawPath(roof, fillCoral);
    
    // Outlines
    canvas.drawRect(body, paint);
    canvas.drawPath(door, paint);
    canvas.drawPath(roof, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _LibraryIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _LibraryIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round;

    final fillMint = Paint()..color = const Color(0xFF06D6A0)..style = PaintingStyle.fill;
    final fillWhite = Paint()..color = Colors.white..style = PaintingStyle.fill;

    // Left page
    final leftPage = Path()
      ..moveTo(size.width * 0.15, size.height * 0.25)
      ..lineTo(size.width * 0.5, size.height * 0.15)
      ..lineTo(size.width * 0.5, size.height * 0.85)
      ..lineTo(size.width * 0.15, size.height * 0.75)
      ..close();

    // Right page
    final rightPage = Path()
      ..moveTo(size.width * 0.85, size.height * 0.25)
      ..lineTo(size.width * 0.5, size.height * 0.15)
      ..lineTo(size.width * 0.5, size.height * 0.85)
      ..lineTo(size.width * 0.85, size.height * 0.75)
      ..close();

    canvas.drawPath(leftPage, fillMint);
    canvas.drawPath(rightPage, fillWhite);
    
    canvas.drawPath(leftPage, paint);
    canvas.drawPath(rightPage, paint);
    
    // Explicit center spine
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.15), Offset(size.width * 0.5, size.height * 0.85), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _TutorIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _TutorIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = isSelected ? PaintingStyle.fill : PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    path.moveTo(size.width * 0.5, size.height * 0.1);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.9, size.height * 0.5);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.5, size.height * 0.9);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.1, size.height * 0.5);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.5, size.height * 0.1);
    path.close();

    canvas.drawPath(path, paint);
    
    final smallPath = Path();
    smallPath.moveTo(size.width * 0.8, size.height * 0.1);
    smallPath.quadraticBezierTo(size.width * 0.8, size.height * 0.2, size.width * 0.9, size.height * 0.2);
    smallPath.quadraticBezierTo(size.width * 0.8, size.height * 0.2, size.width * 0.8, size.height * 0.3);
    smallPath.quadraticBezierTo(size.width * 0.8, size.height * 0.2, size.width * 0.7, size.height * 0.2);
    smallPath.quadraticBezierTo(size.width * 0.8, size.height * 0.2, size.width * 0.8, size.height * 0.1);
    smallPath.close();
    
    canvas.drawPath(smallPath, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ProgressIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _ProgressIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final fillPurple = Paint()..color = const Color(0xFFC7B9FF)..style = PaintingStyle.fill;

    // 3 substantial bars, strictly geometric
    final b1 = Rect.fromLTRB(size.width * 0.15, size.height * 0.65, size.width * 0.3, size.height * 0.9);
    final b2 = Rect.fromLTRB(size.width * 0.425, size.height * 0.4, size.width * 0.575, size.height * 0.9);
    final b3 = Rect.fromLTRB(size.width * 0.7, size.height * 0.15, size.width * 0.85, size.height * 0.9);

    canvas.drawRect(b1, fillPurple);
    canvas.drawRect(b2, fillPurple);
    canvas.drawRect(b3, fillPurple);

    canvas.drawRect(b1, paint);
    canvas.drawRect(b2, paint);
    canvas.drawRect(b3, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ProfileIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _ProfileIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
      
    final fillMint = Paint()..color = const Color(0xFF06D6A0)..style = PaintingStyle.fill;

    // Simple large head
    final head = Rect.fromCircle(center: Offset(size.width * 0.5, size.height * 0.3), radius: size.width * 0.2);
    
    // Simple broad body
    final body = Path()
      ..moveTo(size.width * 0.15, size.height * 0.9)
      ..lineTo(size.width * 0.15, size.height * 0.75)
      ..arcToPoint(Offset(size.width * 0.85, size.height * 0.75), radius: Radius.circular(size.width * 0.35))
      ..lineTo(size.width * 0.85, size.height * 0.9)
      ..close();

    canvas.drawOval(head, fillMint);
    canvas.drawPath(body, fillMint);
    
    canvas.drawOval(head, paint);
    canvas.drawPath(body, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _QuizIconPainter extends CustomPainter {
  final bool isSelected;
  final Color color;

  _QuizIconPainter({required this.isSelected, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
      
    final fillYellow = Paint()..color = const Color(0xFFFFD166)..style = PaintingStyle.fill;
    final fillWhite = Paint()..color = Colors.white..style = PaintingStyle.fill;

    // Simple paper
    final paper = RRect.fromRectAndRadius(Rect.fromLTRB(size.width * 0.2, size.height * 0.1, size.width * 0.8, size.height * 0.9), const Radius.circular(4));
    
    // Header accent
    final header = RRect.fromRectAndRadius(Rect.fromLTRB(size.width * 0.2, size.height * 0.1, size.width * 0.8, size.height * 0.35), const Radius.circular(4));
    
    canvas.drawRRect(paper, fillWhite);
    canvas.drawRRect(header, fillYellow);
    canvas.drawRect(Rect.fromLTRB(size.width * 0.2, size.height * 0.25, size.width * 0.8, size.height * 0.35), fillYellow);

    canvas.drawRRect(paper, paint);
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.35), Offset(size.width * 0.8, size.height * 0.35), paint);

    // Check mark 1
    final check1 = Path()
      ..moveTo(size.width * 0.3, size.height * 0.55)
      ..lineTo(size.width * 0.4, size.height * 0.65)
      ..lineTo(size.width * 0.55, size.height * 0.45);
    canvas.drawPath(check1, paint);
    // Answer line 1
    canvas.drawLine(Offset(size.width * 0.65, size.height * 0.55), Offset(size.width * 0.75, size.height * 0.55), paint);

    // Check mark 2
    final check2 = Path()
      ..moveTo(size.width * 0.3, size.height * 0.75)
      ..lineTo(size.width * 0.4, size.height * 0.85)
      ..lineTo(size.width * 0.55, size.height * 0.65);
    canvas.drawPath(check2, paint);
    // Answer line 2
    canvas.drawLine(Offset(size.width * 0.65, size.height * 0.75), Offset(size.width * 0.75, size.height * 0.75), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ArrowBackPainter extends CustomPainter {
  final Color color;
  _ArrowBackPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawLine(Offset(size.width * 0.8, size.height * 0.5), Offset(size.width * 0.2, size.height * 0.5), paint);
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.5, size.height * 0.2), paint);
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.5, size.height * 0.8), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ArrowForwardPainter extends CustomPainter {
  final Color color;
  _ArrowForwardPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.8, size.height * 0.5), paint);
    canvas.drawLine(Offset(size.width * 0.8, size.height * 0.5), Offset(size.width * 0.5, size.height * 0.2), paint);
    canvas.drawLine(Offset(size.width * 0.8, size.height * 0.5), Offset(size.width * 0.5, size.height * 0.8), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ArrowRightPainter extends CustomPainter {
  final Color color;
  _ArrowRightPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawLine(Offset(size.width * 0.4, size.height * 0.2), Offset(size.width * 0.7, size.height * 0.5), paint);
    canvas.drawLine(Offset(size.width * 0.7, size.height * 0.5), Offset(size.width * 0.4, size.height * 0.8), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _SearchPainter extends CustomPainter {
  final Color color;
  _SearchPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    canvas.drawCircle(Offset(size.width * 0.45, size.height * 0.45), size.width * 0.3, paint);
    canvas.drawLine(Offset(size.width * 0.65, size.height * 0.65), Offset(size.width * 0.9, size.height * 0.9), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _UploadPainter extends CustomPainter {
  final Color color;
  _UploadPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.8), Offset(size.width * 0.5, size.height * 0.2), paint);
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.2), Offset(size.width * 0.25, size.height * 0.45), paint);
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.2), Offset(size.width * 0.75, size.height * 0.45), paint);
    canvas.drawLine(Offset(size.width * 0.1, size.height * 0.9), Offset(size.width * 0.9, size.height * 0.9), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _CameraPainter extends CustomPainter {
  final Color color;
  _CameraPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    final path = Path()
      ..moveTo(size.width * 0.2, size.height * 0.3)
      ..lineTo(size.width * 0.3, size.height * 0.3)
      ..lineTo(size.width * 0.4, size.height * 0.15)
      ..lineTo(size.width * 0.6, size.height * 0.15)
      ..lineTo(size.width * 0.7, size.height * 0.3)
      ..lineTo(size.width * 0.8, size.height * 0.3)
      ..quadraticBezierTo(size.width * 0.9, size.height * 0.3, size.width * 0.9, size.height * 0.4)
      ..lineTo(size.width * 0.9, size.height * 0.8)
      ..quadraticBezierTo(size.width * 0.9, size.height * 0.9, size.width * 0.8, size.height * 0.9)
      ..lineTo(size.width * 0.2, size.height * 0.9)
      ..quadraticBezierTo(size.width * 0.1, size.height * 0.9, size.width * 0.1, size.height * 0.8)
      ..lineTo(size.width * 0.1, size.height * 0.4)
      ..quadraticBezierTo(size.width * 0.1, size.height * 0.3, size.width * 0.2, size.height * 0.3)..close();
    canvas.drawPath(path, paint);
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.6), size.width * 0.2, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _DocumentPainter extends CustomPainter {
  final Color color;
  final bool isPdf;
  _DocumentPainter({required this.color, this.isPdf = false});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    final fillWhite = Paint()..color = Colors.white..style = PaintingStyle.fill;
    final fillMint = Paint()..color = const Color(0xFF06D6A0)..style = PaintingStyle.fill;
    final fillCoral = Paint()..color = const Color(0xFFEF476F)..style = PaintingStyle.fill;
    
    // Main sheet
    final sheet = Path()
      ..moveTo(size.width * 0.2, size.height * 0.1)
      ..lineTo(size.width * 0.6, size.height * 0.1)
      ..lineTo(size.width * 0.8, size.height * 0.3)
      ..lineTo(size.width * 0.8, size.height * 0.9)
      ..lineTo(size.width * 0.2, size.height * 0.9)
      ..close();
      
    // Folded corner
    final fold = Path()
      ..moveTo(size.width * 0.6, size.height * 0.1)
      ..lineTo(size.width * 0.6, size.height * 0.3)
      ..lineTo(size.width * 0.8, size.height * 0.3)
      ..close();

    canvas.drawPath(sheet, fillWhite);
    canvas.drawPath(fold, isPdf ? fillCoral : fillMint);
    
    canvas.drawPath(sheet, paint);
    canvas.drawPath(fold, paint);
    
    // Internal lines
    canvas.drawLine(Offset(size.width * 0.35, size.height * 0.5), Offset(size.width * 0.65, size.height * 0.5), paint);
    canvas.drawLine(Offset(size.width * 0.35, size.height * 0.65), Offset(size.width * 0.55, size.height * 0.65), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ImagePainter extends CustomPainter {
  final Color color;
  _ImagePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawRect(Rect.fromLTRB(size.width * 0.1, size.height * 0.15, size.width * 0.9, size.height * 0.85), paint);
    canvas.drawCircle(Offset(size.width * 0.3, size.height * 0.35), size.width * 0.1, paint);
    final path = Path()..moveTo(size.width * 0.1, size.height * 0.85)..lineTo(size.width * 0.4, size.height * 0.5)..lineTo(size.width * 0.6, size.height * 0.7)..lineTo(size.width * 0.75, size.height * 0.55)..lineTo(size.width * 0.9, size.height * 0.75);
    canvas.drawPath(path, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _CheckPainter extends CustomPainter {
  final Color color;
  _CheckPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.4, size.height * 0.75), paint);
    canvas.drawLine(Offset(size.width * 0.4, size.height * 0.75), Offset(size.width * 0.8, size.height * 0.25), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ClosePainter extends CustomPainter {
  final Color color;
  _ClosePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.2), Offset(size.width * 0.8, size.height * 0.8), paint);
    canvas.drawLine(Offset(size.width * 0.8, size.height * 0.2), Offset(size.width * 0.2, size.height * 0.8), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _RetryPainter extends CustomPainter {
  final Color color;
  _RetryPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    final path = Path()..addArc(Rect.fromCircle(center: Offset(size.width * 0.5, size.height * 0.5), radius: size.width * 0.35), 0.5, 5.0);
    canvas.drawPath(path, paint);
    canvas.drawLine(Offset(size.width * 0.85, size.height * 0.4), Offset(size.width * 0.85, size.height * 0.65), paint);
    canvas.drawLine(Offset(size.width * 0.85, size.height * 0.65), Offset(size.width * 0.6, size.height * 0.65), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _SettingsPainter extends CustomPainter {
  final Color color;
  _SettingsPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.5), size.width * 0.2, paint);
    for (int i = 0; i < 8; i++) {
      canvas.save();
      canvas.translate(size.width * 0.5, size.height * 0.5);
      canvas.rotate(i * 0.785398);
      canvas.drawLine(Offset(0, -size.height * 0.25), Offset(0, -size.height * 0.4), paint);
      canvas.restore();
    }
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _AddPainter extends CustomPainter {
  final Color color;
  _AddPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.2), Offset(size.width * 0.5, size.height * 0.8), paint);
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.8, size.height * 0.5), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _RemovePainter extends CustomPainter {
  final Color color;
  _RemovePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(size.width * 0.2, size.height * 0.5), Offset(size.width * 0.8, size.height * 0.5), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _PlayPainter extends CustomPainter {
  final bool isSelected;
  final Color color;
  _PlayPainter({required this.isSelected, required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = isSelected ? PaintingStyle.fill : PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round;
    final path = Path()..moveTo(size.width * 0.3, size.height * 0.2)..lineTo(size.width * 0.8, size.height * 0.5)..lineTo(size.width * 0.3, size.height * 0.8)..close();
    canvas.drawPath(path, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _LockPainter extends CustomPainter {
  final Color color;
  _LockPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round..strokeCap = StrokeCap.round;
    canvas.drawRect(Rect.fromLTRB(size.width * 0.25, size.height * 0.45, size.width * 0.75, size.height * 0.85), paint);
    final path = Path()..moveTo(size.width * 0.35, size.height * 0.45)..lineTo(size.width * 0.35, size.height * 0.35)..quadraticBezierTo(size.width * 0.5, size.height * 0.15, size.width * 0.65, size.height * 0.35)..lineTo(size.width * 0.65, size.height * 0.45);
    canvas.drawPath(path, paint);
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.65), 1.5, Paint()..color = color);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _BookmarkPainter extends CustomPainter {
  final bool isSelected;
  final Color color;
  _BookmarkPainter({required this.isSelected, required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = isSelected ? PaintingStyle.fill : PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round;
    final path = Path()..moveTo(size.width * 0.3, size.height * 0.1)..lineTo(size.width * 0.7, size.height * 0.1)..lineTo(size.width * 0.7, size.height * 0.9)..lineTo(size.width * 0.5, size.height * 0.7)..lineTo(size.width * 0.3, size.height * 0.9)..close();
    canvas.drawPath(path, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _SendPainter extends CustomPainter {
  final Color color;
  _SendPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round..strokeCap = StrokeCap.round;
    final path = Path()..moveTo(size.width * 0.1, size.height * 0.4)..lineTo(size.width * 0.9, size.height * 0.1)..lineTo(size.width * 0.6, size.height * 0.9)..lineTo(size.width * 0.5, size.height * 0.5)..close();
    canvas.drawPath(path, paint);
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.5), Offset(size.width * 0.9, size.height * 0.1), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _MorePainter extends CustomPainter {
  final Color color;
  _MorePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(size.width * 0.2, size.height * 0.5), 2.5, paint);
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.5), 2.5, paint);
    canvas.drawCircle(Offset(size.width * 0.8, size.height * 0.5), 2.5, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _SparklePainter extends CustomPainter {
  final Color color;
  _SparklePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.fill;
    final path = Path();
    path.moveTo(size.width * 0.5, size.height * 0.1);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.9, size.height * 0.5);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.5, size.height * 0.9);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.1, size.height * 0.5);
    path.quadraticBezierTo(size.width * 0.5, size.height * 0.5, size.width * 0.5, size.height * 0.1);
    path.close();
    canvas.drawPath(path, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _WarningPainter extends CustomPainter {
  final Color color;
  _WarningPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round;
    final path = Path()..moveTo(size.width * 0.5, size.height * 0.1)..lineTo(size.width * 0.9, size.height * 0.9)..lineTo(size.width * 0.1, size.height * 0.9)..close();
    canvas.drawPath(path, paint);
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.4), Offset(size.width * 0.5, size.height * 0.7), paint);
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.8), 1.5, Paint()..color = color);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _SchoolPainter extends CustomPainter {
  final Color color;
  _SchoolPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeJoin = StrokeJoin.round..strokeCap = StrokeCap.round;
    final path = Path()..moveTo(size.width * 0.5, size.height * 0.2)..lineTo(size.width * 0.9, size.height * 0.4)..lineTo(size.width * 0.5, size.height * 0.6)..lineTo(size.width * 0.1, size.height * 0.4)..close();
    canvas.drawPath(path, paint);
    canvas.drawLine(Offset(size.width * 0.25, size.height * 0.475), Offset(size.width * 0.25, size.height * 0.7), paint);
    canvas.drawLine(Offset(size.width * 0.75, size.height * 0.475), Offset(size.width * 0.75, size.height * 0.7), paint);
    canvas.drawArc(Rect.fromLTRB(size.width * 0.25, size.height * 0.6, size.width * 0.75, size.height * 0.8), 0, 3.14159, false, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _IdeaPainter extends CustomPainter {
  final Color color;
  _IdeaPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round;
    canvas.drawCircle(Offset(size.width * 0.5, size.height * 0.4), size.width * 0.25, paint);
    canvas.drawLine(Offset(size.width * 0.4, size.height * 0.75), Offset(size.width * 0.6, size.height * 0.75), paint);
    canvas.drawLine(Offset(size.width * 0.45, size.height * 0.85), Offset(size.width * 0.55, size.height * 0.85), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _QuotePainter extends CustomPainter {
  final Color color;
  _QuotePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(size.width * 0.3, size.height * 0.4), size.width * 0.1, paint);
    canvas.drawCircle(Offset(size.width * 0.7, size.height * 0.4), size.width * 0.1, paint);
    canvas.drawRect(Rect.fromLTRB(size.width * 0.2, size.height * 0.4, size.width * 0.4, size.height * 0.7), paint);
    canvas.drawRect(Rect.fromLTRB(size.width * 0.6, size.height * 0.4, size.width * 0.8, size.height * 0.7), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _LeafPainter extends CustomPainter {
  final Color color;
  _LeafPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    // Central stem
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.9), Offset(size.width * 0.5, size.height * 0.2), paint);
    // Left leaf
    final leftLeaf = Path()
      ..moveTo(size.width * 0.5, size.height * 0.7)
      ..quadraticBezierTo(size.width * 0.2, size.height * 0.7, size.width * 0.2, size.height * 0.4)
      ..quadraticBezierTo(size.width * 0.5, size.height * 0.4, size.width * 0.5, size.height * 0.7);
    canvas.drawPath(leftLeaf, paint);
    // Right leaf
    final rightLeaf = Path()
      ..moveTo(size.width * 0.5, size.height * 0.5)
      ..quadraticBezierTo(size.width * 0.8, size.height * 0.5, size.width * 0.8, size.height * 0.2)
      ..quadraticBezierTo(size.width * 0.5, size.height * 0.2, size.width * 0.5, size.height * 0.5);
    canvas.drawPath(rightLeaf, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _BarChartPainter extends CustomPainter {
  final Color color;
  _BarChartPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    // 3 ascending bars
    canvas.drawRect(Rect.fromLTRB(size.width * 0.2, size.height * 0.6, size.width * 0.35, size.height * 0.9), paint);
    canvas.drawRect(Rect.fromLTRB(size.width * 0.45, size.height * 0.4, size.width * 0.6, size.height * 0.9), paint);
    canvas.drawRect(Rect.fromLTRB(size.width * 0.7, size.height * 0.15, size.width * 0.85, size.height * 0.9), paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _ChallengePainter extends CustomPainter {
  final Color color;
  _ChallengePainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.5..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    // Base/Mountain
    final path = Path()
      ..moveTo(size.width * 0.1, size.height * 0.9)
      ..lineTo(size.width * 0.5, size.height * 0.2)
      ..lineTo(size.width * 0.9, size.height * 0.9)
      ..close();
    canvas.drawPath(path, paint);
    
    // Flag pole at peak
    canvas.drawLine(Offset(size.width * 0.5, size.height * 0.2), Offset(size.width * 0.5, size.height * 0.05), paint);
    // Flag
    final flag = Path()
      ..moveTo(size.width * 0.5, size.height * 0.05)
      ..lineTo(size.width * 0.75, size.height * 0.1)
      ..lineTo(size.width * 0.5, size.height * 0.15);
    canvas.drawPath(flag, Paint()..color = color..style = PaintingStyle.fill);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class _StackPainter extends CustomPainter {
  final Color color;
  _StackPainter({required this.color});
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 2.0..strokeCap = StrokeCap.round..strokeJoin = StrokeJoin.round;
    // Top layer
    final topLayer = Path()
      ..moveTo(size.width * 0.5, size.height * 0.2)
      ..lineTo(size.width * 0.9, size.height * 0.4)
      ..lineTo(size.width * 0.5, size.height * 0.6)
      ..lineTo(size.width * 0.1, size.height * 0.4)
      ..close();
    canvas.drawPath(topLayer, paint);
    
    // Middle layer
    final midLayer = Path()
      ..moveTo(size.width * 0.1, size.height * 0.55)
      ..lineTo(size.width * 0.5, size.height * 0.75)
      ..lineTo(size.width * 0.9, size.height * 0.55);
    canvas.drawPath(midLayer, paint);
    
    // Bottom layer
    final botLayer = Path()
      ..moveTo(size.width * 0.1, size.height * 0.7)
      ..lineTo(size.width * 0.5, size.height * 0.9)
      ..lineTo(size.width * 0.9, size.height * 0.7);
    canvas.drawPath(botLayer, paint);
  }
  @override bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
