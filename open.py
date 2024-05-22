from openai import OpenAI
import streamlit as st
from groq_response import groq_response
import os
import json
import requests

os.environ['OPENA_AI_API_KEY'] = st.secrets['OPENA_AI_API_KEY']
    

client = OpenAI(api_key=os.environ['OPENA_AI_API_KEY'])
prompt = st.chat_input("Type your question...")
my_assistant = client.beta.assistants.retrieve("asst_whBs56nCEId4lym1lgt392vS")
ass_id = "asst_whBs56nCEId4lym1lgt392vS"
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
def retrival_openai(prompt, instructions):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ass_id,
        instructions=instructions
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        assistant_messages = [message for message in messages.data if message.role == 'assistant']
        for message in assistant_messages:
            for content_block in message.content:
                # Check if there's a method or property to get 'value'
                if hasattr(content_block.text, 'value'):
                    return content_block.text.value                    
                else:
                    # Otherwise print the object to debug
                    #st.write(messages)
                    #st.write(content_block.text)
                    return None
    else:
        return None
    

def get_molecule(search_string):    
    response_functions = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[{'role': 'user', 'content': str(search_string)}],
                    functions=molecule_custom_functions,
                    function_call='molecule_custom_functions'
                )
    data = json.loads(response_functions.choices[0].message.function_call.arguments)
    return data['molecule_name']    

