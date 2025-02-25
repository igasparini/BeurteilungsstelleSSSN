import streamlit as st
from config import COPYRIGHT

def field_layout_tool():
    """Display the Rockfall Barrier Field Layout Tool"""
    st.title("Rockfall Barrier Field Layout Tool")
    
    # Header with navigation back to landing page
    if st.button("Back to Main Menu"):
        st.session_state.active_tool = None
        st.session_state.current_page = 'landing'
        st.rerun()
    
    st.markdown("---")
    
    # Placeholder content with tabs for organization
    tabs = st.tabs(["DSM Upload", "Barrier Layout", "Export"])
    
    with tabs[0]:
        st.header("Digital Surface Model Upload")
        st.info("This module is currently under development.")
        
        # Placeholder for site planning features
        st.markdown("""
        ### Coming Eventually:
        - Upload DSM
        - Select barrier placement zone
        """)
        
        # Demonstration image placeholder
        st.markdown("""
        <div style="background-color: #f0f0f0; height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
            <span style="color: #666;">Site planning visualization will appear here</span>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.header("Barrier Layout")
        st.info("This module is currently under development.")
        
        # Placeholder for terrain analysis features
        st.markdown("""
        ### Coming Eventually:
        - Automatic barrier layout with proper geometry constraints
        - Manual editing
        """)
        
        # Demonstration image placeholder
        st.markdown("""
        <div style="background-color: #f0f0f0; height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
            <span style="color: #666;">Terrain analysis visualization will appear here</span>
        </div>
        """, unsafe_allow_html=True)
    
    with tabs[2]:
        st.header("Export & Documentation")
        st.info("This module is currently under development.")
        
        # Placeholder for export features
        st.markdown("""
        ### Coming Eventually:
        - Layout export
            - CAD formats
            - Relevant GPS coordinates
            - ...
        """)
        
        # Placeholder export buttons
        col1, col2 = st.columns(2)
        with col1:
            st.button("Export to CAD (Coming Eventually)", disabled=True)
        with col2:
            st.button("Generate Documentation (Coming Eventually)", disabled=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f'<p style="text-align: center;">{COPYRIGHT}</p>', unsafe_allow_html=True)