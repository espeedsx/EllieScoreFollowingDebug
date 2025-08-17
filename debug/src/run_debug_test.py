#!/usr/bin/env python3
"""
Test runner for score following debug system.
Executes Serpent tests with timeout and captures debug logs.
"""

import os
import sys
import argparse
import subprocess
import signal
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from config import (
    SERPENT_SRC_DIR, LOGS_DIR, SERPENT_EXECUTABLE, TEST_SCRIPT, TEST_TIMEOUT,
    get_log_filename
)
from utils import setup_logging, get_timestamp, format_duration, log_with_line
import logging


logger = setup_logging(__name__)


class TestExecutor:
    """Handles execution of Serpent tests with timeout and logging."""
    
    def __init__(self, test_case_id: int, enable_debug: bool = True):
        self.test_case_id = test_case_id
        self.enable_debug = enable_debug
        self.timestamp = get_timestamp()
        self.log_file = LOGS_DIR / get_log_filename(test_case_id, self.timestamp)
        self.process = None
        
    def run_test(self) -> Dict[str, Any]:
        """
        Execute the test with timeout and capture results.
        
        Returns:
            Dict containing execution results and metadata
        """
        logger.info(f"Starting test case {self.test_case_id}")
        
        # Prepare command
        cmd = self._build_command()
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Prepare environment
        env = self._prepare_environment()
        
        # Execute with timeout
        start_time = datetime.now()
        result = self._execute_with_timeout(cmd, env)
        end_time = datetime.now()
        
        # Compile results
        execution_result = {
            'test_case_id': self.test_case_id,
            'timestamp': self.timestamp,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'command': ' '.join(cmd),
            'log_file': str(self.log_file),
            'success': result['returncode'] == 0 or result['timeout'],
            'timeout': result['timeout'],
            'returncode': result['returncode'],
            'stdout_lines': len(result['stdout'].splitlines()) if result['stdout'] else 0,
            'stderr_lines': len(result['stderr'].splitlines()) if result['stderr'] else 0,
            'debug_enabled': self.enable_debug
        }
        
        # Save execution logs
        self._save_execution_logs(result, execution_result)
        
        logger.info(f"Test completed in {format_duration(execution_result['duration_seconds'])}")
        
        return execution_result
    
    def _build_command(self) -> list:
        """Build the command to execute."""
        cmd = [
            SERPENT_EXECUTABLE,
            TEST_SCRIPT,
            str(self.test_case_id),
            str(self.test_case_id)  # run single test
        ]
        
        if self.enable_debug:
            cmd.extend(['-d'])
        
        return cmd
    
    def _prepare_environment(self) -> dict:
        """Prepare environment variables for execution."""
        env = os.environ.copy()
        
        if self.enable_debug:
            # Set debug file to a separate file that Serpent will write to
            serpent_debug_file = str(self.log_file).replace('.log', '_serpent.log')
            env['DEBUG_LOG_FILE'] = serpent_debug_file
            logger.debug(f"Set DEBUG_LOG_FILE to: {serpent_debug_file}")
        
        return env
    
    def _execute_with_timeout(self, cmd: list, env: dict) -> Dict[str, Any]:
        """Execute command with timeout handling."""
        try:
            # Change to source directory
            original_cwd = os.getcwd()
            os.chdir(SERPENT_SRC_DIR)
            
            logger.info(f"Working directory: {SERPENT_SRC_DIR}")
            logger.info(f"Timeout: {TEST_TIMEOUT} seconds")
            log_with_line(logger, logging.INFO, f"Executing command: {' '.join(cmd)}", context=f"working_dir={SERPENT_SRC_DIR}")
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait with timeout
            try:
                stdout, stderr = self.process.communicate(timeout=TEST_TIMEOUT)
                timeout = False
                returncode = self.process.returncode
                
            except subprocess.TimeoutExpired:
                logger.info(f"Test timed out after {TEST_TIMEOUT} seconds, terminating...")
                
                # Terminate process
                if os.name == 'nt':
                    # Windows
                    self.process.terminate()
                else:
                    # Unix-like
                    self.process.terminate()
                
                # Give it a moment to terminate gracefully
                time.sleep(1)
                
                # Force kill if still running
                if self.process.poll() is None:
                    if os.name == 'nt':
                        self.process.kill()
                    else:
                        os.kill(self.process.pid, signal.SIGKILL)
                
                # Get partial output
                try:
                    stdout, stderr = self.process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", ""
                
                timeout = True
                returncode = -1
                
            return {
                'stdout': stdout,
                'stderr': stderr,
                'returncode': returncode,
                'timeout': timeout
            }
            
        finally:
            # Restore working directory
            os.chdir(original_cwd)
            self.process = None
    
    def _save_execution_logs(self, result: Dict[str, Any], metadata: Dict[str, Any]):
        """Save execution logs and metadata."""
        # Create log file with metadata header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("# Score Following Debug Log\n")
            f.write(f"# Test Case: {self.test_case_id}\n")
            f.write(f"# Timestamp: {self.timestamp}\n")
            f.write(f"# Command: {metadata['command']}\n")
            f.write(f"# Working Dir: {SERPENT_SRC_DIR}\n")
            f.write(f"# Duration: {format_duration(metadata['duration_seconds'])}\n")
            f.write(f"# Timeout: {result['timeout']}\n")
            f.write(f"# Return Code: {result['returncode']}\n")
            f.write("#" + "="*50 + "\n\n")
            
            # Add test start marker
            f.write(f"TEST_START|test_case:{self.test_case_id}|score_file:unknown|performance_file:unknown\n")
            
            # Check if there's a separate debug file from Serpent
            debug_file_env = str(self.log_file)
            serpent_debug_file = debug_file_env.replace('.log', '_serpent.log')
            
            # First, try to read the Serpent debug file if it exists
            serpent_debug_content = ""
            if Path(serpent_debug_file).exists():
                try:
                    with open(serpent_debug_file, 'r', encoding='utf-8') as debug_f:
                        serpent_debug_content = debug_f.read()
                    logger.info(f"Found Serpent debug file: {serpent_debug_file}")
                except Exception as e:
                    logger.warning(f"Could not read Serpent debug file: {e}")
            
            # Write Serpent debug output first (if any)
            if serpent_debug_content:
                f.write("# SERPENT DEBUG OUTPUT:\n")
                f.write(serpent_debug_content)
                f.write("\n")
            
            # Write stdout (console output)
            if result['stdout']:
                f.write("# STDOUT:\n")
                f.write(result['stdout'])
                f.write("\n")
            
            # Write stderr if any
            if result['stderr']:
                f.write("# STDERR:\n")
                f.write(result['stderr'])
                f.write("\n")
            
            # Add test end marker
            f.write(f"TEST_END|test_case:{self.test_case_id}|matches_found:unknown|total_notes:unknown\n")
        
        logger.info(f"Debug log saved to: {self.log_file}")
        
        # Clean up the separate Serpent debug file if it exists
        if Path(serpent_debug_file).exists():
            try:
                Path(serpent_debug_file).unlink()
                logger.debug(f"Cleaned up Serpent debug file: {serpent_debug_file}")
            except Exception as e:
                logger.warning(f"Could not clean up Serpent debug file: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.process and self.process.poll() is None:
            logger.warning("Cleaning up running process")
            self.process.terminate()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run score following test with debug logging")
    parser.add_argument("test_case", type=int, help="Test case ID to run")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug logging")
    parser.add_argument("--timeout", type=int, default=TEST_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update timeout if specified  
    import config
    if args.timeout != TEST_TIMEOUT:
        config.TEST_TIMEOUT = args.timeout
    
    # Create executor
    executor = TestExecutor(
        test_case_id=args.test_case,
        enable_debug=not args.no_debug
    )
    
    try:
        # Run test
        result = executor.run_test()
        
        # Print summary
        print(f"\nTest Execution Summary:")
        print(f"Test Case: {result['test_case_id']}")
        print(f"Duration: {format_duration(result['duration_seconds'])}")
        print(f"Success: {result['success']}")
        print(f"Timeout: {result['timeout']}")
        print(f"Log File: {result['log_file']}")
        
        if not result['success'] and not result['timeout']:
            print(f"Return Code: {result['returncode']}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        executor.cleanup()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running test: {e}")
        executor.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()