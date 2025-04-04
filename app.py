import os, dotenv, sys
from flask import Flask, render_template
from flask_swagger_ui import get_swaggerui_blueprint


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from extensions import db, mig, cors

dotenv.load_dotenv()

# classes de configuration
class Config:
    SECRET_KEY_APP = os.environ.get('SECRET_KEY_APP')
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
    DEBUG = os.environ.get('FLASK_DEBUG')


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # autorise toutes les origines
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    mig.init_app(app, db)
    
    with app.app_context():
        from models import User, Post, Like, Comment, Follow, Notification, Conversation, Message
        # Les modèles sont importés pour être détectés par Flask-Migrate

    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.posts import post_bp

    # config of Swagger UI
    swagger_url = os.environ.get('SWAGGER_URL')
    api_url = os.environ.get('API_URL')


    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            'app_name': "Valenstagram API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/static/openapi.json')
    def serve_swagger_spec():
        with open('openapi.yml', 'r') as yaml_file:
            import yaml, json
            swagger_json = json.dumps(yaml.safe_load(yaml_file))
            return app.response_class(
                response=swagger_json,
                status=200,
                mimetype='application/json'
            )

    return app

app = create_app()

if __name__ == '__main__':
    app.run()