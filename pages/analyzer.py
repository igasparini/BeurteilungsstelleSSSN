import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from modules.geometry import get_default_params, calculate_3d_coordinates
from modules.forces import calculate_forces
from modules.visualization import create_barrier_diagram, create_top_view, create_3d_view
from modules.data import save_barrier_config
from config import CABLE_TYPES, COPYRIGHT

def analyzer_page():
    """Display the main analyzer page with barrier configuration and force calculation"""
    # Title and welcome message
    st.title("Rockfall Barrier Analyzer")
    
    user_role = st.session_state.users[st.session_state.username].get("role", "user")
    user_name = st.session_state.users[st.session_state.username].get("name", st.session_state.username)
    
    # Header with user info and logout button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"Welcome, **{user_name}**")
    
    with col2:
        if user_role == "admin" and st.button("User Management", key="admin_button"):
            st.session_state.current_page = 'admin'
            st.rerun()
    
    with col3:
        if st.button("Logout", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_page = 'landing'
            st.rerun()
    
    st.markdown("---")
    
    # Ensure barrier_config has params
    if 'params' not in st.session_state.barrier_config:
        st.session_state.barrier_config['params'] = get_default_params()
    
    # Create tabs for different sections
    tabs = st.tabs(["Geometry Setup", "Force Measurement", "Results", "Export"])
    
    # Tab 1: Geometry Setup
    with tabs[0]:
        st.subheader("Barrier Geometry Configuration")
        
        # Create columns for parameters and schema
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Basic barrier configuration
            st.markdown("### Basic Configuration")
            num_supports = st.slider("Number of Supports", min_value=2, max_value=6, 
                                     value=st.session_state.barrier_config['params']['num_supports'], step=1)
            
            # Create columns for parameters
            col1a, col1b = st.columns(2)
            
            with col1a:
                # Distances
                a = st.number_input("a: Distance between anchors (m)", min_value=1.0, 
                                   value=float(st.session_state.barrier_config['params']['a']), step=0.1)
                b = st.number_input("b: Edge distance (m)", min_value=0.5, 
                                   value=float(st.session_state.barrier_config['params']['b']), step=0.1)
                d = st.number_input("d: Support distance (m)", min_value=1.0, 
                                   value=float(st.session_state.barrier_config['params']['d']), step=0.1)
                h = st.number_input("h: Base to anchor height (m)", min_value=0.5, 
                                   value=float(st.session_state.barrier_config['params']['h']), step=0.1)
                f = st.number_input("f: Foundation overhang (m)", min_value=0.0, 
                                   value=float(st.session_state.barrier_config['params']['f']), step=0.1)
                L = st.number_input("L: Support length (m)", min_value=1.0, 
                                   value=float(st.session_state.barrier_config['params']['L']), step=0.1)
            
            with col1b:
                # Angles
                theta = st.number_input("θ (Theta): Retention cable angle (°)", min_value=0.0, 
                                       value=float(st.session_state.barrier_config['params']['theta']), step=1.0)
                delta = st.number_input("δ (Delta): Upper support cable angle (°)", min_value=0.0, 
                                       value=float(st.session_state.barrier_config['params']['delta']), step=1.0)
                epsilon = st.number_input("ε (Epsilon): Support inclination (°)", min_value=0.0, 
                                         value=float(st.session_state.barrier_config['params']['epsilon']), step=1.0)
                tau = st.number_input("τ (Tau): Support to cable angle (°)", min_value=0.0, 
                                     value=float(st.session_state.barrier_config['params']['tau']), step=1.0)
                phi = st.number_input("φ (Phi): Terrain inclination (°)", min_value=0.0, 
                                     value=float(st.session_state.barrier_config['params']['phi']), step=1.0)
            
            # Optional intermediate cables
            st.markdown("### Optional Components")
            col1c, col1d = st.columns(2)
            
            with col1c:
                has_delta1 = st.checkbox("Include intermediate cable 1", 
                                        value=st.session_state.barrier_config['params']['has_delta1'])
                if has_delta1:
                    delta1 = st.number_input("δ₁ (Delta_1): Intermediate cable 1 angle (°)", min_value=0.0, 
                                            value=float(st.session_state.barrier_config['params']['delta1']), step=1.0)
                else:
                    delta1 = 0
            
            with col1d:
                has_delta2 = st.checkbox("Include intermediate cable 2", 
                                        value=st.session_state.barrier_config['params']['has_delta2'])
                if has_delta2:
                    delta2 = st.number_input("δ₂ (Delta_2): Intermediate cable 2 angle (°)", min_value=0.0, 
                                            value=float(st.session_state.barrier_config['params']['delta2']), step=1.0)
                else:
                    delta2 = 0
                    
            # Create parameters dictionary
            params = {
                'num_supports': num_supports,
                'a': a,
                'b': b,
                'd': d,
                'h': h,
                'f': f,
                'L': L,
                'theta': theta,
                'delta': delta,
                'delta1': delta1,
                'delta2': delta2,
                'epsilon': epsilon,
                'tau': tau,
                'phi': phi,
                'has_delta1': has_delta1,
                'has_delta2': has_delta2
            }
            
            # Update geometry button
            if st.button("Update Barrier Geometry"):
                st.session_state.barrier_config = calculate_3d_coordinates(params)
                save_barrier_config(st.session_state.username, st.session_state.barrier_config)
                st.success("Barrier geometry updated successfully!")
        
        with col2:
            # Display barrier schema
            st.markdown("### Barrier Schema")
            st.markdown("""
            Refer to the schema for the meaning of each parameter:
            
            **Parameters:**
            
            **θ (Theta)**: Angle between vertical and retention cable
            **δ (Delta)**: Angle between horizontal and upper support cable
            **δ₁ (Delta_1)**: Angle between horizontal and intermediate cable 1 (if present)
            **δ₂ (Delta_2)**: Angle between horizontal and intermediate cable 2 (if present)
            **ε (Epsilon)**: Support inclination relative to vertical
            **τ (Tau)**: Angle between support axis and retention cable axis
            **φ (Phi)**: Terrain inclination
            
            **a**: Distance between anchors of retention cables
            **b**: Distance between edge support and anchor of upper support cable
            **d**: Distance between supports
            **f**: Overhang of foundation
            **h**: Distance between support base and retention cable anchor
            **L**: Support length
            """)
            
            # Display simple diagram of barrier using current configuration
            st.markdown("### Current Configuration Preview")
            
            view_type = st.radio(
                "Select View Type", 
                ["3D View", "2D Side View", "2D Top View"],
                horizontal=True,
                key="config_view_type"
            )
            
            # Display the selected view
            if view_type == "2D Side View":
                side_view = create_barrier_diagram(st.session_state.barrier_config)
                st.plotly_chart(side_view, use_container_width=True, key="geometry_side_view")
            elif view_type == "2D Top View":
                top_view = create_top_view(st.session_state.barrier_config)
                st.plotly_chart(top_view, use_container_width=True, key="geometry_top_view")
            else:  # 3D View
                view_3d = create_3d_view(st.session_state.barrier_config)
                st.plotly_chart(view_3d, use_container_width=True, key="geometry_3d_view")
    
    # Tab 2: Force Measurement
    with tabs[1]:
        st.subheader("Force Measurement Input")
        
        # Display list of cables with force input fields
        st.markdown("### Cable Force Inputs")
        st.markdown("Enter the measured forces for each cable with a load cell:")
        
        # Create a multi-column layout for cable inputs
        force_cols = st.columns(3)
        
        # Group cables by type for better organization
        cable_groups = {
            'rhs': {'name': 'Retention Cables (Rhs)', 'cables': []},
            'tso': {'name': 'Upper Support Cables (Tso)', 'cables': []},
            'tsu': {'name': 'Lower Support Cables (Tsu)', 'cables': []},
            'fa': {'name': 'Catching Cables (Fa)', 'cables': []},
            'sa': {'name': 'Lateral Bracing (Sa)', 'cables': []}
        }
        
        # Group cables by type
        for cable_id, cable in st.session_state.barrier_config['cables'].items():
            cable_type = cable.get('type', '')
            if cable_type in cable_groups:
                cable_groups[cable_type]['cables'].append((cable_id, cable))
        
        # Distribute cable groups across columns
        col_index = 0
        for group_type, group in cable_groups.items():
            with force_cols[col_index % 3]:
                st.markdown(f"#### {group['name']}")
                
                for cable_id, cable in group['cables']:
                    # Create a row for each cable with force input and load cell toggle
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Force input field
                        force = st.number_input(
                            f"{cable['name']} Force (kN)", 
                            min_value=0.0, 
                            value=float(cable['force']), 
                            step=0.1,
                            key=f"force_{cable_id}",
                            format="%.1f"
                        )
                        st.session_state.barrier_config['cables'][cable_id]['force'] = force
                    
                    with col2:
                        # Load cell toggle
                        has_load_cell = st.checkbox(
                            "Load Cell", 
                            value=cable['has_load_cell'],
                            key=f"load_cell_{cable_id}"
                        )
                        st.session_state.barrier_config['cables'][cable_id]['has_load_cell'] = has_load_cell
                
                st.markdown("---")
            
            col_index += 1
        
        # Save force measurements button
        if st.button("Save Force Measurements"):
            save_barrier_config(st.session_state.username, st.session_state.barrier_config)
            st.success("Force measurements saved successfully!")
    
    # Tab 3: Results
    with tabs[2]:
        st.subheader("Force Calculation Results")
        
        # Calculate forces based on current configuration
        results = calculate_forces(st.session_state.barrier_config)
        
        # Display result visualization
        st.markdown("### Force Distribution Visualization")

        results_view_type = st.radio(
            "Select View Type", 
            ["3D View", "2D Side View"],  # Reordered to put 3D View first
            horizontal=True,
            key="results_view_type"
        )
        
        # Display the selected view
        if results_view_type == "2D Side View":
            result_view = create_barrier_diagram(st.session_state.barrier_config, results)
            st.plotly_chart(result_view, use_container_width=True, key="results_view")
        else:  # 3D View
            result_3d_view = create_3d_view(st.session_state.barrier_config, results)
            st.plotly_chart(result_3d_view, use_container_width=True, key="results_3d_view")
        
        # Display total forces
        st.markdown("### Total Forces")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Anchor Force", f"{results['total_anchor_force']:.1f} kN")
        
        with col2:
            st.metric("Total Support Force", f"{results['total_support_force']:.1f} kN")
        
        # Display detailed results in tables
        st.markdown("### Detailed Force Results")
        
        # Create anchor results table
        anchor_data = []
        for anchor_id, anchor in st.session_state.barrier_config['anchors'].items():
            # Skip anchors without position data
            if 'position' not in anchor:
                continue
                
            if anchor_id.startswith('v'):  # Only include retention cable anchors
                anchor_data.append({
                    'Anchor': anchor.get('name', f"Anchor {anchor_id}"),
                    'Force (kN)': round(results.get(anchor_id, 0), 1),
                    'X (m)': round(anchor['position'].get('x', 0), 2),
                    'Y (m)': round(anchor['position'].get('y', 0), 2),
                    'Z (m)': round(anchor['position'].get('z', 0), 2)
                })
        
        df_anchors = pd.DataFrame(anchor_data)
        
        # Create support results table
        support_data = []
        for support_id, support in st.session_state.barrier_config['supports'].items():
            # Skip supports without required data
            if 'base' not in support or 'top' not in support:
                continue
                
            support_data.append({
                'Support': support.get('name', f"Support {support_id}"),
                'Force (kN)': round(results.get(support_id, 0), 1),
                'Base X (m)': round(support['base'].get('x', 0), 2),
                'Base Y (m)': round(support['base'].get('y', 0), 2),
                'Base Z (m)': round(support['base'].get('z', 0), 2),
                'Top X (m)': round(support['top'].get('x', 0), 2),
                'Top Y (m)': round(support['top'].get('y', 0), 2),
                'Top Z (m)': round(support['top'].get('z', 0), 2)
            })
        
        df_supports = pd.DataFrame(support_data)
        
        # Display tables
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### Anchor Forces")
            st.dataframe(df_anchors, use_container_width=True)
        
        with col4:
            st.markdown("#### Support Forces")
            st.dataframe(df_supports, use_container_width=True)
    
    # Tab 4: Export
    with tabs[3]:
        st.subheader("Export Data")
        
        # Calculate forces for export
        export_results = calculate_forces(st.session_state.barrier_config)
        
        # Prepare export data
        export_data = {
            'barrier_config': st.session_state.barrier_config,
            'force_results': export_results,
            'exported_by': st.session_state.username,
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Convert to JSON
        export_json = json.dumps(export_data, indent=2)
        
        # Download button
        st.download_button(
            label="Download Complete Configuration (JSON)",
            data=export_json,
            file_name="rockfall_barrier_analysis.json",
            mime="application/json"
        )
        
        # Export CSV options
        st.markdown("### Export Results as CSV")
        
        # Calculate forces
        results = calculate_forces(st.session_state.barrier_config)
        
        # Prepare CSV data
        col5, col6 = st.columns(2)
        
        with col5:
            # Export anchor forces
            anchor_data = []
            for anchor_id, anchor in st.session_state.barrier_config['anchors'].items():
                # Skip anchors without position data
                if 'position' not in anchor:
                    continue
                    
                if anchor_id.startswith('v'):  # Only include retention cable anchors
                    anchor_data.append({
                        'Anchor': anchor.get('name', f"Anchor {anchor_id}"),
                        'Force (kN)': round(results.get(anchor_id, 0), 1),
                        'X (m)': round(anchor['position'].get('x', 0), 2),
                        'Y (m)': round(anchor['position'].get('y', 0), 2),
                        'Z (m)': round(anchor['position'].get('z', 0), 2)
                    })
            
            df_anchors = pd.DataFrame(anchor_data)
            csv_anchors = df_anchors.to_csv(index=False)
            
            st.download_button(
                label="Download Anchor Forces (CSV)",
                data=csv_anchors,
                file_name="anchor_forces.csv",
                mime="text/csv",
                key="download_anchors"
            )
        
        with col6:
            # Export support forces
            support_data = []
            for support_id, support in st.session_state.barrier_config['supports'].items():
                # Skip supports without required data
                if 'base' not in support or 'top' not in support:
                    continue
                    
                support_data.append({
                    'Support': support.get('name', f"Support {support_id}"),
                    'Force (kN)': round(results.get(support_id, 0), 1),
                    'Base X (m)': round(support['base'].get('x', 0), 2),
                    'Base Y (m)': round(support['base'].get('y', 0), 2),
                    'Base Z (m)': round(support['base'].get('z', 0), 2),
                    'Top X (m)': round(support['top'].get('x', 0), 2),
                    'Top Y (m)': round(support['top'].get('y', 0), 2),
                    'Top Z (m)': round(support['top'].get('z', 0), 2)
                })
            
            df_supports = pd.DataFrame(support_data)
            csv_supports = df_supports.to_csv(index=False)
            
            st.download_button(
                label="Download Support Forces (CSV)",
                data=csv_supports,
                file_name="support_forces.csv",
                mime="text/csv",
                key="download_supports"
            )
        
        # Export cable forces
        cable_data = []
        for cable_id, cable in st.session_state.barrier_config['cables'].items():
            # Skip cables without required coordinates
            if 'start_coords' not in cable or 'end_coords' not in cable:
                continue
                
            # Use get() method to safely retrieve values with defaults
            start_coords = cable.get('start_coords', {})
            end_coords = cable.get('end_coords', {})
            
            cable_data.append({
                'Cable': cable.get('name', f"Cable {cable_id}"),
                'Type': cable.get('type', '').upper(),
                'Force (kN)': cable.get('force', 0) if cable.get('has_load_cell', False) else "No measurement",
                'Has Load Cell': "Yes" if cable.get('has_load_cell', False) else "No",
                'Start X': round(start_coords.get('x', 0), 2),
                'Start Y': round(start_coords.get('y', 0), 2),
                'Start Z': round(start_coords.get('z', 0), 2),
                'End X': round(end_coords.get('x', 0), 2),
                'End Y': round(end_coords.get('y', 0), 2),
                'End Z': round(end_coords.get('z', 0), 2)
            })
        
        df_cables = pd.DataFrame(cable_data)
        csv_cables = df_cables.to_csv(index=False)
        
        st.download_button(
            label="Download Cable Forces (CSV)",
            data=csv_cables,
            file_name="cable_forces.csv",
            mime="text/csv",
            key="download_cables"
        )
        
        # Export all data in one JSON
        st.markdown("### Export All Data")
        
        # Combine all data
        all_data = {
            'Anchors': df_anchors.to_dict(orient='records') if not df_anchors.empty else [],
            'Supports': df_supports.to_dict(orient='records'),
            'Cables': df_cables.to_dict(orient='records'),
            'Total Anchor Force': results.get('total_anchor_force', 0),
            'Total Support Force': results.get('total_support_force', 0),
            'Parameters': st.session_state.barrier_config.get('params', get_default_params())
        }
        
        # Convert to JSON
        all_json = json.dumps(all_data, indent=2)
        
        st.download_button(
            label="Download All Data (JSON)",
            data=all_json,
            file_name="all_data.json",
            mime="application/json",
            key="download_all_json"
        )