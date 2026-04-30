from flask import Blueprint, render_template

models_bp = Blueprint("models", __name__)


@models_bp.route("/")
def index():
    return render_template("models/index.html")
