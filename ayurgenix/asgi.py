# ayurgenix/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayurgenix.settings')
django.setup()

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

# Initialize FastAPI
fastapi_app = FastAPI()

# Optional: Add routes, middleware to FastAPI
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Django ASGI app properly
# Option 1: Use the Django ASGI app directly
application = django_asgi_app

# Option 2: If you need both FastAPI and Django, use this approach instead:
# from fastapi.middleware.asgi import ASGIMiddleware
# fastapi_app.mount("/", ASGIMiddleware(django_asgi_app))
# application = fastapi_app
