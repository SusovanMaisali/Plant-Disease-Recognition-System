import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = input("Enter your GEMINI_API_KEY: ").strip()

if api_key:
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        print(m.name)
else:
    print("API Key not provided. Please set GEMINI_API_KEY environment variable.")