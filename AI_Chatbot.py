import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assisstant", "content": "Yo what up boi, U need help?"} 
    ] 

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Yo we can chat here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    gemini_history = [
        {
            "role": "model" if m["role"] == "assisstant" else "user",
            "parts": [{"text": m["content"]}],
        }
        for m in st.session_state.messages
    ]
    
    with st.chat_message("assisstant"):
        stream = client.models.generate_content_stream(
            model="gemini-3.6-flash",
            contents=gemini_history,
        )

        msg = st.write_stream(chunk.text for chunk in stream)

    st.session_state.messages.append({"role": "assisstant", "content": msg})
