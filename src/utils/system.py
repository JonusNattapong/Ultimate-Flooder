import os
import ctypes
import random
import time
import glob
import tempfile

def load_file_lines(filename, default=None):
    """Load lines from a file, return default if file doesn't exist"""
    if not os.path.exists(filename):
        return default or []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return default or []

def check_root_privileges():
    """Check if running with root privileges"""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows doesn't have geteuid
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def randomize_timing(base_delay=0.1, max_delay=2.0):
    """Add random delays to prevent timing analysis"""
    delay = random.uniform(base_delay, max_delay)
    time.sleep(delay)

def cleanup_temp_files():
    """Clean up temporary files and logs that might contain traces"""
    try:
        temp_dir = tempfile.gettempdir()
        temp_files = glob.glob(os.path.join(temp_dir, "ip-hunter-*"))
        
        for file_path in temp_files:
            try:
                os.remove(file_path)
            except:
                pass
        
        return True, f"Cleaned {len(temp_files)} temp files"
    except Exception as e:
        return False, f"Cleanup failed: {str(e)}"

def stealth_mode_init():
    """Initialize stealth mode with anti-trace measures"""
    cleanup_success, cleanup_msg = cleanup_temp_files()
    return cleanup_success, cleanup_msg
