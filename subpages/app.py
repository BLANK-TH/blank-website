from flask import Blueprint, render_template, request, flash, redirect, url_for
from subpages.apps import *
from pathlib import Path
from os import getcwd

app = Blueprint("app", __name__, static_folder="static", template_folder="template")
app.register_blueprint(collarname, url_prefix="/collar-name")

@app.route("/", methods=["GET", "POST"])
def index():
    if "catpass" in request.args:
        p = request.args["catpass"]
        if not (Path(getcwd() + "/templates/app/privateindex") / (p + ".html")).is_file() or "/" in p:
            flash("Invalid Passphrase", 'warning')
            return redirect(url_for("app.index"))
        return render_template("app/index.html", pth="app", rp={"app": "Apps"}, private="app/privateindex/{}.html"
                               .format(p))
    elif request.method == "POST":
        return redirect(url_for("app.index", catpass=request.form["passphrase"]))
    else:
        return render_template("app/index.html", pth="app", rp={"app":"Apps"})
