import atexit
import json
import os

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)  # fmt: skip
from werkzeug.utils import secure_filename

JSON_FNAME = 'urls.json'
APP_SECRET_KEY = '12345'
USER_FILES = 'user_files'

if os.path.exists(JSON_FNAME):
    with open(JSON_FNAME) as urls_f:
        urls = json.load(urls_f)
else:
    urls = {}

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY


def save_urls():
    with open(JSON_FNAME, 'w') as urls_f:
        json.dump(urls, urls_f)


atexit.register(save_urls)


@app.route('/')
def home():
    return render_template('index.html', session=session)


@app.route('/short-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        code = request.form['code']
        if code in urls:
            flash('Sorry, that Short Name is already taken!')
            return redirect(url_for('home'))
        if 'url' in request.form:
            url = request.form['url']
            urls[code] = {'url': url}
            session[code] = url
            return render_template('short_url.html', code=code, url=url)
        elif 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            fname = code + '_' + filename
            urls[code] = {'file': fname}
            session[code] = filename
            f.save(os.path.join(os.getcwd(), 'static', USER_FILES, fname))
            return render_template('short_url.html', code=code, url=fname)
    elif request.method == 'GET':
        return redirect(url_for('home'))


@app.route('/<string:code>')
def redirect_code(code):
    if code in urls:
        if 'url' in urls[code]:
            return redirect(urls[code]['url'])
        elif 'file' in urls[code]:
            return redirect(
                url_for('static', filename=os.path.join(USER_FILES, urls[code]['file']))
            )
    return abort(404)


@app.route('/api')
def api_session():
    return jsonify(session)


@app.errorhandler(404)
def err_404(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
