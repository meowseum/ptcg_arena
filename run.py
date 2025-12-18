import os
from app import create_app
from app.auth import init_oauth

# Determine configuration
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

# Initialize OAuth with app
init_oauth(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
