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
    """Calculate theta angle based on d, h, L, epsilon, and f"""
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
    
    return round(max(1.0, d), 1)  # Ensure d is at least 1.0

def calculate_b_from_delta(delta, L):
    """Calculate b based on delta and L"""
    delta_rad = deg_to_rad(delta)
    
    # Avoid division by zero or very small tangent
    if delta_rad < 0.01 or np.abs(np.tan(delta_rad)) < 0.01:
        return 50.0  # A large default value
    
    # Calculate b
    b = L / np.tan(delta_rad)
    
    return round(max(0.5, b), 1)  # Ensure b is at least 0.5

def calculate_L_from_delta_b(delta, b):
    """Calculate L from delta and b"""
    delta_rad = deg_to_rad(delta)
    L = b * np.tan(delta_rad)
    return round(max(1.0, L), 1)  # Ensure L is at least 1.0

def calculate_h_from_tau_epsilon_L_f(tau, epsilon, L, f):
    """Calculate h based on tau, epsilon, L, and f"""
    tau_rad = deg_to_rad(tau)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Rearrange the tau equation to solve for h
    h = L * np.sin(epsilon_rad) + np.tan(tau_rad - epsilon_rad) * (L * np.cos(epsilon_rad) + f)
    
    return round(max(0.5, h), 1)  # Ensure h is at least 0.5

def calculate_f_from_tau_epsilon_h_L(tau, epsilon, h, L):
    """Calculate f based on tau, epsilon, h, and L"""
    tau_rad = deg_to_rad(tau)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Rearrange the tau equation to solve for f
    denominator = np.tan(tau_rad - epsilon_rad)
    
    # Handle near-zero denominator
    if abs(denominator) < 0.001:
        return 0.5  # Default value
    
    f = (h - L * np.sin(epsilon_rad)) / denominator - L * np.cos(epsilon_rad)
    
    return round(max(0.1, f), 1)  # Ensure f is at least 0.1

def calculate_L_from_tau_epsilon_h_f(tau, epsilon, h, f):
    """Calculate L based on tau, epsilon, h, and f"""
    tau_rad = deg_to_rad(tau)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Use numerical approach with 1000 test points
    L_range = np.linspace(0.5, 20, 1000)  # Reasonable L range
    min_error = float('inf')
    best_L = 5.0  # Default
    
    for L_test in L_range:
        calculated_tau_rad = epsilon_rad + np.arctan2(
            h - L_test * np.sin(epsilon_rad), 
            L_test * np.cos(epsilon_rad) + f
        )
        error = abs(calculated_tau_rad - tau_rad)
        
        if error < min_error:
            min_error = error
            best_L = L_test
    
    return round(best_L, 1)

def calculate_epsilon_from_theta_d_h_L_f(theta, d, h, L, f):
    """Calculate epsilon based on theta, d, h, L, and f using numerical approach"""
    theta_rad = deg_to_rad(theta)
    
    # Use numerical approach with 1000 test points
    epsilon_range = np.linspace(0, 89, 1000)  # Avoid 90 degrees
    min_error = float('inf')
    best_epsilon = 10.0  # Default
    
    for eps in epsilon_range:
        eps_rad = deg_to_rad(eps)
        
        # Compute the denominator using the current epsilon value
        denominator = np.sqrt((h - L * np.sin(eps_rad))**2 + (L * np.cos(eps_rad) + f)**2)
        
        # Calculate theta for this epsilon
        calculated_theta_rad = np.arctan2(d/2, denominator)
        error = abs(calculated_theta_rad - theta_rad)
        
        if error < min_error:
            min_error = error
            best_epsilon = eps
    
    return round(best_epsilon, 1)

def calculate_h_from_theta_d_L_epsilon_f(theta, d, L, epsilon, f):
    """Calculate h based on theta, d, L, epsilon, and f"""
    theta_rad = deg_to_rad(theta)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Use numerical approach with 1000 test points
    h_range = np.linspace(0.5, 30, 1000)  # Reasonable h range
    min_error = float('inf')
    best_h = 6.0  # Default
    
    for h_test in h_range:
        # Compute denominator with the current h value
        denominator = np.sqrt((h_test - L * np.sin(epsilon_rad))**2 + (L * np.cos(epsilon_rad) + f)**2)
        
        # Calculate theta for this h
        calculated_theta_rad = np.arctan2(d/2, denominator)
        error = abs(calculated_theta_rad - theta_rad)
        
        if error < min_error:
            min_error = error
            best_h = h_test
    
    return round(best_h, 1)

