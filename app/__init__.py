from flask import Flask, render_template
from config import DevConfig


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes.home import home_bp
    from app.routes.vis import vis_bp
    from app.routes.eda import eda_bp
    from app.routes.models import models_bp
    from app.routes.predict import predict_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(vis_bp)
    app.register_blueprint(eda_bp, url_prefix="/eda")
    app.register_blueprint(models_bp, url_prefix="/models")
    app.register_blueprint(predict_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app
