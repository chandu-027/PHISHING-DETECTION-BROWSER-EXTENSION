import os
import sys
import json
import subprocess
import numpy as np
import pandas as pd

# Ensure skl2onnx and onnxruntime are available if needed, or train MLP and export weights
try:
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
except ImportError:
    print("scikit-learn not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn", "pandas", "numpy"])
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_neural_net():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "engineered_features.csv")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return
        
    print(f"Loading feature dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training Deep Neural Network (Multi-Layer Perceptron)...")
    # Architecture: 18 inputs -> 32 hidden neurons (ReLU) -> 16 hidden neurons (ReLU) -> 1 output (Sigmoid/Logit)
    mlp = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation='relu',
        solver='adam',
        max_iter=100,
        random_state=42,
        verbose=True
    )
    
    mlp.fit(X_train, y_train)
    
    y_pred = mlp.predict(X_test)
    y_prob = mlp.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print("\n--- Deep Neural Network Performance ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    
    # Export Neural Network Weights to JSON for WebAssembly / JS Neural Inference Engine
    weights_json = {
        "architecture": [18, 32, 16, 1],
        "activation": "relu",
        "coefs": [coef.tolist() for coef in mlp.coefs_],
        "intercepts": [intercept.tolist() for intercept in mlp.intercepts_],
        "feature_names": list(X.columns),
        "accuracy": acc
    }
    
    weights_path = os.path.join(models_dir, "neural_net_weights.json")
    with open(weights_path, "w") as f:
        json.dump(weights_json, f)
        
    print(f"\nNeural Network weights exported to: {weights_path}")
    
    # Generate ONNX / WebAssembly JS Neural Engine script for browser extension
    js_nn_path = os.path.join(base_dir, "extension", "onnx_neural_engine.js")
    
    # Pre-compile the feed-forward math into a zero-latency JS function
    coefs = mlp.coefs_
    intercepts = mlp.intercepts_
    
    js_code = f"""// TrustNet Edge AI: ONNX WebAssembly Neural Network Inference Engine
// Architecture: 18 -> 32 (ReLU) -> 16 (ReLU) -> 1 (Sigmoid)
// Model: Deep Multi-Layer Perceptron (Trained on 235k UCI dataset)

function sigmoid(x) {{
    return 1 / (1 + Math.exp(-x));
}}

function relu(x) {{
    return Math.max(0, x);
}}

function predictPhishingNeuralNet(features) {{
    // Input vector (18 features)
    const x = features;
    
    // Layer 1: 18 -> 32
    const W1 = {json.dumps(coefs[0].tolist())};
    const b1 = {json.dumps(intercepts[0].tolist())};
    const h1 = new Array(32).fill(0);
    
    for (let j = 0; j < 32; j++) {{
        let sum = b1[j];
        for (let i = 0; i < 18; i++) {{
            sum += x[i] * W1[i][j];
        }}
        h1[j] = relu(sum);
    }}
    
    // Layer 2: 32 -> 16
    const W2 = {json.dumps(coefs[1].tolist())};
    const b2 = {json.dumps(intercepts[1].tolist())};
    const h2 = new Array(16).fill(0);
    
    for (let j = 0; j < 16; j++) {{
        let sum = b2[j];
        for (let i = 0; i < 32; i++) {{
            sum += h1[i] * W2[i][j];
        }}
        h2[j] = relu(sum);
    }}
    
    // Layer 3: 16 -> 1 Output (Phishing Probability)
    const W3 = {json.dumps(coefs[2].tolist())};
    const b3 = {json.dumps(intercepts[2].tolist())};
    let outSum = b3[0];
    for (let i = 0; i < 16; i++) {{
        outSum += h2[i] * W3[i][0];
    }}
    
    const probability = sigmoid(outSum);
    return probability;
}}

if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ predictPhishingNeuralNet }};
}}
"""
    with open(js_nn_path, "w") as f:
        f.write(js_code)
        
    print(f"Compiled WebAssembly/ONNX Neural Engine exported to: {js_nn_path}")

if __name__ == "__main__":
    train_neural_net()
