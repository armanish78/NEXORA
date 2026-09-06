class DocumentMetadata {
  final String id;
  final String filename;
  final String type;
  final DateTime uploadDate;
  
  DocumentMetadata({
    required this.id,
    required this.filename,
    required this.type,
    required this.uploadDate,
  });

  factory DocumentMetadata.fromJson(Map<String, dynamic> json) {
    return DocumentMetadata(
      id: json['id'] as String,
      filename: json['filename'] as String,
      type: json['type'] as String,
      uploadDate: DateTime.parse(json['uploadDate'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'filename': filename,
      'type': type,
      'uploadDate': uploadDate.toIso8601String(),
    };
  }
}
