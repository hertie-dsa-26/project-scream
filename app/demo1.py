from flask import Flask
from routes.home import home_bp
from routes.vis import vis_bp


app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(vis_bp)