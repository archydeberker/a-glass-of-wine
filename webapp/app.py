from flask import Flask, request, render_template, url_for, redirect, send_file, after_this_request, \
    jsonify
import tempfile
import traceback
app = Flask(__name__)


@app.route('/')
def upload_page():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
