import os
import sys
from app import app

def check_environment():
    required_vars = ['GOOGLE_API_KEY', 'EMAIL_ADDRESS', 'EMAIL_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n Check and update your .env file")
        return False
    
    return True

def main():
    if not check_environment():
        sys.exit(1)
    print("Starting Flask app...")

    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n Application stopped by user")
    except Exception as e:
        print(f"\n Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
