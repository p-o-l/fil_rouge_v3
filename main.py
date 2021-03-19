from my_flask_package import app
# specifically need to import the 'app' variable to activate the flask app object.

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')