from flask import Blueprint, render_template

eda_bp = Blueprint("eda", __name__)


@eda_bp.route("/")
def index():
    return render_template("eda/index.html")
