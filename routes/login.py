import streamlit as st
from modules.auth import authenticate
from modules.data import load_barrier_config
from config import get_config
from modules.translations import get_translation

def login_page():
    """Display the login page"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    # Get translated configuration
    config = get_config()
    
    st.title(get_translation("login_title", lang))
    
    # Add back button to return to landing page
    if st.button(get_translation("back_to_main", lang), key="back_to_landing"):
        st.session_state.active_tool = None
        st.session_state.current_page = 'landing'
        st.rerun()
    
    # Apply custom CSS
    st.markdown(config["CUSTOM_CSS"], unsafe_allow_html=True)
    
    left, middle, right = st.columns(3)
    
    with left:
        st.subheader(get_translation("login_instruction", lang))
        
        username = st.text_input(get_translation("username", lang))
        password = st.text_input(get_translation("password", lang), type="password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button(get_translation("login", lang), use_container_width=True):
                if username and password:
                    success, message = authenticate(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.current_page = 'analyzer'
                        st.session_state.barrier_config = load_barrier_config(username)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error(get_translation("enter_both", lang))
        
        with col2:
            if st.button(get_translation("reset_password", lang), use_container_width=True):
                if username:
                    st.info(get_translation("contact_admin", lang))
                else:
                    st.error(get_translation("enter_username", lang))
    
    # # Footer
    # st.markdown('---')
    # st.markdown(f'<p style="text-align: center;">{config["COPYRIGHT"]}</p>', unsafe_allow_html=True)