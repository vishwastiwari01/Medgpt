import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Key length: {len(api_key) if api_key else 0}")
print(f"Key starts with: {api_key[:10] if api_key else 'None'}")
print(f"Key ends with: {api_key[-10:] if api_key else 'None'}")
print(f"Has spaces: {' ' in api_key if api_key else 'N/A'}")
print(f"Has quotes: {'\"' in api_key" }")