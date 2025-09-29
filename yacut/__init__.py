import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

db = SQLAlchemy()

migrate = Migrate()

csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(16).hex())
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DISK_TOKEN'] = os.getenv('DISK_TOKEN')

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .views import index_bp
    from .api_views import api_bp
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app


app = create_app()