from flask import Blueprint, current_app, render_template, request, redirect, flash, abort, Markup, url_for
from random import choice, randint
from string import ascii_letters
from re import match

shortener = Blueprint("shortener", __name__, static_folder="static", template_folder="template")

@shortener.record
def record(state):
    db = state.app.config.get("shortened.db")

    if db is None:
        raise Exception("This blueprint expects you to provide "
                        "database access through shortened.db")

@shortener.route("/", methods=["POST", "GET"])
def new():
    db = current_app.config["shortened.db"]
    a = request.args
    if "short" in a and "pin" in a:
        short = a["short"]
        flash(Markup("Success, alias&nbsp;<span class='highlightBlock'><a href=\"{}\">{}</a></span>&nbsp;created".format(request.url_root + "s/" + short,
                                                                                     short)), "info")
        return render_template("shortener/new.html", short=short, pin=a["pin"])
    elif request.method == "POST":
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
        if short in ["del", "delete"]:
            flash("'{}' is a protected name, think of another alias.".format(short), 'warning')
            return redirect(request.url)
        if db.first_filter(short=short) is not None:
            flash("Alias '{}' already exists. If you were using a random alias, congrats, you should buy a lottery "
                  "ticket. Getting the same random alias has a 1 in 12,230,590,464 chance of happening, try again and "
                  "it should fix itself.".format(short), "warning")
            return redirect(request.url)
        del_pin = str(randint(1000,9999))
        db.insert_one(short=short, long=f["long"], deletion_pin=del_pin)
        return redirect(url_for("shortener.new", short=short, pin=del_pin))
    else:
        return render_template("shortener/new.html", rp={"s":"Shortener"})

@shortener.route("/del/<sub>")
@shortener.route("/delete/<sub>")
def delete(sub):
    db = current_app.config["shortened.db"]
    a = request.args
    if "pin" not in a:
        flash("PIN not provided, deletion failed", 'warning')
        abort(401)
    fltr = db.first_filter(short=sub)
    if fltr is None:
        flash("'{}' is not a valid alias, deletion failed".format(sub), 'warning')
        return redirect("/s")
    if int(a["pin"]) != fltr.deletion_pin:
        abort(403)
    else:
        db.delete_one(fltr)
        flash("'{}' successfully deleted".format(sub), 'info')
        return redirect("/s")

@shortener.route("/<sub>")
def rdr(sub):
    db = current_app.config["shortened.db"]
    r = db.first_filter(short=sub)
    if r is None:
        abort(404)
    return redirect(r.long)