def calculate_f_from_theta_d_h_L_epsilon(theta, d, h, L, epsilon):
    """Calculate f based on theta, d, h, L, and epsilon"""
    theta_rad = deg_to_rad(theta)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Use numerical approach with 1000 test points
    f_range = np.linspace(0.1, 10, 1000)  # Reasonable f range
    min_error = float('inf')
    best_f = 0.5  # Default
    
    for f_test in f_range:
        # Compute denominator with the current f value
        denominator = np.sqrt((h - L * np.sin(epsilon_rad))**2 + (L * np.cos(epsilon_rad) + f_test)**2)
        
        # Calculate theta for this f
        calculated_theta_rad = np.arctan2(d/2, denominator)
        error = abs(calculated_theta_rad - theta_rad)
        
        if error < min_error:
            min_error = error
            best_f = f_test
    
    return round(best_f, 1)

def calculate_L_from_theta_d_h_epsilon_f(theta, d, h, epsilon, f):
    """Calculate L based on theta, d, h, epsilon, and f"""
    theta_rad = deg_to_rad(theta)
    epsilon_rad = deg_to_rad(epsilon)
    
    # Use numerical approach with 1000 test points
    L_range = np.linspace(0.5, 20, 1000)  # Reasonable L range
    min_error = float('inf')
    best_L = 5.0  # Default
    
    for L_test in L_range:
        # Compute denominator with the current L value
        denominator = np.sqrt((h - L_test * np.sin(epsilon_rad))**2 + (L_test * np.cos(epsilon_rad) + f)**2)
        
        # Calculate theta for this L
        calculated_theta_rad = np.arctan2(d/2, denominator)
        error = abs(calculated_theta_rad - theta_rad)
        
        if error < min_error:
            min_error = error
            best_L = L_test
    
    return round(best_L, 1)

def recalculate_parameters(params, changed_param=None, new_value=None):
    """
    Recalculate all dependent parameters when one parameter changes.
    
    Args:
        params: Dictionary of current parameter values
        changed_param: Name of the parameter that was changed
        new_value: New value for the changed parameter
        
    Returns:
        Updated parameters dictionary
    """
    # Create a copy of the parameters
    updated_params = params.copy()
    
    # Update the changed parameter if provided
    if changed_param and new_value is not None:
        updated_params[changed_param] = new_value
    
    # Extract parameters for easier reference
    epsilon = updated_params.get('epsilon', 10.0)
    h = updated_params.get('h', 6.0)
    L = updated_params.get('L', 5.0)
    f = updated_params.get('f', 0.5)
    d = updated_params.get('d', 10.0)
    b = updated_params.get('b', 8.0)
    tau = updated_params.get('tau', 0.0)
    theta = updated_params.get('theta', 0.0)
    delta = updated_params.get('delta', 0.0)
    phi = updated_params.get('phi', 15.0)
    
    # Define which parameter was changed and update dependencies accordingly
    if changed_param == 'theta':
        updated_params['d'] = calculate_d_from_theta(
            new_value, h, L, epsilon, f
        )
        
    elif changed_param == 'tau':
        updated_params['epsilon'] = calculate_epsilon_from_tau(
            new_value, h, L, f
        )
        updated_params['theta'] = calculate_theta(
            updated_params['d'], h, L, updated_params['epsilon'], f
        )
        
    elif changed_param == 'delta':
        updated_params['b'] = calculate_b_from_delta(
            new_value, L
        )
        
    elif changed_param == 'epsilon':
        updated_params['tau'] = calculate_tau(
            new_value, h, L, f
        )
        updated_params['theta'] = calculate_theta(
            d, h, L, new_value, f
        )
        
    elif changed_param == 'd':
        updated_params['theta'] = calculate_theta(
            new_value, h, L, epsilon, f
        )
        
    elif changed_param == 'b':
        updated_params['delta'] = calculate_delta(
            L, new_value
        )
        
    elif changed_param == 'L':
        updated_params['tau'] = calculate_tau(
            epsilon, h, new_value, f
        )
        updated_params['theta'] = calculate_theta(
            d, h, new_value, epsilon, f
        )
        updated_params['delta'] = calculate_delta(
            new_value, b
        )
        
    elif changed_param == 'h':
        updated_params['tau'] = calculate_tau(
            epsilon, new_value, L, f
        )
        updated_params['theta'] = calculate_theta(
            d, new_value, L, epsilon, f
        )
        
    elif changed_param == 'f':
        updated_params['tau'] = calculate_tau(
            epsilon, h, L, new_value
        )
        updated_params['theta'] = calculate_theta(
            d, h, L, epsilon, new_value
        )

    elif changed_param == 'phi':
        pass
    
    # If no parameter was changed, calculate all dependent values
    else:
        updated_params['tau'] = calculate_tau(epsilon, h, L, f)
        updated_params['theta'] = calculate_theta(d, h, L, epsilon, f)
        updated_params['delta'] = calculate_delta(L, b)
    
    return updated_params

