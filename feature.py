import os
import time
import yaml
from dotenv import load_dotenv
from schema import NoteResult

load_dotenv()


def load_prompt(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_model(note, prompt):
    """Sends one note to the model and returns its raw text answer."""
    if prompt.get("provider", "gemini") == "ollama":
        import ollama
        response = ollama.chat(
            model=prompt["model"],
            messages=[
                {"role": "system", "content": prompt["system_prompt"]},
                {"role": "user", "content": note},
            ],
            format=NoteResult.model_json_schema(),
            options={"temperature": 0},
        )
        return response["message"]["content"]

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=prompt["model"],
        contents=note,
        config=types.GenerateContentConfig(
            system_instruction=prompt["system_prompt"],
            response_mime_type="application/json",
        ),
    )
    return response.text


def process_note(note, prompt):
    for attempt in range(1, 4):
        try:
            return NoteResult.model_validate_json(call_model(note, prompt))
        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)[:150]}")
            if "429" in str(e):
                print("Quota used up. Stopping.")
                return None
            time.sleep(5 * attempt)
    return None