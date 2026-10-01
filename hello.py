import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for attempt in range(1, 6):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Say hello in one short sentence."
        )
        print(response.text)
        break
    except Exception as e:
        print(f"Attempt {attempt} failed: {str(e)[:120]}")
        time.sleep(5 * attempt)