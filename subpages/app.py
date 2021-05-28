from flask import Blueprint, render_template
from subpages.apps.collarname import collarname

app = Blueprint("app", __name__, static_folder="static", template_folder="template")
app.register_blueprint(collarname, url_prefix="/collar-name")

@app.route("/")
def index():
    return render_template("app/index.html", pth="app")
