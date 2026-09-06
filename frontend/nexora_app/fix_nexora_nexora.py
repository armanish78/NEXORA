import os
import glob
import re

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    orig_content = content
    
    content = content.replace('NexoraNexoraIcon', 'NexoraIcon')
    # Let's also fix the duplicate import in app_shell.dart if any
    
    if content != orig_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed {filepath}')

