from flask import Flask, render_template, send_from_directory
import os


app = Flask(__name__)


@app.route('/')
def home():

    return render_template('index.html', title='Karfee | Home')

@app.route('/about')
def about():

    return render_template('about.html', title='Karfee | About')


@app.route('/icons/<path:filename>')
def serve_static(filename):

    return send_from_directory(os.path.join(app.root_path, 'static/icons'), filename)


@app.route('/favicon.ico')
def favicon():

    return send_from_directory(os.path.join(app.root_path, 'static/icons'), 'Karfee.png')


if __name__ == '__main__':

    app.run(debug=True)
