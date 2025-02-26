import streamlit as st
import os
from modules.auth import load_users
from modules.data import init_barrier_config, load_barrier_config
from modules.translations import get_translation
from components.language_selector import language_selector
from routes.landing import landing_page
from routes.login import login_page
from routes.admin import admin_page
from routes.analyzer import analyzer_page
from routes.field_layout import field_layout_tool

st.set_page_config(
    page_title="Beurteilungsstelle Steinschlagschutznetze",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SESSION STATE ---

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'users' not in st.session_state:
    st.session_state.users = load_users()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

if 'active_tool' not in st.session_state:
    st.session_state.active_tool = None

if 'barrier_config' not in st.session_state:
    st.session_state.barrier_config = init_barrier_config()

# Initialize language if not present (default to English)
if 'language' not in st.session_state:
    st.session_state.language = "de"

# --- SIDEBAR WITH LANGUAGE SELECTOR ---
with st.sidebar:
    language_selector()
    st.sidebar.markdown("---")

# --- MAIN APPLICATION FLOW ---

# Route to the appropriate page based on session state
if st.session_state.current_page == 'landing' or st.session_state.active_tool is None:
    landing_page()
elif st.session_state.active_tool == 'analyzer':
    if not st.session_state.authenticated:
        login_page()
    else:
        if st.session_state.current_page == 'admin':
            admin_page()
        else:
            analyzer_page()
elif st.session_state.active_tool == 'field_layout':
    field_layout_tool()