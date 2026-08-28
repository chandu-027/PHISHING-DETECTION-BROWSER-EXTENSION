import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def train_and_evaluate():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "engineered_features.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: Engineered dataset not found at {data_path}. Please run extract_features.py first.")
        return
        
    print(f"Loading engineered dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Separate features and target
    X = df.drop(columns=['label'])
    y = df['label']
    
    # Train-test split (80/20, stratified to maintain class balance)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"Training set shape: {X_train.shape}")
    print(f"Testing set shape: {X_test.shape}")
    
    # Models to train
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    }
    
    trained_models = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Predict on test set
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"Results for {name}:")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f} (Ability to avoid false positives)")
        print(f"  Recall:    {rec:.4f} (Ability to find all phishing URLs)")
        print(f"  F1-Score:  {f1:.4f}")
        print("  Confusion Matrix:")
        # Label 0 is Phishing, Label 1 is Legitimate (from our explore_data.py)
        # Confusion matrix is [[TN, FP], [FN, TP]] where 0 is negative and 1 is positive.
        # But wait: let's verify if label 0 is Phishing and label 1 is Legitimate.
        # So:
        # True Phishing (0) classified as Phishing (0) = TN
        # True Phishing (0) classified as Legitimate (1) = FP (Dangerous!)
        # True Legitimate (1) classified as Phishing (0) = FN (Annoying)
        # True Legitimate (1) classified as Legitimate (1) = TP
        print(f"    [[True Phish as Phish, True Phish as Legit],")
        print(f"     [True Legit as Phish, True Legit as Legit]]")
        print(f"    {cm.tolist()}")
        
    return X_train.columns.tolist(), trained_models, X_test, y_test

if __name__ == "__main__":
    train_and_evaluate()
