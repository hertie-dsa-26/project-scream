from flask import Flask, render_template
from config import DevConfig


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes.home import home_bp
    from app.routes.predictions import predictions_bp
    from app.routes.explorer import explorer_bp
    from app.routes.details import details_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(predictions_bp, url_prefix="/predictions")
    app.register_blueprint(explorer_bp, url_prefix="/explorer")
    app.register_blueprint(details_bp, url_prefix="/details")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app
