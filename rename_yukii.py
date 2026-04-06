import os

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'venv' in root:
        continue
    for file in files:
        if file.endswith(('.py', '.txt', '.md', '.env', '.yml', '.sample')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'YUKII' in content or 'yukii' in content or 'Yukii' in content:
                    content = content.replace('YUKIIMUSIC', 'YUKIIMUSIC')
                    content = content.replace('YUKII', 'YUKII')
                    content = content.replace('yukii', 'yukii')
                    content = content.replace('Yukii', 'Yukii')
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
            except Exception:
                pass

if os.path.exists('YUKIIMUSIC'):
    os.rename('YUKIIMUSIC', 'YUKIIMUSIC')
    print("✅ Folder Renamed to YUKIIMUSIC")
