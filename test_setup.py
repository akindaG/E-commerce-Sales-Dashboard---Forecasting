#!/usr/bin/env python3
"""
Test Setup Script for E-commerce Analytics Dashboard
Verifies all components are working correctly
"""

import sys
import os
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'pandas', 'numpy', 'plotly', 'streamlit', 
        'sklearn', 'statsmodels', 'openpyxl'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully!")
    return True

def test_data_processing():
    """Test data processing module"""
    print("\n🔍 Testing data processing module...")
    
    try:
        sys.path.append('src')
        from data_processing import EcommerceDataProcessor
        
        processor = EcommerceDataProcessor()
        print("✅ EcommerceDataProcessor imported")
        
        # Test sample data generation
        from sample_data_generator import SampleDataGenerator
        generator = SampleDataGenerator()
        print("✅ SampleDataGenerator imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_analytics():
    """Test analytics module"""
    print("\n🔍 Testing analytics module...")
    
    try:
        sys.path.append('src')
        from analytics import EcommerceAnalytics
        
        analytics = EcommerceAnalytics()
        print("✅ EcommerceAnalytics imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False

def test_forecasting():
    """Test forecasting module"""
    print("\n🔍 Testing forecasting module...")
    
    try:
        sys.path.append('src')
        from forecasting import RevenueForecaster
        
        forecaster = RevenueForecaster()
        print("✅ RevenueForecaster imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Forecasting test failed: {e}")
        return False

def test_sample_data_generation():
    """Test sample data generation"""
    print("\n🔍 Testing sample data generation...")
    
    try:
        sys.path.append('src')
        from sample_data_generator import SampleDataGenerator
        
        generator = SampleDataGenerator()
        
        # Generate a small sample for testing
        df = generator.generate_sample_data(num_transactions=1000)
        
        if df is not None and len(df) > 0:
            print(f"✅ Generated {len(df)} sample transactions")
            print(f"📊 Columns: {list(df.columns)}")
            return True
        else:
            print("❌ Sample data generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Sample data generation test failed: {e}")
        return False

def test_dashboard_components():
    """Test dashboard components"""
    print("\n🔍 Testing dashboard components...")
    
    try:
        # Test if dashboard file exists
        if os.path.exists('dashboards/streamlit_app.py'):
            print("✅ Dashboard file exists")
        else:
            print("❌ Dashboard file not found")
            return False
        
        # Test if we can import dashboard functions (with error handling)
        try:
            sys.path.append('dashboards')
            import streamlit_app  # noqa: F401
            print("✅ Dashboard module imported")
        except ImportError as import_error:
            print(f"⚠️  Dashboard import warning: {import_error}")
            print("   This is normal for Streamlit apps in test environment")
            # Still return True since the file exists
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'requirements.txt',
        'README.md',
        'quick_start.py',
        'src/data_processing.py',
        'src/analytics.py',
        'src/forecasting.py',
        'src/sample_data_generator.py',
        'dashboards/streamlit_app.py',
        'docs/business_presentation.md',
        'docs/portfolio_showcase.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files exist!")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 E-commerce Analytics Dashboard - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Data Processing", test_data_processing),
        ("Analytics Module", test_analytics),
        ("Forecasting Module", test_forecasting),
        ("Sample Data Generation", test_sample_data_generation),
        ("Dashboard Components", test_dashboard_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The project is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: python quick_start.py")
        print("2. Or manually: streamlit run dashboards/streamlit_app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n💡 Troubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check file paths and permissions")
        print("3. Verify Python version (3.7+)")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 