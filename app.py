import streamlit as st
import subprocess
import sys
import os
import pandas as pd
from groq import Groq

st.title("AI Prospector")

raw_query = st.text_input("What type of lead you want to search:")
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

if st.button("Generate Query"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant, that will generate google search query to help the user find leads for his company. Your answer should be in this format: construção civil São Jose dos campos ( “@gmail.com” OR “@hotmail.com” OR “@yahoo.com”) AND Brazil site:instagram.com"
            },
            {
                "role": "user",
                "content": "Generate a google search query using this information: " + raw_query,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    st.write(chat_completion.choices[0].message.content)


if st.button("Start Crawl"):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"  # Force UTF-8 encoding
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True,
        env=env
    )
    st.write("Crawl started.")
    st.write("Output:", result.stdout)
    st.write("Errors:", result.stderr)


df = pd.read_csv("complete_venues.csv")
st.dataframe(df)