import os, dotenv, sys
from urllib import request

from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_login import LoginManager, login_user
from werkzeug.security import check_password_hash


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from extensions import db, mig, cors, login_manager

dotenv.load_dotenv()

# classes de configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY_APP')
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

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)

    with app.app_context():
        from models import User, Post, Like, Comment, Follow, Notification, Conversation, Message
        # Les modèles sont importés pour être détectés par Flask-Migrate


    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.follow import follow_bp
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
    app.register_blueprint(follow_bp)
    app.register_blueprint(post_bp)

    from admin import init_admin
    init_admin(app)

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login_page():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if user and user.is_admin and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                flash('Login incorrect ^^')
        return render_template("admin/login.html")

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
    
    @app.route('/cache-me')
    def cache():
        return "nginx will cache this response"
    
    @app.route('/info')
    def info():

        resp = {
            'connecting_ip': request.headers['X-Real-IP'],
            'proxy_ip': request.headers['X-Forwarded-For'],
            'host': request.headers['Host'],
            'user-agent': request.headers['User-Agent']
        }

        return jsonify(resp)

    @app.route('/health')
    def flask_health_check():
        return "success"

    return app

app = create_app()

# if __name__ == '__main__':
    # app.run()