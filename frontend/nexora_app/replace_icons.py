import os
import glob
import re

mapping = {
    'file_upload_outlined': 'upload',
    'camera_alt_outlined': 'camera',
    'arrow_forward': 'forward',
    'refresh': 'retry',
    'play_arrow_rounded': 'play',
    'book': 'document',
    'trending_up': 'progress',
    'bookmark_outline': 'bookmark',
    'auto_awesome': 'sparkle',
    'sync': 'retry',
    'menu_book': 'document',
    'warning_amber_rounded': 'warning',
    'description': 'document',
    'lock': 'lock',
    'quiz': 'quiz',
    'school': 'school',
    'add': 'add',
    'send': 'send',
    'arrow_back': 'back',
    'lightbulb_outline': 'idea',
    'keyboard_double_arrow_right': 'forward',
    'picture_as_pdf_outlined': 'pdf',
    'article_outlined': 'document',
    'image_outlined': 'image',
    'insert_drive_file_outlined': 'document',
    'search': 'search',
    'close': 'close',
    'tune': 'settings',
    'format_quote': 'quote',
    'check': 'check',
    'check_circle': 'check',
    'cancel': 'close',
    'auto_stories': 'document',
    'chevron_right': 'forward',
    'error_outline': 'warning',
    'remove': 'remove',
    'person_outline': 'profile'
}

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    if 'nexora_icons.dart' in filepath or 'app_shell.dart' in filepath:
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    orig_content = content
    
    # Replace IconData assignments and conditionals
    content = content.replace('IconData', 'NexoraIcons')
    
    # Replace the Icons.name with NexoraIcons.mapped_name
    for m_old, m_new in mapping.items():
        content = re.sub(rf'\bIcons\.{m_old}\b', f'NexoraIcons.{m_new}', content)
        
    # Replace Icon(NexoraIcons.name, ...) with NexoraIcon(NexoraIcons.name, ...)
    content = re.sub(r'\bIcon\(\s*NexoraIcons', 'NexoraIcon(NexoraIcons', content)
    # Handle variables passed to Icon
    # E.g. Icon(trailingIcon -> NexoraIcon(trailingIcon
    # But ONLY if the file uses NexoraIcons
    
    if content != orig_content:
        # Add import if missing
        if 'nexora_icons.dart' not in content:
            # count directories to lib to figure out relative path, or just use package import
            # Using package import is safer
            import_statement = "import 'package:nexora_app/core/widgets/nexora_icons.dart';\n"
            content = import_statement + content
            
        # Replace variable icons in Icon constructor if any left
        # like Icon(icon, ...)
        # A simple hack: replace Icon( with NexoraIcon( and fix specific cases if needed
        # We'll just carefully replace any Icon( that is not already NexoraIcon(
        content = re.sub(r'(?<!Nexora)Icon\(', 'NexoraIcon(', content)
        # Fix IconButton(icon: NexoraIcon(...) ...
        # wait, IconButton is fine, it takes a Widget for icon. So IconButton(icon: NexoraIcon(...) is correct!
        
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Updated {filepath}')
