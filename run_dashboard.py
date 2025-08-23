#!/usr/bin/env python3
"""
Dashboard Launcher Script
Simple script to launch the Streamlit dashboard
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'psycopg2',
        'sqlalchemy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "dashboard_requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    print("🚀 Stock Market Dashboard Launcher")
    print("=" * 40)
    
    # Check if requirements file exists
    if not os.path.exists("dashboard_requirements.txt"):
        print("❌ dashboard_requirements.txt not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Installing dependencies...")
        
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("pip install -r dashboard_requirements.txt")
            return
    
    print("✅ All dependencies are available!")
    print("\n🌐 Starting Streamlit Dashboard...")
    print("📊 Dashboard will open in your browser at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("\n" + "=" * 40)
    
    try:
        # Launch Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "stock_dashboard.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    main()
