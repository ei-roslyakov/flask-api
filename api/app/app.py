import app.models.shared as models_shared
from app.support.support import setup_db

from flask import Flask, abort, jsonify, request

from .config import (
    API_PREFIX,
    APP_HOST,
    APP_PORT,
    APP_VERSION,
    PRODUCTION_DATABASE_PATH,
)

from app.support.request_handling import read_user_attributes_from_request  # noqa


app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db_uri = "postgresql+psycopg2://{}".format(PRODUCTION_DATABASE_PATH)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

db = setup_db(app, db_uri)
models_shared.db = db

from app.support.data_manipulation import (
    delete_user_by_id,
    init_test_data,
    find_user_by_id,
    get_all_users_in_db,
    add_new_user_to_db,
    modify_user_data_in_db,
)  # noqa


@app.route(API_PREFIX + "/init_data", methods=["POST"])
def init_test_data_endpoint():
    new_users = init_test_data(db)

    new_users = [obj.to_dict() for obj in new_users]
    resp = {"new_users": new_users}

    return jsonify(resp)


@app.route(API_PREFIX + "/users/<user_id>", methods=["PUT"])
def modify_user(user_id):
    if not user_id.isdigit():
        return abort(400)

    new_user_data = read_user_attributes_from_request(request.json)
    if not new_user_data:
        abort(400)

    user_to_be_modified = find_user_by_id(db, user_id)
    if not user_to_be_modified:
        return abort(404)

    edited_user = modify_user_data_in_db(db, user_to_be_modified, new_user_data)

    return jsonify(edited_user.to_dict())


@app.route(API_PREFIX + "/users", methods=["POST"])
def add_user():
    user = read_user_attributes_from_request(request.json)
    if not user:
        abort(400)

    add_new_user_to_db(db, user)

    return jsonify(user), 201


@app.route(API_PREFIX + "/users/<user_id>", methods=["GET"])
def get_single_user(user_id):
    if not user_id.isdigit():
        return abort(400)

    user = find_user_by_id(db, user_id)
    if not user:
        return abort(404)

    return jsonify(user.to_dict())


@app.route(API_PREFIX + "/users", methods=["GET"])
def get_users():
    users = get_all_users_in_db(db)

    return jsonify(users)


@app.route(API_PREFIX + "/users/<user_id>", methods=["DELETE"])
def remove_single_user(user_id):
    if not user_id.isdigit():
        return abort(400)

    user = find_user_by_id(db, user_id)
    if not user:
        return abort(404)

    delete_user_by_id(db, user_id)

    return "user deleted"


@app.route(API_PREFIX + "/version", methods=["GET"])
def get_version():
    resp = {
        "version": APP_VERSION,
        "short_name": "Test REST API for SQLite",
        "long_name": "Test REST API for SQLite, education purpose",
    }

    return jsonify(resp)


def main():
    with app.app_context():
        db.create_all()
    app.run(host=APP_HOST, port=APP_PORT, debug=True)


if __name__ == "__main__":
    main()
