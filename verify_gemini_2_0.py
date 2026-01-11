
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

try:
    print("Attempting to invoke ChatGoogleGenerativeAI with gemini-2.0-flash...")
    llm = ChatGoogleGenerativeAI(model="gemma-3-12b-it")
    response = llm.invoke("Hello, are you working?")
    print("Response:", response.content)
except Exception as e:
    print(f"\nError invoking ChatGoogleGenerativeAI: {e}")