def validate_parameter_limits(params, param_name=None):
    """
    Validate that parameters are within acceptable ranges.
    
    Args:
        params: Dictionary of parameter values
        param_name: Optional specific parameter to validate
        
    Returns:
        Dictionary with validation results
    """
    # Define acceptable ranges for parameters
    param_limits = {
        'epsilon': (0, 80),    # Support inclination (degrees)
        'h': (0.5, 30),        # Distance between support foot and anchoring (m)
        'L': (1, 20),          # Support length (m)
        'f': (0.1, 10),        # Foundation overhang (m)
        'd': (1, 50),          # Distance between supports (m)
        'b': (0.5, 50),        # Distance between edge support and anchor (m)
        'delta': (0, 89),      # Angle between horizontal and upper support beam (degrees)
        'theta': (0, 89),      # Angle between vertical and retaining cable (degrees)
        'tau': (0, 89),        # Angle between support axis and retaining cable axis (degrees)
        'phi': (0, 90),
    }
    
    validation_results = {}
    
    # Check specific parameter or all parameters
    params_to_check = [param_name] if param_name else param_limits.keys()
    
    for param in params_to_check:
        if param in params and param in param_limits:
            min_val, max_val = param_limits[param]
            value = params[param]
            
            # Check if parameter is within limits
            is_valid = min_val <= value <= max_val
            message = ""
            
            if not is_valid:
                if value < min_val:
                    message = f"{param} is below minimum value of {min_val}"
                else:
                    message = f"{param} exceeds maximum value of {max_val}"
            
            validation_results[param] = {
                'valid': is_valid,
                'message': message,
                'min': min_val,
                'max': max_val,
                'value': value
            }
    
    return validation_results

def update_parameter(params, param_name, new_value):
    """
    Update a single parameter and recalculate all dependent parameters.
    This is the main entry point for the UI when a parameter is changed.
    
    Args:
        params: Dictionary of current parameter values
        param_name: Name of the parameter being updated
        new_value: New value for the parameter
        
    Returns:
        Updated parameters dictionary and list of parameters that changed
    """
    # Store original values to track changes
    original_values = params.copy()
    
    # Call recalculate_parameters to update all dependent parameters
    updated_params = recalculate_parameters(params, param_name, new_value)
    
    # Track which parameters changed (for UI highlighting/updates)
    changed_params = []
    for key in updated_params:
        if key in original_values and updated_params[key] != original_values[key]:
            changed_params.append(key)
    
    return updated_params, changed_params

