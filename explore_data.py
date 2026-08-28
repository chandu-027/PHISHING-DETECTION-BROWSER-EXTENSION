import os
import pandas as pd

def explore_dataset():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "PhiUSIIL_Phishing_URL_Dataset.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}. Please run download_data.py first.")
        return
        
    print(f"Loading dataset from {csv_path}...")
    # Read the dataset (handle UTF-8 BOM if present)
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    print("\n" + "="*50)
    print("DATASET OVERVIEW")
    print("="*50)
    print(f"Dataset Shape: {df.shape} (rows, columns)")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
    
    print("\n" + "="*50)
    print("CLASS DISTRIBUTION (label column)")
    print("="*50)
    class_counts = df['label'].value_counts()
    print(class_counts)
    
    # According to the dataset documentation:
    # legitimate = 134,850 and phishing = 100,945
    # Let's map them based on counts
    legit_label = class_counts.idxmax() if class_counts.max() == 134850 else 1
    phish_label = class_counts.idxmin() if class_counts.min() == 100945 else 0
    
    print(f"Detected Mapping:")
    print(f"  - Label {legit_label}: Legitimate (Count: {class_counts.get(legit_label, 0)})")
    print(f"  - Label {phish_label}: Phishing (Count: {class_counts.get(phish_label, 0)})")
    
    print("\n" + "="*50)
    print("SAMPLE URLS")
    print("="*50)
    
    print(f"\nLegitimate URLs (Label {legit_label}) - Random Samples:")
    legit_samples = df[df['label'] == legit_label]['URL'].sample(5, random_state=42)
    for i, url in enumerate(legit_samples, 1):
        print(f"{i}. {url}")
        
    print(f"\nPhishing URLs (Label {phish_label}) - Random Samples:")
    phish_samples = df[df['label'] == phish_label]['URL'].sample(5, random_state=42)
    for i, url in enumerate(phish_samples, 1):
        print(f"{i}. {url}")
        
    print("\n" + "="*50)
    print("BASIC STATISTICAL CORRELATIONS")
    print("="*50)
    # Group by label and compute average of some interesting pre-computed features
    interesting_cols = ['URLLength', 'DomainLength', 'NoOfSubDomain', 'IsHTTPS', 'label']
    available_cols = [col for col in interesting_cols if col in df.columns]
    
    if len(available_cols) > 1:
        grouped = df[available_cols].groupby('label').mean()
        # Rename index for readability
        grouped.index = grouped.index.map({legit_label: 'Legitimate', phish_label: 'Phishing'})
        print("Average feature values by website class:")
        print(grouped)
        
if __name__ == "__main__":
    explore_dataset()
