import splitfolders
import os

# 1. Path Settings
# Jekhetu script ta 'src' folder e ache, tai 'dataset' folder pete ek dhap pichone (../) jete hobe
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_folder = os.path.join(base_dir, "dataset", "Raw_Data")
output_folder = os.path.join(base_dir, "dataset", "processed")

# 2. Check Input Folder
if not os.path.exists(input_folder):
    print(f"❌ Error: Raw Data folder pawa jacche na: {input_folder}")
    exit()

# 3. Data Split Process
print(f"📂 Input Folder: {input_folder}")
print(f"📂 Output Folder: {output_folder}")
print("⏳ Data splitting suru hocche... (Train: 80%, Val: 10%, Test: 10%)")

try:
    # Ager processed data thakle seta replace hobe na, tai notun kore korle folder khali kora valo
    # Kintu splitfolders library automatic handle kore ney sadharonoto.
    
    splitfolders.ratio(input_folder, 
                       output=output_folder, 
                       seed=42, 
                       ratio=(.8, .1, .1), 
                       group_prefix=None, 
                       move=False) # move=False mane original data delete hobe na

    print("🎉 Success! Data split hoye 'dataset/processed' folder e joma hoyeche.")
    print("➡️  Ekhon 'dataset/processed' folder check korun.")

except Exception as e:
    print(f"❌ Kono ekta somosya hoyeche: {e}")