def apply_parameter_changes(params, param_name, new_value):
    """
    Apply parameter changes with validation and constraints.
    This is the main function to call when a parameter is changed by the user.
    
    Args:
        params: Current parameter values
        param_name: Name of parameter being changed
        new_value: New value for the parameter
        
    Returns:
        Tuple containing:
        - Updated parameters
        - List of parameters that changed
        - Validation results
        - Warning messages (if any)
    """
    warnings = []
    
    # First validate the new value
    test_params = params.copy()
    test_params[param_name] = new_value
    validation = validate_parameter_limits(test_params, param_name)
    
    # If the new value is invalid, adjust it to be within limits
    if param_name in validation and not validation[param_name]['valid']:
        if new_value < validation[param_name]['min']:
            new_value = validation[param_name]['min']
            warnings.append(f"{param_name} adjusted to minimum value of {new_value}")
        elif new_value > validation[param_name]['max']:
            new_value = validation[param_name]['max']
            warnings.append(f"{param_name} adjusted to maximum value of {new_value}")
    
    # Update parameter and recalculate dependencies
    updated_params, changed_params = update_parameter(params, param_name, new_value)
    
    # Validate all parameters that changed
    full_validation = validate_parameter_limits(updated_params)
    
    # Check if any derived parameters are outside their limits
    for param in changed_params:
        if param in full_validation and not full_validation[param]['valid']:
            if updated_params[param] < full_validation[param]['min']:
                updated_params[param] = full_validation[param]['min']
                warnings.append(f"{param} was constrained to minimum value of {updated_params[param]}")
            elif updated_params[param] > full_validation[param]['max']:
                updated_params[param] = full_validation[param]['max']
                warnings.append(f"{param} was constrained to maximum value of {updated_params[param]}")
    
    # If any dependent parameters were constrained, recalculate everything one more time
    if warnings:
        updated_params = recalculate_parameters(updated_params)
        # Update the changed parameters list
        changed_params = [param for param in updated_params if updated_params[param] != params[param]]
    
    return updated_params, changed_params, full_validation, warnings

def get_default_params():
    """Return default parameter values with calculated angles"""
    base_params = {
        'num_supports': 4,
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

# Keep the existing calculate_3d_coordinates function
def calculate_3d_coordinates(params):
    """
    Calculate 3D coordinates for all components of the rockfall barrier
    based on the geometric parameters.
    """
    b = params['b']
    d = params['d']
    f = params['f']
    h = params['h']
    L = params['L']
    
    theta = deg_to_rad(params['theta'])
    delta = deg_to_rad(params['delta'])
    delta1 = deg_to_rad(params['delta1']) if params['has_delta1'] else None
    delta2 = deg_to_rad(params['delta2']) if params['has_delta2'] else None
    epsilon = deg_to_rad(params['epsilon'])  
    tau = deg_to_rad(params['tau'])
    phi = deg_to_rad(params['phi'])
    
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

# ======= SUPPORTS =======

    # Calculate support positions and orientations
    for i in range(params['num_supports']):
        # Support base position (x, y, z)
        # Posts are placed along the y-axis with x=0
        x = 0
        y = i * d
        z = 0
        
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

# ======= ANCHORS =======

    # Calculate position for retention cable anchors
    num_anchors = params['num_supports'] + 1
    for i in range(num_anchors):
        if i == 0:  # First anchor
            y = -d/2
        elif i == num_anchors-1:  # Last anchor
            y = total_length + d/2
        else:
            y = (i-1) * d + d/2
        
        x = np.cos(phi) * h
        z = np.sin(phi) * h

        anchors[f'v{i+1}'] = {
            'position': {'x': x, 'y': y, 'z': z},
            'name': f'V{i+1}'
        }

    # Calculate positions for upper support cable anchors
    anchors['tso1_anchor'] = {
        'position': {'x': 0, 'y': -b, 'z': 0},
        'name': 'Tso1 Anchor'
    }

    anchors['tso2_anchor'] = {
        'position': {'x': 0, 'y': total_length + b, 'z': 0},
        'name': 'Tso2 Anchor'
    }

    # Calculate positions for lower support cable anchors (closer to supports)
    anchors['tsu1_anchor'] = {
        'position': {'x': 0, 'y': -b + 1.5, 'z': 0},
        'name': 'Tsu1 Anchor'
    }

    anchors['tsu2_anchor'] = {
        'position': {'x': 0, 'y': total_length + b - 1.5, 'z': 0},
        'name': 'Tsu2 Anchor'
    }
    
    # Calculate positions for lateral bracing anchors (seitliche Abspannung)
    anchors['sa1_anchor'] = {
        'position': {'x': 0, 'y': -b, 'z': 0},
        'name': 'Sa1 Anchor'
    }
    
    anchors['sa2_anchor'] = {
        'position': {'x': 0, 'y': total_length + b, 'z': 0},
        'name': 'Sa2 Anchor'
    }

# ======= CABLES =======

## RETENTION CABLES (Rückhalteseile)
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
    
## UPPER SUPPORT CABLES (Tragseil oben)
    # First segment: First anchor to first support top
    cables['tso_a1s1'] = {
        'start': 'tso1_anchor',
        'end': 's1',
        'type': 'tso',
        'name': 'Tso A1-S1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': anchors['tso1_anchor']['position']['x'],
            'y': anchors['tso1_anchor']['position']['y'],
            'z': anchors['tso1_anchor']['position']['z']
        },
        'end_coords': {
            'x': supports['s1']['top']['x'],
            'y': supports['s1']['top']['y'],
            'z': supports['s1']['top']['z']
        }
    }

    # Middle segments: Support top to next support top
    for i in range(1, params['num_supports']):
        start_id = f's{i}'
        end_id = f's{i+1}'
        cable_id = f'tso_s{i}s{i+1}'
        
        cables[cable_id] = {
            'start': start_id,
            'end': end_id,
            'type': 'tso',
            'name': f'Tso S{i}-S{i+1}',
            'force': 0.0,
            'has_load_cell': False,
            'color': 'red',
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

    # Last segment: Last support top to second anchor
    last_support = f's{params["num_supports"]}'
    cables[f'tso_s{params["num_supports"]}a2'] = {
        'start': last_support,
        'end': 'tso2_anchor',
        'type': 'tso',
        'name': f'Tso S{params["num_supports"]}-A2',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports[last_support]['top']['x'],
            'y': supports[last_support]['top']['y'],
            'z': supports[last_support]['top']['z']
        },
        'end_coords': {
            'x': anchors['tso2_anchor']['position']['x'],
            'y': anchors['tso2_anchor']['position']['y'],
            'z': anchors['tso2_anchor']['position']['z']
        }
    }
    
