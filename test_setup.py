#!/usr/bin/env python3
"""Test script to verify the PowerPoint Search Platform setup."""

import sys
import importlib

def test_imports():
    """Test if all required Python packages are installed."""
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pptx': 'python-pptx',
        'sqlalchemy': 'SQLAlchemy',
        'PIL': 'Pillow'
    }
    
    print("🔍 Testing Python package imports...\n")
    
    all_good = True
    for package, name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {name:<20} - OK")
        except ImportError:
            print(f"❌ {name:<20} - NOT FOUND")
            all_good = False
    
    return all_good

def test_directory_structure():
    """Test if the directory structure is correct."""
    import os
    
    print("\n🔍 Testing directory structure...\n")
    
    required_dirs = [
        'backend',
        'frontend',
        'frontend/src',
        'frontend/public'
    ]
    
    required_files = [
        'backend/main.py',
        'backend/database.py',
        'backend/ppt_parser.py',
        'frontend/package.json',
        'frontend/src/App.js',
        'requirements.txt'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ Directory: {dir_path:<30} - OK")
        else:
            print(f"❌ Directory: {dir_path:<30} - NOT FOUND")
            all_good = False
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✅ File: {file_path:<35} - OK")
        else:
            print(f"❌ File: {file_path:<35} - NOT FOUND")
            all_good = False
    
    return all_good

def test_database():
    """Test database initialization."""
    print("\n🔍 Testing database setup...\n")
    
    try:
        from backend.database import init_db, Base, Presentation, Slide
        print("✅ Database models imported successfully")
        
        # Try to initialize database
        init_db()
        print("✅ Database initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("PowerPoint Search Platform - Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Python Packages", test_imports()))
    
    # Test directory structure
    results.append(("Directory Structure", test_directory_structure()))
    
    # Test database
    results.append(("Database Setup", test_database()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print()
        print("Next steps:")
        print("  1. Run: ./run_backend.sh   (or python backend/main.py)")
        print("  2. Run: ./run_frontend.sh  (or cd frontend && npm start)")
        print("  3. Open: http://localhost:3000")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        print()
        print("Try running:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

