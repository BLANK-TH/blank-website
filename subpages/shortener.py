from flask import Blueprint, render_template, request, url_for, redirect, flash, abort, Markup
from api_helper import mongo_client
from random import choice
from string import ascii_letters
from re import match

shortener = Blueprint("shortener", __name__, static_folder="static", template_folder="template")
db = mongo_client.redirecturls
collection = db.redirecturls

@shortener.route("/", methods=["POST", "GET"])
def new():
    if request.method == "POST":
        f = request.form
        if "long" not in f.keys():
            flash("Missing required field: Long URL", 'warning')
            return redirect(request.url)
        if f["short"] == "":
            short = ''.join(choice(ascii_letters) for _ in range(6))
        else:
            short = f["short"]
        if not match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()"
                     r"@:%_\+.~#?&//=]*)", f["long"]):
            flash("URL '{}' is invalid, make sure it's in format https://www.example.com".format(f["long"]), 'warning')
            return redirect(request.url)
        if collection.find_one({"short": short}) is not None:
            flash("Alias '{}' already exists. If you were using a random alias, congrats, you should buy a lottery "
                  "ticket. Getting the same random alias has a 1 in 12,230,590,464 chance of happening, try again and "
                  "it should fix itself.".format(short), "warning")
            return redirect(request.url)
        collection.insert_one({"short": short, "to": f["long"]})
        flash(Markup("Success, alias&nbsp;<a href=\"{}\">{}</a>&nbsp;created".format(request.url_root + "s/" + short,
                                                                                     short)), "info")
        return redirect(request.url)
    else:
        return render_template("shortener/new.html", pth="s", rp={"s":"Shortener"})

@shortener.route("/<sub>")
def rdr(sub):
    r = collection.find_one({"short": sub})
    if r is None:
        abort(404)
    return redirect(r["to"])

