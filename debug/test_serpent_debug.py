#!/usr/bin/env python3
"""
Test script to check if Serpent debug logging is working.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_serpent_debug():
    """Test if Serpent debug logging works."""
    
    # Change to source directory
    src_dir = Path(__file__).parent.parent / "src"
    os.chdir(src_dir)
    
    # Set up debug environment
    debug_file = Path("test_debug_output.log")
    env = os.environ.copy()
    env['DEBUG_LOG_FILE'] = str(debug_file)
    
    print(f"Testing Serpent debug logging...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Debug file: {debug_file}")
    
    # Run a simple test
    cmd = ["serpent64", "run_bench", "1", "1", "-d"]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Wait with timeout
        try:
            stdout, stderr = process.communicate(timeout=15)
            print(f"Process completed normally")
        except subprocess.TimeoutExpired:
            print(f"Process timed out (expected)")
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = "", ""
        
        print(f"Return code: {process.returncode}")
        print(f"Stdout length: {len(stdout) if stdout else 0}")
        print(f"Stderr length: {len(stderr) if stderr else 0}")
        
        # Check if debug file was created
        if debug_file.exists():
            size = debug_file.stat().st_size
            print(f"[OK] Debug file created: {debug_file} ({size} bytes)")
            
            # Show first few lines
            with open(debug_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
            print(f"First few lines:")
            for i, line in enumerate(lines, 1):
                print(f"  {i}: {line.rstrip()}")
            
            # Clean up
            debug_file.unlink()
        else:
            print(f"[FAIL] Debug file not created")
            
        # Check stdout for debug messages
        if "LOG_DEBUG enabled" in stdout:
            print(f"[OK] LOG_DEBUG flag recognized")
        else:
            print(f"[FAIL] LOG_DEBUG flag not found in output")
            
        # Show some stdout
        if stdout:
            print(f"Stdout sample:")
            for line in stdout.split('\n')[:5]:
                if line.strip():
                    print(f"  {line}")
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_serpent_debug()
    exit(0 if success else 1)