import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Export the raw FastAPI app
# Vercel's Python runtime will handle ASGI automatically
app = app
