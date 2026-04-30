from flask import Blueprint, render_template, request

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    if request.method == "POST":
        # --- model inference goes here ---
        # inputs = request.form
        # prediction = model.predict(...)
        result = "Model not yet trained — prediction unavailable."
    return render_template("predict.html", result=result)
