from flask import render_template, request
from app import app, db

from app.models import Image, Roi

import os

from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from app.models import Roi


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)

    images = Image.query.filter(Image.rois.any()).paginate(page, 5, False)

    return render_template('index.html', title='Home', images=images)


@app.route('/latest')
def latest():
    page = request.args.get('page', 1, type=int)

    # latest images order by time created descending
    images = Image.query.filter(Image.rois.any()).order_by(Image.created.desc()).paginate(page, 5, False)

    return render_template('index.html', title='Home', images=images)

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])


@app.route('/roi', methods=('GET', 'POST'))
def roi():

    form = MyForm()
    if form.validate_on_submit():
        return redirect('/index')

    id = request.args.get('id')
    roi = Roi.query.get(id)

    return render_template('roi.html', form=form, title='', roi=roi)

#    return render_template('roi.html', title='', roi=roi)


@app.route("/roi/<id>")
def roi(id):
    roi_form = model_form(Roi, db_session=db.session)
    model = Roi.query.get(id)
    form = roi_form(request.form, model)

    if request.method == 'POST' and form.validate():
        form.populate_obj(model)
        model.put()
        flash("ROI updated")
        return redirect(url_for("index"))
    return render_template("roi.html", form=form, roi=model)
