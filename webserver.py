import flask
from flask import render_template, redirect, url_for, request
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import os
from dotenv import load_dotenv
import pickle
import json
import traceback

from funcs.get_db import DATABASE
import config

load_dotenv()


app = flask.Flask(__name__)
app.secret_key = os.urandom(24)
app.config["DEBUG"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"  # DEVELOPMENT ONLY

app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_TOKEN")

API_BASE_URL = "https://discordapp.com/api"

discord = DiscordOAuth2Session(app)


@app.route("/")
def redirectHome():
    return redirect(url_for("home"))


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return discord.create_session()


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    try:
        discord.callback()
    except:
        return redirect(url_for("login"))

    return redirect(url_for("dashboard"))


@app.route("/dashboard/<int:id>")
def dashboardID(id):
    user = discord.fetch_user()
    currentSettings = DATABASE.server_settings.find_one({"id": id})
    del currentSettings["_id"]

    iconURL = (
        user.avatar_url if user.avatar_url is not None else user.default_avatar_url
    )

    return render_template(
        "dashboardID.html",
        currentSettings=json.dumps(currentSettings),
        describeSettings=json.dumps(config.describeSettings),
        username=user.name,
        discriminator=user.discriminator,
        userIconURL=iconURL,
        serverName=request.args.get("name"),
        attributes=json.dumps(config.attributes),
        serverIconURL=request.args.get(
            "icon", default="/static/imgs/default_server_icon.png"
        ),
    )


@app.route("/dashboard/save", methods=["POST"])
def save_changes():
    args = request.get_json()
    user = discord.fetch_user()
    check = validate_args(args)
    if not check["status"]:
        return check["response"], 400
    else:
        args = check["newArgs"]

    args["id"] = int(request.referrer.split("?")[0].split("/")[-1])
    print(json.dumps(args, indent=4))

    try:
        DATABASE.server_settings.update_one(
            {"id": args["id"]}, {"$set": args}, upsert=True
        )
    except Exception as e:
        print(traceback.format_exc())
        return traceback.format_exc(), 400

    return {"response": "success"}


def validate_args(args):
    removeKeys = ["logTo", "id"]
    allowedKeys = {
        "id": int,
        "abusiveFiltering": dict,
        "deleteComments": bool,
        "flirtationFiltering": dict,
        "identity_attackFiltering": dict,
        "incoherencyFiltering": dict,
        "inflammatoryFiltering": dict,
        "insultsFiltering": dict,
        "logTo": int,
        "prefixes": list,
        "profanityFiltering": dict,
        "punishment": dict,
        "sexualFiltering": dict,
        "threatsFiltering": dict,
        "toxicityFiltering": dict,
    }

    allowedAttributeKeys = {
        "enabled": bool,
        "threshold": int,
        "allow_nsfw": bool,
    }

    allowedPunishmentAttributeKeys = (
        "abusiveFiltering",
        "flirtationFiltering",
        "identity_attackFiltering",
        "incoherencyFiltering",
        "inflammatoryFiltering",
        "insultsFiltering",
        "profanityFiltering",
        "sexualFiltering",
        "threatsFiltering",
        "toxicityFiltering",
    )

    for k in removeKeys:
        try:
            del args[k]
        except:
            pass

    for key, val in args.items():
        if key not in allowedKeys.keys():
            return {"status": False, "response": f"Disallowed key {key}"}
        elif not isinstance(val, allowedKeys[key]):
            return {
                "status": False,
                "response": f"Disallowed key type {key} {type(val)} (should be {allowedKeys[key]})",
            }

        if isinstance(key, dict):
            if key.endswith("Filtering"):
                for ak, av in val.items():
                    if ak in allowedAttributeKeys.keys():
                        if not isinstance(av, allowedAttributeKeys[ak]):
                            return {
                                "status": False,
                                "response": f"Disallowed attribute key type {key} - {ak}: {av}",
                            }
                    else:
                        return {
                            "status": False,
                            "response": f"Disallowed attribute key {key} - {ak}",
                        }
        elif key == "prefixes":
            if len(val) > 10:
                return {
                    "status": False,
                    "response": f"Too many prefixes {len(val)}",
                }
        elif key == "punishment":
            for pk, pv in val.items():
                if pk not in allowedPunishmentAttributeKeys:
                    return {
                        "status": False,
                        "response": f"Invalid punishment key {pk}",
                    }
                if len(pv) > 10:
                    return {
                        "status": False,
                        "response": f"Too many punishments for {pk} - {len(pv)}",
                    }

    return {"status": True, "newArgs": args}


@app.route("/dashboard")
def dashboard():
    user = discord.fetch_user()
    data = getData(user)

    iconURL = (
        user.avatar_url if user.avatar_url is not None else user.default_avatar_url
    )

    return render_template(
        "dashboard.html",
        username=user.name,
        discriminator=user.discriminator,
        userIconURL=iconURL,
        guilds=json.dumps(data),
    )


def getData(user):
    guilds = [i for i in user.fetch_guilds() if i.permissions.manage_guild]
    guildIDs = [i.id for i in guilds]
    matches = [
        int(i["id"])
        for i in list(
            DATABASE.server_settings.find(
                {
                    "id": {
                        "$in": guildIDs,
                    },
                }
            )
        )
    ]

    servers = [guilds[guildIDs.index(i)] for i in matches]
    return [
        {
            "name": i.name,
            "id": f"{i.id}",
            "icon": i.icon_url
            if i.icon_url is not None
            else url_for("static", filename="imgs/default_server_icon.png"),
        }
        for i in servers
    ]


@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/tos")
def tos():
    return ""


@app.route("/privacy")
def privacy():
    return ""


@app.route("/report")
def report():
    return ""


app.run(debug=True)
