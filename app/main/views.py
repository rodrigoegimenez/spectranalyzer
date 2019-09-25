from flask import render_template, url_for, request
from werkzeug.utils import secure_filename
from . import main
from .forms import NameForm
import os
# from .. import db
# from ..models import User
from spectranalyzer import LaurdanFitter
from zipfile import ZipFile
from glob import glob


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/sendfile', methods=['GET', 'POST'])
def sendfile():
    form = NameForm()
    if form.validate_on_submit():
        print(form.filefield.data)
        print(form.fitter.data)
        print(request.files)
        f = form.filefield.data
        filepath = (
            f"""{main.root_path}{os.path.sep}.."""
            f"""{os.path.sep}static{os.path.sep}""")
        filename = f"{secure_filename(f.filename)}"
        f.save(f"{filepath}{filename}")
        os.chdir(filepath)
        fitter = LaurdanFitter(filename)
        fitter.fit_all_columns(export=True, write_images=True)
        zipfile = ZipFile(f"{filepath}{fitter.name}.zip", "w")
        zipdir(f"{fitter.name}", zipfile)
        zipfile.write(filename)
        zipfile.close()
        os.chdir("..")
        url = url_for('static', filename=f"{fitter.name}.zip")
        imgs = []
        for file in sorted(glob(f"{filepath}{fitter.name}/*.png")):
            file = os.path.sep.join(file.split(os.path.sep)[-2:])
            imgs.append(url_for('static', filename=file))
        return render_template('result.html', url=url, imgs=imgs)
        # f"<a href={url}>link</a>"  # redirect(url_for('.index'))
    return render_template('sendfile.html', form=form)


def zipdir(path, ziph):
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
