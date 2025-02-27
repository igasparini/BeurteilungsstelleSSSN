import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
from modules.geometry import (
    get_default_params, calculate_3d_coordinates, 
    apply_parameter_changes, validate_parameter_limits, 
    calculate_tau, calculate_theta, calculate_delta
)
from modules.forces import calculate_forces
from modules.visualization import create_barrier_diagram, create_top_view, create_3d_view
from modules.data import save_barrier_config
from modules.translations import get_translation
from config import get_config
import os
from PIL import Image

def handle_parameter_change(param_name):
    """
    Handler for parameter changes with the name of the parameter that changed.
    
    Args:
        param_name: The name of the parameter being changed
    """
    # Get the new value from session state
    new_value = st.session_state[f'param_{param_name}']
    
    # Apply the parameter change with interdependencies
    params = st.session_state.barrier_config['params']
    updated_params, changed_params, validation, warnings = apply_parameter_changes(params, param_name, new_value)
    
    # Update session state parameters
    st.session_state.barrier_config['params'] = updated_params
    
    # Recalculate 3D coordinates with updated parameters
    st.session_state.barrier_config = calculate_3d_coordinates(updated_params)
    
    # Save the updated configuration
    save_barrier_config(st.session_state.username, st.session_state.barrier_config)
    
    # Display warnings if any
    if warnings:
        st.warning("\n".join(warnings))

