from os.path import join
from secrets import token_urlsafe

import git
import requests
from flask import Flask, render_template, redirect, abort, send_from_directory, request, flash
from flask_sqlalchemy import SQLAlchemy

import subpages
from api_helper import github_valid, SQL_USERNAME, SQL_PASSWORD, SQL_URI, SQL_HOSTNAME

app = Flask(__name__)
app.secret_key = token_urlsafe(32)
app.config["SQLALCHEMY_DATABASE_URI"] = SQL_URI.format(SQL_USERNAME, SQL_PASSWORD, SQL_HOSTNAME)
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config["db"] = db


class CuspDatabase(object):
    def __init__(self, model):
        self.model = model

    def first_filter(self, *args, **kwargs):
        return self.model.query.filter_by(*args, **kwargs).first()

    def insert_one(self, *args, **kwargs):
        q = self.model(*args, **kwargs)
        db.session.add(q)
        db.session.commit()

    def delete_one(self, *args, **kwargs):
        db.session.delete(*args, **kwargs)
        db.session.commit()


def setup_shortened_db(db):
    class Shortened(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        short = db.Column(db.VARCHAR(200), unique=True, nullable=False)
        long = db.Column(db.VARCHAR(200), nullable=False)
        deletion_pin = db.Column(db.Integer, nullable=False)

    return CuspDatabase(Shortened)


app.config["shortened.db"] = setup_shortened_db(db)

app.register_blueprint(subpages.info, url_prefix="")
app.register_blueprint(subpages.app, url_prefix="/app")
app.register_blueprint(subpages.shortener, url_prefix="/s")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/error/<code>')
def re(code):
    abort(int(code))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/admin')
@app.route('/dashboard')
def fda():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


@app.route("/update_server", methods=["POST"])
def webhook():
    signature = request.headers.get('X-Hub-Signature')
    if not github_valid(signature, request.data):
        abort(403)
    elif request.method == "POST":
        repo = git.Repo()
        origin = repo.remotes.origin
        repo.git.reset('--hard')
        repo.git.clean("-fd")
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        abort(400)


@app.route("/create_all")
def cr():
    if "pswd" not in request.args or request.args["pswd"] != SQL_PASSWORD:
        abort(403)
    else:
        db.create_all()
        return 'Success', 200


@app.route("/cat")
def cat():
    rq = requests.get("https://thecatapi.com/api/images/get")
    if rq.ok:
        return render_template("cat.html", pth="cat", uri=rq.url)
    else:
        flash("ಥ_ಥ I couldn't get a cat image", "error")
        return redirect("/")


@app.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(410)
def gone(e):
    return render_template('errors/410.html'), 410


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
