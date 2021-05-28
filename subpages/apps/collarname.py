from flask import Blueprint, render_template, redirect, url_for, request, flash
from PIL import Image, ImageFont, ImageDraw
from textwrap import wrap
from io import BytesIO
from api_helper import IMGUR_CLIENT
from requests import post
from os import getcwd

collarname = Blueprint("collar-name", __name__, static_folder="static", template_folder="template")

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
        else:
            MID_ORIGIN, TOP_ORIGIN, MAX_HEIGHT, MAX_WIDTH = int(f["midorigin"]), int(f["toporigin"]), \
                                                            int(f["maxheight"]), int(f["maxwidth"])
            name, size, xpadding,  ypadding = f["nametext"], int(f["fsize"]), int(f["xpad"]), int(f["ypad"])
            img = Image.open(getcwd() + "/static/app/collarname/{}.png".format(f["imagebase"]))
            draw = ImageDraw.Draw(img)

            font = ImageFont.truetype("consola.ttf", size)
            w, h = font.getsize(name)
            char_width = font.getsize("W")[0]
            lines = []
            if w + xpadding * 2 > MAX_WIDTH:
                h = 0
                w = MAX_WIDTH
                for line in wrap(name, width=(MAX_WIDTH - xpadding * 2) // char_width):
                    i, j = font.getsize(line)
                    if i > MAX_WIDTH:
                        print("Error in wrapping", i, MAX_WIDTH, (MAX_WIDTH - xpadding * 2) // char_width)
                        exit()
                    h += j + ypadding
                    lines.append(line)
                xpadding = 0
            if h + ypadding * 2 > MAX_HEIGHT:
                print("too tall")
                exit()

            dims = [(MID_ORIGIN - (w / 2) - xpadding, TOP_ORIGIN),
                    (MID_ORIGIN + (w / 2) + xpadding, TOP_ORIGIN + h + ypadding * 2)]
            draw.rectangle(dims, fill="#5d451b")

            if len(lines) < 2:
                draw.text((MID_ORIGIN, TOP_ORIGIN + ypadding), name, fill="black",
                          font=font, anchor="mt")
            else:
                offset = font.getsize(name)[1] + ypadding * 2
                y = TOP_ORIGIN + ypadding
                for i in lines:
                    draw.text((MID_ORIGIN, y), i, fill="black", font=font, anchor="mt")
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
        return render_template('app/collarname/generator.html', pth="app/collar-name",
                               imgur_url=a["imgur_url"] if "imgur_url" in a else None,
                               simg=a["simg"] if "simg" in a else None)

@collarname.route("/tutorial")
def tutorial():
    pass

@collarname.route("/faq")
def faq():
    pass
