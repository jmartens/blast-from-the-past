from flask import render_template, request
from app import app, db

from app.models import Image, Roi

import os


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

