import numpy as np
import plotly.graph_objects as go
from modules.geometry import deg_to_rad, get_default_params
from modules.translations import get_translation
import streamlit as st

def create_barrier_diagram(barrier_config, results=None):
    """Create a 2D side view (x-z plane) diagram of the barrier"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    fig = go.Figure()
    
    # Extract configuration
    supports = barrier_config.get('supports', {})
    anchors = barrier_config.get('anchors', {})
    cables = barrier_config.get('cables', {})
    
    # Set up 2D view (x-z plane)
    # Find the min and max x values to set axis range
    x_values = []
    for anchor_id, anchor in anchors.items():
        if 'position' in anchor and 'x' in anchor['position']:
            x_values.append(anchor['position']['x'])
    
    for support_id, support in supports.items():
        if 'base' in support and 'x' in support['base']:
            x_values.append(support['base']['x'])
        if 'top' in support and 'x' in support['top']:
            x_values.append(support['top']['x'])
    
    # Default values if no valid points were found
    if not x_values:
        x_min, x_max = -10, 10
    else:
        x_min = min(x_values) - 5
        x_max = max(x_values) + 5
    
    # Horizontal line representing terrain
    terrain_x = [x_min, x_max]
    terrain_z = []
    
    # Use terrain inclination from params to calculate terrain profile
    params = barrier_config.get('params', get_default_params())
    phi_rad = deg_to_rad(params['phi'])
    
    for x in terrain_x:
        terrain_z.append(x * np.tan(phi_rad))
    
    # Add terrain line
    fig.add_trace(go.Scatter(
        x=terrain_x,
        y=terrain_z,
        mode='lines',
        line=dict(color='brown', width=2, dash='dash'),
        name=get_translation("terrain", lang)
    ))
    
    # Add supports
    for support_id, support in supports.items():
        # Skip if support doesn't have required fields
        if 'base' not in support or 'top' not in support:
            continue
            
        if 'x' not in support['base'] or 'z' not in support['base'] or 'x' not in support['top'] or 'z' not in support['top']:
            continue
            
        # Add support line
        support_name = support.get('name', f"{get_translation('support', lang)} {support_id}")
        
        fig.add_trace(go.Scatter(
            x=[support['base']['x'], support['top']['x']],
            y=[support['base']['z'], support['top']['z']],
            mode='lines+markers',
            line=dict(color='black', width=3),
            marker=dict(symbol='square', size=10, color='white', line=dict(color='black', width=2)),
            name=support_name,
            hovertext=f"{support_name}: {results.get(support_id, 0):.1f} kN" if results else support_name
        ))
        
        # Add support force annotation if results are provided
        if results:
            fig.add_annotation(
                x=support['base']['x'],
                y=support['base']['z'] - 1,
                text=f"{support_name}: {results.get(support_id, 0):.1f} kN",
                showarrow=False,
                font=dict(size=10, color='black'),
                bgcolor='white',
                bordercolor='black',
                borderwidth=1
            )
    
    # Add anchors
    for anchor_id, anchor in anchors.items():
        # Skip anchors without position data
        if 'position' not in anchor or 'x' not in anchor['position'] or 'z' not in anchor['position']:
            continue
            
        if anchor_id.startswith('v'):  # Only retention cable anchors in main view
            anchor_name = anchor.get('name', f"{get_translation('anchor', lang)} {anchor_id}")
            
            fig.add_trace(go.Scatter(
                x=[anchor['position']['x']],
                y=[anchor['position']['z']],
                mode='markers',
                marker=dict(symbol='cross', size=12, color='black'),
                name=anchor_name,
                hovertext=f"{anchor_name}: {results.get(anchor_id, 0):.1f} kN" if results else anchor_name
            ))
            
            # Add anchor force annotation if results are provided
            if results:
                fig.add_annotation(
                    x=anchor['position']['x'],
                    y=anchor['position']['z'] + 1,
                    text=f"{anchor_name}: {results.get(anchor_id, 0):.1f} kN",
                    showarrow=False,
                    font=dict(size=10, color='green'),
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1
                )
    
    # Add cables
    for cable_id, cable in cables.items():
        # Check if start_coords and end_coords are available
        if 'start_coords' not in cable or 'end_coords' not in cable:
            continue
            
        # Check if coordinates have required fields
        if 'x' not in cable['start_coords'] or 'z' not in cable['start_coords'] or 'x' not in cable['end_coords'] or 'z' not in cable['end_coords']:
            continue
            
        # Get start coordinates
        start_x = cable['start_coords']['x']
        start_z = cable['start_coords']['z']
        
        # Get end coordinates
        end_x = cable['end_coords']['x']
        end_z = cable['end_coords']['z']
        
        # Determine line style based on load cell presence
        line_dash = None if cable.get('has_load_cell', False) else 'dot'
        
        # Get cable name
        cable_name = cable.get('name', f"{get_translation('cable', lang)} {cable_id}")
        
        # Add cable line
        fig.add_trace(go.Scatter(
            x=[start_x, end_x],
            y=[start_z, end_z],
            mode='lines',
            line=dict(color=cable.get('color', 'gray'), width=2, dash=line_dash),
            name=cable_name,
            hovertext=f"{cable_name}: {cable.get('force', 0):.1f} kN" if cable.get('has_load_cell', False) else f"{cable_name}: {get_translation('no_measurement', lang)}"
        ))
        
        # Add load cell marker if applicable
        if cable.get('has_load_cell', False):
            # Place marker at middle of cable
            marker_x = (start_x + end_x) / 2
            marker_z = (start_z + end_z) / 2
            
            fig.add_trace(go.Scatter(
                x=[marker_x],
                y=[marker_z],
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=8,
                    color='white',
                    line=dict(color='black', width=1)
                ),
                showlegend=False,
                hovertext=f"{get_translation('load_cell', lang)}: {cable.get('force', 0):.1f} kN"
            ))
    
    # Update layout
    fig.update_layout(
        title=get_translation("barrier_diagram_title", lang),
        xaxis_title=f"X ({get_translation('meter', lang)})",
        yaxis_title=f"Z ({get_translation('meter', lang)})",
        template="plotly_white",
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def create_top_view(barrier_config):
    """Create a top view of the barrier (x-y plane)"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    fig = go.Figure()
    
    # Extract configuration
    supports = barrier_config.get('supports', {})
    anchors = barrier_config.get('anchors', {})
    cables = barrier_config.get('cables', {})
    
    # Add supports
    for support_id, support in supports.items():
        # Skip if base doesn't have required fields
        if 'base' not in support or 'x' not in support['base'] or 'y' not in support['base']:
            continue
            
        support_name = support.get('name', f"{get_translation('support', lang)} {support_id}")
        
        fig.add_trace(go.Scatter(
            x=[support['base']['x']],
            y=[support['base']['y']],
            mode='markers',
            marker=dict(symbol='square', size=10, color='white', line=dict(color='black', width=2)),
            name=support_name
        ))
    
    # Add anchors
    for anchor_id, anchor in anchors.items():
        # Skip anchors without position data
        if 'position' not in anchor or 'x' not in anchor['position'] or 'y' not in anchor['position']:
            continue
            
        anchor_name = anchor.get('name', f"{get_translation('anchor', lang)} {anchor_id}")
        
        fig.add_trace(go.Scatter(
            x=[anchor['position']['x']],
            y=[anchor['position']['y']],
            mode='markers',
            marker=dict(symbol='cross', size=12, color='black'),
            name=anchor_name
        ))
    
    # Add cables
    for cable_id, cable in cables.items():
        # Check if start_coords and end_coords are available
        if 'start_coords' not in cable or 'end_coords' not in cable:
            continue
            
        # Check if coordinates have required fields
        if 'x' not in cable['start_coords'] or 'y' not in cable['start_coords'] or 'x' not in cable['end_coords'] or 'y' not in cable['end_coords']:
            continue
            
        # Get start coordinates
        start_x = cable['start_coords']['x']
        start_y = cable['start_coords']['y']
        
        # Get end coordinates
        end_x = cable['end_coords']['x']
        end_y = cable['end_coords']['y']
        
        # Determine line style based on load cell presence
        line_dash = None if cable.get('has_load_cell', False) else 'dot'
        
        cable_name = cable.get('name', f"{get_translation('cable', lang)} {cable_id}")
        
        # Add cable line
        fig.add_trace(go.Scatter(
            x=[start_x, end_x],
            y=[start_y, end_y],
            mode='lines',
            line=dict(color=cable.get('color', 'gray'), width=2, dash=line_dash),
            name=cable_name
        ))
    
    # Update layout
    fig.update_layout(
        title=get_translation("top_view_title", lang),
        xaxis_title=f"X ({get_translation('meter', lang)})",
        yaxis_title=f"Y ({get_translation('meter', lang)})",
        template="plotly_white",
        height=400,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Make the plot square to preserve angle perception
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    
    return fig

def create_3d_view(barrier_config, results=None):
    """Create a 3D view of the barrier configuration"""
    # Get current language
    lang = st.session_state.get('language', 'en')
    
    fig = go.Figure()
    
    # Extract configuration
    supports = barrier_config.get('supports', {})
    anchors = barrier_config.get('anchors', {})
    cables = barrier_config.get('cables', {})
    
    # Find the min and max x and y values to set terrain range
    x_values = []
    y_values = []
    
    for anchor_id, anchor in anchors.items():
        if 'position' in anchor:
            if 'x' in anchor['position']:
                x_values.append(anchor['position']['x'])
            if 'y' in anchor['position']:
                y_values.append(anchor['position']['y'])
    
    for support_id, support in supports.items():
        if 'base' in support:
            if 'x' in support['base']:
                x_values.append(support['base']['x'])
            if 'y' in support['base']:
                y_values.append(support['base']['y'])
    
    # Default values if no valid points were found
    if not x_values:
        x_min, x_max = -10, 10
    else:
        x_min = min(x_values) - 5
        x_max = max(x_values) + 5
        
    if not y_values:
        y_min, y_max = -10, 10
    else:
        y_min = min(y_values) - 5
        y_max = max(y_values) + 5
    
    # Create a terrain mesh grid
    params = barrier_config.get('params', get_default_params())
    phi = params['phi']
    phi_rad = deg_to_rad(params['phi'])
    
    if phi == 90:
        # For vertical terrain, create a vertical plane at x=0
        n_points = 20
        
        # Create 2D arrays for the vertical plane
        y_grid = np.linspace(y_min, y_max, n_points)
        z_grid = np.linspace(-20, 20, n_points)
        y_grid, z_grid = np.meshgrid(y_grid, z_grid)
        
        # Fixed x position at 0
        x_grid = np.zeros_like(y_grid)

    elif phi >= 87:
        # Generate normal terrain grid points
        x_terrain = np.linspace(x_min, x_max, 50)
        y_terrain = np.linspace(y_min, y_max, 50)
        x_grid, y_grid = np.meshgrid(x_terrain, y_terrain)
        
        # Calculate z values using terrain inclination and clip to reasonable range
        z_grid = x_grid * np.tan(phi_rad)
        z_grid = np.clip(z_grid, -20, 20)  # Limit to -20 to +20 range
        x_grid = np.clip(x_grid, -1, 1)

    elif phi >= 85:
        # Generate normal terrain grid points
        x_terrain = np.linspace(x_min, x_max, 50)
        y_terrain = np.linspace(y_min, y_max, 50)
        x_grid, y_grid = np.meshgrid(x_terrain, y_terrain)
        
        # Calculate z values using terrain inclination and clip to reasonable range
        z_grid = x_grid * np.tan(phi_rad)
        z_grid = np.clip(z_grid, -20, 20)  # Limit to -20 to +20 range
        x_grid = np.clip(x_grid, -2, 2)
    
    elif phi >= 80:
        # Generate normal terrain grid points
        x_terrain = np.linspace(x_min, x_max, 50)
        y_terrain = np.linspace(y_min, y_max, 50)
        x_grid, y_grid = np.meshgrid(x_terrain, y_terrain)
        
        # Calculate z values using terrain inclination and clip to reasonable range
        z_grid = x_grid * np.tan(phi_rad)
        z_grid = np.clip(z_grid, -20, 20)  # Limit to -20 to +20 range
        x_grid = np.clip(x_grid, -4, 4)

    elif phi >= 70:
        # Generate normal terrain grid points
        x_terrain = np.linspace(x_min, x_max, 50)
        y_terrain = np.linspace(y_min, y_max, 50)
        x_grid, y_grid = np.meshgrid(x_terrain, y_terrain)
        
        # Calculate z values using terrain inclination and clip to reasonable range
        z_grid = x_grid * np.tan(phi_rad)
        z_grid = np.clip(z_grid, -25, 25)  # Limit to -20 to +20 range
        # x_grid = np.clip(x_grid, -4, 4)

    else:
        # Generate normal terrain grid points
        x_terrain = np.linspace(x_min, x_max, 20)
        y_terrain = np.linspace(y_min, y_max, 20)
        x_grid, y_grid = np.meshgrid(x_terrain, y_terrain)
        
        # Calculate z values using terrain inclination and clip to reasonable range
        z_grid = x_grid * np.tan(phi_rad)
        z_grid = np.clip(z_grid, -20, 20)  # Limit to -20 to +20 range
    
    # Add terrain surface (with hover disabled)
    fig.add_trace(go.Surface(
        x=x_grid,
        y=y_grid,
        z=z_grid,
        colorscale='Earth',
        opacity=0.8,
        showscale=False,
        name=get_translation("terrain", lang),
        hoverinfo='skip'  # Disable hover for terrain
    ))
    
    # Add supports as simple 3D lines with grey cube at base
    for support_id, support in supports.items():
        # Skip if support doesn't have required fields
        if 'base' not in support or 'top' not in support:
            continue
            
        # Check if coordinates are complete
        if ('x' not in support['base'] or 'y' not in support['base'] or 'z' not in support['base'] or
            'x' not in support['top'] or 'y' not in support['top'] or 'z' not in support['top']):
            continue
        
        # Get support name
        support_name = support.get('name', f"{get_translation('support', lang)} {support_id}")
        base_name = f"{get_translation('base', lang)} {support_name}"
        
        # Add grey cube at support base
        cube_size = 0.5  # Size of the cube
        fig.add_trace(go.Mesh3d(
            x=[
                support['base']['x'] - cube_size/2, support['base']['x'] + cube_size/2, support['base']['x'] + cube_size/2, support['base']['x'] - cube_size/2,
                support['base']['x'] - cube_size/2, support['base']['x'] + cube_size/2, support['base']['x'] + cube_size/2, support['base']['x'] - cube_size/2
            ],
            y=[
                support['base']['y'] - cube_size/2, support['base']['y'] - cube_size/2, support['base']['y'] + cube_size/2, support['base']['y'] + cube_size/2,
                support['base']['y'] - cube_size/2, support['base']['y'] - cube_size/2, support['base']['y'] + cube_size/2, support['base']['y'] + cube_size/2
            ],
            z=[
                support['base']['z'] - cube_size/4, support['base']['z'] - cube_size/4, support['base']['z'] - cube_size/4, support['base']['z'] - cube_size/4,
                support['base']['z'] + cube_size/4, support['base']['z'] + cube_size/4, support['base']['z'] + cube_size/4, support['base']['z'] + cube_size/4
            ],
            i=[0, 0, 0, 2, 2, 4],
            j=[1, 2, 3, 3, 6, 5],
            k=[2, 3, 7, 7, 7, 6],
            color='grey',
            opacity=1,
            flatshading=True,
            name=base_name,
            hoverinfo='skip'
        ))
            
        # Prepare hover text
        if results:
            hover_text = f"{support_name} - {results.get(support_id, 0):.1f} kN"
        else:
            hover_text = support_name
            
        # Add support as 3D line (just the line, no markers for top/bottom)
        fig.add_trace(go.Scatter3d(
            x=[support['base']['x'], support['top']['x']],
            y=[support['base']['y'], support['top']['y']],
            z=[support['base']['z'], support['top']['z']],
            mode='lines',  # Just lines, no markers
            line=dict(color='black', width=6),
            name=support_name,
            text=hover_text,
            hoverinfo='text'
        ))
    
    # Add anchors as 3D markers with cross symbol (like original depiction)
    for anchor_id, anchor in anchors.items():
        # Skip anchors without position data
        if 'position' not in anchor:
            continue
            
        # Skip if coordinates are incomplete
        if 'x' not in anchor['position'] or 'y' not in anchor['position'] or 'z' not in anchor['position']:
            continue
            
        # Determine anchor color based on type
        color = 'red' if anchor_id.startswith('v') else 'green'
        
        # Get anchor name
        anchor_name = anchor.get('name', f"{get_translation('anchor', lang)} {anchor_id}")
        
        # Prepare hover text
        if results:
            hover_text = f"{anchor_name}: {results.get(anchor_id, 0):.1f} kN"
        else:
            hover_text = anchor_name
        
        fig.add_trace(go.Scatter3d(
            x=[anchor['position']['x']],
            y=[anchor['position']['y']],
            z=[anchor['position']['z']],
            mode='markers',
            marker=dict(
                size=12,
                color=color,
                symbol='cross',  # Use cross symbol as in original visualization
                line=dict(color='black', width=1)
            ),
            name=anchor_name,
            text=hover_text,
            hoverinfo='text'
        ))
    
    # Add cables as 3D lines
    for cable_id, cable in cables.items():
        # Skip if cable data is incomplete
        if 'start_coords' not in cable or 'end_coords' not in cable:
            continue
            
        # Skip if coordinates are incomplete
        if ('x' not in cable['start_coords'] or 'y' not in cable['start_coords'] or 'z' not in cable['start_coords'] or
            'x' not in cable['end_coords'] or 'y' not in cable['end_coords'] or 'z' not in cable['end_coords']):
            continue
            
        # Get coordinates
        start_x = cable['start_coords']['x']
        start_y = cable['start_coords']['y']
        start_z = cable['start_coords']['z']
        end_x = cable['end_coords']['x']
        end_y = cable['end_coords']['y']
        end_z = cable['end_coords']['z']
        
        # Get cable color based on type
        color = cable.get('color', 'gray')
        
        # Get cable name
        cable_name = cable.get('name', f"{get_translation('cable', lang)} {cable_id}")
        
        # Prepare hover text
        if cable.get('has_load_cell', False):
            hover_text = f"{cable_name} - {cable.get('force', 0):.1f} kN"
        else:
            hover_text = f"{cable_name}: {get_translation('no_measurement', lang)}"
        
        # Add cable as 3D line
        fig.add_trace(go.Scatter3d(
            x=[start_x, end_x],
            y=[start_y, end_y],
            z=[start_z, end_z],
            mode='lines',
            line=dict(
                color=color,
                width=4,
                dash='solid' if cable.get('has_load_cell', False) else 'dash'
            ),
            name=cable_name,
            text=hover_text,
            hoverinfo='text'
        ))
        
        # Add load cell marker if applicable (now WHITE instead of yellow)
        if cable.get('has_load_cell', False):
            # Place marker at middle of cable
            marker_x = (start_x + end_x) / 2
            marker_y = (start_y + end_y) / 2
            marker_z = (start_z + end_z) / 2
            
            load_cell_name = f"{get_translation('load_cell', lang)}: {cable_name}"
            load_cell_text = f"{get_translation('load_cell', lang)}: {cable.get('force', 0):.1f} kN"
            
            fig.add_trace(go.Scatter3d(
                x=[marker_x],
                y=[marker_y],
                z=[marker_z],
                mode='markers',
                marker=dict(
                    size=6,
                    color='white',  # Changed from yellow to white
                    symbol='circle',
                    line=dict(color='black', width=1)
                ),
                name=load_cell_name,
                text=load_cell_text,
                hoverinfo='text',
                showlegend=False
            ))
    
    # Update layout for 3D view - DISABLE GRID LINES ON HOVER
    fig.update_layout(
        title=get_translation("3d_view_title", lang),
        scene=dict(
            xaxis=dict(
                title=f"X ({get_translation('meter', lang)})",
                showspikes=False,  # Disable hover grid lines
                showgrid=True,
                zeroline=True
            ),
            yaxis=dict(
                title=f"Y ({get_translation('meter', lang)})",
                showspikes=False,  # Disable hover grid lines
                showgrid=True,
                zeroline=True
            ),
            zaxis=dict(
                title=f"Z ({get_translation('meter', lang)})",
                showspikes=False,  # Disable hover grid lines
                showgrid=True,
                zeroline=True
            ),
            aspectmode='data'
        ),
        height=800,
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig