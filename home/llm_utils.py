from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
from transformers import BitsAndBytesConfig

# Free GPU Memory Before Running
torch.cuda.empty_cache()

# Path to the model
MODEL_PATH = "C:\\codes\\llama1B\\"
DATASET_PATH = "C:\\codes\\llama1B\\AyurGenixAI_Dataset.csv"

# Load dataset
data = pd.read_csv(DATASET_PATH)

# Configure 8-bit quantization
bnb_config = BitsAndBytesConfig(load_in_8bit=True)

# Load model and tokenizer once
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto",
    quantization_config=bnb_config
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# Initialize pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

def retrieve_relevant_data(user_input, data):
    """Filter dataset for matching symptoms."""
    relevant_rows = data[data["Symptoms"].str.contains(user_input, case=False, na=False)]
   
    if relevant_rows.empty:
        return "No match found in dataset. Proceeding with Ayurvedic knowledge."

    return "\n".join(
        f"Symptom: {row['Symptoms']}, Disease: {row['Disease']}, Remedies: {row['Herbal/Alternative Remedies']}"
        for _, row in relevant_rows.iterrows()
    )

def generate_ayurvedic_response(user_input):
    """Generate an Ayurvedic health report using LLaMA."""
    filtered_context = retrieve_relevant_data(user_input, data)

    # Improved prompt structure
    input_prompt = f"""### Task Description:
You are an experienced Ayurvedic practitioner analyzing symptoms to create a health report. Use the following context and strictly follow the output format:

### Context:
{filtered_context}

### Output Format:
1. Disease: [Condition name]
2. Hindi Name: [Romanized Hindi]
3. Marathi Name: [Romanized Marathi]
4. Diagnosis & Tests: [Tests]
5. Duration of Treatment: [Timeframe]
6. Risk Factors: [Factors]
7. Environmental Factors: [Influences]
8. Herbal/Alternative Remedies: [Remedies]
9. Ayurvedic Herbs: [Herbs]
10. Formulation: [Formulation]
11. Diet and Lifestyle: [Recommendations]
12. Yoga & Physical Therapy: [Suggestions]
13. Medical Intervention: [When needed]
14. Prevention: [Measures]
15. Prognosis: [Outlook]
16. Complications: [Risks]
17. Patient Recommendations: [Actionable steps]

### Ayurvedic Principles:
- Use simple language
- Root recommendations in Ayurveda
- Be culturally appropriate

### Response:
Based on the symptoms "{user_input}", here is the Ayurvedic health report:

1. Disease: """  # The model will continue from here

    # Generate response with controlled length
    response = pipe(
        input_prompt,
        max_new_tokens=1000,
        temperature=0.7,
        top_k=50,
        do_sample=True,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    # Extract and clean the response
    full_response = response[0]["generated_text"]
    
    # Remove the input prompt from the response
    cleaned_response = full_response.replace(input_prompt, "").strip()
    
    # Further clean if needed (remove any trailing instructions)
    if "###" in cleaned_response:
        cleaned_response = cleaned_response.split("###")[0].strip()
    
    return cleaned_response