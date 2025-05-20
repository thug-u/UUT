from dash import Dash
from config.shared_config import SERVER_CONFIG
from web.layout import create_layout
from web.callbacks import register_callbacks
import logging

logging.basicConfig(level=logging.DEBUG, filename='logs/dash.log')

def create_dash_app():
    app = Dash(
        __name__,
        assets_folder='assets',
        external_stylesheets=[
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
            'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'
        ]
    )
    
    # 레이아웃 설정
    app.layout = create_layout()
    
    # 콜백 등록
    register_callbacks(app)
    
    return app

def run_dash():
    create_dash_app().run(
        host=SERVER_CONFIG['flask_host'],
        port=SERVER_CONFIG['dash_port'],
        debug=False,
        use_reloader=False
    )