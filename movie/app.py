from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client.dbjungle


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/list", methods=["GET"])
def show_movies():
    sortMode = request.args.get("sortMode", "likes")

    if sortMode == "likes":
        movies = list(db.movies.find({"trashed": False}, {}).sort("likes", -1))
    elif sortMode == "viewers":
        movies = list(db.movies.find({"trashed": False}, {}).sort("viewers", -1))
    elif sortMode == "date":
        movies = list(
            db.movies.find({"trashed": False}, {}).sort(
                [("open_year", -1), ("open_month", -1), ("open_day", -1)]
            )
        )

    else:
        return jsonify({"result": "failure"})

    return jsonify({"result": "success", "movies_list": movies})


@app.route("/api/list/trash", methods=["GET"])
def show_trash_movies():
    sortMode = request.args.get("sortMode", "likes")

    if sortMode == "likes":
        movies = list(db.movies.find({"trashed": True}, {}).sort("likes", -1))
    elif sortMode == "viewers":
        movies = list(db.movies.find({"trashed": True}, {}).sort("viewers", -1))
    elif sortMode == "date":
        movies = list(
            db.movies.find({"trashed": True}, {}).sort(
                [("open_year", -1), ("open_month", -1), ("open_date", -1)]
            )
        )
    else:
        return jsonify({"result": "failure"})

    return jsonify({"result": "success", "movies_list": movies})


@app.route("/api/like", methods=["POST"])
def like_movie():
    info_receive = request.form["info_give"]
    movie = db.movies.find_one({"title": info_receive})

    new_likes = movie["likes"] + 1

    result = db.movies.update_one(
        {"title": info_receive}, {"$set": {"likes": new_likes}}
    )

    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/restore", methods=["POST"])
def restore_movie():
    info_receive = request.form["info_give"]

    result = db.movies.update_one({"title": info_receive}, {"$set": {"trashed": False}})

    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/delete", methods=["POST"])
def delete0_movie():
    info_receive = request.form["info_give"]

    result = db.movies.delete_one({"title": info_receive})

    if result.deleted_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/trash", methods=["POST"])
def trash_movie():
    info_receive = request.form["info_give"]

    result = db.movies.update_one({"title": info_receive}, {"$set": {"trashed": True}})

    return jsonify({"result": "success"})


@app.route("/api/memoAdd", methods=["POST"])
def memo_add():
    info_receive_title = request.form["info_give_title"]

    memo_data = {"title": info_receive_title, "complete": False}
    result = db.memo.insert_one(memo_data)

    if result.acknowledged:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/memos", methods=["GET"])
def memo_show():
    title = list(db.memo.find({}))
    # print(title)

    return jsonify({"result": "success", "memo_list": title})


@app.route("/api/complete", methods=["POST"])
def complete_memo():
    info_receive = request.form["info_give"]

    result = db.memo.update_one({"title": info_receive}, {"$set": {"complete": True}})

    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/delete/memo", methods=["POST"])
def delete_memo():
    info_receive = request.form["info_give"]
    result = db.memo.delete_one({"title": info_receive})

    if result.deleted_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


@app.route("/api/memo_update", methods=["POST"])
def update_memo():
    info_new = request.form["info_new"]
    info_original = request.form["info_original"]

    result = db.memo.update_one({"title": info_original}, {"$set": {"title": info_new}})

    if result.modified_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure"})


if __name__ == "__main__":
    print(sys.executable)
    app.run("0.0.0.0", port=5000, debug=True)
#for git branch test