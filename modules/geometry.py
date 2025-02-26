import numpy as np

def deg_to_rad(degrees):
    """Convert degrees to radians"""
    return degrees * np.pi / 180.0

def rad_to_deg(radians):
    """Convert radians to degrees"""
    return radians * 180.0 / np.pi

def calculate_tau(epsilon, h, L, f):
    """Calculate tau angle based on epsilon, h, L, and f"""
    epsilon_rad = deg_to_rad(epsilon)
    tau_rad = epsilon_rad + np.arctan2(h - L * np.sin(epsilon_rad), L * np.cos(epsilon_rad) + f)
    tau_deg = rad_to_deg(tau_rad)
    return round(tau_deg, 1)

def calculate_theta(d, h, L, epsilon, f):
    """Calculate theta angle based on a, h, L, epsilon, and f"""
    epsilon_rad = deg_to_rad(epsilon)
    numerator = d / 2
    denominator = np.sqrt((h - L * np.sin(epsilon_rad))**2 + (L * np.cos(epsilon_rad) + f)**2)
    theta_rad = np.arctan2(numerator, denominator)
    theta_deg = rad_to_deg(theta_rad)
    return round(theta_deg, 1)

def calculate_delta(L, b):
    """Calculate delta angle based on L and b"""
    delta_rad = np.arctan2(L, b)
    delta_deg = rad_to_deg(delta_rad)
    return round(delta_deg, 1)

def calculate_epsilon_from_tau(tau, h, L, f):
    """Calculate epsilon based on tau, h, L, and f"""
    tau_rad = deg_to_rad(tau)
    
    # Use a numerical approach with 1000 test points
    epsilon_range = np.linspace(0, 89, 1000)  # Avoid 90 degrees
    min_error = float('inf')
    best_epsilon = 10.0  # Default
    
    for eps in epsilon_range:
        eps_rad = deg_to_rad(eps)
        calculated_tau_rad = eps_rad + np.arctan2(h - L * np.sin(eps_rad), L * np.cos(eps_rad) + f)
        error = abs(calculated_tau_rad - tau_rad)
        
        if error < min_error:
            min_error = error
            best_epsilon = eps
    
    return round(best_epsilon, 1)

def calculate_d_from_theta(theta, h, L, epsilon, f):
    """Calculate d based on theta, h, L, epsilon, and f"""
    theta_rad = deg_to_rad(theta)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Compute denominator
    denominator = np.sqrt((h - L * np.sin(epsilon_rad))**2 + (L * np.cos(epsilon_rad) + f)**2)
    
    # Calculate d
    d = 2 * denominator * np.tan(theta_rad)
    
    return round(max(1.0, d), 1)  # Ensure a is at least the minimum value

def calculate_b_from_delta(delta, L):
    """Calculate b based on delta and L"""
    delta_rad = deg_to_rad(delta)
    
    # Avoid division by zero or very small tangent
    if delta_rad < 0.01 or np.abs(np.tan(delta_rad)) < 0.01:
        return 50.0  # A large default value
    
    # Calculate b
    b = L / np.tan(delta_rad)
    
    return round(max(0.5, b), 1)  # Ensure b is at least the minimum value

def get_default_params():
    """Return default parameter values with calculated angles"""
    base_params = {
        'num_supports': 4,
        # 'a': 10.0,
        'b': 8.0,
        'd': 10.0,
        'h': 6.0,
        'f': 0.5,
        'L': 5.0,
        'epsilon': 10.0,
        'phi': 15.0,
        'delta1': 0.0,
        'delta2': 0.0,
        'has_delta1': False,
        'has_delta2': False
    }
    
    theta = calculate_theta(
        base_params['d'], 
        base_params['h'], 
        base_params['L'], 
        base_params['epsilon'], 
        base_params['f']
    )
    
    delta = calculate_delta(
        base_params['L'], 
        base_params['b']
    )
    
    tau = calculate_tau(
        base_params['epsilon'], 
        base_params['h'], 
        base_params['L'], 
        base_params['f']
    )
    
    base_params['theta'] = theta
    base_params['delta'] = delta
    base_params['tau'] = tau
    
    return base_params

