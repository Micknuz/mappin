import datetime
import flask
from flask import Flask, request, render_template, redirect, url_for, g, flash

from model import *
import db

from _exceptions import *

app = Flask(__name__)

from member_controller import *
import utils

@app.route("/")
def index():
    if g.user:
        return map_list_of(g.user.id)
    else:
        return map_list_of(None)

@app.route("/map")
@app.route("/map/list")
def map_list():
    return map_list_of('admin')


@app.route("/map/create", methods=["POST", "GET"])
@login_required
def map_create():
    if request.method == "POST":
        name = request.values.get("name")
        description = request.values.get("description")
        m = Map(name=name, description=description, manager_id=current_user().id)
        db.session.add(m)
        db.session.commit()
        return redirect(url_for("map_list"))
    elif request.method == "GET":
        return render_template("map_create.html")

@app.route("/map/list/by_user/<string:id>")
def map_list_of(id):
    if not id:
        maps = db.session.query(Map).all()
    else:
        maps = db.session.query(Map).filter_by(manager_id=id)

    return render_template("map_list.html", maps=maps)

@app.route("/map/<int:id>")
def map_view(id):
    m = db.session.query(Map).filter_by(id=id).first()
    logined = current_user() is not None
    form = PinForm()
    form.action = u'pin_add'
    url_form = UrlForm()
    url_form.action = u'url_add'
    return render_template("map_view.html", map=m, logined=logined, form=form, url_form=url_form)

@app.route("/map/<int:map_id>/pin/add", methods=["POST"])
@login_required
def pin_add(map_id):
    m = db.session.query(Map).filter_by(id=map_id).first()

    if m.manager_id != g.user.id and g.user.privileged is not True:
        flash('no privilige')
        return utils.redirect_back('map_list')

    mp = Mappin()
    name = request.values.get("name")
    description = request.values.get("description")
    lat = request.values.get("lat")
    lng = request.values.get("lng")
    score = request.values.get("score")
    address = request.values.get("address")
    pin = Pin(name=name, description=description, lat=lat, lng=lng,
            score=score, address=address)
    mp.pin = pin
    m.pins.append(mp)
    db.session.commit()

    return redirect(url_for("map_view", id=map_id))

@app.route("/pin/edit/<int:pin_id>", methods=['POST','GET'])
@login_required
def pin_edit(pin_id):
    p = Pin.query.filter_by(id=pin_id).first()
    if request.method == 'POST':
        form = PinForm(request.form)
        if form.validate():
            for key, value in form.data.items():
                setattr(p, key, value)
            db.session.commit()
            
            return redirect(url_for('map_view', id=p.maps[0].map_id))
        else:
            flash('form not valid')

    form = PinForm(obj=p)
    form.id = pin_id
    form.action = u'pin_edit'
    return render_template("pin_edit.html", form=form) 

@app.route("/map/<int:map_id>/unlink/<int:pin_id>", methods=['GET'])
@login_required
def mappin_unlink(map_id, pin_id):
    if not map_id:
        Mappin.query.filter_by(pin_id=pin_id).delete()
    else:
        Mappin.query.filter_by(map_id=map_id, pin_id=pin_id).delete()
    db.session.commit()
    return redirect(url_for('map_view', id=map_id))

@app.route("/pin/delete/<int:pin_id>")
@login_required
def pin_delete(pin_id):
    mappin_unlink(0, pin_id)
    Pin.query.filter_by(id=pin_id).delete()
    db.session.commit()
    return redirect(url_for("pin_list"))

@app.route("/pin/list")
def pin_list():
    pins = Pin.query.all()
    return render_template("pin_list.html", pins=pins)

@app.route("/url/add", methods=['POST','GET'])
@login_required
def url_add():
    pin_id = request.values.get('url_pin_id');
    url = Url()
    url.pin_id = pin_id

    if request.method == 'POST':
        form = UrlForm(request.form)
        if form.validate():
            for key, value in form.data.items():
                setattr(url, key, value)
            db.session.add(url)
            db.session.commit()
            
            return utils.redirect_back('map_list')
        else:
            flash('form not valid')


app.secret_key = "!%)NDVSO)UJ!@"

if __name__ == "__main__":
    app.run(debug=True)
