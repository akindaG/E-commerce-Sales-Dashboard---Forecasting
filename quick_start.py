#!/usr/bin/env python3
"""
Quick Start Script for E-commerce Analytics Dashboard
Guides users through setup and running the dashboard
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print welcome banner"""
    print("\033[95m" + "=" * 60 + "\033[0m")
    print("\033[96m🛒  E-commerce Analytics Dashboard - Quick Start\033[0m")
    print("\033[95m" + "=" * 60 + "\033[0m")
    print()

def check_dependencies():
    """Check if required packages are installed"""
    print("\033[94m📦 Checking dependencies...\033[0m")
    
    required_packages = [
        'pandas', 'numpy', 'plotly', 'streamlit',
        'scikit-learn', 'statsmodels', 'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"\033[92m✅ {package}\033[0m")
        except ImportError:
            print(f"\033[91m❌ {package} - missing\033[0m")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n\033[93m⚠️  Missing packages: {', '.join(missing_packages)}\033[0m")
        print("\033[93mInstalling missing packages...\033[0m")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("\033[92m✅ Dependencies installed successfully!\033[0m")
        except subprocess.CalledProcessError:
            print("\033[91m❌ Failed to install dependencies. Please run:\033[0m")
            print("\033[93mpip install -r requirements.txt\033[0m")
            return False
    
    print("\033[92m✅ All dependencies are installed!\033[0m")
    return True

def check_data_files():
    """Check if data files exist"""
    print("\n\033[94m📁 Checking data files...\033[0m")
    data_dir = os.path.join('data')
    if not os.path.isdir(data_dir):
        print(f"\033[91m❌ Data directory '{data_dir}' not found. Creating it...\033[0m")
        os.makedirs(data_dir, exist_ok=True)

    real_data = os.path.join(data_dir, 'Online_Retail.xlsx')
    sample_data = os.path.join(data_dir, 'sample_online_retail.xlsx')

    if os.path.exists(real_data):
        print("\033[92m✅ Found UCI Online Retail Dataset\033[0m")
        return 'real'
    if os.path.exists(sample_data):
        print("\033[92m✅ Found sample data\033[0m")
        return 'sample'
    print("\033[91m❌ No data files found\033[0m")
    return None

def generate_sample_data():
    """Generate sample data if needed"""
    print("\n\033[94m🎲 Generating sample data...\033[0m")
    try:
        sys.path.append('src')
        if not os.path.exists(os.path.join('src', 'sample_data_generator.py')):
            print("\033[91m❌ sample_data_generator.py not found in src/\033[0m")
            return False
        from sample_data_generator import SampleDataGenerator
        generator = SampleDataGenerator()
        success = generator.save_sample_data()
        if success:
            print("\033[92m✅ Sample data generated successfully!\033[0m")
            return True
        else:
            print("\033[91m❌ Failed to generate sample data\033[0m")
            return False
    except Exception as e:
        print(f"\033[91m❌ Error generating sample data: {e}\033[0m")
        return False

def run_data_processing():
    """Run data processing"""
    print("\n\033[94m🔄 Running data processing...\033[0m")
    data_processing_path = os.path.join('src', 'data_processing.py')
    if not os.path.exists(data_processing_path):
        print(f"\033[91m❌ Data processing script not found: {data_processing_path}\033[0m")
        return False
    try:
        result = subprocess.run([
            sys.executable, data_processing_path
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print("\033[92m✅ Data processing completed!\033[0m")
            return True
        else:
            print(f"\033[91m❌ Data processing failed: {result.stderr}\033[0m")
            return False
    except Exception as e:
        print(f"\033[91m❌ Error running data processing: {e}\033[0m")
        return False

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("\n\033[96m🚀 Starting dashboard...\033[0m")
    print("\033[96m📊 Dashboard will open in your browser\033[0m")
    print("\033[93m🔄 Press Ctrl+C to stop the dashboard\033[0m")
    print()
    dashboard_path = os.path.join('dashboards', 'streamlit_app.py')
    if not os.path.exists(dashboard_path):
        print(f"\033[91m❌ Dashboard script not found: {dashboard_path}\033[0m")
        return
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', dashboard_path,
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
    except FileNotFoundError:
        print("\033[91m❌ Streamlit is not installed. Please run:\033[0m")
        print("\033[93mpip install streamlit\033[0m")
    except KeyboardInterrupt:
        print("\n\033[96m👋 Dashboard stopped. Thanks for using E-commerce Analytics!\033[0m")
    except Exception as e:
        print(f"\033[91m❌ Error starting dashboard: {e}\033[0m")

def main():
    """Main quick start function"""
    print_banner()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first:")
        print("pip install -r requirements.txt")
        return
    
    # Step 2: Check data files
    data_status = check_data_files()
    
    if data_status is None:
        print("\n\033[94m📊 No data files found. Options:\033[0m")
        print("\033[93m1. Download the UCI Online Retail Dataset\033[0m")
        print("   - Visit: \033[96mhttps://archive.ics.uci.edu/ml/datasets/online+retail\033[0m")
        print("   - Save as: \033[92mdata/Online_Retail.xlsx\033[0m")
        print()
        print("\033[93m2. Generate sample data (recommended for demo)\033[0m")
        print()
        choice = input("\033[96mChoose option (1 or 2): \033[0m").strip()
        print()
        if choice == '2':
            if not generate_sample_data():
                print("\033[91m❌ Failed to generate sample data\033[0m")
                return
        else:
            print("\033[93mPlease download the dataset and place it in the data/ folder\033[0m")
            return
    
    # Step 3: Run data processing
    if not run_data_processing():
        print("❌ Data processing failed")
        return
    
    # Step 4: Start dashboard
    print("\n\033[92m🎉 Setup completed successfully!\033[0m")
    print("\033[96m📊 Starting the dashboard...\033[0m")
    time.sleep(2)
    start_dashboard()

if __name__ == "__main__":
    main()
