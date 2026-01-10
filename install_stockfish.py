# Script to download and install Stockfish automatically
import os
import platform
import urllib.request
import zipfile
import shutil

def install_stockfish():
    """Download and install Stockfish for the current platform"""
    system = platform.system()
    
    print("Installing Stockfish chess engine...")
    
    if system == 'Windows':
        # Try multiple download sources
        urls = [
            "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip",
            "https://stockfishchess.org/files/stockfish_15_win_x64_avx2.zip"
        ]
        filename = "stockfish.zip"
        
        # Try each URL
        for url_idx, url in enumerate(urls):
            try:
                print(f"\nTrying download source {url_idx + 1}...")
                print(f"Downloading from: {url}")
                urllib.request.urlretrieve(url, filename)
                
                print("Extracting...")
                extract_dir = 'stockfish_temp'
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Find the executable (check all subdirectories)
                stockfish_path = None
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file.lower() == 'stockfish.exe' or file == 'stockfish':
                            stockfish_path = os.path.join(root, file)
                            break
                    if stockfish_path:
                        break
                
                if stockfish_path and os.path.exists(stockfish_path):
                    # Copy to current directory
                    target_path = 'stockfish.exe'
                    shutil.copy(stockfish_path, target_path)
                    print(f"\n✓ Stockfish installed successfully at: {os.path.abspath(target_path)}")
                    # Clean up
                    shutil.rmtree(extract_dir, ignore_errors=True)
                    if os.path.exists(filename):
                        os.remove(filename)
                    return os.path.abspath(target_path)
                else:
                    print("Warning: Could not find stockfish.exe in extracted files")
                    print("Listing extracted files:")
                    for root, dirs, files in os.walk(extract_dir):
                        level = root.replace(extract_dir, '').count(os.sep)
                        indent = ' ' * 2 * level
                        print(f"{indent}{os.path.basename(root)}/")
                        subindent = ' ' * 2 * (level + 1)
                        for file in files:
                            print(f"{subindent}{file}")
                    shutil.rmtree(extract_dir, ignore_errors=True)
                    if os.path.exists(filename):
                        os.remove(filename)
                    # Try next URL
                    continue
                    
            except Exception as e:
                print(f"Error with this source: {e}")
                if os.path.exists(filename):
                    os.remove(filename)
                if os.path.exists('stockfish_temp'):
                    shutil.rmtree('stockfish_temp', ignore_errors=True)
                continue
        
        # If we get here, all URLs failed
        print("\n✗ All download sources failed.")
        print("\nPlease download Stockfish manually:")
        print("1. Go to: https://stockfishchess.org/download/")
        print("2. Download the Windows version")
        print("3. Extract stockfish.exe to this folder")
        return None
    
    elif system == 'Linux':
        print("For Linux, please install Stockfish using your package manager:")
        print("  sudo apt-get install stockfish")
        print("  or")
        print("  sudo yum install stockfish")
        return None
    
    elif system == 'Darwin':  # macOS
        print("For macOS, please install Stockfish using Homebrew:")
        print("  brew install stockfish")
        return None
    
    return None

if __name__ == '__main__':
    result = install_stockfish()
    if result:
        print(f"\n✓ Installation complete! Stockfish is ready at: {result}")
    else:
        print("\n✗ Installation failed. Please install manually (see instructions above).")
