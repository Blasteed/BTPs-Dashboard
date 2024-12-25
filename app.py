import os
import asyncio
from flask import Flask, render_template, send_from_directory, redirect, url_for
from scripts.get_btp_data_async import get_btp_data


app = Flask(__name__)


refreshed = False


loading = True
print("Start - Getting BTPs Data")
btp_data = asyncio.run(get_btp_data())
print("Start - Got BTPs Data")
loading = False


@app.route('/')
def home():
    global refreshed, btp_data, loading

    return render_template('btp.html', title='Karfee | BTP', btp_data=btp_data, loading=loading)


@app.route('/refresh', methods=['POST'])
def refresh():
    global refreshed, btp_data, loading

    loading = True
    print("\"/refresh\" - Getting BTPs Data")
    btp_data = asyncio.run(get_btp_data())
    print("\"/refresh\" - Got BTPs Data")
    loading = False

    refreshed = True

    return redirect(url_for('home'))


# @app.route('/about')
# def about():
#     return render_template('about.html', title='Karfee | About')


# @app.route('/btp')
# def btp():
#     return render_template('btp.html', title='Karfee | BTP', btp_data=btp_data)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/icons'), 'Karfee.png')


@app.route('/icons/<path:filename>')
def icons(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/icons'), filename)


# @app.route('/css/<path:filename>')
# def css(filename):
#     return send_from_directory(os.path.join(app.root_path, 'static/css'), filename)


# @app.route('/js/<path:filename>')
# def js(filename):
#     return send_from_directory(os.path.join(app.root_path, 'static/js'), filename)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
