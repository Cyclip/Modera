import flask
from flask import render_template

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


app.run()
