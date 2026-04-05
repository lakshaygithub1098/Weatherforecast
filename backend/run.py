"""
Main entry point for FastAPI application
Run with: python -m uvicorn app.main:app --reload
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("[DEBUG] Starting app import...")
    # Import the app
    from app.main import app
    print("[DEBUG] App imported successfully")
    
    print("[DEBUG] Running main block...")
    import uvicorn
    from app.config import settings
    
    print(f"[DEBUG] Settings loaded: host={settings.host}, port={settings.port}")
    print(f"[DEBUG] About to run uvicorn...")
    
    try:
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=False,  # Disable reload to avoid subprocess issues
            workers=1
        )
    except Exception as uvicorn_error:
        print(f"[ERROR] Uvicorn error: {uvicorn_error}")
        import traceback
        traceback.print_exc()
        raise
        
except Exception as e:
    print(f"[ERROR] Startup failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