## LOWER SUPPORT CABLES (Tragseil unten)
    # First segment: First anchor to first support base
    cables['tsu_a1s1'] = {
        'start': 'tsu1_anchor',
        'end': 's1',
        'type': 'tsu',
        'name': 'Tsu A1-S1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': anchors['tsu1_anchor']['position']['x'],
            'y': anchors['tsu1_anchor']['position']['y'],
            'z': anchors['tsu1_anchor']['position']['z']
        },
        'end_coords': {
            'x': supports['s1']['base']['x'],
            'y': supports['s1']['base']['y'],
            'z': supports['s1']['base']['z']
        }
    }

    # Middle segments: Support base to next support base
    for i in range(1, params['num_supports']):
        start_id = f's{i}'
        end_id = f's{i+1}'
        cable_id = f'tsu_s{i}s{i+1}'
        
        cables[cable_id] = {
            'start': start_id,
            'end': end_id,
            'type': 'tsu',
            'name': f'Tsu S{i}-S{i+1}',
            'force': 0.0,
            'has_load_cell': False,
            'color': 'red',
            'start_coords': {
                'x': supports[start_id]['base']['x'],
                'y': supports[start_id]['base']['y'],
                'z': supports[start_id]['base']['z']
            },
            'end_coords': {
                'x': supports[end_id]['base']['x'],
                'y': supports[end_id]['base']['y'],
                'z': supports[end_id]['base']['z']
            }
        }

    # Last segment: Last support base to second anchor
    last_support = f's{params["num_supports"]}'
    cables[f'tsu_s{params["num_supports"]}a2'] = {
        'start': last_support,
        'end': 'tsu2_anchor',
        'type': 'tsu',
        'name': f'Tsu S{params["num_supports"]}-A2',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'red',
        'start_coords': {
            'x': supports[last_support]['base']['x'],
            'y': supports[last_support]['base']['y'],
            'z': supports[last_support]['base']['z']
        },
        'end_coords': {
            'x': anchors['tsu2_anchor']['position']['x'],
            'y': anchors['tsu2_anchor']['position']['y'],
            'z': anchors['tsu2_anchor']['position']['z']
        }
    }
    
