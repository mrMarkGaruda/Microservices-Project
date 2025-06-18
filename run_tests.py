#!/usr/bin/env python3
"""
Test runner script with proper environment setup
"""
import os
import sys
import subprocess

# Set required environment variables for testing
test_env = {
    'DATABASE_URL': 'sqlite:///:memory:',
    'BILLING_DATABASE_URL': 'sqlite:///:memory:',
    'STATS_DATABASE_URL': 'sqlite:///:memory:',
    'FIT_API_KEY': 'test-api-key',
    'BOOTSTRAP_KEY': 'bootstrap-secret-key',
    'RABBITMQ_HOST': 'localhost',
    'RABBITMQ_PORT': '5672',
    'RABBITMQ_USER': 'guest',
    'RABBITMQ_PASS': 'guest',
    'FLASK_ENV': 'testing',
    'LOG_LEVEL': 'ERROR'
}

def main():
    # Update environment
    env = os.environ.copy()
    env.update(test_env)
    
    # Default pytest arguments
    default_args = [
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--strict-markers'
    ]
    
    # Combine with user arguments
    pytest_args = [sys.executable, '-m', 'pytest'] + default_args + sys.argv[1:]
    
    print(f"Running tests with environment variables: {', '.join(test_env.keys())}")
    print(f"Command: {' '.join(pytest_args)}")
    
    try:
        result = subprocess.run(pytest_args, env=env, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
