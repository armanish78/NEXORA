import os
import glob
import re

mapping = {
    'add_rounded': 'add',
    'check_box_outlined': 'check',
    'chat_bubble_outline': 'more',
    'format_quote_rounded': 'quote',
    'arrow_forward_rounded': 'forward',
    'lightbulb_rounded': 'idea',
    'refresh_rounded': 'retry',
    'close_rounded': 'close',
    'search_rounded': 'search',
    'play_circle_fill': 'play',
    'library_books': 'library',
    'file_copy': 'document',
    'warning_rounded': 'warning',
    'school_rounded': 'school',
    'picture_as_pdf': 'pdf',
    'image': 'image',
    'camera_alt': 'camera',
    'file_upload': 'upload',
    'settings': 'settings'
}

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    orig_content = content
    
    # Catch any remaining Icons.xyz
    def replace_icon(match):
        icon_name = match.group(1)
        # Try to map, otherwise just use a default like check or document
        new_icon = mapping.get(icon_name)
        if not new_icon:
            if 'add' in icon_name: new_icon = 'add'
            elif 'check' in icon_name: new_icon = 'check'
            elif 'arrow_forward' in icon_name or 'chevron_right' in icon_name: new_icon = 'forward'
            elif 'arrow_back' in icon_name or 'chevron_left' in icon_name: new_icon = 'back'
            elif 'close' in icon_name or 'cancel' in icon_name or 'clear' in icon_name: new_icon = 'close'
            elif 'search' in icon_name: new_icon = 'search'
            elif 'refresh' in icon_name or 'sync' in icon_name: new_icon = 'retry'
            elif 'warning' in icon_name or 'error' in icon_name: new_icon = 'warning'
            elif 'book' in icon_name or 'file' in icon_name or 'document' in icon_name or 'article' in icon_name: new_icon = 'document'
            elif 'image' in icon_name or 'photo' in icon_name: new_icon = 'image'
            elif 'pdf' in icon_name: new_icon = 'pdf'
            elif 'camera' in icon_name: new_icon = 'camera'
            elif 'upload' in icon_name: new_icon = 'upload'
            elif 'settings' in icon_name or 'tune' in icon_name: new_icon = 'settings'
            elif 'play' in icon_name: new_icon = 'play'
            elif 'lock' in icon_name: new_icon = 'lock'
            elif 'bookmark' in icon_name: new_icon = 'bookmark'
            elif 'send' in icon_name: new_icon = 'send'
            elif 'school' in icon_name: new_icon = 'school'
            elif 'idea' in icon_name or 'lightbulb' in icon_name: new_icon = 'idea'
            elif 'quote' in icon_name: new_icon = 'quote'
            elif 'more' in icon_name or 'chat' in icon_name: new_icon = 'more'
            else: new_icon = 'check' # fallback
            
        return f'NexoraIcons.{new_icon}'

    content = re.sub(r'\bIcons\.([a-zA-Z0-9_]+)\b', replace_icon, content)
    
    if content != orig_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed {filepath}')

