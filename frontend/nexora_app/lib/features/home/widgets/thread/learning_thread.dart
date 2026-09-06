import 'package:flutter/material.dart';
import 'thread_segment.dart';
import 'current_thread_node.dart';

class LearningThread extends StatelessWidget {
  final bool isEmpty;
  final VoidCallback onUpload;
  final bool isUploading;

  const LearningThread({
    super.key,
    required this.isEmpty,
    required this.onUpload,
    this.isUploading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isEmpty) {
      return CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: CurrentThreadNode(
              type: ThreadNodeType.genesis,
              title: 'START HERE',
              buttonText: 'UPLOAD MATERIAL',
              onAction: onUpload,
              isLoading: isUploading,
              isFirst: true,
              isLast: true,
            ),
          ),
        ],
      );
    }

    // When real data exists, it will populate this list
    return const CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: SizedBox.shrink(),
        ),
      ],
    );
  }
}
