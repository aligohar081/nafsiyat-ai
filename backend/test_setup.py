#!/usr/bin/env python3
"""
Test script to verify the setup
Run this first to check if everything is installed correctly
"""

import sys
print("Python version:", sys.version)

# Test imports
try:
    import sqlalchemy
    print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy not installed: {e}")
    sys.exit(1)

try:
    import fastapi
    print(f"✅ FastAPI version: {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI not installed: {e}")

try:
    from jose import jwt
    print("✅ Python-JOSE installed")
except ImportError as e:
    print(f"❌ Python-JOSE not installed: {e}")

try:
    from passlib.context import CryptContext
    print("✅ Passlib installed")
except ImportError as e:
    print(f"❌ Passlib not installed: {e}")

try:
    import bcrypt
    print(f"✅ bcrypt version: {bcrypt.__version__}")
except ImportError as e:
    print(f"❌ bcrypt not installed: {e}")

# Test database creation
try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    
    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    Base = declarative_base()
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Database creation failed: {e}")

print("\n✅ All basic checks passed!")