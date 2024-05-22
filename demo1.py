from groq import Groq
import groq
import streamlit as st
from openai import OpenAI
import json
from groq_response import groq_response
import streamlit.components.v1 as components
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtubesearchpython import VideosSearch
import os
import queue
import re
import tempfile
import threading
import requests
from bs4 import BeautifulSoup
from open import retrival_openai
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

# --- USER AUTHENTICATION ---
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
#------------------------------------------------------------
if st.session_state["authentication_status"]:
    
    ass_id = "asst_whBs56nCEId4lym1lgt392vS"
    os.environ['OPENA_AI_API_KEY'] = st.secrets['OPENA_AI_API_KEY']
    os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
    
        
    client_groq = Groq(api_key=os.environ['GROQ_API_KEY'])
    client_openai = OpenAI(api_key=os.environ['OPENA_AI_API_KEY'] )
    
    link_custom_functions = [
        {
            'name': 'extract_website_url',
            'description': 'Get the website url',
            'parameters': {
                'type': 'object',
                'properties': {
                    'link': {'type': 'string', 'description': 'website url'},
            }
        }
        }
    ]
    
    
    # Initialize your clients with API keys
    client_openai = OpenAI(api_key=os.environ['OPENA_AI_API_KEY'])
    client_groq = Groq(api_key=os.environ['GROQ_API_KEY'])
    client_groq_one = Groq(api_key=os.environ['GROQ_API_KEY'])
    
    # Define your custom functions for OpenAI
    scenario_custom_functions = [
        {
            'name': 'extract_scenario_info',
            'description': 'Get the individual scenarios text',
            'parameters': {
                'type': 'object',
                'properties': {
                    'scenario_1': {'type': 'string', 'description': 'scenario number 1 full text'},
                    'scenario_2': {'type': 'string', 'description': 'scenario number 2 full text'},
                    'scenario_3': {'type': 'string', 'description': 'scenario number 3 full text'},
                    'scenario_4': {'type': 'string', 'description': 'scenario number 4 full text'},
                }
            }
        }
    ]
    
    scenario_keyword_functions = [
        {
            'name': 'extract_scenario_info',
            'description': 'Get the individual scenarios text',
            'parameters': {
                'type': 'object',
                'properties': {
                    'keyword_1': {'type': 'string', 'description': 'keyword 1'},
                    'keyword_2': {'type': 'string', 'description': 'keyword 2'},
                    'keyword_3': {'type': 'string', 'description': 'keyword 3'},
                    'keyword_4': {'type': 'string', 'description': 'keyword 4'},
                }
            }
        }
    ]
    
    video_custom_functions = [
        {
            'name': 'extract_video_id',
            'description': 'Get the video ID',
            'parameters': {
                'type': 'object',
                'properties': {
                    'video_id': {'type': 'string', 'description': 'video ID'},
            }
        }
        }
    ]
    # Initialize a string to store all transcripts
    all_video_transcripts = ""
    
    molecule_custom_functions = [
        {
            'name': 'extract_molecule_info',
            'description': 'Get the molecule name',
            'parameters': {
                'type': 'object',
                'properties': {
                    'molecule_name': {'type': 'string', 'description': 'name of the molecule'},
            }
        }
        }
    ]
    
    keyword_custom_functions = [
        {
            'name': 'extract_keyword_info',
            'description': 'Get the search query keyword',
            'parameters': {
                'type': 'object',
                'properties': {
                    'keyword': {'type': 'string', 'description': 'keyword of teh search query'},
            }
        }
        }
    ]
    # Streamlit UI
    st.title("Materials Science")
    image_variable = None
    # Session states initialization
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ''
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = []
    if 'selected_options_reaction' not in st.session_state:
        st.session_state.selected_options_reaction = []
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = []    
    
    
    # User inputs
    st.session_state.selected_options = st.multiselect("Select options", ["fun based", "context based", "real world based", "conceptual textbook based"])
    st.session_state.prompt = st.text_input("Enter your prompt")
    check_box = st.checkbox("Open Chem Sketcher")
    st.session_state.selected_language = st.multiselect("Select options", ["Deutsch", "English", ])
    
    
    with st.sidebar:
        st.sidebar.title("Chat with the assistant 🤖")
        # Input for search query
        search_query = st.sidebar.text_input("Enter your video search query")    
        messages = st.container(height=630)
        if check_box:
            messages.chat_message("assistant").write("Here is the Chem Sketcher for you to draw the molecule:")
            with messages.chat_message("assistant"):
                components.iframe("https://marvinjs.chemicalize.com/v1/fcc0cc8570204c48a6447859c71cf611/editor.html?frameId=2cd5fd97-f496-4b6f-8cbc-417acc66684f&origin=https%3A%2F%2Fwww.rcsb.org", height=600)     
        prompt_sidebar = st.chat_input("Say something")
        if prompt_sidebar:
            messages.chat_message("user").write(prompt_sidebar)
            prompt = prompt_sidebar
            sidebar_chat = retrival_openai(prompt, instructions="Please answer this query")
            if sidebar_chat is None:
                sidebar_chat = groq_response("please answer this query : ", prompt)
            messages.chat_message("assistant").write(sidebar_chat)
                
    if st.session_state.prompt:
            prompt = st.session_state.prompt
            selected_options = " ".join(st.session_state.selected_options)
            response = retrival_openai(prompt, instructions=f"Please create a brief detailed explaination of the query and give back information from the book and teh user wants to learn the topic in a {selected_options} ")
            language = " ".join(st.session_state.selected_language)
            messages = [
                {"role": "user", "content": f"create a {selected_options} scenarios based task question for learning matrial science from teh given explaination of teh topic, create 4 scenarios each time and number them: {response} and the language in which you need to create teh scenarios is {language}"},
            ]
            chat_completion = client_groq.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",
            )
            response = chat_completion.choices[0].message.content
    
            if response:
                response_functions = client_openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role': 'user', 'content': response}],
                    functions=scenario_custom_functions,
                    function_call='auto'
                )
                data = json.loads(response_functions.choices[0].message.function_call.arguments)
    
                # Tabs for scenarios
                scenario_tabs = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']
                tabs = st.tabs(scenario_tabs)
                for i, tab in enumerate(tabs):
                    with tab:
                        st.header(scenario_tabs[i])
                        scenario_text = data[f'scenario_{i+1}']
                        st.write(scenario_text)
                        prompt = scenario_text
                        content = "subdivide this scenario into three subquestions and only give the questions. The scenario is: "
                        chat_completion_subquestions = groq_response(content, prompt)
                        scenario_generated = chat_completion_subquestions
                        st.write(scenario_generated)
                        prompt = scenario_generated
                        content = f"give a sample ideal step-by-step format to attempt to answer this scenario question as a hint in the {language} language . Scenario: "
                        chat_completion_hint = groq_response(content, prompt)
                        st.text_area("Enter your answer here", key=f'answer_{i}')
                        
                        with st.expander("See hint for answering the question" + str(i+1) + "😀"): 
                            st.write(chat_completion_hint)
                        # Upload PDF button
                        uploaded_file = st.file_uploader("Upload your answer (PDF)", type="pdf", key=f"pdf_uploader_{i}")
                        if uploaded_file is not None:
                            st.success("File uploaded successfully!")
                            
    
                        col1, col2 = st.columns(2)
                        with col1:
                            with st.expander("See explanation 3D"):
                                components.iframe("https://embed.molview.org/v1/?mode=balls&cid=124527813")
                        with col2:
                            with st.expander("See explanation 2D"):
                                components.iframe("https://marvinjs.chemicalize.com/v1/fcc0cc8570204c48a6447859c71cf611/editor.html?frameId=2cd5fd97-f496-4b6f-8cbc-417acc66684f&origin=https%3A%2F%2Fwww.rcsb.org")
    
    # Example of error handling with client_groq API callss