def calculate_3d_coordinates(params):
    """
    Calculate 3D coordinates for all components of the rockfall barrier
    based on the geometric parameters.
    """
    # Extract parameters
    # a = params['a']  # Distance between anchors of retention cables
    b = params['b']  # Distance between edge support and anchor of upper support cable
    d = params['d']  # Distance between supports
    f = params['f']  # Overhang of foundation
    h = params['h']  # Distance between support base and retention cable anchor
    L = params['L']  # Support length
    
    # Convert angles from degrees to radians
    theta = deg_to_rad(params['theta'])  # Angle between vertical and retention cable
    delta = deg_to_rad(params['delta'])  # Angle between horizontal and upper support cable
    delta1 = deg_to_rad(params['delta1']) if params['has_delta1'] else None  # Intermediate cable 1
    delta2 = deg_to_rad(params['delta2']) if params['has_delta2'] else None  # Intermediate cable 2
    epsilon = deg_to_rad(params['epsilon'])  # Support inclination relative to vertical
    tau = deg_to_rad(params['tau'])  # Angle between support axis and retention cable axis
    phi = deg_to_rad(params['phi'])  # Terrain inclination
    
    # Number of field sections (supports minus 1)
    num_fields = params['num_supports'] - 1
    
    # Total barrier length
    total_length = (num_fields * d)
    
    # Initialize dictionaries to store coordinates
    supports = {}
    anchors = {}
    cables = {}
    
    # Calculate terrain height at each position based on inclination
    def terrain_height(x):
        return x * np.tan(phi)
    
    # Calculate support positions and orientations
    for i in range(params['num_supports']):
        # Support base position (x, y, z)
        # Posts are placed along the y-axis with x=0
        x = 0
        y = i * d
        z = terrain_height(x)
        
        # Step 1: Calculate direction vector for support considering both inclinations
        # Normal to terrain is (-sin(phi), 0, cos(phi))
        # Rotate this normal by epsilon in the x-z plane
        normal_x = -np.sin(phi)
        normal_z = np.cos(phi)
        
        # Apply rotation by epsilon around y-axis to the normal vector
        # This gives the direction of the support
        support_dir_x = normal_x * np.cos(epsilon) - normal_z * np.sin(epsilon)
        support_dir_z = normal_x * np.sin(epsilon) + normal_z * np.cos(epsilon)
        
        # Normalize the direction vector
        dir_length = np.sqrt(support_dir_x**2 + support_dir_z**2)
        support_dir_x /= dir_length
        support_dir_z /= dir_length
        
        # Calculate top position using the normalized direction
        top_x = x + L * support_dir_x
        top_y = y  # y-coordinate remains the same
        top_z = z + L * support_dir_z
        
        supports[f's{i+1}'] = {
            'base': {'x': x, 'y': y, 'z': z},
            'top': {'x': top_x, 'y': top_y, 'z': top_z},
            'length': L,
            'name': f'S{i+1}'
        }
    
    # Calculate retention cable anchor positions
    num_anchors = params['num_supports'] + 1
    for i in range(num_anchors):
        # Determine position based on field structure
        if i == 0:  # First anchor
            x = h
            y = -d/2
        elif i == num_anchors-1:  # Last anchor
            x = h
            y = total_length + d/2
        else:
            # Intermediate anchors are at distance 'a' from the support line (x=0)
            # and aligned with the supports along the y-axis
            x = h
            y = (i-1) * d + d/2
        
        # Calculate anchor height based on terrain inclination
        z = terrain_height(x)
        
        # Add height offset h for retention cable anchors
        z_offset = h
        
        # Anchor position (x, y, z)
        anchors[f'v{i+1}'] = {
            'position': {'x': x, 'y': y, 'z': z + z_offset},
            'name': f'V{i+1}'
        }

    # Calculate positions for upper support cable anchors (more distant from supports)
    anchors['tso1_anchor'] = {
        'position': {'x': b, 'y': -b, 'z': terrain_height(b)},
        'name': 'Tso1 Anchor'
    }

    anchors['tso2_anchor'] = {
        'position': {'x': b, 'y': total_length + b, 'z': terrain_height(b)},
        'name': 'Tso2 Anchor'
    }

    # Calculate positions for lower support cable anchors (closer to supports)
    anchors['tsu1_anchor'] = {
        'position': {'x': -b, 'y': -b, 'z': terrain_height(-b)},
        'name': 'Tsu1 Anchor'
    }

    anchors['tsu2_anchor'] = {
        'position': {'x': -b, 'y': total_length + b, 'z': terrain_height(-b)},
        'name': 'Tsu2 Anchor'
    }
    
    # Calculate positions for lateral bracing anchors (seitliche Abspannung)
    anchors['sa1_anchor'] = {
        'position': {'x': 0, 'y': -b, 'z': terrain_height(0) - h/2},
        'name': 'Sa1 Anchor'
    }
    
    anchors['sa2_anchor'] = {
        'position': {'x': 0, 'y': total_length + b, 'z': terrain_height(0) - h/2},
        'name': 'Sa2 Anchor'
    }
    
    # Create retention cables (Rückhalteseile)
    for i in range(params['num_supports']):
        cable_id = f'rhs{i+1}'
        support_id = f's{i+1}'
        
        if i == 0:  # First support connects to first anchor
            anchor_id = 'v1'
        else:
            anchor_id = f'v{i+1}'
        
        cables[cable_id] = {
            'start': support_id,
            'end': anchor_id,
            'type': 'rhs',
            'name': f'Rhs {i+1}',
            'force': 0.0,
            'has_load_cell': True,
            'color': 'green',
            'start_coords': {
                'x': supports[support_id]['top']['x'],
                'y': supports[support_id]['top']['y'],
                'z': supports[support_id]['top']['z']
            },
            'end_coords': {
                'x': anchors[anchor_id]['position']['x'],
                'y': anchors[anchor_id]['position']['y'],
                'z': anchors[anchor_id]['position']['z']
            }
        }
        
    # Next retention cables
    for i in range(params['num_supports']):
        cable_id = f'rhs{i+params["num_supports"]+1}'
        support_id = f's{i+1}'
        
        if i == params['num_supports']-1:  # Last support connects to last anchor
            anchor_id = f'v{params["num_supports"]+1}'
        else:
            anchor_id = f'v{i+2}'
        
        cables[cable_id] = {
            'start': support_id,
            'end': anchor_id,
            'type': 'rhs',
            'name': f'Rhs {i+params["num_supports"]+1}',
            'force': 0.0,
            'has_load_cell': True,
            'color': 'green',
            'start_coords': {
                'x': supports[support_id]['top']['x'],
                'y': supports[support_id]['top']['y'],
                'z': supports[support_id]['top']['z']
            },
            'end_coords': {
                'x': anchors[anchor_id]['position']['x'],
                'y': anchors[anchor_id]['position']['y'],
                'z': anchors[anchor_id]['position']['z']
            }
        }
    
    # Create upper support cables (Tragseil oben)
    cables['tsoS1'] = {
        'start': 's1',
        'end': 'tso1_anchor',
        'type': 'tso',
        'name': 'Tso S1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports['s1']['top']['x'],
            'y': supports['s1']['top']['y'],
            'z': supports['s1']['top']['z']
        },
        'end_coords': {
            'x': anchors['tso1_anchor']['position']['x'],
            'y': anchors['tso1_anchor']['position']['y'],
            'z': anchors['tso1_anchor']['position']['z']
        }
    }
    
    cables['tsoS4'] = {
        'start': f's{params["num_supports"]}',
        'end': 'tso2_anchor',
        'type': 'tso',
        'name': f'Tso S{params["num_supports"]}',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports[f's{params["num_supports"]}']['top']['x'],
            'y': supports[f's{params["num_supports"]}']['top']['y'],
            'z': supports[f's{params["num_supports"]}']['top']['z']
        },
        'end_coords': {
            'x': anchors['tso2_anchor']['position']['x'],
            'y': anchors['tso2_anchor']['position']['y'],
            'z': anchors['tso2_anchor']['position']['z']
        }
    }
    
    # Create lower support cables (Tragseil unten)
    cables['tsuS1'] = {
        'start': 's1',
        'end': 'tsu1_anchor',
        'type': 'tsu',
        'name': 'Tsu S1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports['s1']['top']['x'],
            'y': supports['s1']['top']['y'],
            'z': supports['s1']['top']['z']
        },
        'end_coords': {
            'x': anchors['tsu1_anchor']['position']['x'],
            'y': anchors['tsu1_anchor']['position']['y'],
            'z': anchors['tsu1_anchor']['position']['z']
        }
    }
    
    cables['tsuS4'] = {
        'start': f's{params["num_supports"]}',
        'end': 'tsu2_anchor',
        'type': 'tsu',
        'name': f'Tsu S{params["num_supports"]}',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports[f's{params["num_supports"]}']['top']['x'],
            'y': supports[f's{params["num_supports"]}']['top']['y'],
            'z': supports[f's{params["num_supports"]}']['top']['z']
        },
        'end_coords': {
            'x': anchors['tsu2_anchor']['position']['x'],
            'y': anchors['tsu2_anchor']['position']['y'],
            'z': anchors['tsu2_anchor']['position']['z']
        }
    }
    
    # Create catching cables (Fangseile) between supports
    for i in range(params['num_supports'] - 1):
        cable_id = f'zwS{i+1}'
        start_id = f's{i+1}'
        end_id = f's{i+2}'
        
        cables[cable_id] = {
            'start': start_id,
            'end': end_id,
            'type': 'zw',
            'name': f'Zw S{i+1}',
            'force': 0.0,
            'has_load_cell': True,
            'color': 'gold',
            'start_coords': {
                'x': supports[start_id]['top']['x'],
                'y': supports[start_id]['top']['y'],
                'z': supports[start_id]['top']['z']
            },
            'end_coords': {
                'x': supports[end_id]['top']['x'],
                'y': supports[end_id]['top']['y'],
                'z': supports[end_id]['top']['z']
            }
        }
    
    # Create lateral bracing cables (seitliche Abspannung)
    cables['sa1'] = {
        'start': 's1',
        'end': 'sa1_anchor',
        'type': 'sa',
        'name': 'Sa 1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'blue',
        'start_coords': {
            'x': supports['s1']['top']['x'],
            'y': supports['s1']['top']['y'],
            'z': supports['s1']['top']['z']
        },
        'end_coords': {
            'x': anchors['sa1_anchor']['position']['x'],
            'y': anchors['sa1_anchor']['position']['y'],
            'z': anchors['sa1_anchor']['position']['z']
        }
    }
    
    cables['sa2'] = {
        'start': f's{params["num_supports"]}',
        'end': 'sa2_anchor',
        'type': 'sa',
        'name': 'Sa 2',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'blue',
        'start_coords': {
            'x': supports[f's{params["num_supports"]}']['top']['x'],
            'y': supports[f's{params["num_supports"]}']['top']['y'],
            'z': supports[f's{params["num_supports"]}']['top']['z']
        },
        'end_coords': {
            'x': anchors['sa2_anchor']['position']['x'],
            'y': anchors['sa2_anchor']['position']['y'],
            'z': anchors['sa2_anchor']['position']['z']
        }
    }
    
    # Create intermediate cables if specified
    if params['has_delta1']:
        # Implementation for intermediate cable 1
        pass
    
    if params['has_delta2']:
        # Implementation for intermediate cable 2
        pass
    
    # Return the complete barrier configuration
    barrier_config = {
        'supports': supports,
        'anchors': anchors,
        'cables': cables,
        'params': params  # Store the original parameters
    }
    
    return barrier_config