def analyzer_page():
    """Display the main analyzer page with barrier configuration and force calculation"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    # Get translated configuration
    config = get_config()
    
    # Title and welcome message
    st.title(get_translation("barrier_analyzer", lang))
    
    user_role = st.session_state.users[st.session_state.username].get("role", "user")
    user_name = st.session_state.users[st.session_state.username].get("name", st.session_state.username)
    
    # Header with user info and logout button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"{get_translation('welcome', lang)}**{user_name}**")
    
    with col2:
        if user_role == "admin" and st.button(get_translation("user_management", lang), key="admin_button"):
            st.session_state.current_page = 'admin'
            st.rerun()
    
    with col3:
        if st.button(get_translation("logout", lang), key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_page = 'landing'
            st.rerun()
    
    st.markdown("---")
    
    # Ensure barrier_config has params
    if 'params' not in st.session_state.barrier_config:
        st.session_state.barrier_config['params'] = get_default_params()
    
    # Create tabs for different sections
    tabs = st.tabs([
        get_translation("geometry_setup", lang), 
        get_translation("force_measurement", lang), 
        get_translation("results", lang), 
        get_translation("export", lang)
    ])
    
    # Tab 1: Geometry Setup
    with tabs[0]:
        st.subheader(get_translation("barrier_geometry", lang))
        
        # Create columns for parameters and schema
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            # Basic barrier configuration
            st.markdown(f"### {get_translation('basic_config', lang)}")
            num_supports = st.slider(
                get_translation("num_supports", lang), 
                min_value=2, 
                max_value=6, 
                value=st.session_state.barrier_config['params']['num_supports'], 
                step=1,
                key="param_num_supports",
                on_change=lambda: handle_parameter_change('num_supports')
            )
            
            # Create columns for parameters
            col1a, col1b = st.columns(2)

            with col1a:
                # Distances
                b = st.number_input(
                    f"b: {get_translation('edge_distance', lang)} (m)", 
                    min_value=0.5, 
                    value=float(st.session_state.barrier_config['params']['b']), 
                    step=0.1,
                    key="param_b",
                    on_change=lambda: handle_parameter_change('b')
                )
                
                d = st.number_input(
                    f"d: {get_translation('support_distance', lang)} (m)", 
                    min_value=1.0, 
                    value=float(st.session_state.barrier_config['params']['d']), 
                    step=0.1,
                    key="param_d",
                    on_change=lambda: handle_parameter_change('d')
                )
                
                h = st.number_input(
                    f"h: {get_translation('base_anchor_height', lang)} (m)", 
                    min_value=0.5, 
                    value=float(st.session_state.barrier_config['params']['h']), 
                    step=0.1,
                    key="param_h",
                    on_change=lambda: handle_parameter_change('h')
                )
                
                f = st.number_input(
                    f"f: {get_translation('foundation_overhang', lang)} (m)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['f']), 
                    step=0.1,
                    key="param_f",
                    on_change=lambda: handle_parameter_change('f')
                )
                
                L = st.number_input(
                    f"L: {get_translation('support_length', lang)} (m)", 
                    min_value=1.0, 
                    value=float(st.session_state.barrier_config['params']['L']), 
                    step=0.1,
                    key="param_L",
                    on_change=lambda: handle_parameter_change('L')
                )

            with col1b:
                # Angles
                theta = st.number_input(
                    f"θ ({get_translation('theta', lang)}): {get_translation('retention_cable_angle', lang)} (°)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['theta']), 
                    step=1.0,
                    key="param_theta",
                    on_change=lambda: handle_parameter_change('theta')
                )
                
                delta = st.number_input(
                    f"δ ({get_translation('delta', lang)}): {get_translation('upper_support_cable_angle', lang)} (°)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['delta']), 
                    step=1.0,
                    key="param_delta",
                    on_change=lambda: handle_parameter_change('delta')
                )
                
                epsilon = st.number_input(
                    f"ε ({get_translation('epsilon', lang)}): {get_translation('support_inclination', lang)} (°)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['epsilon']), 
                    step=1.0,
                    key="param_epsilon",
                    on_change=lambda: handle_parameter_change('epsilon')
                )
                
                tau = st.number_input(
                    f"τ ({get_translation('tau', lang)}): {get_translation('support_cable_angle', lang)} (°)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['tau']), 
                    step=1.0,
                    key="param_tau",
                    on_change=lambda: handle_parameter_change('tau')
                )
                
                phi = st.number_input(
                    f"φ ({get_translation('phi', lang)}): {get_translation('terrain_inclination', lang)} (°)", 
                    min_value=0.0, 
                    value=float(st.session_state.barrier_config['params']['phi']), 
                    step=1.0,
                    key="param_phi",
                    on_change=lambda: handle_parameter_change('phi')
                )
            
            # Optional intermediate cables
            st.markdown(f"### {get_translation('optional_components', lang)}")
            col1c, col1d = st.columns(2)
            
            with col1c:
                has_delta1 = st.checkbox(
                    get_translation("include_intermediate_cable1", lang), 
                    value=st.session_state.barrier_config['params']['has_delta1'],
                    key="param_has_delta1",
                    on_change=lambda: handle_parameter_change('has_delta1')
                )
                
                if has_delta1:
                    delta1 = st.number_input(
                        f"δ₁ ({get_translation('delta1', lang)}): {get_translation('intermediate_cable1_angle', lang)} (°)", 
                        min_value=0.0, 
                        value=float(st.session_state.barrier_config['params']['delta1']), 
                        step=1.0,
                        key="param_delta1",
                        on_change=lambda: handle_parameter_change('delta1')
                    )
                else:
                    st.session_state.barrier_config['params']['delta1'] = 0
            
            with col1d:
                has_delta2 = st.checkbox(
                    get_translation("include_intermediate_cable2", lang), 
                    value=st.session_state.barrier_config['params']['has_delta2'],
                    key="param_has_delta2",
                    on_change=lambda: handle_parameter_change('has_delta2')
                )
                
                if has_delta2:
                    delta2 = st.number_input(
                        f"δ₂ ({get_translation('delta2', lang)}): {get_translation('intermediate_cable2_angle', lang)} (°)", 
                        min_value=0.0, 
                        value=float(st.session_state.barrier_config['params']['delta2']), 
                        step=1.0,
                        key="param_delta2",
                        on_change=lambda: handle_parameter_change('delta2')
                    )
                else:
                    st.session_state.barrier_config['params']['delta2'] = 0
            
            # Update geometry button
            if st.button(get_translation("update_barrier_geometry", lang)):
                # Recalculate 3D coordinates with current parameters
                st.session_state.barrier_config = calculate_3d_coordinates(st.session_state.barrier_config['params'])
                save_barrier_config(st.session_state.username, st.session_state.barrier_config)
                st.success(get_translation("geometry_updated", lang))
        
        with col2:
            # Display preview of barrier using current configuration
            st.markdown(f"### {get_translation('current_config_preview', lang)}")
            
            view_type = st.radio(
                get_translation("select_view_type", lang), 
                [
                    get_translation("3d_view", lang),
                    get_translation("2d_side_view", lang),
                    get_translation("2d_top_view", lang)
                ],
                horizontal=True,
                key="config_view_type",
                format_func=lambda x: x  # We're already passing translated values
            )
            
            # Display the selected view
            if view_type == get_translation("2d_side_view", lang):
                side_view = create_barrier_diagram(st.session_state.barrier_config)
                st.plotly_chart(side_view, use_container_width=True, key="geometry_side_view")
            elif view_type == get_translation("2d_top_view", lang):
                top_view = create_top_view(st.session_state.barrier_config)
                st.plotly_chart(top_view, use_container_width=True, key="geometry_top_view")
            else:  # 3D View
                view_3d = create_3d_view(st.session_state.barrier_config)
                st.plotly_chart(view_3d, use_container_width=True, key="geometry_3d_view")

        # Display barrier schema
        st.markdown(f"### {get_translation('barrier_schema', lang)}")

        st.markdown('<div class="schema-container">', unsafe_allow_html=True)
        schema_path = "assets/schema.png"  # Adjust path to match your schema location
        
        # Check if schema file exists
        if os.path.exists(schema_path):
            schema = Image.open(schema_path)
            st.image(schema, use_container_width=True)  # Adjust width as needed
        else:
            # Fallback if image not found
            st.warning("schema image not found. Please add the image file to assets/schema.png")
            
            # Placeholder rectangle for schema position
            st.markdown("""
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; width: 200px; height: 80px; text-align: center;">
                <p style="margin: 0; color: #666;">schema</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        **{get_translation('parameters', lang)}:**""")

        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
                **θ ({get_translation('theta', lang)})**: {get_translation('theta_desc', lang)}<br>
                **δ ({get_translation('delta', lang)})**: {get_translation('delta_desc', lang)}<br>
                **δ₁ ({get_translation('delta1', lang)})**: {get_translation('delta1_desc', lang)}<br>
                **δ₂ ({get_translation('delta2', lang)})**: {get_translation('delta2_desc', lang)}<br>
                **ε ({get_translation('epsilon', lang)})**: {get_translation('epsilon_desc', lang)}<br>
                **τ ({get_translation('tau', lang)})**: {get_translation('tau_desc', lang)}<br>
                **φ ({get_translation('phi', lang)})**: {get_translation('phi_desc', lang)}""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                **a**: {get_translation('a_desc', lang)}<br>
                **b**: {get_translation('b_desc', lang)}<br>
                **d**: {get_translation('d_desc', lang)}<br>
                **f**: {get_translation('f_desc', lang)}<br>
                **h**: {get_translation('h_desc', lang)}<br>
                **L**: {get_translation('L_desc', lang)}
                """, unsafe_allow_html=True)
    
    # Tab 2: Force Measurement
    with tabs[1]:
        st.subheader(get_translation("force_measurement_input", lang))
        
        # Display list of cables with force input fields
        st.markdown(f"### {get_translation('cable_force_inputs', lang)}")
        st.markdown(get_translation("enter_forces", lang))
        
        # Create a multi-column layout for cable inputs
        force_cols = st.columns(3)
        
        # Group cables by type for better organization
        cable_groups = {
            'rhs': {'name': get_translation("rhs", lang), 'cables': []},
            'tso': {'name': get_translation("tso", lang), 'cables': []},
            'tsu': {'name': get_translation("tsu", lang), 'cables': []},
            'fa': {'name': get_translation("fa", lang), 'cables': []},
            'sa': {'name': get_translation("sa", lang), 'cables': []},
            'zw': {'name': get_translation("zw", lang), 'cables': []}  # Add catching cables if missing
        }

        # Group cables by type, filtering out intermediate segments
        for cable_id, cable in st.session_state.barrier_config['cables'].items():
            cable_type = cable.get('type', '')
            
            # Check if this is an anchor-connected segment
            is_anchor_segment = False
            start_point = cable.get('start', '')
            end_point = cable.get('end', '')
            
            # Only include anchor-connected segments
            if (start_point in st.session_state.barrier_config['anchors'] or 
                end_point in st.session_state.barrier_config['anchors']):
                # This is an anchor-connected segment, include it
                if cable_type in cable_groups:
                    cable_groups[cable_type]['cables'].append((cable_id, cable))
                
                # Ensure it's marked as capable of having a load cell in the configuration
                st.session_state.barrier_config['cables'][cable_id]['can_have_load_cell'] = True
            else:
                # This is an intermediate segment, don't include it in the UI
                # But ensure it's marked as not capable of having a load cell in the configuration
                st.session_state.barrier_config['cables'][cable_id]['can_have_load_cell'] = False
                st.session_state.barrier_config['cables'][cable_id]['has_load_cell'] = False

        # Distribute cable groups across columns
        col_index = 0
        for group_type, group in cable_groups.items():
            # Only show groups that have cables
            if group['cables']:
                with force_cols[col_index % 3]:
                    st.markdown(f"#### {group['name']}")
                    
                    for cable_id, cable in group['cables']:
                        # Create a row for each cable with force input and load cell toggle
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Force input field
                            force = st.number_input(
                                f"{cable['name']} {get_translation('force_kn', lang)}", 
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
                                get_translation("load_cell", lang), 
                                value=cable['has_load_cell'],
                                key=f"load_cell_{cable_id}"
                            )
                            st.session_state.barrier_config['cables'][cable_id]['has_load_cell'] = has_load_cell
                    
                    st.markdown("---")
                
                col_index += 1
        
        # Save force measurements button
        if st.button(get_translation("save_force_measurements", lang)):
            save_barrier_config(st.session_state.username, st.session_state.barrier_config)
            st.success(get_translation("forces_saved", lang))
    
    # Tab 3: Results
    with tabs[2]:
        st.subheader(get_translation("force_calculation_results", lang))
        
        # Calculate forces based on current configuration
        results = calculate_forces(st.session_state.barrier_config)
        
        # Display result visualization
        st.markdown(f"### {get_translation('force_distribution_viz', lang)}")

        results_view_type = st.radio(
            get_translation("select_view_type", lang), 
            [
                get_translation("3d_view", lang),
                get_translation("2d_side_view", lang)
            ],
            horizontal=True,
            key="results_view_type",
            format_func=lambda x: x  # We're already passing translated values
        )
        
        # Display the selected view
        if results_view_type == get_translation("2d_side_view", lang):
            result_view = create_barrier_diagram(st.session_state.barrier_config, results)
            st.plotly_chart(result_view, use_container_width=True, key="results_view")
        else:  # 3D View
            result_3d_view = create_3d_view(st.session_state.barrier_config, results)
            st.plotly_chart(result_3d_view, use_container_width=True, key="results_3d_view")
        
        # Display total forces
        st.markdown(f"### {get_translation('total_forces', lang)}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(get_translation("total_anchor_force", lang), f"{results['total_anchor_force']:.1f} kN")
        
        with col2:
            st.metric(get_translation("total_support_force", lang), f"{results['total_support_force']:.1f} kN")
        
        # Display detailed results in tables
        st.markdown(f"### {get_translation('detailed_force_results', lang)}")
        
        # Create anchor results table
        anchor_data = []
        for anchor_id, anchor in st.session_state.barrier_config['anchors'].items():
            # Skip anchors without position data
            if 'position' not in anchor:
                continue
                
            if anchor_id.startswith('v'):  # Only include retention cable anchors
                anchor_data.append({
                    get_translation('anchor', lang): anchor.get('name', f"{get_translation('anchor', lang)} {anchor_id}"),
                    f"{get_translation('force', lang)} (kN)": round(results.get(anchor_id, 0), 1),
                    f"X ({get_translation('meter', lang)})": round(anchor['position'].get('x', 0), 2),
                    f"Y ({get_translation('meter', lang)})": round(anchor['position'].get('y', 0), 2),
                    f"Z ({get_translation('meter', lang)})": round(anchor['position'].get('z', 0), 2)
                })
        
        df_anchors = pd.DataFrame(anchor_data)
        
        # Create support results table
        support_data = []
        for support_id, support in st.session_state.barrier_config['supports'].items():
            # Skip supports without required data
            if 'base' not in support or 'top' not in support:
                continue
                
            support_data.append({
                get_translation('support', lang): support.get('name', f"{get_translation('support', lang)} {support_id}"),
                f"{get_translation('force', lang)} (kN)": round(results.get(support_id, 0), 1),
                f"{get_translation('base', lang)} X ({get_translation('meter', lang)})": round(support['base'].get('x', 0), 2),
                f"{get_translation('base', lang)} Y ({get_translation('meter', lang)})": round(support['base'].get('y', 0), 2),
                f"{get_translation('base', lang)} Z ({get_translation('meter', lang)})": round(support['base'].get('z', 0), 2),
                f"{get_translation('top', lang)} X ({get_translation('meter', lang)})": round(support['top'].get('x', 0), 2),
                f"{get_translation('top', lang)} Y ({get_translation('meter', lang)})": round(support['top'].get('y', 0), 2),
                f"{get_translation('top', lang)} Z ({get_translation('meter', lang)})": round(support['top'].get('z', 0), 2)
            })
        
        df_supports = pd.DataFrame(support_data)
        
        # Display tables
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown(f"#### {get_translation('anchor_forces', lang)}")
            st.dataframe(df_anchors, use_container_width=True)
        
        with col4:
            st.markdown(f"#### {get_translation('support_forces', lang)}")
            st.dataframe(df_supports, use_container_width=True)
    
    # Tab 4: Export
    with tabs[3]:
        st.subheader(get_translation("export_data", lang))
        
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
            label=get_translation("download_complete_config", lang),
            data=export_json,
            file_name="rockfall_barrier_analysis.json",
            mime="application/json"
        )
        
        # Export CSV options
        st.markdown(f"### {get_translation('export_results_csv', lang)}")
        
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
                        get_translation('anchor', lang): anchor.get('name', f"{get_translation('anchor', lang)} {anchor_id}"),
                        f"{get_translation('force', lang)} (kN)": round(results.get(anchor_id, 0), 1),
                        f"X ({get_translation('meter', lang)})": round(anchor['position'].get('x', 0), 2),
                        f"Y ({get_translation('meter', lang)})": round(anchor['position'].get('y', 0), 2),
                        f"Z ({get_translation('meter', lang)})": round(anchor['position'].get('z', 0), 2)
                    })
            
            df_anchors = pd.DataFrame(anchor_data)
            csv_anchors = df_anchors.to_csv(index=False)
            
            st.download_button(
                label=get_translation("download_anchor_forces_csv", lang),
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
                    get_translation('support', lang): support.get('name', f"{get_translation('support', lang)} {support_id}"),
                    f"{get_translation('force', lang)} (kN)": round(results.get(support_id, 0), 1),
                    f"{get_translation('base', lang)} X ({get_translation('meter', lang)})": round(support['base'].get('x', 0), 2),
                    f"{get_translation('base', lang)} Y ({get_translation('meter', lang)})": round(support['base'].get('y', 0), 2),
                    f"{get_translation('base', lang)} Z ({get_translation('meter', lang)})": round(support['base'].get('z', 0), 2),
                    f"{get_translation('top', lang)} X ({get_translation('meter', lang)})": round(support['top'].get('x', 0), 2),
                    f"{get_translation('top', lang)} Y ({get_translation('meter', lang)})": round(support['top'].get('y', 0), 2),
                    f"{get_translation('top', lang)} Z ({get_translation('meter', lang)})": round(support['top'].get('z', 0), 2)
                })
            
            df_supports = pd.DataFrame(support_data)
            csv_supports = df_supports.to_csv(index=False)
            
            st.download_button(
                label=get_translation("download_support_forces_csv", lang),
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
                get_translation('cable', lang): cable.get('name', f"{get_translation('cable', lang)} {cable_id}"),
                get_translation('type', lang): cable.get('type', '').upper(),
                f"{get_translation('force', lang)} (kN)": cable.get('force', 0) if cable.get('has_load_cell', False) else get_translation("no_measurement", lang),
                get_translation('has_load_cell', lang): get_translation("yes", lang) if cable.get('has_load_cell', False) else get_translation("no", lang),
                f"{get_translation('start', lang)} X": round(start_coords.get('x', 0), 2),
                f"{get_translation('start', lang)} Y": round(start_coords.get('y', 0), 2),
                f"{get_translation('start', lang)} Z": round(start_coords.get('z', 0), 2),
                f"{get_translation('end', lang)} X": round(end_coords.get('x', 0), 2),
                f"{get_translation('end', lang)} Y": round(end_coords.get('y', 0), 2),
                f"{get_translation('end', lang)} Z": round(end_coords.get('z', 0), 2)
            })
        
        df_cables = pd.DataFrame(cable_data)
        csv_cables = df_cables.to_csv(index=False)
        
        st.download_button(
            label=get_translation("download_cable_forces_csv", lang),
            data=csv_cables,
            file_name="cable_forces.csv",
            mime="text/csv",
            key="download_cables"
        )
        
        # Export all data in one JSON
        st.markdown(f"### {get_translation('export_all_data', lang)}")
        
        # Combine all data
        all_data = {
            get_translation('anchors', lang): df_anchors.to_dict(orient='records') if not df_anchors.empty else [],
            get_translation('supports', lang): df_supports.to_dict(orient='records'),
            get_translation('cables', lang): df_cables.to_dict(orient='records'),
            get_translation('total_anchor_force', lang): results.get('total_anchor_force', 0),
            get_translation('total_support_force', lang): results.get('total_support_force', 0),
            get_translation('parameters', lang): st.session_state.barrier_config.get('params', get_default_params())
        }
        
        # Convert to JSON
        all_json = json.dumps(all_data, indent=2)
        
        st.download_button(
            label=get_translation("download_all_json", lang),
            data=all_json,
            file_name="all_data.json",
            mime="application/json",
            key="download_all_json"
        )