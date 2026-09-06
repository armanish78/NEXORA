import os
import glob

for filepath in glob.glob('/home/nova/Desktop/RAG/frontend/nexora_app/lib/**/*.dart', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    orig_content = content
    content = content.replace('const NexoraIcon(', 'NexoraIcon(')
    content = content.replace('const  NexoraIcon(', 'NexoraIcon(')
    content = content.replace('const\nNexoraIcon(', 'NexoraIcon(')
    
    if content != orig_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed {filepath}')

