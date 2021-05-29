from flask import Blueprint, render_template

info = Blueprint("info", __name__, static_folder="static", template_folder="template")

@info.route("/about")
def about():
    return render_template("info/about.html", pth="about")

@info.route("/about/blank")
@info.route("/about/blank_dvth")
def aboutblank():
    return '<p style="color:white">Get it? About BLANK? about:blank?</p>'

@info.route("terms-of-service")
def tos():
    return render_template("info/termsofservice.html", pth="terms-of-service")

@info.route("privacy-policy")
def privacy_policy():
    return render_template("info/privacypolicy.html", pth="privacy-policy")

@info.route("cookie-policy")
def cookie_policy():
    return render_template("info/cookiepolicy.html", pth="cookie-policy")
