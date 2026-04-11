from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
@home_bp.route("/home")
def home():
    items = ["Here's a list", "With a bunch of items", "Isn't this fun :)"]
    return render_template('home.html', heading='My App', items=items)