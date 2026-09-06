import os
import glob
import re

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    orig_content = content
    
    content = content.replace('Icon(NexoraIcons', 'NexoraIcon(NexoraIcons')
    
    # Also replace Icon(icon) where icon is a parameter, wait, I can just replace Icon(
    # if it's followed by something that isn't Icons. or a known IconData.
    # Actually, NexoraBadge and NexoraButton have:
    # NexoraIcon(icon!,
    
    if content != orig_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed {filepath}')

