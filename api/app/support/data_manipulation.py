from app.models.users import User
from app.support.test_data import TEST_DATA


def init_test_data(db):
    new_users_created = []

    for item in TEST_DATA:
        new_user = User()

        new_user.name = item[0]
        new_user.last_name = item[1]
        new_user.description = item[2]
        new_user.employee = item[3]

        db.session.add(new_user)
        db.session.flush()

        new_users_created.append(new_user)

    db.session.commit()

    return new_users_created


def modify_user_data_in_db(db, user_by_modify, new_user_data):
    if "name" in new_user_data:
        user_by_modify.name = new_user_data["name"]
    if "last_name" in new_user_data:
        user_by_modify.last_name = new_user_data["last_name"]
    if "description" in new_user_data:
        user_by_modify.description = new_user_data["description"]
    if "employee" in new_user_data:
        user_by_modify.employee = new_user_data["employee"]

    db.session.flush()
    db.session.commit()

    return user_by_modify


def add_new_user_to_db(db, request_data):
    new_user = User()

    new_user.name = request_data["name"]
    new_user.last_name = request_data["last_name"]
    new_user.description = request_data["description"]
    new_user.employee = request_data["employee"]

    db.session.add(new_user)
    db.session.flush()

    db.session.commit()


def get_all_users_in_db(db):
    users = db.session.query(User).all()

    data_to_return = []
    for user in users:
        new_data = user.to_dict()
        data_to_return.append(new_data)

    return data_to_return


def find_user_by_id(db, user_id):
    return db.session.query(User).filter(User.id == user_id).scalar()


def delete_user_by_id(db, user_id):
    db.session.query(User).filter(User.id == user_id).delete(synchronize_session=False)

    db.session.commit()
