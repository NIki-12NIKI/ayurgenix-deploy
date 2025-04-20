# Import key components to make them available when importing the package
from .main import app  # Makes 'app' available when someone imports FastAPI_llama.app
from .model import generate_ayurvedic_response  # Exposes the main function

# Optional: Define what gets imported with 'from FastAPI_llama.app import *'
__all__ = ['app', 'generate_ayurvedic_response']