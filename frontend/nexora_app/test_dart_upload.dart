import 'dart:io';
import 'package:nexora_app/core/network/api_client.dart';

void main() async {
  final apiClient = ApiClient();
  final filePath = '/home/nova/Downloads/BME654B-module-2-pdf.pdf';
  
  if (!File(filePath).existsSync()) {
    print('File does not exist: $filePath');
    return;
  }
  
  print('Uploading...');
  final success = await apiClient.uploadDocument(filePath, filename: 'BME654B-module-2-pdf.pdf');
  print('Upload success: $success');
  
  print('Fetching topics...');
  final topics = await apiClient.getDocumentTopics('BME654B-module-2-pdf.pdf');
  print('Topics count: ${topics.length}');
  print('First few topics: ${topics.take(5).toList()}');
}
