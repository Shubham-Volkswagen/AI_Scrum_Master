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
 
