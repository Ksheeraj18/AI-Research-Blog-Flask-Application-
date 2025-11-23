#!/usr/bin/env python3
import sys
import subprocess

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--no-cache-dir"])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

if __name__ == "__main__":
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    
    packages = ["flask", "flask-sqlalchemy", "requests", "python-dotenv", "apscheduler"]
    
    for package in packages:
        print(f"\nInstalling {package}...")
        install_package(package)
    
    print("\n" + "="*50)
    print("Testing imports...")
    
    modules = ["flask", "flask_sqlalchemy", "requests", "dotenv", "apscheduler"]
    
    for module in modules:
        test_import(module)
