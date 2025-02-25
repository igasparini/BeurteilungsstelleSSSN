import streamlit as st
from modules.auth import authenticate
from modules.data import load_barrier_config
from config import CUSTOM_CSS, COPYRIGHT

def login_page():
    """Display the login page"""
    st.title("Rockfall Barrier Analyzer - Login")
    
    # Add back button to return to landing page
    if st.button("← Back to Main Menu", key="back_to_landing"):
        st.session_state.active_tool = None
        st.session_state.current_page = 'landing'
        st.rerun()
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    left, middle, right = st.columns(3)
    
    with left:
        st.subheader("Login to access the analyzer")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Login", use_container_width=True):
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
                    st.error("Please enter both username and password")
        
        with col2:
            if st.button("Reset Password", use_container_width=True):
                if username:
                    st.info("Please contact your administrator to reset your password.")
                else:
                    st.error("Please enter your username")
    
    # # Footer
    # st.markdown('---')
    # st.markdown(f'<p style="text-align: center;">{COPYRIGHT}</p>', unsafe_allow_html=True)