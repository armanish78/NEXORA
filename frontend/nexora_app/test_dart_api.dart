import 'dart:convert';
import 'dart:io';

void main() async {
  final baseUrl = 'http://127.0.0.1:8000';
  final filename = 'test.pdf'; // Assuming test.pdf
  final endpoint = '$baseUrl/documents/${Uri.encodeComponent(filename)}/topics';
  
  print('Requesting: $endpoint');
  
  try {
    final client = HttpClient();
    final request = await client.getUrl(Uri.parse(endpoint));
    final response = await request.close();
    
    print('Status code: ${response.statusCode}');
    
    final body = await response.transform(utf8.decoder).join();
    print('Body: $body');
    
    if (response.statusCode == 200) {
      final data = jsonDecode(body) as Map<String, dynamic>;
      if (data.containsKey('topics')) {
        final topics = List<String>.from(data['topics']);
        print('Topics length: ${topics.length}');
      }
    }
  } catch (e) {
    print('Error: $e');
  }
}
