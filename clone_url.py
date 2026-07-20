import subprocess
import os
import shutil
import time
import stat
import tempfile
from pathlib import Path

DIR = "repositories/langgraph"

def remove_readonly(func, path, excinfo):
    """Clear the readonly bit and reattempt removal on Windows"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Error removing {path}: {e}")

def kill_git_processes():
    """Kill any hanging git processes"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'git.exe'], 
                      capture_output=True, timeout=5, check=False)
        subprocess.run(['taskkill', '/F', '/IM', 'git-credential-manager.exe'], 
                      capture_output=True, timeout=5, check=False)
        time.sleep(1)
    except Exception as e:
        print(f"Error killing git processes: {e}")

def clear_directory():
    """Clear the directory with multiple retry strategies"""
    if not os.path.exists(DIR):
        print(f"Directory -> {DIR} does not exist")
        return True
    
    # First, try to kill any git processes that might have locks
    kill_git_processes()
    
    # Try multiple times with increasing delays
    for attempt in range(5):
        try:
            # Use onerror handler to handle readonly files
            shutil.rmtree(DIR, onerror=remove_readonly)
            print(f"Directory -> {DIR} removed successfully.")
            return True
        except PermissionError as e:
            print(f"Permission error on attempt {attempt + 1}: {e}")
            
            # On Windows, try to handle locked files specifically
            if attempt < 4:
                print(f"Retrying... (attempt {attempt + 1}/5)")
                time.sleep(2 ** attempt)  # Exponential backoff
                
                # Kill git processes again if still failing
                kill_git_processes()
            else:
                # Last resort: rename the directory and delete later
                try:
                    temp_dir = DIR + "_old_" + str(int(time.time()))
                    print(f"Renaming to {temp_dir} and will try to delete it later")
                    os.rename(DIR, temp_dir)
                    print(f"Directory renamed successfully")
                    
                    # Try to delete the renamed directory in background
                    try:
                        shutil.rmtree(temp_dir, onerror=remove_readonly)
                    except:
                        print(f"Will delete {temp_dir} on next run")
                    return True
                except Exception as rename_error:
                    print(f"Failed to rename directory: {rename_error}")
                    raise
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == 4:
                raise
    
    return False

def clone_url(url):
    """Clone repository with proper error handling"""
    # Clear the directory first
    if not clear_directory():
        print("Failed to clear directory, attempting to continue anyway...")
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(DIR), exist_ok=True)
    
    # Check if git is available
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise Exception("Git is not installed or not in PATH")
    
    # Clone using subprocess with better error handling
    try:
        print(f"Cloning {url} into {DIR}...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', url, DIR],  # --depth 1 for faster clones
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print("Repository cloned successfully")
            return True
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"Clone failed: {error_msg}")
            
            # If it's a permission error, try alternative approach
            if "access is denied" in error_msg.lower() or "permission denied" in error_msg.lower():
                print("Permission error detected, trying alternative clone method...")
                return clone_with_alternative_method(url)
            else:
                raise Exception(f"Git clone failed: {error_msg}")
                
    except subprocess.TimeoutExpired:
        print("Clone timed out after 600 seconds")
        raise
    except Exception as e:
        print(f"Clone failed: {e}")
        raise

def clone_with_alternative_method(url):
    """Alternative clone method using temp directory and move"""
    temp_dir = None
    try:
        # Clone to a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="git_clone_")
        print(f"Cloning to temporary directory: {temp_dir}")
        
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', url, temp_dir],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise Exception(f"Alternative clone failed: {error_msg}")
        
        # If clone succeeded, move the repository to the target location
        print(f"Moving repository from {temp_dir} to {DIR}")
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(DIR), exist_ok=True)
        
        # Remove existing directory if it exists
        if os.path.exists(DIR):
            clear_directory()
        
        # Move the directory (rename works on same filesystem)
        shutil.move(temp_dir, DIR)
        print("Repository moved successfully")
        return True
        
    except Exception as e:
        print(f"Alternative clone method failed: {e}")
        raise
    finally:
        # Clean up temp directory if it still exists
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except:
                pass

# Usage example
if __name__ == "__main__":
    repo_url = "https://github.com/langchain-ai/langgraph.git"  # Replace with actual URL
    try:
        clone_url(repo_url)
        print("Cloning completed successfully!")
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)