import json
import streamlit as st
from modules.geometry import get_default_params, calculate_3d_coordinates

def init_barrier_config():
    """Create a new barrier configuration with default parameters"""
    params = get_default_params()
    return calculate_3d_coordinates(params)

def load_barrier_config(username):
    """Load barrier configuration for a specific user"""
    try:
        with open(f"{username}_barrier_config.json", "r") as f:
            config = json.load(f)
            
            # Ensure 'params' key exists
            if 'params' not in config:
                config['params'] = get_default_params()
                
            # Ensure required structure exists
            if 'supports' not in config:
                config['supports'] = {}
            if 'anchors' not in config:
                config['anchors'] = {}
            if 'cables' not in config:
                config['cables'] = {}
                
            return config
    except FileNotFoundError:
        # Return default config if no saved config exists
        return init_barrier_config()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return init_barrier_config()

def save_barrier_config(username, config):
    """Save barrier configuration for a specific user"""
    # Ensure params exists
    if 'params' not in config:
        config['params'] = get_default_params()
        
    try:
        with open(f"{username}_barrier_config.json", "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        st.error(f"Error saving configuration: {e}")