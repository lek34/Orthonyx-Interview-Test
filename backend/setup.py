#!/usr/bin/env python3
"""
Setup script for Medical Symptom Checker API
This script helps with initial project setup and database initialization.
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    return True

def install_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def setup_environment_file():
    """Create .env file from template"""
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            if run_command("copy env.example .env", "Creating .env file"):
                print("📝 Please edit the .env file with your configuration")
                return True
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        # Try to import and test database connection
        from app.config import settings
        
        print("🔄 Testing database connection...")
        
        # Try to connect to MySQL
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        if connection.is_connected():
            print("✅ Database connection successful")
            connection.close()
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except ImportError:
        print("⚠️  Database dependencies not installed yet")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure MySQL is running and credentials are correct in .env")
        return False

def create_database_schema():
    """Create database schema"""
    try:
        from app.config import settings
        
        print("🔄 Creating database schema...")
        
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Read and execute schema file
        schema_file = Path("app/schema.sql")
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = schema_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            connection.commit()
            print("✅ Database schema created successfully")
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ Schema file not found: app/schema.sql")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Medical Symptom Checker API Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("❌ Failed to setup environment file")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("❌ Database connection failed")
        print("💡 Please check your MySQL setup and .env configuration")
        sys.exit(1)
    
    # Create database schema
    if not create_database_schema():
        print("❌ Failed to create database schema")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your OpenAI API key and other settings")
    print("2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\Activate.ps1")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   uvicorn app.main:app --reload")
    print("4. Visit http://127.0.0.1:8000/docs for API documentation")
    print("5. Run tests:")
    print("   pytest tests/test_e2e.py -v")

if __name__ == "__main__":
    main() 