# CATCHING CABLES (Fangseile) between supports
    # Calculate intermediate heights (50% of the way up each support)
    for i in range(params['num_supports']):
        support_id = f's{i+1}'
        # Calculate intermediate position for this support (50% height)
        mid_x = (supports[support_id]['base']['x'] + supports[support_id]['top']['x']) / 2
        mid_y = supports[support_id]['base']['y']  # Keep same y-coordinate as base
        mid_z = (supports[support_id]['base']['z'] + supports[support_id]['top']['z']) / 2
        
        # Add mid-point to support data
        if 'mid' not in supports[support_id]:
            supports[support_id]['mid'] = {}
        
        supports[support_id]['mid'] = {
            'x': mid_x,
            'y': mid_y,
            'z': mid_z
        }

    # First segment: First anchor to first support mid-point
    cables['zw_a1s1'] = {
        'start': 'tso1_anchor',  # Using upper support cable anchor
        'end': 's1',
        'type': 'zw',
        'name': 'Zw A1-S1',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'gold',
        'start_coords': {
            'x': anchors['tso1_anchor']['position']['x'],
            'y': anchors['tso1_anchor']['position']['y'],
            'z': anchors['tso1_anchor']['position']['z']
        },
        'end_coords': {
            'x': supports['s1']['mid']['x'],
            'y': supports['s1']['mid']['y'],
            'z': supports['s1']['mid']['z']
        }
    }

    # Middle segments: Connect intermediate points between supports
    for i in range(1, params['num_supports']):
        start_id = f's{i}'
        end_id = f's{i+1}'
        cable_id = f'zw_s{i}s{i+1}'
        
        cables[cable_id] = {
            'start': start_id,
            'end': end_id,
            'type': 'zw',
            'name': f'Zw S{i}-S{i+1}',
            'force': 0.0,
            'has_load_cell': False,
            'color': 'gold',
            'start_coords': {
                'x': supports[start_id]['mid']['x'],
                'y': supports[start_id]['mid']['y'],
                'z': supports[start_id]['mid']['z']
            },
            'end_coords': {
                'x': supports[end_id]['mid']['x'],
                'y': supports[end_id]['mid']['y'],
                'z': supports[end_id]['mid']['z']
            }
        }

    # Last segment: Last support mid-point to second anchor
    last_support = f's{params["num_supports"]}'
    cables[f'zw_s{params["num_supports"]}a2'] = {
        'start': last_support,
        'end': 'tso2_anchor',  # Using upper support cable anchor
        'type': 'zw',
        'name': f'Zw S{params["num_supports"]}-A2',
        'force': 0.0,
        'has_load_cell': True,
        'color': 'gold',
        'start_coords': {
            'x': supports[last_support]['mid']['x'],
            'y': supports[last_support]['mid']['y'],
            'z': supports[last_support]['mid']['z']
        },
        'end_coords': {
            'x': anchors['tso2_anchor']['position']['x'],
            'y': anchors['tso2_anchor']['position']['y'],
            'z': anchors['tso2_anchor']['position']['z']
        }
    }
    
## LATERAL BRACING CABLES (seitliche Abspannung)
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

def calculate_3d_coordinates_with_params(base_params, **param_changes):
    """
    Calculate 3D coordinates with parameter changes.
    This is a wrapper around calculate_3d_coordinates that handles parameter interdependencies.
    
    Args:
        base_params: Base parameter values
        **param_changes: Keyword arguments for parameters to change
        
    Returns:
        Updated barrier configuration
    """
    # Start with base parameters
    updated_params = base_params.copy()
    
    # Apply each parameter change, calculating interdependencies
    for param_name, new_value in param_changes.items():
        updated_params, _, _, _ = apply_parameter_changes(updated_params, param_name, new_value)
    
    # Calculate 3D coordinates with the updated parameters
    return calculate_3d_coordinates(updated_params)