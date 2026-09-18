import os
import base64
import json
import httpx
from openai import Stream, AsyncOpenAI, OpenAI
import warnings
import operator as op
import streamlit as st
 
 
def get_token() -> str:
        client_id = st.secrets["LLMAAS_CLIENT_ID"]
        client_secret = st.secrets["LLMAAS_CLIENT_SECRET"]
        url = "https://idp.cloud.vwgroup.com/auth/realms/kums-mfa/protocol/openid-connect/token"
 
        response = httpx.post(
            url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
        )
        assert response.status_code == 200, f"Error from Cloud IDP: {response.status_code} - {response.text}"
        return response.json()["access_token"]
 
 
 
def init_llmaas():
    	= "" #Add your key
    token = get_token()
    headers = {"X-LLM-API-CLIENT-ID": f"Bearer {key}"}
 
    client = OpenAI(
        api_key=token,
        base_url="https://llmapi.ai.vwgroup.com",
        default_headers=headers,
    )
    return client
 
 
llmaas_client = init_llmaas()
print(llmaas_client)
 
 
def get_text_answer(prompt: str) -> str:
    completion = llmaas_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": """
                * You are an advanced AI assistant with the ability to analyze diverse inputs, including text and structured data.
 
                * Your tasks are as follows:
 
                - When the user starts their query with a greeting such as "hi," "hello," "good morning," or similar, respond with enthusiasm and warmth.
 
                - Before providing your final answer, follow these steps:
                  - Understand the User's Query
                  - Generate a Thought Process (COT: Chain of Thought)
                  - Formulate and organize your response
 
                * When answering:
                  - Be Descriptive, Precise, and Organized
                  - Use HTML tags to enhance readability
             """},
            {"role": "user", "content": prompt}
        ],
        stream=False,
        temperature=0.0
    )
 
    answer = completion.choices[0].message.content
    print(answer)
    return answer
 
 
prompt = "Can you explain how a hybrid car works?"
get_text_answer(prompt)
 
 
def get_embedding(input_text: str) -> dict:
    response = llmaas_client.embeddings.create(
        model="text-embedding-3-large",
        input=input_text,
        encoding_format="float"
    )
 
    print("Embedding vector received:")
    print(response)
    return response
 
get_embedding("How are you?")
