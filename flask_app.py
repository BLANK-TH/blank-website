from os.path import join
from secrets import token_urlsafe

import git
from flask import Flask, render_template, redirect, abort, send_from_directory, request

import subpages

app = Flask(__name__)
app.secret_key = token_urlsafe(32)
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
    if request.method == "POST":
        repo = git.Repo()
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong Request Type', 400


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


if __name__ == '__main__':
    app.run()
