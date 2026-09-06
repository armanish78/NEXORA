import os
import glob
import re

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    if 'nexora_icons.dart' in filepath:
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    orig_content = content
    
    if 'NexoraIcon' in content and 'package:nexora_app/core/widgets/nexora_icons.dart' not in content:
        content = "import 'package:nexora_app/core/widgets/nexora_icons.dart';\n" + content
    
    # Fix nullable NexoraIcons in NexoraIcon constructor in nexora_badge.dart and nexora_button.dart
    if 'nexora_badge.dart' in filepath or 'nexora_button.dart' in filepath:
        content = content.replace('NexoraIcon(icon,', 'NexoraIcon(icon!,')
        
    if content != orig_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed {filepath}')

