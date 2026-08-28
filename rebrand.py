import os

def rebrand():
    ext_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extension")
    
    replacements = {
        "Phishing Shield AI": "TrustNet",
        "Phishing Shield": "TrustNet",
        "PhishGuard AI": "TrustNet",
        "PhishGuard": "TrustNet"
    }
    
    for root, dirs, files in os.walk(ext_dir):
        for file in files:
            if file.endswith(('.html', '.js', '.css', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    modified = False
                    for old, new in replacements.items():
                        if old in content:
                            content = content.replace(old, new)
                            modified = True
                            
                    if modified:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Rebranded {file}")
                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    rebrand()
