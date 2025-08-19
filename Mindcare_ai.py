import os
import time
import streamlit as st
import speech_recognition as sr
import pyttsx3
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import threading


# ==============================
# Configure API Key
# ==============================
os.environ["GROQ_API_KEY"] = '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'

# ==============================
# Initialize Groq LLM
# ==============================
llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)
prompt = ChatPromptTemplate.from_template("""
You are a compassionate mental health assistant.
Respond in a calm, empathetic, and reassuring way.
Always encourage professional help if needed.

User: {user_input}
Assistant:
""")
chain = prompt | llm | StrOutputParser()

# ==============================
# Voice Engine (TTS)
# ==============================


engine = pyttsx3.init() # disable blocking loop



voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)


def speak(text):
    def run_speech():
      engine.say(text)
      engine.runAndWait()
    threading.Thread(target=run_speech, daemon=True).start()


# ==============================
# Streamlit UI
# ==============================
st.set_page_config(page_title="MindCare AI", page_icon="💬")
st.title("💬 MindCare AI with Voice")
st.markdown("Speak with an empathetic assistant powered by **Groq LLaMA 3**.")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Input Box (manual typing fallback)
user_input = st.text_input("🗨️ Type your feelings or message (or speak using your mic)")

if st.button("Send") and user_input:
    response = chain.invoke({"user_input": user_input})
    st.session_state.conversation.append(("You", user_input))
    st.session_state.conversation.append(("MindCare AI", response))
    speak(response)

# Display conversation
for role, text in st.session_state.conversation:
    if role == "You":
        st.markdown(f"**🧑 You:** {text}")
    else:
        st.markdown(f"**🤖 MindCare AI:** {text}")

# ==============================
# 🎙 Speech Recognition Button
# ==============================
if st.button("🎙 Speak"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        user_text = recognizer.recognize_google(audio)
        st.success(f"You said: {user_text}")
        response = chain.invoke({"user_input": user_text})
        st.session_state.conversation.append(("You", user_text))
        st.session_state.conversation.append(("MindCare AI", response))
        speak(response)
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio.")
    except sr.RequestError:
        st.error("❌ Speech recognition service error.")
