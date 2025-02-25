import streamlit as st
from config import CUSTOM_CSS, COPYRIGHT, APP_TITLE
from PIL import Image
import os

def landing_page():
    """Display the main landing page with tool selection"""
    # Apply custom CSS for better styling
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Add additional CSS for logo positioning
    st.markdown("""
    <style>
    .logo-section {
        margin-bottom: 30px;
    }
    .logo-container {
        text-align: left;
        margin-bottom: 10px;
    }
    .title-container {
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo and title section
    st.markdown('<div class="logo-section">', unsafe_allow_html=True)
    
    # Logo on top left
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    logo_path = "assets/logo.png"  # Adjust path to match your logo location
    
    # Check if logo file exists
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.image(logo, width=300)  # Adjust width as needed
    else:
        # Fallback if image not found
        st.warning("Logo image not found. Please add the image file to assets/logo.png")
        
        # Placeholder rectangle for logo position
        st.markdown("""
        <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; width: 200px; height: 80px; text-align: center;">
            <p style="margin: 0; color: #666;">Logo</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Title centered under the logo
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.markdown(f'<h1 style="text-align: center;">{APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Swiss Federal Assessment Center for Rockfall Protection</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Centered "Select a Tool" heading
    st.markdown('<h3 class="centered-title">Select a Tool</h3>', unsafe_allow_html=True)
    
    # Create two columns for the tool options
    col1, col2 = st.columns(2)
    
    with col1:
        # Tool card for the analyzer
        st.markdown("""
        <div class="tool-card" id="analyzer-card">
            <h3>Rockfall Barrier Analyzer</h3>
            <p>Configure, analyze, and calculate forces for rockfall protection barriers.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Button for analyzer that spans the entire width
        if st.button("Rockfall Barrier Analyzer", key="analyzer_btn", use_container_width=True):
            st.session_state.active_tool = 'analyzer'
            st.session_state.current_page = 'login'
            st.rerun()
    
    with col2:
        # Tool card for the layout tool
        st.markdown("""
        <div class="tool-card" id="layout-card">
            <h3>Rockfall Barrier Field Layout Tool</h3>
            <p>Design and plan field layouts for rockfall protection installations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Button for field layout tool that spans the entire width
        if st.button("Rockfall Barrier Field Layout Tool", key="layout_btn", use_container_width=True):
            st.session_state.active_tool = 'field_layout'
            st.session_state.current_page = 'field_layout_tool'
            st.rerun()
    
    # Footer
    st.markdown('---')
    st.markdown(f'<p style="text-align: center;">{COPYRIGHT}</p>', unsafe_allow_html=True)