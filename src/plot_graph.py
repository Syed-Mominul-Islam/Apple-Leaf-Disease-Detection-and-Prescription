import matplotlib.pyplot as plt
import os
import config

# আপনার ট্রেনিং লগ থেকে সংগৃহীত ডেটা
epochs = range(1, 26)

# Training Accuracy vs Validation Accuracy Data
accuracy = [0.2832, 0.5525, 0.7813, 0.8867, 0.9546, 0.9748, 0.9810, 0.9830, 0.9803, 0.9851, 
            0.9848, 0.9825, 0.9877, 0.9831, 0.9890, 0.9912, 0.9916, 0.9924, 0.9930, 0.9940, 
            0.9931, 0.9929, 0.9943, 0.9947, 0.9940]

val_accuracy = [0.2248, 0.4862, 0.7246, 0.8478, 0.9326, 0.9807, 0.9777, 0.9792, 0.9874, 0.9829, 
                0.9874, 0.9420, 0.9814, 0.9807, 0.9911, 0.9926, 0.9926, 0.9926, 0.9926, 0.9940, 
                0.9948, 0.9955, 0.9940, 0.9948, 0.9940]

# Training Loss vs Validation Loss Data
loss = [1.8797, 1.2533, 0.6927, 0.3522, 0.1303, 0.0746, 0.0613, 0.0554, 0.0547, 0.0447, 
        0.0452, 0.0471, 0.0413, 0.0472, 0.0321, 0.0280, 0.0266, 0.0266, 0.0231, 0.0223, 
        0.0235, 0.0214, 0.0196, 0.0193, 0.0204]

val_loss = [1.9456, 1.3332, 0.7824, 0.4743, 0.1933, 0.0655, 0.0728, 0.0627, 0.0439, 0.0490, 
            0.0386, 0.1836, 0.0484, 0.0542, 0.0222, 0.0246, 0.0257, 0.0230, 0.0206, 0.0188, 
            0.0197, 0.0163, 0.0184, 0.0180, 0.0192]

def plot_metrics():
    # গ্রাফ সেভ করার ফোল্ডার চেক করা
    log_dir = os.path.join(config.BASE_DIR, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    plt.figure(figsize=(14, 6))

    # 1. Accuracy Graph
    plt.subplot(1, 2, 1)
    plt.plot(epochs, accuracy, label='Training Accuracy', marker='o')
    plt.plot(epochs, val_accuracy, label='Validation Accuracy', marker='o')
    plt.title('Model Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    # 2. Loss Graph
    plt.subplot(1, 2, 2)
    plt.plot(epochs, loss, label='Training Loss', marker='o')
    plt.plot(epochs, val_loss, label='Validation Loss', marker='o')
    plt.title('Model Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    # Save Graph inside 'logs' folder
    save_path = os.path.join(log_dir, "accuracy_loss_graph.png")
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"✅ Graph saved at: {save_path}")
    plt.show()

if __name__ == "__main__":
    plot_metrics()