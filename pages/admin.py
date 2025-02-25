import streamlit as st
import pandas as pd
import base64
from modules.auth import create_user, update_user, delete_user, generate_password, generate_credentials

def admin_page():
    """Display the admin page for user management"""
    st.title("User Management")
    
    if st.session_state.users.get(st.session_state.username, {}).get('role') != 'admin':
        st.error("You do not have permission to access this page")
        return
    
    with st.expander("Create New User", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", key="new_username")
            new_password = st.text_input("Password", type="password", key="new_password")
            generate_pwd = st.checkbox("Generate random password")
            if generate_pwd:
                new_password = generate_password()
                st.code(new_password)
        
        with col2:
            new_name = st.text_input("Full Name", key="new_name")
            new_email = st.text_input("Email", key="new_email")
            new_role = st.selectbox("Role", ["user", "admin"], key="new_role")
        
        if st.button("Create User"):
            if new_username and (new_password or generate_pwd) and new_name and new_email:
                success, message = create_user(new_username, new_password, new_name, new_email, new_role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")
    
    with st.expander("Bulk Create Users", expanded=False):
        num_users = st.slider("Number of users to create", 1, 20, 5)
        
        if st.button("Generate Credentials"):
            credentials = generate_credentials(num_users)
            
            # Create the users
            created_users = []
            for username, password in credentials:
                success, _ = create_user(
                    username, 
                    password, 
                    f"User {username}", 
                    f"{username}@example.com",
                    "user"
                )
                if success:
                    created_users.append((username, password))
            
            if created_users:
                st.success(f"Created {len(created_users)} users")
                
                # Display the credentials
                df = pd.DataFrame(created_users, columns=["Username", "Password"])
                st.dataframe(df, use_container_width=True)
                
                # Add download button for CSV
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="user_credentials.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
    
    st.subheader("Existing Users")
    
    # Convert user data to DataFrame for display
    user_data = []
    for username, user in st.session_state.users.items():
        user_data.append({
            "Username": username,
            "Name": user.get("name", ""),
            "Email": user.get("email", ""),
            "Role": user.get("role", "user"),
            "Created": user.get("created_at", ""),
            "Last Login": user.get("last_login", "Never")
        })
    
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True)
    
    # Edit/Delete Users
    st.subheader("Edit User")
    selected_user = st.selectbox("Select User", list(st.session_state.users.keys()))
    
    if selected_user:
        user = st.session_state.users[selected_user]
        
        col1, col2 = st.columns(2)
        with col1:
            edit_name = st.text_input("Name", value=user.get("name", ""), key="edit_name")
            edit_email = st.text_input("Email", value=user.get("email", ""), key="edit_email")
        
        with col2:
            edit_password = st.text_input("New Password (leave empty to keep current)", type="password", key="edit_password")
            edit_role = st.selectbox("Role", ["user", "admin"], index=0 if user.get("role") == "user" else 1, key="edit_role")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update User"):
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
            if st.button("Delete User", type="primary", help="This action cannot be undone"):
                if selected_user != st.session_state.username:  # Prevent self-deletion
                    success, message = delete_user(selected_user)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("You cannot delete your own account")
    
    # Back to analyzer button
    if st.button("Back to Analyzer"):
        st.session_state.current_page = 'analyzer'
        st.rerun()