import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    """Función que crea y configura la aplicación Flask."""

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para continuar'
    login_manager.login_message_category = 'warning'

    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Gemini configurado correctamente")
    else:
        print("⚠️  Advertencia: GEMINI_API_KEY no encontrada en .env")

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.dashboard_api import bp as dashboard_api_bp
    from app.routes.reportes import bp as reportes_bp
    from app.routes.ia_hermes import bp as ia_hermes_bp
    from app.routes.clients import bp as clients_bp
    from app.routes.suppliers import bp as suppliers_bp
    from app.routes.products import bp as products_bp
    from app.routes.orders import bp as orders_bp
    from app.routes.shipments import bp as shipments_bp
    from app.routes.placeholder import bp as placeholder_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dashboard_api_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(ia_hermes_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(shipments_bp)
    app.register_blueprint(placeholder_bp)

    return app