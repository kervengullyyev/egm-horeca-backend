#!/usr/bin/env python3
"""
Database Management Script for EGM Horeca
Provides easy commands for common database operations
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_alembic_installed():
    """Check if alembic is available"""
    try:
        subprocess.run(["alembic", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    if len(sys.argv) < 2:
        print("🔧 EGM Horeca Database Management")
        print("")
        print("Usage: python manage_db.py <command>")
        print("")
        print("Commands:")
        print("  init      - Initialize database with Alembic")
        print("  migrate   - Run all pending migrations")
        print("  upgrade   - Upgrade to latest version")
        print("  downgrade - Downgrade one version")
        print("  current   - Show current database version")
        print("  history   - Show migration history")
        print("  create    - Create a new migration")
        print("  reset     - Reset database (drop all tables)")
        print("")
        return

    command = sys.argv[1]
    
    if not check_alembic_installed():
        print("❌ Alembic is not installed. Please install it first:")
        print("   pip install alembic")
        return

    if command == "init":
        print("🚀 Initializing database...")
        if run_command("alembic upgrade head", "Running initial migration"):
            print("✅ Database initialized successfully!")
            print("🌱 You can now seed the database with: python manage_db.py seed")
    
    elif command == "migrate":
        print("🔄 Running database migrations...")
        run_command("alembic upgrade head", "Running migrations")
    
    elif command == "upgrade":
        print("⬆️  Upgrading database...")
        run_command("alembic upgrade head", "Upgrading database")
    
    elif command == "downgrade":
        print("⬇️  Downgrading database...")
        run_command("alembic downgrade -1", "Downgrading database")
    
    elif command == "current":
        print("📊 Current database version:")
        run_command("alembic current", "Checking current version")
    
    elif command == "history":
        print("📜 Migration history:")
        run_command("alembic history", "Showing migration history")
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide a migration message:")
            print("   python manage_db.py create 'Add new table'")
            return
        message = sys.argv[2]
        print(f"📝 Creating migration: {message}")
        run_command(f'alembic revision --autogenerate -m "{message}"', "Creating migration")
    
    elif command == "reset":
        print("⚠️  WARNING: This will drop all tables and data!")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() == 'yes':
            print("🗑️  Resetting database...")
            if run_command("alembic downgrade base", "Dropping all tables"):
                print("✅ Database reset successfully!")
                print("🌱 You can now reinitialize with: python manage_db.py init")
        else:
            print("❌ Database reset cancelled")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage_db.py' to see available commands")

if __name__ == "__main__":
    main()
