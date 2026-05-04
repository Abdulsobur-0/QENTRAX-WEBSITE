#!/usr/bin/env python3
"""
Run this once to initialize the database, then start the server.
"""
import subprocess, sys, os

def run():
    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--quiet'])
    
    # Init DB
    from app import init_db
    init_db()
    print("✓ Database initialized")
    
    # Start server
    print("✓ Starting Qentrax Africa server on http://0.0.0.0:5000")
    os.execlp(sys.executable, sys.executable, 'app.py')

if __name__ == '__main__':
    run()
