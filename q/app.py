from flask import Flask
from config import Config
from extensions import db  
from routes.report import report_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)       
    from models import Item, Stock, Incoming, Outgoing   
    # استيراد الـ Blueprints
    from routes.main import main_bp
    from routes.incoming import incoming_bp
    from routes.outgoing import outgoing_bp
    from routes.search  import search_bp

    # ➌ تسجيل الـ Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(incoming_bp, url_prefix='/incoming')
    app.register_blueprint(outgoing_bp, url_prefix='/outgoing')
    app.register_blueprint(search_bp,   url_prefix='/search')
    app.register_blueprint(report_bp, url_prefix='/report')

   
    return app

