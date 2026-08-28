import os
import subprocess
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, roc_curve, auc

# Ensure matplotlib is installed
try:
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib
    import matplotlib.pyplot as plt

def generate_plots():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "engineered_features.csv")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"Error: Engineered dataset not found at {data_path}. Please run extract_features.py first.")
        return
        
    print(f"Loading engineered dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print("Training Decision Tree model for plotting...")
    model = DecisionTreeClassifier(max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_probs = model.predict_proba(X_test)[:, 1] # Class 1 (Legitimate) probabilities
    # Wait! Let's plot ROC curve for the Phishing class (Class 0) or Legitimate class (Class 1).
    # Since Class 1 is Legitimate and Class 0 is Phishing:
    # Let's plot ROC curve for the Phishing class (Class 0).
    # The probability of Class 0 (Phishing) is:
    phish_probs = model.predict_proba(X_test)[:, 0]
    # For Class 0 (Phishing), the target is 1 - y_test (where 1 is Phishing and 0 is Legitimate)
    y_test_phish = 1 - y_test
    
    # 1. Generate Confusion Matrix Plot
    print("Generating Confusion Matrix plot...")
    cm = confusion_matrix(y_test, y_pred)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.3)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(x=j, y=i, s=f"{cm[i, j]:,d}", va='center', ha='center', size='xx-large', weight='bold')
            
    plt.xlabel('Predicted Labels', fontsize=12)
    plt.ylabel('True Labels', fontsize=12)
    plt.title('Confusion Matrix', fontsize=14, pad=15)
    
    # Set tick labels (0 = Phishing, 1 = Legitimate)
    ax.set_xticklabels(['', 'Phishing', 'Legitimate'])
    ax.set_yticklabels(['', 'Phishing', 'Legitimate'])
    
    plt.tight_layout()
    cm_path = os.path.join(models_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"Confusion Matrix saved to {cm_path}")
    
    # 2. Generate ROC Curve Plot
    print("Generating ROC Curve plot...")
    fpr, tpr, thresholds = roc_curve(y_test_phish, phish_probs)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (FPR)', fontsize=12)
    plt.ylabel('True Positive Rate (TPR)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) - Phishing Class', fontsize=14)
    plt.legend(loc="lower right", fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    roc_path = os.path.join(models_dir, "roc_curve.png")
    plt.savefig(roc_path, dpi=150)
    plt.close()
    print(f"ROC Curve saved to {roc_path}")
    
    print("Plots generation complete!")

if __name__ == "__main__":
    generate_plots()
