import os
from groq import Groq

key = os.getenv("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")
model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not key:
    print("❌ GROQ_API_KEY missing")
    raise SystemExit

print(f"🔑 Using key prefix: {key[:10]}...")
print(f"🧠 Model: {model}")

client = Groq(api_key=key)

try:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say OK if you can read this."},
        ],
        max_tokens=10,
    )
    print("✅ Response:", resp.choices[0].message.content.strip())
except Exception as e:
    print("❌ Error:", e)
