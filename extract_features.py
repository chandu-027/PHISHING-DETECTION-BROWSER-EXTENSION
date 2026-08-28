import os
import re
import pandas as pd
from urllib.parse import urlparse

def extract_features_from_url(url):
    """
    Extracts lexical and structural features from a URL.
    This feature set is designed to be easily reproducible in JavaScript.
    """
    features = {}
    
    # Ensure URL has a scheme for proper parsing
    url_str = str(url)
    if not re.match(r'^[a-zA-Z]+://', url_str):
        parsed_url_str = 'http://' + url_str
    else:
        parsed_url_str = url_str
        
    try:
        parsed_url = urlparse(parsed_url_str)
        hostname = parsed_url.hostname or ""
    except Exception:
        hostname = ""
        
    # 1. Length features
    features['url_length'] = len(url_str)
    features['domain_length'] = len(hostname)
    
    # 2. IP address check
    # Check if domain is an IPv4 address (e.g. 192.168.0.1) or has an IPv6 format
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    features['is_ip'] = 1 if re.match(ip_pattern, hostname) or ':' in hostname else 0
    
    # 3. Character counts
    features['qty_dot'] = url_str.count('.')
    features['qty_hyphen'] = url_str.count('-')
    features['qty_slash'] = url_str.count('/')
    features['qty_questionmark'] = url_str.count('?')
    features['qty_equal'] = url_str.count('=')
    features['qty_at'] = url_str.count('@')
    features['qty_and'] = url_str.count('&')
    features['qty_exclamation'] = url_str.count('!')
    features['qty_underline'] = url_str.count('_')
    
    # 4. Protocol check
    features['is_https'] = 1 if url_str.lower().startswith('https') else 0
    
    # 5. Digits and letters
    digits = sum(c.isdigit() for c in url_str)
    letters = sum(c.isalpha() for c in url_str)
    features['qty_digits'] = digits
    features['qty_letters'] = letters
    features['digit_ratio'] = digits / len(url_str) if len(url_str) > 0 else 0
    
    # 6. Subdomain count
    parts = hostname.split('.')
    if len(parts) > 0 and parts[0] == 'www':
        parts = parts[1:]
    
    if features['is_ip']:
        features['qty_subdomains'] = 0
    else:
        # Subtract 1 for domain and 1 for TLD (e.g. example.com has parts=2, qty_subdomains=0)
        features['qty_subdomains'] = max(0, len(parts) - 2)
        
    # 7. Suspicious keywords
    suspicious_words = [
        'login', 'verify', 'secure', 'webscr', 'ebayisapi', 
        'signin', 'bank', 'account', 'update', 'free', 
        'bonus', 'paypal', 'wp-admin', 'verification'
    ]
    features['has_suspicious_key'] = 0
    url_lower = url_str.lower()
    for word in suspicious_words:
        if word in url_lower:
            features['has_suspicious_key'] = 1
            break
            
    return features

def engineer_dataset(sample_size=100000):
    """
    Loads the dataset, extracts features from raw URLs, and saves the engineered dataset.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, "data", "PhiUSIIL_Phishing_URL_Dataset.csv")
    output_csv = os.path.join(base_dir, "data", "engineered_features.csv")
    
    if not os.path.exists(input_csv):
        print(f"Error: Raw dataset not found at {input_csv}. Please run download_data.py first.")
        return
        
    print(f"Loading raw dataset from {input_csv}...")
    df = pd.read_csv(input_csv, encoding='utf-8-sig')
    
    # Sample dataset if it's too large to process quickly
    if len(df) > sample_size:
        print(f"Sampling {sample_size} records from {len(df)} total rows for faster feature extraction...")
        # Stratified sampling to maintain class balance
        df = df.groupby('label', group_keys=False).apply(lambda x: x.sample(min(len(x), sample_size // 2), random_state=42))
        
    print(f"Extracting features from {len(df)} URLs...")
    feature_list = []
    
    # Track progress
    total = len(df)
    for idx, (i, row) in enumerate(df.iterrows()):
        if idx % 20000 == 0 and idx > 0:
            print(f"Processed {idx}/{total} URLs...")
        feats = extract_features_from_url(row['URL'])
        feats['label'] = row['label']  # Add target label
        feature_list.append(feats)
        
    # Create DataFrame
    feat_df = pd.DataFrame(feature_list)
    
    # Ensure directory exists and save
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    print(f"Saving engineered dataset to {output_csv}...")
    feat_df.to_csv(output_csv, index=False)
    print(f"Engineered dataset saved. Shape: {feat_df.shape}")

if __name__ == "__main__":
    engineer_dataset()
