from io import BytesIO
from os import getcwd
from textwrap import wrap

from PIL import Image, ImageFont, ImageDraw
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from requests import post

from api_helper import IMGUR_CLIENT

collarname = Blueprint("collar-name", __name__, static_folder="static", template_folder="template")

default_values = {
    "normal": {
        "nametext": "I'm cute!",
        "fsize": "10",
        "fcolour": "#000000",
        "bcolour": "#5d451b",
        "xpad": "2",
        "ypad": "2",
        "midorigin": "287",
        "toporigin": "258",
        "maxheight": "125",
        "maxwidth": "94"
    },
    "elina": {
        "nametext": "I'm cute!",
        "fsize": "15",
        "fcolour": "#908989",
        "midorigin": "383",
        "toporigin": "333",
        "maxheight": "18",
        "maxwidth": "75",
        "xpad": "0",
        "ypad": "2",
    }
}


@collarname.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        f = request.form
        if f["imagebase"] == "custom":
            ctmimg = request.files["customfile"]
            if ctmimg.filename == '':
                flash("No image provided for custom base", "warning")
                return redirect(request.url)
            if ctmimg.filename[-4:].lower() != ".png":
                flash("Custom file must be a PNG", "warning")
                return redirect(request.url)
            img = Image.open(request.files["customfile"].stream)
        else:
            img = Image.open(getcwd() + "/static/app/collarname/{}.png".format(f["imagebase"]))
        session["cnnpastform"] = request.form
        MID_ORIGIN, TOP_ORIGIN, MAX_HEIGHT, MAX_WIDTH = int(f["midorigin"]), int(f["toporigin"]), \
                                                        int(f["maxheight"]), int(f["maxwidth"])
        name, size, xpadding, ypadding = f["nametext"], int(f["fsize"]), int(f["xpad"]), int(f["ypad"])
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(getcwd() + "/static/fonts/Consolas.ttf", size)
        w, h = font.getsize(name)
        char_width = font.getsize("W")[0]
        lines = []
        if w + xpadding * 2 > MAX_WIDTH:
            h = 0
            w = MAX_WIDTH
            for line in wrap(name, width=(MAX_WIDTH - xpadding * 2) // char_width):
                i, j = font.getsize(line)
                if i > MAX_WIDTH:
                    return "Error in Mapping", 500
                h += j + ypadding
                lines.append(line)
            xpadding = 0
        if h + ypadding * 2 > MAX_HEIGHT:
            flash("Text Too Long, try shortening it or decreasing the font size.", "warning")
            return redirect(request.url)

        dims = [(MID_ORIGIN - (w / 2) - xpadding, TOP_ORIGIN),
                (MID_ORIGIN + (w / 2) + xpadding, TOP_ORIGIN + h + ypadding * 2)]
        draw.rectangle(dims, fill=f["bcolour"])

        if len(lines) < 2:
            draw.text((MID_ORIGIN, TOP_ORIGIN + ypadding), name, fill=f["fcolour"],
                      font=font, anchor="mt")
        else:
            offset = font.getsize(name)[1] + ypadding * 2
            y = TOP_ORIGIN + ypadding
            for i in lines:
                draw.text((MID_ORIGIN, y), i, fill=f["fcolour"], font=font, anchor="mt")
                y += offset
        buf = BytesIO()
        img.save(buf, format="PNG")
        rq = post("https://api.imgur.com/3/upload.json", data={"image": buf.getvalue()},
                  headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
        cropped = img.crop((225, 182, 349, 384))
        cropped_buf = BytesIO()
        cropped.save(cropped_buf, format="PNG")
        rq2 = post("https://api.imgur.com/3/upload.json", data={"image": cropped_buf.getvalue()},
                   headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
        if rq.ok and rq2.ok:
            fn = rq.json()["data"]["link"]
            fn2 = rq2.json()["data"]["link"]
            return redirect(url_for("app.collar-name.index", imgur_url=fn, simg=fn2))
        else:
            flash("Unable to upload to imgur, try again later", "error")
            return redirect(request.url)
    else:
        a = request.args
        return render_template('app/collarname/generator.html',
                               imgur_url=a["imgur_url"] if "imgur_url" in a else None,
                               simg=a["simg"] if "simg" in a else None,
                               pastvalues=session.pop("cnnpastform") if "cnnpastform" in session else default_values[
                                   "normal"])


@collarname.route("/elina", methods=["POST", "GET"])
def elina():
    if request.method == "POST":
        f = request.form
        session["cnepastform"] = request.form
        img = Image.open(getcwd() + "/static/app/collarname/elina.png")
        MID_ORIGIN, TOP_ORIGIN, MAX_HEIGHT, MAX_WIDTH = int(f["midorigin"]), int(f["toporigin"]), \
                                                        int(f["maxheight"]), int(f["maxwidth"])
        name, size, xpadding, ypadding = f["nametext"], int(f["fsize"]), int(f["xpad"]), int(f["ypad"])
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(getcwd() + "/static/fonts/BITCBLKAD.ttf", size)
        w, h = font.getsize(name)
        if w + xpadding * 2 > MAX_WIDTH or h + ypadding * 2 > MAX_HEIGHT:
            flash("Text Too Long, try shortening it or decreasing the font size.", "warning")
            return redirect(request.url)

        draw.text((MID_ORIGIN, TOP_ORIGIN + ypadding), name, fill=f["fcolour"],
                  font=font, anchor="mm")

        buf = BytesIO()
        img.save(buf, format="PNG")
        rq = post("https://api.imgur.com/3/upload.json", data={"image": buf.getvalue()},
                  headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
        cropped = img.crop((330, 255, 437, 344))
        cropped_buf = BytesIO()
        cropped.save(cropped_buf, format="PNG")
        rq2 = post("https://api.imgur.com/3/upload.json", data={"image": cropped_buf.getvalue()},
                   headers={"Authorization": 'Client-ID ' + IMGUR_CLIENT})
        if rq.ok and rq2.ok:
            fn = rq.json()["data"]["link"]
            fn2 = rq2.json()["data"]["link"]
            return redirect(url_for("app.collar-name.elina", imgur_url=fn, simg=fn2))
        else:
            flash("Unable to upload to imgur, try again later", "error")
            return redirect(request.url)
    else:
        a = request.args
        return render_template('app/collarname/generator-elina.html',
                               imgur_url=a["imgur_url"] if "imgur_url" in a else None,
                               simg=a["simg"] if "simg" in a else None,
                               pastvalues=session.pop("cnepastform") if "cnepastform" in session else default_values[
                                   "elina"])


@collarname.route("/tutorial")
def tutorial():
    return render_template("app/collarname/tutorial.html")


@collarname.route("/tutorial/elina")
def tutorial_elina():
    return render_template("app/collarname/tutorial-elina.html")
