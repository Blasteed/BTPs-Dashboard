import app as flask_app


if __name__ == "__main__":
    flask_app.run(debug=False, use_reloader=False)


# Command to start: gunicorn --bind 0.0.0.0:5000 wsgi:app
