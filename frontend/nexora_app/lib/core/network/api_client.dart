import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiClient {
  static String get baseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://127.0.0.1:8000';
  }

  Future<Map<String, dynamic>> health() async {
    final response = await http.get(
      Uri.parse('$baseUrl/health'),
    );

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> askQuestion({
    required String query,
    int topK = 5,
    String? filename,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/questions'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'query': query,
        'top_k': topK,
        'filename': filename,
      }),
    );

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> uploadDocument(String filePath, {String? filename}) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/documents'),
    );

    request.files.add(
      await http.MultipartFile.fromPath('file', filePath, filename: filename),
    );

    final response = await request.send();
    final body = await response.stream.bytesToString();

    return jsonDecode(body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createQuiz(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/quizzes'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createPersonalizedQuiz(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/quizzes/personalized'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> submitAnswer(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/answers'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getUserProgress(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$userId/progress'),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<dynamic> getWeakTopics(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$userId/weak-topics'),
    );
    return jsonDecode(response.body);
  }

  Future<dynamic> getStrongTopics(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$userId/strong-topics'),
    );
    return jsonDecode(response.body);
  }

  Future<List<String>> getDocumentTopics(String filename) async {
    final endpoint = '$baseUrl/documents/${Uri.encodeComponent(filename)}/topics';
    print('[Suggestions] filename: $filename');
    print('[Suggestions] endpoint: $endpoint');
    
    final response = await http.get(Uri.parse(endpoint));
    print('[Suggestions] status: ${response.statusCode}');
    
    if (response.statusCode != 200) {
      throw Exception('TOPIC FETCH FAILED -> HTTP ${response.statusCode}');
    }
    
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    if (data.containsKey('topics')) {
      final topics = List<String>.from(data['topics']);
      print('[Suggestions] topics received: ${topics.length}');
      print('[Suggestions] topics: ${topics.take(5).toList()}');
      return topics;
    }
    return [];
  }
}
