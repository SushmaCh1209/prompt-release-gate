import os
import time
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schema import NoteResult

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_prompt(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def process_note(note, prompt):
    for attempt in range(1, 7):
        try:
            response = client.models.generate_content(
                model=prompt["model"],
                contents=note,
                config=types.GenerateContentConfig(
                    system_instruction=prompt["system_prompt"],
                    response_mime_type="application/json",
                ),
            )
            return NoteResult.model_validate_json(response.text)
        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)[:150]}")
            if "429" in str(e):
                print("Daily quota used up. Stopping.")
                return None
            time.sleep(10 * attempt)
    return None