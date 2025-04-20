# ayurgenix/asgi.py

import os
import django
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

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

# Mount Django inside FastAPI
fastapi_app.mount("/", WSGIMiddleware(django_asgi_app))

# Final app to serve
application = fastapi_app
