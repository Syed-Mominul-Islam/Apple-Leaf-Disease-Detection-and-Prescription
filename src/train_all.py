import os
import sys
import argparse

# Add the directory to the path so python can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from train import train
from evaluate_model import evaluate
from plot_roc_curve import plot_roc_curve
from generate_6class_metrics import generate_6class_results
from latex_table_generator import generate_latex_table

def run_experiment(model_name):
    print(f"\n" + "="*60)
    print(f"[START] Starting Experiment Pipeline for: {model_name}")
    print("="*60 + "\n")
    
    # Override configuration parameters dynamically
    config.MODEL_NAME = model_name
    config.MODEL_DIR = os.path.join(config.BASE_DIR, "models", model_name)
    config.LOG_DIR = os.path.join(config.BASE_DIR, "logs", model_name)
    
    # Ensure folders exist
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    config.MODEL_SAVE_PATH = os.path.join(config.MODEL_DIR, f"{model_name}_model.keras")
    config.HISTORY_SAVE_PATH = os.path.join(config.LOG_DIR, f"{model_name}_history.pkl")
    
    # 1. Train Model
    print(f"[INFO] [1/5] Training {model_name}...")
    train()
    
    # 2. Evaluate Model
    print(f"[INFO] [2/5] Evaluating {model_name} on test set...")
    try:
        evaluate()
    except Exception as e:
        print(f"[ERROR] Evaluation failed for {model_name}: {e}")
        
    # 3. Generate ROC Curve
    print(f"[INFO] [3/5] Generating ROC Curve for {model_name}...")
    try:
        plot_roc_curve()
    except Exception as e:
        print(f"[ERROR] ROC Curve plotting failed for {model_name}: {e}")
        
    # 4. Generate 6-Class Metrics & Confusion Matrix
    print(f"[INFO] [4/5] Generating 6-Class metrics & CM for {model_name}...")
    try:
        generate_6class_results()
    except Exception as e:
        print(f"[ERROR] 6-Class metrics generation failed for {model_name}: {e}")
        
    # 5. Generate LaTeX Table
    print(f"[INFO] [5/5] Generating LaTeX Table for {model_name}...")
    try:
        generate_latex_table()
    except Exception as e:
        print(f"[ERROR] LaTeX Table generation failed for {model_name}: {e}")

    print(f"\n[SUCCESS] Finished Experiment Pipeline for: {model_name}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run training and evaluation for multiple models.")
    parser.add_argument(
        "--models", 
        type=str, 
        default="mobilenetv2,resnet50,densenet121,efficientnetb0",
        help="Comma-separated list of models to train (e.g. mobilenetv2,resnet50)"
    )
    args = parser.parse_args()
    
    target_models = [m.strip() for m in args.models.split(",") if m.strip()]
    
    print(f"Scheduled experiments for: {target_models}")
    
    for model in target_models:
        try:
            run_experiment(model)
        except Exception as e:
            print(f"[FATAL] Pipeline crashed for {model}: {e}")
