import pickle
import os

history_path = r'd:\PMIT-FINAL-REPORT-WRITING\PMIT-FINAL-PROJECT\logs\training_history.pkl'
if os.path.exists(history_path):
    with open(history_path, 'rb') as f:
        h = pickle.load(f)
    
    final_acc = h['accuracy'][-1]
    val_acc = h['val_accuracy'][-1]
    final_loss = h['loss'][-1]
    val_loss = h['val_loss'][-1]
    
    print(f'Final Training Accuracy: {final_acc*100:.2f}%')
    print(f'Final Validation Accuracy: {val_acc*100:.2f}%')
    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Validation Loss: {val_loss:.4f}')
    
    # Check for overfitting
    acc_gap = abs(final_acc - val_acc)
    print(f'Accuracy Gap: {acc_gap*100:.2f}%')
    
    if acc_gap > 0.10: # More than 10% gap
        print('Status: Significant Overfitting detected.')
    elif acc_gap > 0.05:
        print('Status: Slight Overfitting detected.')
    else:
        print('Status: Well-generalized (No major overfitting).')
else:
    print('Log file not found at:', history_path)
