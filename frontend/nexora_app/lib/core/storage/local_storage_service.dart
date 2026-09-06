import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/document_metadata.dart';
import '../../features/study/models/study_message.dart';

class LocalStorageService {
  static const String _documentsKey = 'nexora_documents';
  static const String _lastAccessedKey = 'nexora_last_accessed_document_id';

  Future<void> saveDocument(DocumentMetadata document) async {
    final prefs = await SharedPreferences.getInstance();
    final docs = await getDocuments();
    
    // Remove if exists to update it
    docs.removeWhere((d) => d.id == document.id);
    docs.insert(0, document); // Add to beginning (most recent)
    
    final String encoded = jsonEncode(docs.map((d) => d.toJson()).toList());
    await prefs.setString(_documentsKey, encoded);
    
    // Also set as last accessed
    await setLastAccessedDocument(document.id);
  }

  Future<List<DocumentMetadata>> getDocuments() async {
    final prefs = await SharedPreferences.getInstance();
    final String? encoded = prefs.getString(_documentsKey);
    
    if (encoded == null) return [];
    
    try {
      final List<dynamic> decoded = jsonDecode(encoded);
      return decoded.map((json) => DocumentMetadata.fromJson(json)).toList();
    } catch (e) {
      return [];
    }
  }

  Future<void> setLastAccessedDocument(String id) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_lastAccessedKey, id);
  }

  Future<DocumentMetadata?> getLastAccessedDocument() async {
    final prefs = await SharedPreferences.getInstance();
    final String? id = prefs.getString(_lastAccessedKey);
    
    if (id == null) return null;
    
    final docs = await getDocuments();
    try {
      return docs.firstWhere((d) => d.id == id);
    } catch (e) {
      return null;
    }
  }

  Future<void> saveConversation(String documentId, List<StudyMessage> messages) async {
    final prefs = await SharedPreferences.getInstance();
    final String encoded = jsonEncode(messages.map((m) => m.toJson()).toList());
    await prefs.setString('nexora_chat_$documentId', encoded);
  }

  Future<List<StudyMessage>> getConversation(String documentId) async {
    final prefs = await SharedPreferences.getInstance();
    final String? encoded = prefs.getString('nexora_chat_$documentId');
    
    if (encoded == null) return [];
    
    try {
      final List<dynamic> decoded = jsonDecode(encoded);
      return decoded.map((json) => StudyMessage.fromJson(json)).toList();
    } catch (e) {
      return [];
    }
  }
}
