import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurgenix.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Create FastAPI application
application = FastAPI(
    middleware=[
        # Add CORSMiddleware to handle CORS
        CORSMiddleware(
            allow_origins=["*"],  # Allows all origins, adjust based on your use case
            allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
            allow_headers=["*"],  # Allows all headers
        )
    ]
)

# Mount the Django app under the root path ("/")
application.mount("/", WSGIMiddleware(django_app))

# Import and mount FastAPI app (ensure this path is correct)
try:
    from FastAPI_llama.app.main import app as fastapi_app
    application.mount("/api/llama", fastapi_app)
except ImportError as e:
    import logging
    logging.warning(f"Failed to import FastAPI app: {e}")
