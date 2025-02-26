import streamlit as st
import pandas as pd
import base64
from modules.auth import create_user, update_user, delete_user, generate_password, generate_credentials
from modules.translations import get_translation
from config import get_config

def admin_page():
    """Display the admin page for user management"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    # Get translated configuration
    config = get_config()
    
    st.title(get_translation("user_management", lang))
    
    if st.session_state.users.get(st.session_state.username, {}).get('role') != 'admin':
        st.error(get_translation("no_permission", lang))
        return
    
    with st.expander(get_translation("create_new_user", lang), expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input(get_translation("username", lang), key="new_username")
            new_password = st.text_input(get_translation("password", lang), type="password", key="new_password")
            generate_pwd = st.checkbox(get_translation("generate_random_password", lang))
            if generate_pwd:
                new_password = generate_password()
                st.code(new_password)
        
        with col2:
            new_name = st.text_input(get_translation("full_name", lang), key="new_name")
            new_email = st.text_input(get_translation("email", lang), key="new_email")
            new_role = st.selectbox(get_translation("role", lang), 
                                   ["user", "admin"], 
                                   format_func=lambda x: get_translation(x, lang),
                                   key="new_role")
        
        if st.button(get_translation("create_user", lang)):
            if new_username and (new_password or generate_pwd) and new_name and new_email:
                success, message = create_user(new_username, new_password, new_name, new_email, new_role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error(get_translation("fill_all_fields", lang))
    
    with st.expander(get_translation("bulk_create_users", lang), expanded=False):
        num_users = st.slider(get_translation("num_users_to_create", lang), 1, 20, 5)
        
        if st.button(get_translation("generate_credentials", lang)):
            credentials = generate_credentials(num_users)
            
            # Create the users
            created_users = []
            for username, password in credentials:
                success, _ = create_user(
                    username, 
                    password, 
                    f"{get_translation('user', lang)} {username}", 
                    f"{username}@example.com",
                    "user"
                )
                if success:
                    created_users.append((username, password))
            
            if created_users:
                st.success(f"{get_translation('created', lang)} {len(created_users)} {get_translation('users', lang)}")
                
                # Display the credentials
                df = pd.DataFrame(created_users, columns=[
                    get_translation("username", lang), 
                    get_translation("password", lang)
                ])
                st.dataframe(df, use_container_width=True)
                
                # Add download button for CSV
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="user_credentials.csv">{get_translation("download_csv", lang)}</a>'
                st.markdown(href, unsafe_allow_html=True)
    
    st.subheader(get_translation("existing_users", lang))
    
    # Convert user data to DataFrame for display
    user_data = []
    for username, user in st.session_state.users.items():
        user_data.append({
            get_translation("username", lang): username,
            get_translation("name", lang): user.get("name", ""),
            get_translation("email", lang): user.get("email", ""),
            get_translation("role", lang): get_translation(user.get("role", "user"), lang),
            get_translation("created", lang): user.get("created_at", ""),
            get_translation("last_login", lang): user.get("last_login", get_translation("never", lang))
        })
    
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True)
    
    # Edit/Delete Users
    st.subheader(get_translation("edit_user", lang))
    selected_user = st.selectbox(get_translation("select_user", lang), list(st.session_state.users.keys()))
    
    if selected_user:
        user = st.session_state.users[selected_user]
        
        col1, col2 = st.columns(2)
        with col1:
            edit_name = st.text_input(get_translation("name", lang), value=user.get("name", ""), key="edit_name")
            edit_email = st.text_input(get_translation("email", lang), value=user.get("email", ""), key="edit_email")
        
        with col2:
            edit_password = st.text_input(get_translation("new_password_empty", lang), type="password", key="edit_password")
            edit_role = st.selectbox(
                get_translation("role", lang), 
                ["user", "admin"], 
                index=0 if user.get("role") == "user" else 1, 
                format_func=lambda x: get_translation(x, lang),
                key="edit_role"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_translation("update_user", lang)):
                success, message = update_user(
                    selected_user,
                    name=edit_name,
                    email=edit_email,
                    password=edit_password,
                    role=edit_role
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        with col2:
            if st.button(get_translation("delete_user", lang), type="primary", help=get_translation("delete_warning", lang)):
                if selected_user != st.session_state.username:  # Prevent self-deletion
                    success, message = delete_user(selected_user)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error(get_translation("cannot_delete_self", lang))
    
    # Back to analyzer button
    if st.button(get_translation("back_to_analyzer", lang)):
        st.session_state.current_page = 'analyzer'
        st.rerun()