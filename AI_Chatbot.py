import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv()

api_key = os.getenv("MY_OPEN_AI_API_KEY")

client = OpenAI(api_key=api_key)
client1 = genai.Client()

respone = client1.models.generate_content(
    model="gemini-3.6-flash",
    contents='Say hello!'
)

print(respone.text)