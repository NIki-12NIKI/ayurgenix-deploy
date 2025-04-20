# model.py

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd
import os

# Optional: Free GPU memory
torch.cuda.empty_cache()

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "AyurGenixAI_Dataset.csv")

# Load dataset once
data = pd.read_csv(DATASET_PATH)

# Lazy-load globals
_model = None
_tokenizer = None
_pipe = None

def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        model_path = os.getenv("MODEL_PATH", "sshleifer/tiny-gpt2")
        _model = AutoModelForCausalLM.from_pretrained(model_path)
        _tokenizer = AutoTokenizer.from_pretrained(model_path)
    return _model, _tokenizer

def get_pipeline():
    global _pipe
    if _pipe is None:
        model, tokenizer = get_model_and_tokenizer()
        _pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer
        )
    return _pipe

def retrieve_relevant_data(user_input):
    relevant_rows = data[data["Symptoms"].str.contains(user_input, case=False, na=False)]
    if relevant_rows.empty:
        return "No match found in dataset. Proceeding with Ayurvedic knowledge."
    return "\n".join(
        f"Symptom: {row['Symptoms']}, Disease: {row['Disease']}, Remedies: {row['Herbal/Alternative Remedies']}"
        for _, row in relevant_rows.iterrows()
    )

def generate_ayurvedic_response(user_input):
    filtered_context = retrieve_relevant_data(user_input)

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

1. Disease: """

    pipe = get_pipeline()
    tokenizer = get_model_and_tokenizer()[1]
    
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

    full_response = response[0]["generated_text"]
    cleaned_response = full_response.replace(input_prompt, "").strip()
    if "###" in cleaned_response:
        cleaned_response = cleaned_response.split("###")[0].strip()
    return cleaned_response
