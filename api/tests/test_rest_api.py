import copy
import os
import random
import uuid

import app.models.shared as models_shared
from app.app import API_PREFIX
from app.config import SQLALCHEMY_URI_KEY_NAME
from app.support.test_data import TEST_DATA

import pytest
import webtest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

TMP_FILE_PATH = "./tmp"


def create_app():
    """Create a fresh Flask app instance for testing"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    # Register API routes after database setup
    return app

def register_routes(app, api_prefix):
    """Register all API routes on the Flask app"""
    from flask import jsonify, request, abort
    from app.config import APP_VERSION

    @app.route(api_prefix + "/version", methods=["GET"])
    def get_version():
        resp = {
            "version": APP_VERSION,
            "short_name": "Test REST API for SQLite",
            "long_name": "Test REST API for SQLite, education purpose",
        }
        return jsonify(resp)

    @app.route(api_prefix + "/init_data", methods=["POST"])
    def init_test_data_endpoint():
        from app.support.data_manipulation import init_test_data
        import app.models.shared as models_shared

        new_users = init_test_data(models_shared.db)
        new_users = [obj.to_dict() for obj in new_users]
        resp = {"new_users": new_users}
        return jsonify(resp)

    @app.route(api_prefix + "/users", methods=["GET"])
    def get_users():
        from app.support.data_manipulation import get_all_users_in_db
        import app.models.shared as models_shared

        users = get_all_users_in_db(models_shared.db)
        return jsonify(users)

    @app.route(api_prefix + "/users/<user_id>", methods=["GET"])
    def get_single_user(user_id):
        from app.support.data_manipulation import find_user_by_id
        import app.models.shared as models_shared

        if not user_id.isdigit():
            return abort(400)

        user = find_user_by_id(models_shared.db, user_id)
        if not user:
            return abort(404)

        return jsonify(user.to_dict())

    @app.route(api_prefix + "/users", methods=["POST"])
    def add_user():
        from app.support.request_handling import read_user_attributes_from_request
        from app.support.data_manipulation import add_new_user_to_db
        import app.models.shared as models_shared

        user = read_user_attributes_from_request(request.json)
        if not user:
            abort(400)

        add_new_user_to_db(models_shared.db, user)
        return jsonify(user), 201

    @app.route(api_prefix + "/users/<user_id>", methods=["PUT"])
    def modify_user(user_id):
        from app.support.request_handling import read_user_attributes_from_request
        from app.support.data_manipulation import find_user_by_id, modify_user_data_in_db
        import app.models.shared as models_shared

        if not user_id.isdigit():
            return abort(400)

        new_user_data = read_user_attributes_from_request(request.json)
        if not new_user_data:
            abort(400)

        user_to_be_modified = find_user_by_id(models_shared.db, user_id)
        if not user_to_be_modified:
            return abort(404)

        edited_user = modify_user_data_in_db(models_shared.db, user_to_be_modified, new_user_data)
        return jsonify(edited_user.to_dict())

    @app.route(api_prefix + "/users/<user_id>", methods=["DELETE"])
    def remove_single_user(user_id):
        from app.support.data_manipulation import find_user_by_id, delete_user_by_id
        import app.models.shared as models_shared

        if not user_id.isdigit():
            return abort(400)

        user = find_user_by_id(models_shared.db, user_id)
        if not user:
            return abort(404)

        delete_user_by_id(models_shared.db, user_id)
        return "user deleted"


@pytest.fixture(scope="function")
def test_app():
    app = create_app()
    return app


@pytest.fixture(scope="function")
def test_db(test_app, request):
    def teardown():
        with test_app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(test_file_name):
            os.remove(test_file_name)

    if not os.path.exists(TMP_FILE_PATH):
        os.mkdir(TMP_FILE_PATH)

    test_uid = str(uuid.uuid4())

    test_data_file_name = test_uid
    test_file_name = os.path.join(TMP_FILE_PATH, test_data_file_name)
    test_file_name = os.path.abspath(test_file_name)
    test_file_name = os.path.normpath(test_file_name)
    test_file_name += ".sqlite"

    db_uri = "sqlite:///{}".format(test_file_name)

    # Configure Flask-SQLAlchemy properly
    test_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    # Create a fresh SQLAlchemy instance for testing
    db = SQLAlchemy()
    db.init_app(test_app)

    # Update the shared models reference
    models_shared.db = db

    # Create User model dynamically for this test db instance
    class User(db.Model):
        __tablename__ = "users"

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        last_name = db.Column(db.String)
        description = db.Column(db.String)
        employee = db.Column(db.Boolean)

        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "last_name": self.last_name,
                "description": self.description,
                "employee": self.employee,
            }

    # Make User available through models_shared
    models_shared.User = User

    from app.support.data_manipulation import init_test_data

    # Register API routes
    register_routes(test_app, API_PREFIX)

    with test_app.app_context():
        db.create_all()
        init_test_data(db)

    request.addfinalizer(teardown)
    return db


def test_version_route_returns_data(test_app, test_db):
    my_app = webtest.TestApp(test_app)
    resp = my_app.get(API_PREFIX + "/version")

    assert resp.status_int == 200
    assert resp.json

    required_attributes = ["version", "short_name", "long_name"]

    for required_attribute in required_attributes:
        assert required_attribute in resp.json


def test_returns_single_user_data(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    required_attributes = ["id", "name", "last_name", "description", "employee"]

    for expected_user_id in range(1, len(TEST_DATA) + 1):
        resp = my_app.get(API_PREFIX + "/users/{}".format(expected_user_id))

        assert resp.status_int == 200
        assert resp.json

        for required_attribute in required_attributes:
            assert required_attribute in resp.json


def test_remove_routing_able_to_remove_users(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    for expected_user_id in range(1, len(TEST_DATA) + 1):
        resp = my_app.get(API_PREFIX + "/users/{}".format(expected_user_id))

        assert resp.status_int == 200
        assert resp.json

        resp = my_app.delete(API_PREFIX + "/users/{}".format(expected_user_id))
        assert resp.status_int == 200

        resp = my_app.get(
            API_PREFIX + "/users/{}".format(expected_user_id), expect_errors=True
        )
        assert resp.status_int == 404


def test_add_user_to_db(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    new_user_data = {
        "name": "TEST_USER_NAME",
        "last_name": "TEST_LAST_NAME",
        "description": "TEST_POSITION",
        "employee": "true",
    }
    resp = my_app.post_json(API_PREFIX + "/users", new_user_data)
    assert resp.status_int == 201

    # resp = resp.json
    #
    # actual_result = my_app.get(API_PREFIX + '/users/{}'.format(resp["id"]))
    # assert actual_result.status_int == 200

    # TODO: read from database (using id in response and check that added data is correct
    # TODO: change reponse code! 201 code should be returned (https://www.restapitutorial.com/httpstatuscodes.html)


def test_modify_user_data(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    new_user_data = {
        "name": "test_name",
        "last_name": "test last name",
        "description": "description long description",
        "employee": True,
    }

    for expected_user_id in range(1, len(TEST_DATA) + 1):

        updated_user_data = copy.deepcopy(new_user_data)

        updated_user_data["name"] += " " + str(uuid.uuid4())
        updated_user_data["last_name"] += " " + str(uuid.uuid4())
        updated_user_data["description"] += " " + str(uuid.uuid4())
        updated_user_data["employee"] = random.choice([True, False])

        resp = my_app.put_json(
            API_PREFIX + "/users/{}".format(expected_user_id), updated_user_data
        )
        assert resp.status_int == 200

        assert resp.status_int == 200
        assert updated_user_data["name"] == resp.json["name"]
        assert updated_user_data["last_name"] == resp.json["last_name"]
        assert updated_user_data["description"] == resp.json["description"]
        assert updated_user_data["employee"] == resp.json["employee"]

        resp = my_app.get(API_PREFIX + "/users/{}".format(expected_user_id))
        assert resp.status_int == 200
        assert updated_user_data["name"] == resp.json["name"]
        assert updated_user_data["last_name"] == resp.json["last_name"]
        assert updated_user_data["description"] == resp.json["description"]
        assert updated_user_data["employee"] == resp.json["employee"]

        for user_id_to_test in range(expected_user_id + 1, len(TEST_DATA) + 1):
            non_damaged_user_resp = my_app.get(
                API_PREFIX + "/users/{}".format(user_id_to_test)
            )
            assert non_damaged_user_resp.status_int == 200
            expected_user_data = TEST_DATA[user_id_to_test - 1]

            non_damaged_user_data = non_damaged_user_resp.json
            assert non_damaged_user_data["name"] == expected_user_data[0]
            assert non_damaged_user_data["last_name"] == expected_user_data[1]
            assert non_damaged_user_data["description"] == expected_user_data[2]
            assert non_damaged_user_data["employee"] == expected_user_data[3]


def test_modify_user_data_source_code_by_jenecka0(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    for expected_user_id in range(1, len(TEST_DATA) + 1):

        new_user_data = {
            "name": str(uuid.uuid4()),
            "last_name": str(uuid.uuid4()),
            "description": str(uuid.uuid4()),
            "employee": random.choice([True, False]),
        }

        resp = my_app.put_json(
            API_PREFIX + "/users/{}".format(expected_user_id), new_user_data
        )
        assert resp.status_int == 200

        actual_result = my_app.get(API_PREFIX + "/users/{}".format(expected_user_id))
        assert actual_result.status_int == 200

        assert new_user_data["name"] == actual_result.json["name"]
        assert new_user_data["last_name"] == actual_result.json["last_name"]
        assert new_user_data["description"] == actual_result.json["description"]

        for tested_user_id in range(expected_user_id + 1, len(TEST_DATA) + 1):
            tested_user = my_app.get(API_PREFIX + "/users/{}".format(tested_user_id))
            assert tested_user.status_int == 200
            tested_user = tested_user.json

            data_to_check = TEST_DATA[tested_user_id - 1]

            assert tested_user["name"] == data_to_check[0]
            assert tested_user["last_name"] == data_to_check[1]
            assert tested_user["description"] == data_to_check[2]
            assert tested_user["employee"] == data_to_check[3]


def test_lack_of_attributes(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    new_user_data = {
        "last_name": "TEST_LAST_NAME",
        "description": "TEST_POSITION",
        "employee": "true",
    }

    resp = my_app.post_json(API_PREFIX + "/users", new_user_data, expect_errors=True)
    assert resp.status_int == 400

    new_user_data = {
        "name": "TEST_USER_NAME",
        "description": "TEST_POSITION",
        "employee": "true",
    }

    resp = my_app.post_json(API_PREFIX + "/users", new_user_data, expect_errors=True)
    assert resp.status_int == 400

    new_user_data = {
        "name": "TEST_USER_NAME",
        "last_name": "TEST_LAST_NAME",
        "employee": "true",
    }

    resp = my_app.post_json(API_PREFIX + "/users", new_user_data, expect_errors=True)
    assert resp.status_int == 400

    new_user_data = {
        "name": "TEST_USER_NAME",
        "last_name": "TEST_LAST_NAME",
        "description": "TEST_POSITION",
    }

    resp = my_app.post_json(API_PREFIX + "/users", new_user_data, expect_errors=True)
    assert resp.status_int == 400


def test_no_user_to_delete_in_db(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    user_id = random.randrange(100000000000, 200000000000000000000)

    resp = my_app.delete(API_PREFIX + "/users/{}".format(user_id), expect_errors=True)
    assert resp.status_int == 404


def test_get_version_app(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    resp = my_app.get(API_PREFIX + "/version")

    assert resp.status_int == 200


def test_connection_to_db(test_app, test_db):
    my_app = webtest.TestApp(test_app)

    resp = my_app.get(
        API_PREFIX + "/users/{}".format(random.randrange(1, len(TEST_DATA) + 1))
    )

    assert resp.status_int == 200
