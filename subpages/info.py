from flask import Blueprint, render_template

info = Blueprint("info", __name__, static_folder="static", template_folder="template")

@info.route("/about")
def about():
    # TODO: Create about
    return render_template("info/about.html", pth="about")

@info.route("terms-of-service")
def tos():
    # TODO: Create ToS
    pass
