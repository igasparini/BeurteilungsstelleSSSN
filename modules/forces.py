def calculate_forces(barrier_config):
    """Calculate forces at each anchor and support based on measured cable forces"""
    results = {}
    
    # Get safe references to configuration components
    anchors = barrier_config.get('anchors', {})
    supports = barrier_config.get('supports', {})
    cables = barrier_config.get('cables', {})
    
    # Reset all anchor forces to 0
    for anchor_id in anchors:
        results[anchor_id] = 0.0
    
    # Reset all support forces to 0
    for support_id in supports:
        results[support_id] = 0.0
    
    # Iterate through cables to accumulate forces
    for cable_id, cable in cables.items():
        # Skip if no load cell or zero force
        if not cable.get('has_load_cell', False) or cable.get('force', 0) == 0:
            continue
        
        # Get start and end points
        start_point = cable.get('start', '')
        end_point = cable.get('end', '')
        
        # Add force to anchors
        if start_point in anchors:
            results[start_point] += cable.get('force', 0)
        elif end_point in anchors:
            results[end_point] += cable.get('force', 0)
        
        # Add force to supports
        if start_point in supports:
            results[start_point] += cable.get('force', 0)
        elif end_point in supports:
            results[end_point] += cable.get('force', 0)
    
    # Calculate total forces
    results['total_anchor_force'] = sum(results.get(a_id, 0) for a_id in anchors if a_id.startswith('v'))
    results['total_support_force'] = sum(results.get(s_id, 0) for s_id in supports)
    
    return results