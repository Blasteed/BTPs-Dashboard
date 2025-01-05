import os
import asyncio

from scripts.get_btp_data_async import get_btp_data

from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, redirect, url_for


app = Flask(__name__)


DATE_FORMAT = "%H:%M %d/%m/%Y"


###############################
#          METHODS            #
###############################

def load_btp_data():
    print("Start - Getting BTPs Data")

    data = asyncio.run(get_btp_data())

    print("Start - Got BTPs Data")

    return data


def get_refresh_time():
    refresh_time = datetime.now().strftime(DATE_FORMAT)

    print("Refresh Time - Got Refresh Time | Refreshed at:", refresh_time)

    return refresh_time

###############################


btp_data = load_btp_data()
refresh_time = get_refresh_time()


@app.route('/')
def home():
    global btp_data, refresh_time

    return render_template('btp.html', title='Karfee | BTP',
                           btp_data=btp_data,
                           refresh_time=refresh_time,
                           )


@app.route('/refresh', methods=['POST'])
def refresh():
    global btp_data, refresh_time

    btp_data = load_btp_data()

    refresh_time = get_refresh_time()

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
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
