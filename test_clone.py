import subprocess
import os
import shutil
import stat

DIR = "repositories/test"

def remove_readonly(func, path, excinfo):
    """Clear the readonly bit and reattempt removal on Windows"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

if os.path.exists(DIR):
    shutil.rmtree(DIR, onerror=remove_readonly)

result = subprocess.run(
    ['git', 'clone', "https://github.com/uday986675/gender_classification", DIR],
    capture_output=True,
    text=True,
    timeout=300
)

if result.returncode == 0:
    print("Repository cloned successfully")
else:
    print(f"Clone failed: {result.stderr}")

print("Done")
