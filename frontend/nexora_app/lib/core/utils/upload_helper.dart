import 'package:nexora_app/core/widgets/nexora_icons.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import '../network/api_client.dart';
import '../storage/local_storage_service.dart';
import '../models/document_metadata.dart';
import '../theme/app_colors.dart';

class UploadHelper {
  static final ImagePicker _imagePicker = ImagePicker();
  static final ApiClient _apiClient = ApiClient();
  static final LocalStorageService _storage = LocalStorageService();

  static void showAddMaterialOptions(BuildContext context, {required Function(bool) onSelect}) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'Add Material',
                  style: TextStyle(
                    fontFamily: 'BricolageGrotesque',
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              ListTile(
                leading: NexoraIcon(NexoraIcons.upload),
                title: const Text('Upload File (PDF, JPG, PNG)'),
                onTap: () {
                  Navigator.pop(context);
                  onSelect(false);
                },
              ),
              ListTile(
                leading: NexoraIcon(NexoraIcons.camera),
                title: const Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  onSelect(true);
                },
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  static Future<DocumentMetadata?> handleUpload(BuildContext context, bool isCamera, Function(bool) setLoading) async {
    String? filePath;
    String? filename;
    String? fileType;

    if (isCamera) {
      final XFile? photo = await _imagePicker.pickImage(source: ImageSource.camera);
      if (photo != null) {
        filePath = photo.path;
        filename = photo.name;
        final ext = photo.name.contains('.') 
            ? photo.name.split('.').last.toLowerCase() 
            : 'jpg';
        fileType = ext == 'jpeg' ? 'jpg' : ext;
      }
    } else {
      final result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
      );
      if (result.isNotEmpty && result.first.path != null) {
        filePath = result.first.path!;
        filename = result.first.name;
        fileType = result.first.extension?.toLowerCase() ?? 'unknown';
      }
    }

    if (filePath == null || filename == null) return null;

    setLoading(true);

    try {
      final response = await _apiClient.uploadDocument(filePath, filename: filename);
      
      if (response['success'] == true) {
        final finalFilename = response['filename'] as String? ?? filename;
        
        final newDoc = DocumentMetadata(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          filename: finalFilename,
          type: fileType ?? 'unknown',
          uploadDate: DateTime.now(),
        );
        
        await _storage.saveDocument(newDoc);
        
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Material added to library')),
          );
        }
        return newDoc;
      } else {
        final reason = response['reason'] ?? 'Server rejected the file.';
        throw Exception(reason);
      }
    } catch (e) {
      if (context.mounted) {
        String errorMsg = e.toString().toLowerCase();
        String friendlyMessage = "Couldn't upload that material. Please try again.";
        
        if (errorMsg.contains('connection') || errorMsg.contains('socket') || errorMsg.contains('host')) {
          friendlyMessage = "Couldn't connect to NEXORA. Check your connection and try again.";
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(friendlyMessage),
            backgroundColor: AppColors.nexoraCoral,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return null;
    } finally {
      setLoading(false);
    }
  }
}
