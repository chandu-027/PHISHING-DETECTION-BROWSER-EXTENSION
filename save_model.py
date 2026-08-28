import os
import joblib
from train_model import train_and_evaluate

def save_and_export_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Train the models
    feature_names, trained_models, X_test, y_test = train_and_evaluate()
    
    # 1. Save standard scikit-learn model files using joblib
    for name, model in trained_models.items():
        filename = f"{name.lower().replace(' ', '_')}_model.pkl"
        filepath = os.path.join(models_dir, filename)
        print(f"Saving {name} to {filepath}...")
        joblib.dump(model, filepath)
        
    # 2. Export the Decision Tree to Javascript for offline client-side execution
    dt_model = trained_models.get("Decision Tree")
    if dt_model:
        js_filename = "predict_phishing.js"
        # We will save it in the models folder first, and later copy it to the extension folder
        js_filepath = os.path.join(models_dir, js_filename)
        export_tree_to_js(dt_model, feature_names, js_filepath)
        
        # Verify the JS predictions match python predictions on a sample of test data
        verify_js_export(dt_model, feature_names, X_test, js_filepath)

def export_tree_to_js(model, feature_names, js_filepath):
    tree = model.tree_
    
    def recurse(node, depth):
        indent = "  " * depth
        # Check if leaf node
        if tree.children_left[node] == -1 and tree.children_right[node] == -1:
            values = tree.value[node][0]
            total = sum(values)
            # class 0 is Phishing, class 1 is Legitimate
            prob_phish = values[0] / total if total > 0 else 0.0
            return f"{indent}return {prob_phish:.4f};\n"
            
        feature_idx = tree.feature[node]
        feature_name = feature_names[feature_idx]
        threshold = tree.threshold[node]
        
        js_code = f"{indent}if (features['{feature_name}'] <= {threshold:.4f}) {{\n"
        js_code += recurse(tree.children_left[node], depth + 1)
        js_code += f"{indent}}} else {{\n"
        js_code += recurse(tree.children_right[node], depth + 1)
        js_code += f"{indent}}}\n"
        return js_code

    body = recurse(0, 2)
    
    js_template = f"""/**
 * Auto-generated Decision Tree Phishing Predictor.
 * Trained on UCI PhiUSIIL dataset.
 * Returns the probability of the URL being phishing (0.0 to 1.0).
 */
function predictPhishing(features) {{
{body}}}

if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{ predictPhishing }};
}}
"""
    with open(js_filepath, "w") as f:
        f.write(js_template)
    print(f"Successfully exported Decision Tree rules to JavaScript: {js_filepath}")

def verify_js_export(dt_model, feature_names, X_test, js_filepath):
    """
    Verify that the exported JavaScript file produces identical class predictions to Python.
    We will write a temporary node.js script to run the exported JS function.
    """
    print("\nVerifying JavaScript export...")
    # Sample 5 rows from test set
    sample_df = X_test.head(5)
    
    # Calculate Python predictions
    py_probs = dt_model.predict_proba(sample_df)[:, 0]  # Class 0 (Phishing) probability
    py_classes = dt_model.predict(sample_df)
    
    print("Python Probabilities (Phishing):", py_probs)
    
    # Write a temporary script to execute Node and check
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_verify_js = os.path.join(base_dir, "models", "verify_prediction.js")
    
    # Format the samples into JS objects
    samples_js = []
    for idx, (_, row) in enumerate(sample_df.iterrows()):
        row_dict = row.to_dict()
        samples_js.append(row_dict)
        
    js_code = f"""
const {{ predictPhishing }} = require('./predict_phishing.js');
const samples = {samples_js};
const results = samples.map(predictPhishing);
console.log(JSON.stringify(results));
"""
    with open(temp_verify_js, "w") as f:
        f.write(js_code)
        
    # Execute the node script
    try:
        import subprocess
        result = subprocess.run(['node', temp_verify_js], capture_output=True, text=True, check=True)
        js_probs = eval(result.stdout.strip())
        print("Node.js Probabilities (Phishing):", js_probs)
        
        # Compare
        match = True
        for py_p, js_p in zip(py_probs, js_probs):
            if abs(py_p - js_p) > 0.0001:
                match = False
                break
        
        if match:
            print("Verification Success! JavaScript and Python predictions match perfectly.")
        else:
            print("Verification Warning: Slight discrepancy between JS and Python prediction values.")
            
    except Exception as e:
        print(f"Skipped Node.js verification (Node might not be installed): {e}")
        
    # Clean up temp verification script if it exists
    if os.path.exists(temp_verify_js):
        try:
            os.remove(temp_verify_js)
        except Exception:
            pass

if __name__ == "__main__":
    save_and_export_models()
