from groq import Groq
import groq
import os
import streamlit as st

os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
    
client_groq = Groq(api_key=os.environ['GROQ_API_KEY'])

def groq_response(content, prompt):
    try:
        response = client_groq.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content + prompt,
                }
            ],
            model="mixtral-8x7b-32768",
        )
        return response.choices[0].message.content
    except groq.APIConnectionError as e:
        st.error("The server could not be reached, please try again later.")
    except  groq.RateLimitError as e:
        st.error("You have exceeded the rate limit for the demo version, please try again in some time.")    
