import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurgenix.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Create FastAPI application
application = FastAPI()

# Add CORS middleware
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Django app at root
application.mount("/", WSGIMiddleware(django_app))

# Mount FastAPI LLaMA app at /api/llama
try:
    from FastAPI_llama.app.main import app as fastapi_app
    application.mount("/api/llama", fastapi_app)
except ImportError as e:
    import logging
    logging.warning(f"Failed to import FastAPI app: {e}")
