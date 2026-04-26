import os
from dotenv import load_dotenv

load_dotenv()

DB_URL=os.getenv("DB_URL")

if not DB_URL:
    import streamlit as st
    DB_URL=st.secrets["DB_URL"]
