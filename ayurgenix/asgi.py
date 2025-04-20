import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurgenix.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Create combined application
application = FastAPI(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
)
application = FastAPI()
# Mount applications
application.mount("/", WSGIMiddleware(django_app))

# Import and mount FastAPI app (ensure this path is correct)
try:
    from FastAPI_llama.app.main import app as fastapi_app
    application.mount("/api/llama", fastapi_app)
except ImportError as e:
    import logging
    logging.warning(f"Failed to import FastAPI app: {e}")