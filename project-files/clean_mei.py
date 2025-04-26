import os
import shutil
import glob

# Get the Temp directory path
temp_dir = os.path.join(os.environ.get("LOCALAPPDATA"), "Temp")

# Find all folders starting with "_MEI"
mei_folders = glob.glob(os.path.join(temp_dir, "_MEI*"))

# Delete each found folder
for folder in mei_folders:
    try:
        shutil.rmtree(folder)
        print(f"Deleted: {folder}")
    except Exception as e:
        print(f"Failed to delete {folder}: {e}")

print("Cleanup completed!")

#pyinstaller --noconsole --onefile --name=start --hidden-import encodings --hidden-import charset_normalizer start.py
#Manually Extract base_library.zip