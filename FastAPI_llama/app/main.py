from fastapi import FastAPI, Request
from pydantic import BaseModel
from .model import generate_ayurvedic_response  # Now uses correct relative import

app = FastAPI()

class InputData(BaseModel):
    user_input: str

@app.post("/generate")
async def generate(input_data: InputData):
    try:
        response = generate_ayurvedic_response(input_data.user_input)
        return {"response": response}
    except Exception as e:
        # Print full error to console and return it in the response
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
