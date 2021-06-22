from datetime import timedelta
from math import floor, ceil
from os import getcwd
from pathlib import Path

from flask import Blueprint, render_template, request, flash, redirect, url_for

from subpages.apps import *

app = Blueprint("app", __name__, static_folder="static", template_folder="template")
app.register_blueprint(collarname, url_prefix="/collar-name")


@app.route("/", methods=["GET", "POST"])
def index():
    if "catpass" in request.args:
        p = request.args["catpass"]
        if not (Path(getcwd() + "/templates/app/privateindex") / (p + ".html")).is_file() or "/" in p:
            flash("Invalid Passphrase", 'warning')
            return redirect(url_for("app.index"))
        return render_template("app/index.html", rp={"app": "Apps"}, private="app/privateindex/{}.html"
                               .format(p))
    elif request.method == "POST":
        return redirect(url_for("app.index", catpass=request.form["passphrase"]))
    else:
        return render_template("app/index.html", rp={"app": "Apps"})


@app.route("/time-calculator", methods=["GET", "POST"])
def time_calculator():
    def time_calc(multiplier):
        return timedelta(seconds=256 * (multiplier - 1) + 128)

    if request.method == "POST":
        f = {i: (int(j) if ["hour", "minute", "second"] else j) for i, j in request.form.items()}
        seconds = f["hour"] * 3600 + f["minute"] * 60 + f["second"]
        if seconds == 0:
            flash("Time can't be 0", 'warning')
            return redirect(request.url)
        cm = (seconds - 128) / 256
        cm += 1
        if ceil(cm) > 320:
            flash("Time too large", 'warning')
            return redirect(request.url)
        elif cm.is_integer():
            return render_template("app/time-calculator.html", data={"exact": int(cm),
                                                                     "time": str(timedelta(seconds=seconds))})
        else:
            lower = floor(cm)
            higher = ceil(cm)
            return render_template("app/time-calculator.html",
                                   data={"lower": lower, "higher": higher, "lower_time": time_calc(lower),
                                         "higher_time": time_calc(higher), "target": str(timedelta(seconds=seconds))})
    else:
        return render_template("app/time-calculator.html")
