from io import BytesIO

from PIL import Image
from flask import Blueprint, Response, render_template, redirect, url_for, request, flash, current_app, \
    stream_with_context
from flask_httpauth import HTTPBasicAuth
from requests import post
from werkzeug.security import check_password_hash

from api_helper import is_human, ADMIN_HASH, IMGUR_CLIENT

dynamiccatalog = Blueprint("dynamic_catalog", __name__, static_folder="static", template_folder="template")
auth = HTTPBasicAuth()


@dynamiccatalog.record
def record(state):
    db = state.app.config.get("dyn.db")
    if db is None:
        raise Exception("This blueprint expects you to provide database access through dyn.db")


@auth.verify_password
def verify_password(username, password):
    if username == "admin" and check_password_hash(ADMIN_HASH, password):
        return "admin"


@dynamiccatalog.route("/")
def index():
    db = current_app.config["dyn.db"]
    page = request.args.get('page', 1, type=int)
    textures = db.model.query.order_by(db.model.id.desc()).paginate(page=page, per_page=10)
    return render_template("app/dynamiccatalog/index.html", textures=textures)


@dynamiccatalog.route("/add", methods=["POST", "GET"])
def add():
    db = current_app.config["dyn.db"]
    if request.method == "POST":
        f = request.form
        data = {"type": f["type"]}
        if request.files["resfile"].filename[-4:].lower() != ".png":
            flash("Texture file must be a PNG", "warning")
            return redirect(request.url)
        buf = BytesIO()
        Image.open(request.files["resfile"]).save(buf, format="PNG")
        rq = post("https://api.imgur.com/3/upload.json", data={"image": buf.getvalue()},
                  headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
        if rq.ok:
            data["url"] = rq.json()["data"]["link"]
        else:
            flash("Unable to upload to Imgur, try again later", "error")
            return redirect(request.url)
        data["author"] = f["author"] if len(f["author"].strip()) > 0 else None
        if "preview" in f:
            if request.files["preview"].filename[-4:].lower() != ".png":
                flash("Preview file must be a PNG", "warning")
                return redirect(request.url)
            buf = BytesIO()
            Image.open(request.files["preview"]).save(buf, format="PNG")
            rq = post("https://api.imgur.com/3/upload.json", data={"image": buf.getvalue()},
                      headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
            if rq.ok:
                data["preview"] = rq.json()["data"]["link"]
        data["notes"] = f["notes"] if len(f["notes"].strip()) > 0 else None
        db.insert_one(**data)
        flash("Successfully added new texture to catalog.", "info")
        return redirect(request.url)
    else:
        return render_template("app/dynamiccatalog/add.html")


@dynamiccatalog.route("/filter", methods=["POST", "GET"])
def fltr():
    if request.method == "POST" or len(request.args) > 0:
        db = current_app.config["dyn.db"]
        if request.method == "POST":
            f = request.form
        else:
            f = request.args
        query = db.model.query
        fltrd = False
        if "id" in f and len(f["id"].strip()) > 0:
            query = query.filter_by(id=f["id"])
            fltrd = True
        if "author" in f and len(f["author"].strip()) > 0:
            query = query.filter(db.model.author.contains(f["author"]))
            fltrd = True
        if "type" in f and f["type"] != "None":
            query = query.filter_by(type=f["type"])
            fltrd = True
        if "notes" in f and len(f["notes"].strip()) > 0:
            query = query.filter(db.model.notes.contains(f["notes"]))
            fltrd = True
        if not request.method == "POST" and not fltrd:
            return render_template("app/dynamiccatalog/filter.html")
        return render_template("app/dynamiccatalog/filter_results.html",
                               textures=query.order_by(db.model.id.desc()).all(), fltr_u=url_for(
                "app.dynamic_catalog.fltr", **{i: j for i, j in f.items()
                                               if len(j.strip()) > 0 and not (i == "type" and j == "None")}))
    else:
        return render_template("app/dynamiccatalog/filter.html")


@dynamiccatalog.route("/export", methods=["POST", "GET"])
def export():
    if request.method == "POST":
        captcha_response = request.form["g-recaptcha-response"]
        if is_human(captcha_response):
            def generate():
                db = current_app.config["dyn.db"]
                yield "ID,Author,Type,URL,Preview,Notes\n"
                for i in db.get_all():
                    yield "{},{},{},{},{},{}\n".format(i.id, i.author, i.type, i.url, i.preview, i.notes)

            return Response(stream_with_context(generate()), mimetype="text/csv")
        else:
            flash("You failed the reCAPTCHA", 'warning')
            return redirect(request.url)
    else:
        return render_template("app/dynamiccatalog/export.html")


@dynamiccatalog.route("/delete/<id>")
@auth.login_required
def delete(id):
    db = current_app.config["dyn.db"]
    fltr = db.first_filter(id=id)
    if fltr is None:
        flash("ID '{}' does not exist".format(id), 'warning')
        return redirect(url_for("app.dynamic_catalog.index"))
    db.delete_one(fltr)
    flash("'{}' successfully deleted".format(id), 'info')
    return redirect(url_for("app.dynamic_catalog.index"))
