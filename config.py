# Global configuration settings
APP_TITLE = "Beurteilungsstelle Steinschlagschutznetze"
COPYRIGHT = "© 2025 Beurteilungsstelle Steinschlagschutznetze. All Rights Reserved."

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

# File paths
USERS_FILE = "users.json"

# Cable type definitions
CABLE_TYPES = {
    'rhs': {'name': 'Retention Cables (Rhs)', 'color': 'green'},
    'tso': {'name': 'Upper Support Cables (Tso)', 'color': 'red'},
    'tsu': {'name': 'Lower Support Cables (Tsu)', 'color': 'red'},
    'fa': {'name': 'Catching Cables (Fa)', 'color': 'gold'},
    'sa': {'name': 'Lateral Bracing (Sa)', 'color': 'blue'}
}

# Custom CSS for styling
CUSTOM_CSS = """
<style>
.centered-title {
    text-align: center;
    margin-bottom: 20px;
}
.tool-card {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 10px;
    text-align: center;
    height: 100%;
    transition: all 0.3s;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    margin-bottom: 10px;
}
.tool-card:hover {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
    background-color: #f8f9fa;
}
.logo-container {
    text-align: center;
    margin-bottom: 40px;
}
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    border-radius: 10px;
    background-color: #f8f9fa;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
"""